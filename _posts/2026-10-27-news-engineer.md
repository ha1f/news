---
layout: post
title: "Cloudflare で他社の応答が混入、JetBrains はエージェント IDE（ソフトウェアエンジニア）"
date: 2026-10-27
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [AI, セキュリティ]
  - [AI, 開発]
  - [AI, 開発]
  - [AI]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア]
  - [開発]
  - [ハードウェア]
---

Cloudflare の Workers AI で、別の顧客の応答が混じった回答が155件。原因は推論エンジンの不具合でした。JetBrains はエージェント前提の IDE「ThinkRail」を公開し、エージェントの土台をどう組むかの議論も続きます。Apple は有機EL化した iPad mini を発表、Mac では毎年恒例の旧 Xcode 問題も。

1. [Cloudflare、GLM-5.3 で他社の応答が混入した155件を報告](https://blog.cloudflare.com/kv-cache-exposure-remediation/) (HN・英語)<br>
   68万トークンを超える長い入力でだけ起き、推論エンジン SGLang の不具合と設定の食い違いが重なった

2. [エージェントの土台は「チェーン→グラフ→コード」へ](https://www.infoq.com/articles/agentic-ai-architecture-harness-evolution/) (InfoQ・英語)<br>
   Karthik Ramgopal 氏が3方式の脆さを比べ、要件を満たす最も単純な構成を選ぶよう勧める

3. [JetBrains、pi エージェントを核にした IDE「ThinkRail」](https://github.com/JetBrains/thinkrail) (GitHub Trending・英語)<br>
   作業ごとに git worktree を切り、複数のエージェントを並行で走らせる設計で、JetBrains のインキュベータ発

4. [手元の PC で動く ChatGPT 代替「Hob」](https://github.com/FrigadeHQ/hob) (HN・英語)<br>
   Frigade 製の MIT ライセンスのアプリで、PC の性能に合うオープンウェイトモデルを自動で選んで設定する

5. [Microsoft、Python の型解析を問い合わせる「Type Server Protocol」](https://github.com/microsoft/pylance-release/blob/main/docs/tsp/type-server-protocol.md) (HN・英語)<br>
   Pylance チームによる JSON-RPC の仕様で、LSP のデータ形を流用。まだ破壊的変更のありうる 0.x 版

6. [OpenTofu 1.13、plan 時点の「未確定値」を減らす関数を追加](https://www.infoq.com/news/2026/10/opentofu-1-13-unknown-values/) (InfoQ・英語)<br>
   Terraform 互換の OpenTofu で、モジュール作者が値の前提を書け、外れたら apply 時にエラーで止まる

7. [Classi、Claude Code と Ruby の公式イメージを自前ビルド](https://tech.classi.jp/entry/2026/10/26/163000) (はてブ)<br>
   PHP の緊急パッチで公式イメージを約3時間待った経験から、pixiv の手法を Ruby に移した記録

8. [macOS 27 で起動しない Xcode 26 を GUI で切り替える](https://zenn.dev/yanasan/articles/72820d8af11976) (Zenn)<br>
   実行ファイルの直接起動と xcode-select の併用が要点で、DEVELOPER_DIR だけでは SDK が混ざった

9. [Apple、有機EL・8.5型の新 iPad mini を発表](https://www.apple.com/jp/newsroom/2026/10/apple-gives-ipad-mini-its-biggest-update-ever/) (はてブ)<br>
   A20 Pro を積んで薄さ5.4mm、iPadOS 27 を搭載し、11万9800円からで11月6日に発売

10. [Mac・iPhone・iPad 向けの OSS ブラウザ「Crest」](https://github.com/pauljoda/Crest) (GitHub Trending・英語)<br>
    SwiftUI 製で、Mac では Chromium と WebKit を使い分け、用途別の Spaces ごとに Cookie も履歴も分ける

11. [Pollen Robotics の小型ロボ「Microduck」、2万台が売れる](https://techcrunch.com/2026/10/23/hottest-toy-for-christmas-nvidia-ceo-plays-with-adorable-microduck-robots-20000-sell/) (TechCrunch・英語)<br>
    音声の合図で座り、倒れて昼寝し、宙返りもする。同社のリポジトリは今日の GitHub Trending にも並ぶ
