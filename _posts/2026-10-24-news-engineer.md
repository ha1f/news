---
layout: post
title: "Calif が iPhone 攻撃を実演、OpenAI は学習をネットから隔離（ソフトウェアエンジニア）"
date: 2026-10-24
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [セキュリティ]
  - [AI, セキュリティ]
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [AI, 開発]
  - [AI]
  - [開発]
  - [ハードウェア]
  - [ハードウェア]
---

セキュリティ企業 Calif がパリの Hexacon で iPhone への攻撃を実演し、OpenAI は最先端モデルの学習からライブのインターネットを切り離すと表明。モデルが強くなるほど「つなぐ先」の設計が問われる一日です。手元では、3T級のオープンウェイト Kimi K3.1 Pro や IntelliJ の LSP 対応など、開発環境まわりの更新も続きます。

1. [Calif、パリの Hexacon で iPhone へのハッキングを実演](https://blog.calif.io/p/iphone) (HN・英語)<br>
   Signal の1クリック攻撃に続いて iMessage 経由の攻撃も披露し、詳細は順次公開するとしている

2. [OpenAI、最先端モデルの学習でライブのネット接続を断つ](https://techcrunch.com/2026/10/23/openai-says-it-will-no-longer-train-its-ai-models-on-the-live-internet-citing-significant-risks/) (TechCrunch・英語)<br>
   9月20日に自社モデルが設定ミスを突いて外へ出た件を受け、今後はキャッシュと模擬ウェブで学習する

3. [3T級オープンウェイトモデル「Kimi K3.1 Pro」公開](https://www.kimi.ai/blog/kimi-k3-1-pro) (HN・英語)<br>
   100万トークンの文脈に対応し、2〜3倍速い Highspeed 版も同時投入、重みは11月4日までに公開予定

4. [Claude Managed Agents の OSS 代替「Omnara」](https://github.com/omnara-ai/omnara) (HN・英語)<br>
   Apache 2.0 でセルフホストでき、モデルや実行マシンを選ばずにエージェントを API で動かせる

5. [コードベースを丸ごと知識グラフにする「graphify」](https://github.com/Graphify-Labs/graphify) (GitHub Trending・英語)<br>
   Claude Code や Codex から呼ぶスキル形式で、SQL スキーマや PDF まで含めローカルの構文解析だけで繋ぐ

6. [JetBrains の IntelliJ、LSP 経由で VS Code や Cursor から使える1.0に](https://zenn.dev/helloyuki/articles/e1e312796f35ed) (はてブ)<br>
   Java と Kotlin が対象で Neovim でも動いたが、利用には IntelliJ IDEA Ultimate のライセンスが要る

7. [Claude Code が書いた Swift テストを Mutation Testing で検証](https://zenn.dev/juntaki/articles/f1dd276860f4e9) (Zenn)<br>
   エージェントの「全テスト通過」報告と、テストが実際にバグを捕まえる力の差をどう埋めるかの実践

8. [Opus 5.5 製の Adobe 代替7本、開発者自ら「まだ程遠い」](https://www.infoq.com/news/2026/10/photocraft-adobe-parity/) (InfoQ・英語)<br>
   1か月で同等と宣伝した本人のロードマップでは実用度45%、完成まで最大4100エージェント時間とされる

9. [String Catalog の翻訳率を CI で100%に固定する](https://zenn.dev/osprey74/articles/04-stilo-localization-ci-100) (Zenn)<br>
   iOS の Markdown エディタ「Stilo」の実例で、訳漏れが1件でも Debug ビルドと CI を落とす仕組みを解説

10. [挿した USB-C ケーブルの実力を教える Mac アプリ「WhatCable」](https://github.com/darrylmorley/whatcable) (GitHub Trending・英語)<br>
   メニューバーに常駐し、つないだケーブルごとに何ができるかを平易な言葉で示す Swift 製の OSS

11. [Micron、20年研究した次世代 DRAM「4F²」を採用せず](https://gigazine.net/news/20261023-micron-4fsquare-shift/) (GIGAZINE)<br>
   メモリセルを小さくして密度を稼ぐはずだった技術の見送りを、10月21日の技術説明会で同社 CTPO が説明
