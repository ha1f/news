---
layout: post
title: "Deno合流とCopilotのRust化、再編相次ぐ（ソフトウェアエンジニア）"
date: 2026-10-10
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, 科学, ハードウェア]
article_tags:
  - [開発]
  - [AI, ビジネス]
  - [開発]
  - [セキュリティ, AI]
  - [セキュリティ]
  - [AI, 開発]
  - [AI]
  - [ハードウェア]
  - [AI, 科学]
  - [開発]
---

Deno チームが Cloudflare に合流し、TypeSafe AI は 8.7 億ドルを調達した。GitHub は Copilot の実行基盤 80 万行を Rust へ移し、Anthropic は OSS 向けの脆弱性スキャンを無償で始める。ランタイム、AI インフラ、セキュリティの再編が一度に動いた日。

1. [Deno チームが Cloudflare に合流、workerd と celld も統合へ](https://deno.com/blog/cloudflare) (HN・英語)<br>
   Ryan Dahl が語る動機は、Workers と Durable Objects を自前環境でも動かしやすくすること。

2. [TypeSafe AI、a16z 主導で 8.7 億ドル調達](https://typesafe.ai/blog/series-ai) (HN・英語)<br>
   評価額は 75 億ドルで、Martin Casado が取締役に就く。同社は意思決定向けモデル「Jev」を早期提供中。

3. [GitHub、Copilot 実行基盤を AI 支援で Rust 化](https://www.infoq.com/news/2026/10/github-copilot-rust-migration/) (InfoQ・英語)<br>
   TypeScript と Node.js の 80 万行超を約 14.5 週で移行し、N-API で段階的に置き換えた。

4. [Anthropic、OSS 向け脆弱性スキャナ「OSS Scanner」を開始](https://www.anthropic.com/research/launching-opt-in-vuln-finding-service-for-open-source) (はてブ)<br>
   参加プロジェクトは定期スキャンを無料で受けられる。候補 2.9 万件のうち人手で精査できたのは約 6,000 件で、確認作業が詰まりどころ。

5. [Let's Encrypt、証明書の有効期間を 64 日に短縮](https://gigazine.net/news/20261009-lets-encrypt-cuts-certificate-lifetimes-64-days/) (GIGAZINE)<br>
   2027 年 2 月 10 日から、従来の 90 日が変わる。自動更新の間隔や監視設定の見直し時期。

6. [Haiku 5.5 を機に、サブエージェントの割り当てを見直した](https://zenn.dev/genda_jp/articles/haiku-5-5-subagent-roles) (Zenn)<br>
   GENDA の開発者が、Haiku で初めて effort を指定できる点と単価を手がかりに役割分担を組み直した記録。

7. [Qwen3.8-27B を 7.89GB にした量子化モデル「Saluki 27B」](https://pc.watch.impress.co.jp/docs/news/2147095.html) (はてブ)<br>
   Underdog が公開した約 2bit の GGUF で、ツール呼び出しの精度維持に重点を置く。標準の llama.cpp でそのまま動く。

8. [Steam 更新で 0.5GiB の DL に SSD 書き込み 6GiB](https://zenn.dev/berobero/articles/steam-update-ssd-writes) (Zenn)<br>
   専用サーバー版 Rust の更新を steamcmd で実測。ReFS の block clone を使うと書き込みは約 2 割減った。

9. [AI に 400 年分の史料を読ませ、忘れられた隕石報告を発掘](https://jessewaites.com/blog/post/i-pointed-ai-at-400-years-of-archives/) (HN・英語)<br>
   歴史家 Breen の dodo 発見に触発された開発者が、オランダ東インド会社の史料検索で別の記録も拾った。

10. [Quake を安全な Rust に移植、ブラウザで遊べる](https://quake-srp.pages.dev/) (HN・英語)<br>
    依存ゼロの Rust を WebAssembly にして、シェアウェア版の第 1 エピソードが動く。
