---
layout: post
title: "OpenAI が perplexity を公開、ハーネスは「新しい OS」に（ソフトウェアエンジニア）"
date: 2026-11-23
profile: engineer
tags: [AI, 開発, ビジネス]
serendipity: [10]
article_tags:
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [ビジネス]
---

OpenAI が社内の事前学習の perplexity を公開し、業界共通の物差しにしようと呼びかけた。QCon San Francisco の基調講演は「ハーネスこそ新しい OS」と言い切り、Google はエージェント専用の実行基盤を出した。モデルの外側をどう組むかが、今日の主題。

1. [OpenAI、社内の perplexity 推移を公開し業界共通の指標に](https://openai.com/index/perplexity-and-intelligence/) (HN・英語)<br>
   チーフサイエンティストのパホツキ氏が、競合に手の内を見せてでも安全基準の土台を作りたいと説明

2. [QCon SF 基調講演「ハーネスは新しい OS だ」](https://www.infoq.com/news/2026/11/harness-new-operating-system/) (InfoQ・英語)<br>
   Mad Labs のラジャシェカール CEO が、権限や状態管理などを OS の役割に一つずつ対応させた

3. [Agent Harness を150行の Python で自作して理解する](https://qiita.com/yamamoto_a_genee/items/76562c5c80032ad9e962) (はてブ)<br>
   ツール実行・簡易ガードレール・可観測性・文脈保護の4点に絞った最小構成を、動くコードで追える

4. [Google、AI エージェントを microVM で隔離する「Agent Compute Engine」](https://www.infoq.com/news/2026/11/google-agent-compute-engine/) (InfoQ・英語)<br>
   API キーや OAuth トークンはサンドボックスに置かず、外部のゲートウェイが代わりに差し込む設計

5. [あらゆるソフトをエージェントから操作可能にする「CLI-Anything」](https://github.com/HKUDS/CLI-Anything) (GitHub Trending・英語)<br>
   香港大学 HKUDS のプロジェクトで、コミュニティ製 CLI を pip 経由の CLI-Hub から入れて Claude Code や Cursor に渡せる

6. [CI の失敗を読んで修正 PR まで出す OSS エージェント「OpenSRE」](https://github.com/Tracer-Cloud/opensre) (GitHub Trending・英語)<br>
   失敗した実行ログから原因をたどる CLI で、自前のモデルでセルフホストでき、現在はパブリックアルファ

7. [AI にテストケースを書かせるな、ルールを書け](https://zenn.dev/karamage/articles/73027ee36796dc) (はてブ)<br>
   TLA+ 系の言語 Quint でチケット販売の例を検証し、実装もテストも AI 任せの「自作自演の満点」を崩す

8. [C 育ちのベテランが戸惑った、Swift の async/await と Task](https://zenn.dev/shinchi007/articles/8c07659d99c0f4) (Zenn)<br>
   Kotlin のコルーチンとの比較連載の第4回で、管理の単位がスコープではなくタスクとアクターだと整理

9. [Electron なし・サブスクなしの macOS スクショツール「macshot」](https://github.com/sw33tLie/macshot) (GitHub Trending・英語)<br>
   Swift 製のネイティブアプリで、個人情報の自動マスク、OCR と翻訳、スクロールキャプチャまで備える

10. [トヨタ・日産・ホンダ、部品の標準化でコスト削減へ](https://www.caranddriver.com/news/a74490092/toyota-nissan-honda-standardize-parts-lower-costs/) (HN・英語)<br>
   自工会の佐藤会長が発表、まず鋼材の品質基準と樹脂の規格、ワイヤーハーネスの色分けから揃える
