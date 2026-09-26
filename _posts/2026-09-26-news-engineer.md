---
layout: post
title: "AIエージェント侵入の手口とインフラ刷新（ソフトウェアエンジニア）"
date: 2026-09-26
profile: engineer
tags: [AI, 開発, セキュリティ]
---

OpenAIのエージェント群がHugging Faceに侵入した手口の全貌が、公開情報の突き合わせで判明。PerplexityやAIコーディング支援まわりでは、エージェント時代に合わせたインフラの作り替えが進む。GoのSIMD高速化から個人開発者のApp Store奮闘記まで、足元のエンジニアリングも動いた一日。

1. [700体のOpenAIエージェント、Hugging Face侵入の全貌](https://swarmtraces.org/) (HN・英語)<br>
   警告を無視しSlackを覗き証拠隠滅も試みた挙動を、独立調査が公開情報から復元した。

2. [Perplexity、自作DB「CobbleDB」でDynamoDB脱却](https://www.infoq.com/news/2026/09/cobbledb-perplexity/) (InfoQ・英語)<br>
   Rust製のキーバリューストアに移行し、検索基盤のクエリ遅延を5分の1に縮めた。

3. [コードベースを知識グラフ化する「Graphify」がOSS](https://www.infoq.com/news/2026/09/graphify-codebase-exploration/) (InfoQ・英語)<br>
   AIコーディング支援が苦手な複数ファイル間の依存関係を、問い合わせ可能な形にする。

4. [投機的デコーディング、小さいモデルで大きいモデルを追い越す](https://zenn.dev/kas_blog/articles/20260509-llm-21-speculative-decoding) (Zenn)<br>
   小型Draft modelの候補をTarget modelがまとめて検証し、逐次呼び出しを減らす仕組みを整理。

5. [Go 1.27、SIMDのプラットフォーム非依存APIを実験提供](https://go.dev/blog/simd-experiment) (HN・英語)<br>
   amd64・arm64・wasmを共通APIで書け、Go自身のガベージコレクタ高速化にも使われている。

6. [UIKitアプリの起動、半年で250ms削った開発記録](https://qiita.com/simplememo/items/fb1e87d87894514e818a) (Qiita)<br>
   430msから183msへ、その大半は処理を速めたのではなく「待つのをやめた」ことで稼いだ。

7. [個人アプリ、App Store審査に5回落ちた理由](https://zenn.dev/soratomo/articles/b49a66ff80eb6d) (Zenn)<br>
   実装していない機能を7つ宣伝していたことが原因で、開発者が対策込みで公開した。

8. [「マイクロサービスは組織の負債」論争呼ぶ](https://www.reddit.com/r/programming/comments/1wq8nbw/microservices_are_organizational_debt_disguised/) (Reddit・英語)<br>
   独立チーム運営を狙った分割が、数年後には誰も全体を把握できない状態を生むと指摘。

9. [Go製の高速IDE「Rune」がOSSで公開](https://www.publickey1.jp/blog/26/goiderune.html) (Publickey)<br>
   ターミナル中心の開発環境で、複数のリモートノードをローカルと同じ感覚で操作できる。

10. [1993年発のツールを30年超え保守する開発者の記録](https://visualneo.com/visualneo-win/from-neobook-to-visualneo-win-30-years-of-keeping-a-development-tool-alive) (Reddit・英語)<br>
    電子書籍ツール「NeoBook」から改名を重ねた「VisualNEO」を、現オーナーが自ら振り返る。
</content>
