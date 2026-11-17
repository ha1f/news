---
layout: post
title: "Fable 5.2 公開、エージェント前提でテストと基盤を組み直す（ソフトウェアエンジニア）"
date: 2026-11-10
profile: engineer
tags: [AI, 開発, セキュリティ, 社会]
serendipity: [10, 11]
article_tags:
  - [AI]
  - [AI]
  - [開発, AI]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [セキュリティ, 社会]
---

Anthropic が Claude Fable 5.2 と Mythos 5.2 を公開し、Meta は最小モデル Muse Ember で安さを競う。モデルの更新と並んで、エージェントが書く前提でテストや実行基盤を組み直す話が目立つ一日。

1. [Anthropic、Claude Fable 5.2 と Mythos 5.2 を公開](https://www.anthropic.com/claude-fable-and-mythos-5-2) (HN・英語)<br>
   同じモデルを安全策の強弱で2つに分けた構成で、出力は5.1比で最大3割速く値下げもされた

2. [Meta の最小モデル「Muse Ember」、エージェントの反復作業向け](https://research.meta.ai/blog/muse-ember) (HN・英語)<br>
   Claude Haiku 5.5 の最高スコアに約3分の1のコストで並ぶと Meta が主張し、比較の数字も載せている

3. [Google、エージェント基盤「Agent Substrate」と gVisor を CNCF へ寄贈](https://www.publickey1.jp/blog/26/googlekubernetes10aiagent_sustrategvisorcncf.html) (Publickey)<br>
   エージェントは時間の9割以上を待ちに使うという Google の見立てから、Pod 1つに1体の無駄をどう省くかがわかる

4. [静的型付けは AI のバグを減らすか、TS と JS で同じ CLI を書かせて比較](https://zenn.dev/torudev/articles/dd45de860fc7c3) (Zenn)<br>
   TS は JS の1.6倍の時間と費用がかかるという mame 氏の計測を受け、Claude Code で残るバグ数を確かめた検証

5. [Shopify のネイティブ回帰を支える設計「Reflex」を Swift と Kotlin で試す](https://zenn.dev/tellernovel_inc/articles/reflex-native-swift-kotlin) (Zenn)<br>
   コードは共有せず TypeScript の振る舞いテストを両 OS に流す方式で、Shopify では1700本超が約4分で回る

6. [C# 15 に union 型、.NET 11 と同時に登場](https://www.reddit.com/r/programming/comments/1xrrmk7/c_15_union_types_closed_hierarchies_and_the_one/) (Reddit・英語)<br>
   Elm や F# を書く筆者が RC 版 SDK で実際に動かし、default(T) がすり抜ける穴を指摘している

7. [バクラク、go build の並列度を9から2に下げて2.4倍速く](https://speakerdeck.com/tomoaki25/slides-cd95d381-a27b-4a9a-8b53-0abd69397a1b) (はてブ)<br>
   LayerX の発表資料で、-debug-actiongraph を使い monorepo で重複コンパイルが起きる理由を実測で示す

8. [Cloudflare、1.1.1.1 の DNS キャッシュで100TBのメモリを節約](https://www.reddit.com/r/programming/comments/1xs558h/how_we_saved_100_terabytes_of_memory_by/) (Reddit・英語)<br>
   常時2500億件を抱える Rust 製の基盤で1件あたりの容量を半分以下にし、挿入も43%速くなった

9. [k-means を10倍速くする「e-means」、損失は同等](https://e-means.github.io/) (HN・英語)<br>
   Lloyd 法が25エポックかける損失に1.2〜3エポックで届き、GPU では Flash-KMeans の10〜45倍速い

10. [USPS、ZIP コードの公式な境界ポリゴンを提供](https://postalpro.usps.com/zcb) (HN・英語)<br>
   米郵政公社が配達先の住所と位置から境界を引き、年4回更新する。用途別に3種類のライセンスがある

11. [全国800超の機関リポジトリが停止、つくばリポジトリも復旧の目途立たず](https://www.tsukuba-sp.org/news/wghx7ljlx7/) (はてブ)<br>
   国立情報学研究所の共用基盤 JAIRO Cloud に依存し、10月28日から筑波大の論文や博士論文が読めない
