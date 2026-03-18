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

## 前提

- GitHub Pages が有効化済みで、main ブランチの `/` をソースとして配信している
- リポジトリルートに `_config.yml`、`index.md`、`_posts/` が存在する

未セットアップの場合は「付録: 初回セットアップ」の手順でセットアップを行う。

## 手順

### 1. `/curate-news` の実行

Skill ツールで `curate-news` を実行する。

完了後、今日の出力ファイルを特定する:
```bash
ls .claude/skills/curate-news/output/{今日の日付}*.md
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

Jekyll はファイル名の日付で記事をソートする。フロントマターの `title` が記事ページの見出しになるため、本文からは `## ニュース (...)` の見出し行を取り除いてリード文から始める。

```yaml
---
layout: post
title: "{YYYY}年{M}月{D}日"
date: {YYYY-MM-DD}
---

{リード文から始まる curate-news の出力内容}
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
