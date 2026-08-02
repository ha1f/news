---
description: "ニュースキュレーションを実行し、GitHub Pagesにデプロイする"
---

# GitHub Pages デプロイ

`/curate-news` でニュースキュレーションを実行し、結果を main ブランチ向けの PR として作成・マージする。マージされると GitHub Pages に自動デプロイされる。

## 引数

スキルの `args` でプロファイルを指定できる。

- 引数なし → デフォルト + `profiles/*.md` の全プロファイル（`--all-profiles` と同じ）
- `--profile designer` → 指定プロファイルのみ
- `--all-profiles` → 引数なしと同じ（後方互換のエイリアス）

## 手順

### 1. プロファイルの決定

`{YYYY-MM-DD}` は JST (Asia/Tokyo) 基準の日付とする。推測せず、以下のコマンドで取得する:
```bash
TZ=Asia/Tokyo date +%F
```

引数に応じてキュレーション対象を決める:
- `--profile {name}` → `["{name}"]`
- それ以外（引数なし / `--all-profiles`） → デフォルト (`null`) + `profiles/*.md` から取得した名前のリスト:
  ```bash
  ls .claude/skills/curate-news/profiles/*.md 2>/dev/null | xargs -I{} basename {} .md
  ```
  プロファイルが存在しなければ `[null]`（デフォルト1件のみ）。

以降、このリストの各要素を「対象プロファイル」と呼ぶ。`null` はデフォルトプロファイルを表す。

### 2. `/curate-news` の実行

対象プロファイルごとに Skill ツールで `curate-news` を実行する:
- デフォルト (`null`): 引数なしで実行
- 名前付き: `--profile {name}` を `args` に渡して実行

各実行後、出力ファイルを特定する:
```bash
ls .claude/skills/curate-news/output/{YYYY-MM-DD}*.md
```

出力ファイルの内容を Read で読み込む。ファイル名のステム部分（例: `2026-03-18-23cfb1cf`）を記録する。

### 3. ブランチの作成

現在のブランチを確認してから、最新の origin/main からトピックブランチを作成する。

対象が1件の場合はステムをブランチ名に使う。複数の場合は日付ベースにする:
- 1件: `pages/{ステム}`
- 複数: `pages/{YYYY-MM-DD}-multi`

```bash
git branch --show-current
git fetch origin main
git checkout -b pages/{ブランチ名} origin/main
```

同日に再実行した場合、同名ブランチが既に存在する。その場合は `git checkout pages/{ブランチ名}` で切り替え、既存の PR が自動更新される。

### 4. 投稿ファイルの作成

各プロファイルの出力内容を Jekyll の投稿形式に変換して `_posts/` に配置する。

ファイルパス:
- デフォルト: `_posts/{YYYY-MM-DD}-news.md`
- 名前付き: `_posts/{YYYY-MM-DD}-news-{profile}.md`

`{YYYY-MM-DD}` を含め、以下の `title` / `date` も**すべてステップ 1 で確定した JST 基準の日付**を使い回す。

フロントマターの `title` が記事ページの見出しになるため、本文はリード文から始める（curate-news 出力の先頭にある `## ニュース (...)` 見出し行はタイトルと重複するので含めない）。

デフォルトプロファイル:
```yaml
---
layout: post
title: "{YYYY}年{M}月{D}日"
date: {YYYY-MM-DD}
---

{リード文から始まる本文}
```

名前付きプロファイル（タイトルにプロファイル名を付加し、同日の他プロファイル記事と区別する）:
```yaml
---
layout: post
title: "{YYYY}年{M}月{D}日 ({name})"
date: {YYYY-MM-DD}
profile: {name}
---

{リード文から始まる本文}
```

### 5. コミットと PR 作成

```bash
git add _posts/
git commit -m "Add news curation for {YYYY-MM-DD}"
git push -u origin pages/{ブランチ名}
```

PR タイトル:
- 1件: `ニュース: {YYYY-MM-DD}`
- 複数: `ニュース: {YYYY-MM-DD} ({件数}プロファイル)`

PR を作成する。`gh` CLI が使えない環境（CCR 等）では GitHub MCP ツールで同等の操作を行う。

```bash
gh pr create --base main --title "{タイトル}" --body "/curate-news の結果を GitHub Pages にデプロイします。"
```

PR の URL をユーザーに表示する。

### 6. マージ

PR を squash マージしてブランチを削除する。

```bash
gh pr merge --squash --delete-branch
```

`gh` が使えなければ MCP ツールで squash マージする。

### 7. 元のブランチに戻る

ステップ 3 で確認したブランチに戻る。

### 8. 振り返りと改善

Skill ツールで `reflect-and-improve` を実行する。作成された改善 PR は ready 化する（`gh pr ready` または MCP ツール。次の review-and-merge のレビュー対象になる）。
