---
layout: post
title: "Python 3.15が安定版に、SQLiteにはベクトル検索拡張（ソフトウェアエンジニア）"
date: 2026-10-11
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [開発]
  - [開発]
  - [開発]
  - [AI, セキュリティ]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [AI, セキュリティ]
  - [AI]
  - [AI, 開発]
  - [開発]
---

Python 3.15.0 が 10月9日に安定版となり、JIT の高速化や遅延 import が入った。SQLite 本体にはベクトル検索拡張 vec1 が取り込まれ、DuckDB 2.0 や Cloudflare も足回りの改良を続ける。AI エージェントを閉じ込める枠組みや、エージェント向けの道具も次々に出てきた。

1. [Python 3.15.0 が安定版に、JIT 高速化と遅延 import](https://www.python.org/downloads/release/python-3150/) (Reddit・英語)<br>
   1,012 人が 5,643 コミットを重ねた版で、frozendict の追加と UTF-8 既定化も含む。

2. [SQLite 本体に公式ベクトル検索拡張 vec1](https://zenn.dev/mattn/articles/6e9996319ac099) (はてブ)<br>
   9月30日に Dan Kennedy 氏が取り込んだ約1.3万行の拡張で、距離は L2 とコサインに対応する。

3. [DuckDB 2.0 alpha はなぜ速いか](https://motherduck.com/blog/why-duckdb-20-is-faster/) (HN・英語)<br>
   M5 ノート上の実測で、再帰 CTE が最大90倍、S3 の読み取りが2.4倍になった。

4. [Microsoft、AI エージェントを閉じ込める実行コンテナ Mxc 1.0](https://blogs.windows.com/windowsdeveloper/2026/10/07/microsoft-execution-containers-policy-driven-containment-for-ai-agents/) (HN・英語)<br>
   ファイルやネットワークへの権限をポリシーで絞り、全開放か全遮断かの二択を避ける狙い。

5. [コーディングエージェント用の逆アセンブル支援ツール REA](https://rea.tools/) (HN・英語)<br>
   npx で入れてエージェントに渡すと、電卓アプリが「200+10%」を220と返す規則まで追える例を示す。

6. [Cloudflare Traces が公開ベータ、プロキシ層を OpenTelemetry スパンに](https://www.infoq.com/news/2026/10/cloudflare-traces-open-beta/) (InfoQ・英語)<br>
   WAF ルールやキャッシュも計測対象になり、課金は12月1日から取り込み量ベースに変わる。

7. [Go の defer を TypeScript コンパイラに足してみた](https://healeycodes.com/adding-defer-to-the-typescript-compiler) (Reddit・英語)<br>
   tsc を改造して try/finally なしで後始末を書けるようにしたが、著者は結局「入れるべきでない」と結論づける。

8. [ブラウザ内で動く個人情報フィルタ Rampart](https://ndstudio.gov/posts/say-hello-to-rampart) (HN・英語)<br>
   正規表現と MiniLM を組み合わせ、チャットボットに送る前に氏名や住所を端末内で検出する。

9. [最新 AI は ML 研究の「新手法の発明」を再現できず](https://epoch.ai/publications/innovationeval) (HN・英語)<br>
   Epoch AI の InnovationEval では、GPU 代に数千ドルをかけても人間の成果に並べなかった。

10. [SwiftUI の落とし穴を LLM に避けさせるエージェントスキル](https://github.com/twostraws/SwiftUI-Agent-Skill) (GitHub Trending・英語)<br>
    twostraws 作で、非推奨 API や VoiceOver 対応など、LLM が実際に間違える点に絞った指針。

11. [技術ブログはゆるやかに衰退している](https://zenn.dev/northward/articles/decline-of-tech-blogs) (Zenn)<br>
    2026年に Zenn へ投稿された5.2万件を分析して、衰退の姿と今後を考える。
