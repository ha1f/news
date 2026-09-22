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

- 実装前に解き方を2〜3案挙げ、DESIGN.md に照らして選ぶ。最初に思いついた案に直行しない。検討した案と選定理由は issue の要約コメントの「判断と理由」欄に記録する（設計判断を含まない変更では省略可。「含まない」の基準: レイアウト・色・インタラクションのいずれも代替案が存在しない場合）
- `_layouts/` に触ったら、ローカルビルドに対して回帰検査を回す（トップページ・プロファイルページの見出しが記事単位の着地点を指しているかの確認。#326）:

  ```bash
  jekyll build -d _site && python3 .claude/scripts/check_article_anchors.py _site
  ```

- `check_protected_paths.py --diff` の出力に `ui_changes` がある場合、以下のスクリーンショット確認を必ず行う（このフィールドは上記 paths に該当するファイルが diff に含まれるとき自動で出力される）
- 実装中はローカルビルドを配信して撮り、素早く回す。ビルド・配信・撮影の手順は [.claude/notes/develop-issue.md](../notes/develop-issue.md) にある
- 日本語は既定で任意の文字位置で折れる。短いラベルを区切りで連ねた行（`AI / 開発 / 社会` 等）を狭い幅や目立つ位置に出すときは `word-break: keep-all` をセットにし、モバイル幅で `ハー` ⏎ `ドウェア` のようなラベル内改行が出ていないか実測する。既存の面で使えていることは可読性の担保にならない（実測 PR #392: トップ7枚中5枚と archive.html が該当）
- push 後は jekyll-build-check の screenshot artifact を取得して実際に見る。トップ・記事・アーカイブ・プロファイルの各ページが light / dark の両方、デスクトップ幅とモバイル幅で撮られており、ローカルで撮った1〜2枚より網羅的（取得手順はノート参照）
- DESIGN.md の判定基準で自己レビューしてから ready 化する
- 撮影できない事情があるときは、変更後の HTML/CSS を DESIGN.md のパレット・原則と突合し、描画未確認である旨を PR に明記する
