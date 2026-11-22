---
paths:
  - "_layouts/**"
  - "_includes/**"
  - "assets/**"
  - "index.md"
  - "archive.md"
  - "profiles/**"
  - "about.md"
  - "404.html"
---

UI に触る変更（レンダリング結果が変わるもの）の進め方:

- 実装前に解き方を2〜3案挙げ、[DESIGN.md](../../DESIGN.md) に照らして選ぶ。最初に思いついた案に直行しない。検討した案と選定理由は issue の要約コメントの「判断と理由」欄に記録する（設計判断を含まない変更では省略可。「含まない」の基準: レイアウト・色・インタラクションのいずれも代替案が存在しない場合）
- 一覧の見出しリンクや `<li>` の構造に触ったら（`_layouts/` `_includes/` `archive.md` `profiles/index.md`）、ローカルビルドに対して回帰検査 `python3 .claude/scripts/check_article_anchors.py _site` を回し（トップページ・プロファイルページの見出しが記事単位の着地点を指しているかの確認。#326）、変更前のビルド（`origin/main` を `git worktree add` してビルドしたもの）と検査件数を比べる。ITEM_RE に合わない項目はエラーにならず検査から黙って外れる（実測 2026-11-20 #674: `_includes/` と `profiles/index.md` だけの変更で 7369 → 7219 件、失敗 0 のまま）。ビルドは [ノート「ローカルでビルド・描画確認する」](../notes/develop-issue.md) の形で行う（`jekyll` は PATH に無いので、PATH を足すのと同じ行で実行する）

- `git fetch origin main` のうえ `check_protected_paths.py --diff origin/main` の出力に `ui_changes` がある場合、以下のスクリーンショット確認を必ず行う（fetch 前はマージ済みの他 PR の変更が自分の diff に混ざる）
- 実装中はローカルビルドを配信して撮り、素早く回す。ビルド・配信・撮影の手順は [.claude/notes/develop-issue.md](../notes/develop-issue.md) にある
- 日本語は既定で任意の文字位置で折れる。短いラベルを区切りで連ねた行（`AI / 開発 / 社会` 等）を狭い幅や目立つ位置に出すときは `word-break: keep-all` をセットにし、モバイル幅で `ハー` ⏎ `ドウェア` のようなラベル内改行が出ていないか実測する。既存の面で使えていることは可読性の担保にならない（実測 PR #392: トップ7枚中5枚と archive.html が該当）
- push 後は jekyll-build-check の screenshot artifact を取得して実際に見る。トップ・記事・アーカイブ・プロファイル一覧・プロファイルの各ページが light / dark の両方で、トップはモバイル幅でも撮られており、ローカルで撮った1〜2枚より網羅的（取得手順はノート参照。他ページのモバイル描画はローカルで補う）。見た artifact の run id と、light / dark で確認したページを issue の要約コメントの「受け入れ条件との突合」に1行で書く（確認したかどうかを run の外から検証できるようにする。実測 2026-10-18: 週内の UI PR 3件のうち1件に記録が無かった）
- DESIGN.md の判定基準で自己レビューしてから ready 化する
- 撮影できない事情があるときは、変更後の HTML/CSS を DESIGN.md のパレット・原則と突合し、描画未確認である旨を PR に明記する
