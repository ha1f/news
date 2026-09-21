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

キュレーションはコンテキストを大きく消費するので、オーケストレータ自身は実行せず、対象プロファイル1件につき fresh context の subagent を1つ、並列に起動する（1件のみの場合も同様）。指示は次のテンプレートの `{name}` と `{YYYY-MM-DD}` を**実値に置換してから**渡す。デフォルトプロファイルには1文目を「`curate-news` スキルを Skill ツールで引数なしで実行する。」に差し替える:

> `curate-news` スキルを Skill ツールで `--profile {name}` を `args` に渡して実行する。日付はこの指示で渡した `{YYYY-MM-DD}` を使い、ステップ6で再計算しない。完了したら、ステップ6「結果の保存」で**自分が書き出した**ファイルのフルパスを報告する。`ls` で探さないこと（同じ日付のファイルが他プロファイルの分も並ぶため、自分の出力を判別できない）。

プロファイルと出力ファイルの対応はディスパッチした時点で決まっている。各 subagent が報告したパスを記録し、Read で内容を読み込む（ステップ3で使うステムは basename から取る）。

同じソース・カテゴリを複数の subagent が同時に取りにいっても、`fetch_feeds.py` 経由ならキャッシュキー単位のロックで直列化され、重複リクエストも壊れたキャッシュも出ない。

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

ファイル名の `{YYYY-MM-DD}` と以下の `date` は、**すべてステップ 1 で確定した JST 基準の日付**を使い回す。

フロントマターの `title` は記事ページの見出し・一覧・OGP・RSS に共通で使われる。リード文と記事一覧を読み、その日いちばん大きい話題を凝縮した見出しを日本語で作る（見出し部分で15〜30字が目安。`（{表示名}）` は字数に数えない。定型の言い回しに当てはめず、実際の内容から判断する）。**日付は入れない**（一覧のバッジと記事ページの `<time>` で別途出るため、入れると隣接して二重に表示される。#341）。本文はリード文から始める（curate-news 出力の先頭にある `## ニュース (...)` 見出し行はタイトルと重複するので含めない）。

記事本文を読み、以下のトピック一覧から該当するものを `tags:` に列挙する（該当なしは空配列）。各記事の見出しと読みどころから判断し、1記事でも該当すればそのトピックを含める:

`AI` / `開発` / `セキュリティ` / `ビジネス` / `科学` / `デザイン` / `経済` / `ハードウェア` / `社会`

デフォルトプロファイル:
```yaml
---
layout: post
title: "{その日の内容から作った見出し}"
date: {YYYY-MM-DD}
tags: [{該当トピックをカンマ区切り}]
---

{リード文から始まる本文}
```

名前付きプロファイル（見出し末尾にプロファイルの日本語表示名を付加し、同日の他プロファイル記事と区別する）。`{表示名}` は `profiles/{name}.md` の `title` フロントマターから取得する（例: engineer → ソフトウェアエンジニア）:
```yaml
---
layout: post
title: "{その日の内容から作った見出し}（{表示名}）"
date: {YYYY-MM-DD}
profile: {name}
tags: [{該当トピックをカンマ区切り}]
---

{リード文から始まる本文}
```

投稿ファイルを作ったら、各項目の読みどころとソース表記を確認する。読みどころが「読みどころなし」または「出どころの紹介だけ」なら、curate-news の「読みどころ」節に従って記事ページから事実を取り直す（取れなければその項目を差し替える）。ソース表記が1件でも落ちていれば「ソース名と読者向け属性」節に従って補う。どちらも解消してから次へ進む。引数なしで実行すると内部で当日 JST の日付を再計算してしまい、JST 日跨ぎで対象ファイルが見つからず空振り exit 1 になる（ステップ 1 で確定した日付を使い回す方針に反する）ため、確定済みの `{YYYY-MM-DD}` を明示して渡す:

```bash
python3 .claude/scripts/check_article_notes.py _posts/{YYYY-MM-DD}-*.md
python3 .claude/scripts/check_source_hints.py _posts/{YYYY-MM-DD}-*.md
```

続けて、デフォルトプロファイルの各項目を**予備知識のない読者として上から読み、「誰が・何を」に口で答える**（#371）。他プロファイルの記事から分かったことは使わず、その面の見出しと読みどころだけで答える。答えられない項目は、curate-news の「各記事の見出し」「読みどころ」節に従って主語か固有名詞の説明を補う（字数は増やさず、詳細を削って入れ替える）。

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

`gh` が使えなければ MCP ツールで squash マージする（`merge_pull_request` に `--delete-branch` 相当のオプションは無い）。リポジトリの「Automatically delete head branches」設定が有効なら、マージ後に GitHub 側でブランチは自動削除される。手動で `git push origin --delete pages/{ブランチ名}` を試みても、既に削除済みなら `remote ref does not exist` で失敗するだけで実害はないため、成功を確認する必要はない。

### 7. 元のブランチに戻る

ステップ 3 で確認したブランチに戻る。

### 8. 振り返りと改善

Skill ツールで `reflect-and-improve` を実行する。作成された改善 PR は ready 化する（`gh pr ready` または MCP ツール。次の review-and-merge のレビュー対象になる）。
