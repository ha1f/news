---
description: "ニュースキュレーションを実行し、GitHub Pagesにデプロイする"
---

# GitHub Pages デプロイ

`/curate-news` で全プロファイル分のニュースキュレーションを実行し、結果を main ブランチ向けの PR として作成・マージする。マージされると GitHub Pages に自動デプロイされる。1回の実行で全フィードを1つの PR にまとめる。

## 手順

### 1. `/curate-news` の実行

Skill ツールで `curate-news` を実行する（プロファイルを指定せず、全プロファイルを対象にする）。

完了後、プロファイル一覧と今日の出力ファイルを確認する。`{YYYY-MM-DD}` は JST (Asia/Tokyo) 基準の日付とする。推測せず、以下のコマンドで取得してから `ls` に渡す:

```bash
TZ=Asia/Tokyo date +%F
python3 .claude/skills/curate-news/scripts/profiles.py
ls .claude/skills/curate-news/output/{YYYY-MM-DD}-*.md
```

出力ファイルは `{YYYY-MM-DD}-{プロファイルID}.md`。ここで確定した JST 基準の `{YYYY-MM-DD}` を、以降の全ステップで使い回す（再度日付を判定し直さない）。

出力が存在するプロファイルだけを公開対象にする。欠けているプロファイルがあれば理由を控えておき、ステップ4の PR 本文に書く。

### 2. ブランチの作成

現在のブランチを確認してから、最新の origin/main からトピックブランチを作成する。

```bash
git branch --show-current
git fetch origin main
git checkout -b pages/{YYYY-MM-DD} origin/main
```

同日に再実行した場合、同名ブランチが既に存在する。その場合は `git checkout pages/{YYYY-MM-DD}` で切り替え、既存の PR が自動更新される。

### 3. 投稿ファイルの作成

公開対象のプロファイルごとに、出力ファイルの内容を Read で読み、Jekyll の投稿形式に変換して `_posts/` に配置する。

ファイルパス: `_posts/{YYYY-MM-DD}-{post_slug}.md`（`post_slug` は `profiles.py` の一覧に出るもの。プロファイルIDとは別で、記事 URL に入る）

フロントマターの `title` が記事ページの見出しになるため、本文はリード文から始める（curate-news 出力の先頭にある `## ニュース (...)` 見出し行はタイトルと重複するので含めない）。`profile` はその記事がどのフィードに載るかを決める（省略すると既定フィード扱いになるため、必ず明示する）。

```yaml
---
layout: post
title: "{YYYY}年{M}月{D}日"
date: {YYYY-MM-DD}
profile: {プロファイルID}
---

{リード文から始まる本文}
```

### 4. コミットと PR 作成

コミットメッセージ・PR タイトルの `{YYYY-MM-DD}` も、新たに日付を判定せずステップ 1 で確定した日付をそのまま使う。

```bash
git add _posts/
git commit -m "Add news curation for {YYYY-MM-DD}"
git push -u origin pages/{YYYY-MM-DD}
```

PR を作成する（本文には公開したフィードと、欠けたフィードがあればその理由を書く）:
```bash
gh pr create --base main --title "ニュース: {YYYY-MM-DD}" --body "$(cat <<'EOF'
/curate-news の結果を GitHub Pages にデプロイします。

- 公開したフィード: {プロファイル名のリスト}

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
