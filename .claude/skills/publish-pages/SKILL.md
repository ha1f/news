---
description: "ニュースキュレーションを実行し、GitHub Pagesにデプロイする"
---

# GitHub Pages デプロイ

`/curate-news` でニュースキュレーションを実行し、結果を main ブランチ向けの PR として作成・マージする。マージされると GitHub Pages に自動デプロイされる。

## 手順

### 1. `/curate-news` の実行

Skill ツールで `curate-news` を実行する。

完了後、今日の出力ファイルを特定する。`{YYYY-MM-DD}` は JST (Asia/Tokyo) 基準の日付とする。推測せず、以下のコマンドで取得してから `ls` に渡す:
```bash
TZ=Asia/Tokyo date +%F
ls .claude/skills/curate-news/output/{YYYY-MM-DD}*.md
```

出力ファイルの内容を Read で読み込む。ファイル名のステム部分（例: `2026-03-18-23cfb1cf`）を後続のステップで使う。ステム先頭の日付部分がここで確定した JST 基準の `{YYYY-MM-DD}` であり、後続ステップの `{YYYY-MM-DD}` は全てこの値を使い回す（再度日付を判定し直さない）。

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

この `{YYYY-MM-DD}` を含め、以下の `title` / `date` も**すべてステップ 1 で確定した JST 基準の日付**を使い回す（ここで改めて日付を判定しない）。

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

コミットメッセージ・PR タイトルの `{YYYY-MM-DD}` も、新たに日付を判定せずステップ 1 で確定した日付をそのまま使う。

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
)"
```

PR の URL をユーザーに表示する。

### 5. マージ

PR を squash マージしてブランチを削除する。

```bash
gh pr merge --squash --delete-branch
```

### 6. 元のブランチに戻る

ステップ 2 で確認したブランチに戻る。

### 7. 振り返りと改善

Skill ツールで `reflect-and-improve` を実行する。作成された改善 PR は ready 化する（`gh pr ready`。次の review-and-merge のレビュー対象になる）。
