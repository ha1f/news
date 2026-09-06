---
paths:
  - "_layouts/**"
  - "_includes/**"
  - "assets/**"
  - "index.md"
  - "archive.md"
  - "about.md"
  - "404.html"
---

UI に触る変更（レンダリング結果が変わるもの）の進め方:

- 実装前に解き方を2〜3案挙げ、DESIGN.md に照らして選ぶ。最初に思いついた案に直行しない。検討した案と選定理由は issue の要約コメントの「判断と理由」欄に記録する（設計判断を含まない変更では省略可。「含まない」の基準: レイアウト・色・インタラクションのいずれも代替案が存在しない場合）
- PR を push したら、jekyll-build-check が生成する screenshot artifact をダウンロードして実際に見る。DESIGN.md の判定基準で自己レビューしてから ready 化する
- artifact が存在しない・取得できない場合は、変更後の HTML/CSS を DESIGN.md のパレット・原則と突合し、描画未確認である旨を PR に明記する
