---
description: "ニュースキュレーションを実行し、GitHub Pagesにデプロイする"
---

# GitHub Pages デプロイ

`/curate-news` でニュースキュレーションを実行し、結果を main ブランチ向けの PR として作成する。PR がマージされると GitHub Pages に自動デプロイされる。

各ステップの開始時に進捗を表示する:

| タイミング | 表示 |
|---|---|
| curate-news 開始時 | `📰 ニュースキュレーションを実行します` |
| ブランチ作成時 | `🌿 ブランチ pages/{stem} を作成します` |
| PR 作成時 | `📝 PR を作成します` |

## 手順

### 0. 前提チェック

main ブランチに `_config.yml` が存在するか確認する:
```bash
git fetch origin main
git show origin/main:_config.yml 2>/dev/null
```

存在しない場合は「付録: 初回セットアップ」の手順でセットアップを行い、完了後に改めて実行する。

### 1. `/curate-news` の実行

Skill ツールで `curate-news` を実行する。

完了後、今日の出力ファイルを特定する:
```bash
ls .claude/skills/curate-news/output/{YYYY-MM-DD}*.md
```

出力ファイルの内容を Read で読み込む。ファイル名のステム部分（例: `2026-03-18-23cfb1cf`）を後続のステップで使う。

### 2. ブランチの作成

現在のブランチを確認してから、最新の origin/main からトピックブランチを作成する。ブランチ名に出力ファイルのステムを使うことで、出力と1対1で対応させる。

```bash
git branch --show-current
git fetch origin main
git checkout -b pages/{ステム} origin/main
```

同日に再実行した場合、同名ブランチが既に存在する。その場合は `git checkout pages/{ステム}` で切り替え、既存の PR が自動更新される。

### 3. 投稿ファイルの作成

ステップ 1 で読み込んだ出力内容を Jekyll の投稿形式に変換して `_posts/` に配置する。

ファイルパス: `_posts/{YYYY-MM-DD}-news.md`

フロントマターの `title` が記事ページの見出しになるため、本文はリード文から始める（curate-news 出力の先頭にある `## ニュース (...)` 見出し行はタイトルと重複するので含めない）。

```yaml
---
layout: post
title: "{YYYY}年{M}月{D}日"
date: {YYYY-MM-DD}
---

{リード文から始まる本文}
```

### 4. コミットと PR 作成

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

### 5. 元のブランチに戻る

ステップ 2 で確認したブランチに戻る。

## 付録: 初回セットアップ

`_config.yml` が存在しない場合に実行する。Jekyll の最小構成を追加し、GitHub Pages を有効化する。

### A1. ブランチの作成

```bash
git fetch origin main
git checkout -b setup-github-pages origin/main
```

### A2. Jekyll 構成ファイルの作成

**`_config.yml`:**
```yaml
title: "News"
description: "気になるテック・経済ニュースを毎日キュレーション"
theme: minima
baseurl: "/news"  # リポジトリ名に合わせる（GitHub Pages は `{user}.github.io/{repo}` で配信されるため）
header_pages: []
```

**`index.md`:**
```markdown
---
layout: home
---
```

**`_posts/.gitkeep`:** 空ファイル

### A3. コミット・プッシュ・PR 作成

```bash
git add _config.yml index.md _posts/.gitkeep
git commit -m "Setup GitHub Pages with Jekyll"
git push -u origin setup-github-pages
gh pr create --base main --title "Setup GitHub Pages" --body "Jekyll最小構成の追加" --draft
```

### A4. GitHub Pages の有効化

```bash
gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pages -X POST -f 'source[branch]=main' -f 'source[path]=/'
```

既に有効な場合のエラーは無視してよい。

### A5. ユーザーへの案内

セットアップ PR の URL を表示し、マージを依頼する。マージが完了したら `/publish-pages` を再度実行するよう案内して、元のブランチに戻って終了する。
