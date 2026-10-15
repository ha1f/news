---
layout: post
title: "OpenCode 2.0 登場、Go 1.27 は接続再利用で約5倍速（ソフトウェアエンジニア）"
date: 2026-10-15
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [AI, 開発]
  - [AI, 開発]
  - [AI, ハードウェア]
  - [AI]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [セキュリティ]
  - [セキュリティ]
  - [開発]
---

OpenCode 2.0 が登場し、Go 1.27 は HTTP/1 の接続再利用で 100 回の逐次リクエストを約 710 ミリ秒から 150 ミリ秒へ縮めた。エージェント基盤もランタイムも土台の作り替えが続く一日。ローカル向けの軽量モデルや、AI 時代の開発のボトルネックを問う記事も並ぶ。

1. [OpenCode 2.0 公開、常駐サービス化と API 刷新](https://anoma.ly/notes/opencode-2-0/) (HN・英語)<br>
   TUI・Web・デスクトップが同じ常駐プロセスを共有する構成に変わり、旧 API は作り直された。

2. [TypeSafe AI が Jev 1.14.0 を公開](https://typesafe.ai/blog/jev-1-14) (HN・英語)<br>
   画像や長いコンテキストは本番非推奨の「danger zone」フラグ付きで提供し、安定版とは分ける方針。

3. [Liquid AI の「LFM2.5-24B-A2B」、ローカルエージェント向け](https://gigazine.net/news/20261014-lfm2-5-24b-a2b/) (GIGAZINE)<br>
   Gemma 4 や Qwen3.6 の同クラス版を上回るとする比較結果が示されている。

4. [埋め込みモデルを文字起こしに転用した Embedding Gemma Transcribe](https://gigazine.net/news/20261014-embetting-gemma-transcribe/) (GIGAZINE)<br>
   Apple Silicon の Mac 上でオフライン動作し、15分の音声が約3秒で文字になるという。

5. [AI にコードを書かせた先で、詰まりはどこへ移ったか](https://findy-code.io/media/articles/aisaji-gota_bara) (はてブ)<br>
   cc-sdd の作者が、実装が速くなった後に残る4つの詰まりどころを整理する。

6. [Go 1.27、HTTP/1 の接続再利用を改善](https://go.dev/blog/http-connection-reuse) (HN・英語)<br>
   Go チームの計測で、同一ホストへの逐次 GET 100 回が約5倍速くなった理由を TCP/TLS の往復から解説する。

7. [Next.js の公開ページで読む chunk を 48 本から 16 本に](https://zenn.dev/onthebakery/articles/5a27024f61405f) (Zenn)<br>
   webpack の splitChunks に20行ほど足した設定と、まとめた結果の副作用を実例で書く。

8. [「パスキーは罠」論への反論、同期型に attestation はない](https://scotthelme.co.uk/passkeys-are-not-a-trap/) (HN・英語)<br>
   続報（10/12掲載）。iCloud キーチェーンや 1Password の同期パスキーはサイトに製造元の証明を渡さない、と技術面から検証する。

9. [Yandex 攻撃後、悪性ボットは消えず他社ホスティングへ移動](https://blog.cloudflare.com/yandex-outage/) (HN・英語)<br>
   Cloudflare Radar の ASN 別データで、検索クローラの減少と脆弱性スキャンの移転を切り分ける。

10. [curl で見られる自分のサイトを手書き ANSI で作る](https://nytpu.com/gemlog/2026-03-18) (HN・英語)<br>
   参考にした2サイトが10/14に動かなくなった経緯とあわせ、端末向けページの作り方を紹介する。
