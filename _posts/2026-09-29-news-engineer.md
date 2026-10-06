---
layout: post
title: "Sonnet 5.5公開、Cloudflareはエージェント向けCLIへ（ソフトウェアエンジニア）"
date: 2026-09-29
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [AI]
  - [AI, セキュリティ]
  - [開発, AI]
  - [開発]
  - [開発]
  - [セキュリティ, 開発]
  - [開発]
  - [開発]
  - [ハードウェア]
  - [開発]
---

Anthropic が Claude Sonnet 5.5 を公開した。前世代より3割以上速く、料金は据え置き。暴走するAIエージェントへの対策が Nvidia から出る一方、Cloudflare は CLI の主な利用者をエージェントと見て作り直した。Rust、Java、HTTP/3 と、足回りの話も続く。

1. [Anthropic、Claude Sonnet 5.5 を公開](https://www.anthropic.com/claude-sonnet-5-5) (HN・英語)<br>
   前世代の Sonnet 5 より30%以上高速で、コーディング評価 Terminal-Bench 4.0 は10.3%から70.6%に上昇。

2. [Nvidia、暴走AIエージェントを封じ込める安全基盤を発表](https://techcrunch.com/2026/09/28/nvidia-launches-new-platform-for-reining-in-rogue-ai-agents/) (TechCrunch・英語)<br>
   ソフトとハードで独立した防御層を設け、エージェントがテスト環境から出ないようにする。今夏の Hugging Face 侵入事件が背景。

3. [Cloudflare、エージェント向けCLI「cf」を公開](https://blog.cloudflare.com/cloudflare-cf-cli-launch/) (HN・英語)<br>
   Wrangler の利用の48%がエージェント経由になり、約280操作だった対応範囲を全 API に広げた。設定は TypeScript で書ける。

4. [Meta、ZippyDB の前段に無状態プロキシ「ZGateway」](https://www.infoq.com/news/2026/09/meta-zgateway-zippydb-proxy/) (InfoQ・英語)<br>
   毎秒10億超の操作をさばき、常時接続数を約19分の1に減らす見積もり。接続管理を DB の外へ出す設計。

5. [マイクロソフト、Rust を社内 Tier 1 言語に格上げ](https://www.publickey1.jp/blog/26/rustcctstier_1.html) (Publickey)<br>
   C++・C#・TypeScript と並ぶ扱いになり、Windows ネイティブの社内開発環境とも統合される。

6. [オラクル、Java のセキュリティパッチを毎月提供へ](https://www.publickey1.jp/blog/26/javaai.html) (Publickey)<br>
   従来の3カ月ごとから短縮し、8月分から提供済み。AI による脆弱性発見の加速が理由。

7. [HTTP/3 を Docker で動かして確かめる](https://zenn.dev/sonicmoov/articles/http3-hands-on) (Zenn)<br>
   TCP を捨てて QUIC に土台を載せ替えた理由から入り、手元で挙動を確認する入門記事。

8. [傘予報アプリが毎朝「昔の天気」を通知していた](https://zenn.dev/soratomo/articles/986020b7f48c54) (Zenn)<br>
   iOS のローカル通知で repeats: true が原因だった。日ごとの予約とバックグラウンド更新で直した記録。

9. [PS5 の配信を DNS で横取りして画面共有](https://yashgarg.dev/posts/hijacking-ps5-rtmp-stream/) (HN・英語)<br>
   キャプチャカードなしで Discord に映すため、PS5 が使う RTMP の配信先ホスト名を書き換える手順。

10. [昔の「ビデオCD」が Windows のエクスプローラーを固まらせる](https://gigazine.net/news/20260928-windows-explorer-video-cd/) (GIGAZINE)<br>
    コピー中に転送速度が0になり UI が壊れる。Windows 10/11 で確認され、2023年前半の更新以降に発生。
