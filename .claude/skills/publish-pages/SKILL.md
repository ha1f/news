---
description: "ニュースキュレーションを実行し、GitHub Pagesにデプロイする"
---

# GitHub Pages デプロイ

`/curate-news` でニュースキュレーションを実行し、結果を main ブランチ向けの PR として作成する。PR がマージされると GitHub Pages に自動デプロイされる。

処理が長いため、各ステップの開始時に進捗をユーザーに表示する:

| タイミング | 表示 |
|---|---|
| 初回セットアップ検出時 | `🔧 GitHub Pages の初回セットアップを行います` |
| curate-news 開始時 | `📰 ニュースキュレーションを実行します` |
| ブランチ作成時 | `🌿 ブランチ pages/{stem} を作成します` |
| PR 作成時 | `📝 PR を作成します` |

## 手順

### 1. 初回セットアップの確認

main ブランチに `_config.yml` が存在するか確認する。存在すればステップ 3 へ進む。

```bash
git show origin/main:_config.yml 2>/dev/null
```

### 2. 初回セットアップ

GitHub Pages 用の Jekyll 最小構成を追加する PR を作成する。

#### 2.1 ブランチの作成

```bash
git fetch origin main
git checkout -b setup-github-pages origin/main
```

#### 2.2 Jekyll 構成ファイルの作成

以下のファイルをリポジトリルートに作成する。Jekyll がマークダウンを HTML に変換してホスティングするために必要。

**`_config.yml`:**
```yaml
title: "ha1f news"
theme: minima
baseurl: "/news"
header_pages: []
```

**`index.md`:**
```markdown
---
layout: home
---
```

**`_posts/.gitkeep`:** 空ファイル

#### 2.3 コミット・プッシュ・PR 作成

```bash
git add _config.yml index.md _posts/.gitkeep
git commit -m "Setup GitHub Pages with Jekyll"
git push -u origin setup-github-pages
gh pr create --base main --title "Setup GitHub Pages" --body "Jekyll最小構成の追加" --draft
```

#### 2.4 GitHub Pages の有効化

リポジトリのオーナーとリポジトリ名を取得して Pages API を呼ぶ:

```bash
gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pages -X POST -f source[branch]=main -f source[path]=/
```

既に有効な場合のエラーは無視してよい。

#### 2.5 ユーザーへの案内

セットアップ PR の URL を表示し、マージを依頼する。マージが完了したら `/publish-pages` を再度実行するよう案内して、元のブランチに戻って終了する。

### 3. `/curate-news` の実行

Skill ツールで `curate-news` を実行する。

完了後、最新の出力ファイルを特定する:
```bash
ls -t .claude/skills/curate-news/output/*.md | grep -v gitkeep | head -1
```

出力ファイルの内容を Read で読み込む。ファイル名のステム部分（例: `2026-03-18-23cfb1cf`）を後続のステップで使う。

### 4. ブランチの作成

現在のブランチを確認してから、最新の origin/main からトピックブランチを作成する。ブランチ名には出力ファイルのステムを使い、出力と1対1で対応させる。

```bash
git branch --show-current
git fetch origin main
git checkout -b pages/{ステム} origin/main
```

同名ブランチが既に存在する場合は `git checkout pages/{ステム}` で切り替える。

### 5. 投稿ファイルの作成

ステップ 3 で読み込んだ出力内容に Jekyll フロントマターを付加し、`_posts/` に配置する。Jekyll はファイル名の日付でソートするため `{YYYY-MM-DD}-news.md` の命名規則に従う。

ファイルパス: `_posts/{YYYY-MM-DD}-news.md`

```yaml
---
layout: post
title: "{YYYY}年{M}月{D}日"
date: {YYYY-MM-DD}
---

{curate-news の出力内容（先頭の `## ニュース (...)` 見出しは除く。タイトルと重複するため）}
```

### 6. コミットと PR 作成

```bash
git add _posts/
git commit -m "Add news curation for {YYYY-MM-DD}"
git push -u origin pages/{ステム}
```

PR を作成する:
```bash
gh pr create --base main --title "ニュース: {YYYY-MM-DD}" --body "$(cat <<'EOF'
/curate-news の結果を GitHub Pages にデプロイします。

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" --draft
```

PR の URL をユーザーに表示する。

### 7. 元のブランチに戻る

ステップ 4 で確認したブランチに戻る。
