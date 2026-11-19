---
layout: post
title: "Nginx の HTTP/2 に RCE 2件、AI 時代の詰まりはレビューへ（ソフトウェアエンジニア）"
date: 2026-11-19
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
serendipity: [10, 11]
article_tags:
  - [セキュリティ]
  - [開発, セキュリティ]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [科学]
  - [AI, 科学]
---

Nginx の HTTP/2 に CVSS 9.2 の RCE が2件、今夜は PHP もサポート中の全版で修正版を出す。足元のミドルウェアが揺れる朝だ。一方でハーバード大の調査は、AI エージェントの時代にボトルネックがコードレビューへ移ったと示し、「どこまで読むか」を問う記事が並ぶ。

1. [Nginx の HTTP/2 に認証不要の RCE が2件](https://www.wiz.io/blog/nginx-http2-rce-vulnerabilities) (HN・英語)<br>
   Wiz など5組織が別々に発見し、片方は2015年の 1.9.5 以降が影響を受ける

2. [PHP、サポート中の全版で「致命的」な脆弱性を今夜修正](https://forest.watch.impress.co.jp/docs/news/2157690.html) (はてブ)<br>
   公開は日本時間19日23時台の予定で、Critical の件は既定外の構成に限って影響するという

3. [AI エージェントでコードは3割増、レビュー時間は49%増](https://gigazine.net/news/20261119-ai-coding-agents-shifted-bottleneck-code-review/) (GIGAZINE)<br>
   ハーバード大の2人が718社を分析し、変更要求を受ける PR の割合はほぼ倍になった

4. [最近、コードを真面目に読まなくなった](https://zenn.dev/hiromoo/articles/reading-less-preparing-more) (はてブ)<br>
   AI の差分を全部は精読せず、テストで判断が難しい箇所だけ掘るという時間配分の見直し論

5. [Tencent、エージェントに PR まで出させる自前運用の基盤「LoopForge」](https://github.com/Tencent/LoopForge) (GitHub Trending・英語)<br>
   Claude Code や Codex など10種の CLI を Docker の砂場で動かし、手順を SOP として使い回せる。MIT ライセンス

6. [Snapchat、Claude Code や Cursor で AR レンズを作れる CLI](https://techcrunch.com/2026/11/18/snapchat-now-lets-developers-build-ar-lenses-with-ai-coding-assistants-like-claude-code-and-cursor/) (TechCrunch・英語)<br>
   プロンプト1つでレンズを作る既存の「Easy Lens」を、開発者の手元の作業に持ち込む「Easy Lens CLI」

7. [Apple Foundation Models に任せるのは「抜き出し」だけ](https://zenn.dev/leafdev/articles/273a3d6093262f) (Zenn)<br>
   カレンダーアプリ「Aica」の作者が、日付計算はルールで補い、行ごとに渡すと精度が上がったと報告

8. [Meta、Android の仮想デバイス基盤 Cuttlefish を Apple Silicon の Mac へ](https://engineering.fb.com/2026/11/13/android/cuttlefish-on-mac/) (HN・英語)<br>
   Linux 専用だった AOSP の仕組みを、AI グラスの開発のために QEMU ごと macOS へ移植した経緯

9. [PostgreSQL 上の MongoDB 互換 DB「DocumentDB」が 1.0](https://www.infoq.com/news/2026/11/mongodb-compatible-documentdb/) (InfoQ・英語)<br>
   Microsoft が2025年に始めた OSS で、PostgreSQL 15〜18 に対応し Kubernetes オペレーターも付く

10. [「遊☆戯☆王」の詰めデュエルは NP 困難](https://gigazine.net/news/20261118-yugioh-factoring/) (GIGAZINE)<br>
   YouTube の Bengal Tiger が、ライフ1236桁の盤面を使ってカードの手順を計算問題に置き換える

11. [AI の鼻は人並み、Osmo が嗅覚の基盤モデルを主張](https://www.technologyreview.com/2026/11/18/1148816/smell-startup-osmo-ai-nose-good-as-humans/) (MIT TR・英語/一部会員限定)<br>
   約30人の嗅ぎ手が付けた香りの記述を学習データにし、香水業界ではすでに調香に使われている
