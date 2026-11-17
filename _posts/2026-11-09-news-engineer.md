---
layout: post
title: "Claude Code の利用制限と秘密情報の漏れ、任せ方が論点に（ソフトウェアエンジニア）"
date: 2026-11-09
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, 社会]
serendipity: [9]
article_tags:
  - [AI, ビジネス]
  - [AI, セキュリティ]
  - [AI, 開発]
  - [開発, AI]
  - [AI, 開発]
  - [開発]
  - [開発, AI]
  - [開発]
  - [社会]
---

Goldman Sachs が Claude Code を開発部門の外から引き上げ、公開リポジトリでは「今後確認しない」が残した秘密情報が1,379件見つかった。コーディングエージェントは、誰に・どこまで任せるかを決める段階に入っている。MCP の Ruby SDK、エージェント前提の Git フォージ、iPhone からエージェントを見守るアプリと、道具のほうも揃ってきた。

1. [Goldman Sachs、トレーダーと銀行員から Claude Code を取り上げ](https://www.thestateofai.com/news/goldman-sachs-claude-code-traders-bankers) (HN・英語)<br>
   10月の社内指針で Claude Code と GitHub をエンジニア限定にした。7月には CIO が非技術職のバイブコーディングを持ち上げていた

2. [Claude Code の「今後確認しない」、秘密情報を GitHub に残す](https://dev.ponkotsu.dev/entry/claude-code-settings-local-secrets) (はてブ)<br>
   承認したコマンドが settings.local.json に平文で残る仕組みと、DB パスワード379件など漏れた中身の内訳

3. [Claude Code をやめて最小構成のエージェント「Pi」へ](https://caleb.software/posts/claude-to-pi.html) (HN・英語)<br>
   長年の利用者が、CLAUDE.md と AGENTS.md の二重管理など積み重なった不満を挙げて乗り換えを説明する

4. [元 GitHub CEO の Entire、エージェントと人が協働する Git フォージ](https://www.infoq.com/news/2026/11/entire-git-forge-coding-agents/) (InfoQ・英語)<br>
   PR 中心のレビューではなく、エージェントの作業の調整・版管理・監査を軸に据える設計を Dohmke CEO が語る

5. [MCP 公式の Ruby SDK が仕様の全機能に対応、「Tier 1」に](https://www.publickey1.jp/blog/26/mcpmcpruby_sdkmcp_sdk_tier_1.html) (Publickey)<br>
   7月の 1.0 時点では Tier 2。TypeScript・Python・C#・Go・Rust に続く6言語目で、ステートレス接続も使える

6. [Cloudflare、D1 の制御プレーンを数百万 DB 規模へ作り直し](https://www.infoq.com/news/2026/11/cloudflare-d1-control-plane/) (InfoQ・英語)<br>
   メタデータは Postgres、分析は ClickHouse、ルーティングは Workers KV と役割を分け、クエリ処理はエッジに残す構成

7. [iPhone から手元のコーディングエージェントを操る「Heeler」](https://github.com/ZingerLittleBee/Heeler) (GitHub Trending・英語)<br>
   SSH 越しに herdr のエージェントを見守る Swift 製アプリ。libghostty の端末を積み、人の判断が要るとプッシュ通知が来る

8. [iPhone で macOS を動かすエミュレーター「Henge」公開](https://smhn.info/202611-henge-macos-emulator-iphone-ipad-release) (はてブ)<br>
   開発者の levi 氏は独自 JIT で arm64 コードを実行し、iPhone 17 Pro で macOS 15.6.1 が約15秒でロック画面まで起動する

9. [エンジニアのための家庭菜園入門「Vegetable Gardening for Engineers」](https://jrcpl.us/contrib/2020/gardening-for-engineers/) (HN・英語)<br>
   John Chang 氏が大学の普及資料や種苗会社の作物ガイドから、光・温度・養分を表にまとめた水耕・鉢栽培の手引き
