---
layout: post
title: "Opus 5.5公開、運用コスト4割減（ソフトウェアエンジニア）"
date: 2026-09-23
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
---

Anthropicが「Claude Opus 5.5」を公開し、運用コストを4割抑えつつ最高性能を更新。同じ日、OpenAIの「GPT-6 Astra」は2005年から未解読だった暗号文を独力で解読してみせた。DoorDashやCloudflareの現場ではAIエージェントとインフラ最適化が地道に進み、Swiftの世界にも新顔のツールが相次ぐ一日に。

1. [Anthropic、Claude Opus 5.5を公開](https://www.anthropic.com/claude-opus-5-5) (HN・英語)<br>
   コード68万行の移行を1日で終えた例も。運用コストはOpus 5比40%減。

2. [GPT-6 Astra、未解読エニグマ暗号を独力解読](https://www.cryptocellar.org/bgac/the-mvueh-break.html) (HN・英語)<br>
   続報（9/22掲載）。自作のEnigmaシミュレータとBombeで暗号解読に成功。

3. [並列AIエージェントの衝突を防ぐ「Foremerge」](https://github.com/naw103/foremerge) (HN・英語)<br>
   Git上で動くOSS。Claude CodeやCursorが同じコードに触る前に警告する。

4. [DoorDash、AIエージェントでフラグ6万件を整理](https://www.infoq.com/news/2026/09/doordash-feature-flag-cleanup/) (InfoQ・英語)<br>
   50件の試験で45件が使えるPRに、1件平均13.8分・4.79ドルで完了。

5. [Cloudflare、オリジンTLSの設定を自動計測](https://www.infoq.com/news/2026/09/cloudflare-automatic-key-exchang/) (InfoQ・英語)<br>
   ハンドシェイク再試行を52%→3.7%に削減、p90遅延も150ms短縮。

6. [Swift向け音声AI SDK「FluidAudio」が急上昇](https://github.com/FluidInference/FluidAudio) (GitHub Trending・英語)<br>
   Appleの神経エンジンで文字起こしや話者分離をオンデバイス実行、GPU不要。

7. [LinuxやWindowsでiOSアプリを作れる「xtool」](https://github.com/xtool-org/xtool) (GitHub Trending・英語)<br>
   Xcode不要、SwiftPMだけでビルド・署名・実機インストールまで完結。

8. [小米、新モデル「MiMo-V2.6」を公開](https://www.reddit.com/r/MachineLearning/comments/1wn36d4/xiaomi_releases_mimov26_frontier_intelligence_all/) (Reddit・英語)<br>
   強化学習の総コストは350万ドル。ベンチマーク結果をダッシュボードで公開中。

9. [ドメインの変換はHandlerとUseCaseのどちらでやるべきか](https://zenn.dev/jisou/articles/b7e19c4a2d80f6) (Zenn)<br>
   Handlerでドメインオブジェクトを組み立てる実例から、責務の境界を考察。

10. [ポケモンGO Plus+を分解、睡眠計測を自動化](https://zenn.dev/koichi73/articles/pokemon-go-plus-teardown-esp32) (Zenn)<br>
    振動モーターで揺らし、狙った睡眠段階の割合を意図的に再現する装置を作った。
