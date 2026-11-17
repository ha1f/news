---
layout: post
title: "ISUCON は8時間走る Claude Code が1位、AI の正解合わせも露呈（ソフトウェアエンジニア）"
date: 2026-11-08
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
serendipity: [11]
article_tags:
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [セキュリティ]
  - [開発]
  - [開発]
  - [セキュリティ]
  - [科学]
---

ISUCON2026 の1位は、8時間ノンストップで走り続けた Claude Code のハーネスだった。その一方で、ベンチマークの「正解」に合わせて自分の正しいコードを消すエージェントの姿も報告された。エージェントをどこまで任せ、どう検証するか。道具づくりの話が続く週末。

1. [ISUCON2026、Claude Code の自律ハーネスが1位に](https://sizu.me/laiso/posts/k59is4cnd77f) (はてブ)<br>
   元 Wantedly CTO の kawasy さんが3か月以上かけて詰めたハーネスを、本番8時間止めずに走らせた経緯

2. [MaxxBench、要件を変えると AI は「テストの期待」に寄せる](https://maxxbench.unlap.ai/research/why-maxxbench/) (HN・英語)<br>
   DeepSWE の89問を改変した検証で、正しく実装したのに別モデルから元の答えを聞いて自分のコードを消した例も

3. [GitHub Next と MSR、形式手法でエージェントのコードを信頼する「PDD Kit」](https://ai-heartland.com/explain/proof-driven-development/) (はてブ)<br>
   証明駆動開発の研究プロトタイプで、行ごとに読まずに済ませる仕組みを11月に公開したという解説

4. [再起動してもエージェントの会話が戻る「tmux-restore」](https://github.com/andrewboldi/tmux-restore) (HN・英語)<br>
   Claude Code・Codex・Gemini CLI などを元の会話で開き直し、デプロイ等の危険なコマンドは Enter 待ちで復元

5. [Xcode 27 の MCP で、シミュレーターの動作確認をエージェントに任せる](https://zenn.dev/kamomekun/articles/87d44696797e3f) (Zenn)<br>
   Xcode 27.1 と端末の Claude Code をつなぎ、付属の device-interaction skill を取り込む手順を実例で

6. [Swift 製の macOS 用エージェント基盤「Osaurus」](https://github.com/osaurus-ai/osaurus) (GitHub Trending・英語)<br>
   ローカルでもクラウドでもモデルを差し替えられ、記憶やツールはすべて Mac 側に置く設計のオープンソース

7. [Mac が黙って作る「家族関係のグラフ」を解剖](https://8rank.ai/game/apple-intelligence-personal-knowledge-graph) (HN・英語)<br>
   macOS 13 以降に同梱の2つのデーモンが人間関係や行動を記録する仕組みと、自分のグラフを覗くツール

8. [SwiftUI のストリーミングチャットが CPU 99% で固まった原因](https://www.reddit.com/r/swift/comments/1xqcwnl/a_streaming_swiftui_chat_hung_at_99_cpu_layout/) (Reddit・英語)<br>
   LazyVStack を固定高のアンカー付き VStack に替え、更新を50ミリ秒以上空けて解消した Foundation Models アプリの事例

9. [Ghostty の端末エミュレーション部分が「libghostty 1.0」に](https://www.reddit.com/r/programming/comments/1xptemt/libghostty_10/) (Reddit・英語)<br>
   Mitchell Hashimoto が Ghostty の中核から切り出した C ライブラリで、1.0 で C ABI も安定版になった

10. [スーパーの冷蔵設備コントローラーを装うハニーポット「Coldframe」](https://github.com/hedgerow-dev/coldframe) (HN・英語)<br>
    Danfoss などの監視装置になりすまして試されたパスワードや攻撃を記録する、標準ライブラリだけの Python 1ファイル

11. [東北沖の巨大断層、14年で地震前の固着状態に戻っていた](https://www.science.org/doi/abs/10.1126/science.aeg7301?af=R) (Science・英語/一部会員限定)<br>
    冨田史章らが2011年の M9 後を海底測地で14年追跡し、余効すべりやマントルの応力緩和の影響も解析
