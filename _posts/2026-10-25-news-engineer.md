---
layout: post
title: "Brotli の欠陥 HTTP2Shell が拡大、Anthropic はサブエージェント削減を提唱（ソフトウェアエンジニア）"
date: 2026-10-25
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [セキュリティ]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [AI]
---

Google の圧縮ライブラリ Brotli の欠陥「HTTP2Shell」が、Node.js から Python など HTTP を扱う実装全般へ広がった。Anthropic はサブエージェントを減らす設計指針を公開し、VS Code 1.142 はエージェントと同じ画面を触れる Canvas を載せた。エージェントをどう組むかが今日の主題。

1. [Brotli の欠陥「HTTP2Shell」、Node.js 以外の HTTP 実装にも波及](https://www.aikido.dev/blog/python-packages-vulnerable-node2shell-brotli-cve-2026-111497) (HN・英語)<br>
   セキュリティ企業 Aikido の整理。Python も対象で、修正前は Brotli 展開の無効化を勧める

2. [Anthropic、サブエージェントを本体ループに畳む設計指針](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop) (はてブ)<br>
   複数の企業導入の比較で、スキルを持たせた単一エージェントが品質とコストで勝つ例が多かったという

3. [VS Code 1.142、エージェントと同じ画面を触れる「Canvas」](https://qiita.com/shahin0809/items/81e6a6737b2254bdc6ed) (はてブ)<br>
   10月14日公開版のプレビュー機能。チャット横に開く画面の使いどころを Qiita の投稿者が整理

4. [エージェントのスキルを一括管理する Mac アプリ「chops」](https://github.com/Shpigford/chops) (GitHub Trending・英語)<br>
   対応は Claude Code、Cursor、Codex、Windsurf、Amp の5種。ツールをまたぐ編集が一画面で済む

5. [ヒープも GC も持たない安全なシステム言語「Goose」](https://aardappel.github.io/goose/) (HN・英語)<br>
   16本のベンチマークで素直な C++ の3.3倍、最良の安全な Rust の1.12倍の速度と主張

6. [Cloudflare、一貫性ハッシュの最適化で RAM を100TB削減](https://www.infoq.com/news/2026/10/cloudflare-hashing-optimization/) (InfoQ・英語)<br>
   負荷分散サービスの Rust 実装 pingora-ketama で、ハッシュリングの項目を詰めて省メモリ化した

7. [SwiftUI の @State はなぜマクロになったのか](https://zenn.dev/takehito/articles/50145459523321) (Zenn)<br>
   Xcode 27 からの実装変更を Xcode 26.6 と 27.1 で比べ、初期値の遅延評価の利点と代償を整理

8. [Wireshark の代替を狙う Mac 用パケット表示「TCPViewer」](https://github.com/ProxymanApp/TCPViewer) (GitHub Trending・英語)<br>
   HTTP デバッグプロキシ「Proxyman」の開発元が公開した、macOS 向けのオープンソース

9. [macOS 27 で Mission Control が壁紙だけに、原因は Aqua Voice](https://zenn.dev/tktcorporation/articles/macos27-mission-control-aqua-voice-pet) (Zenn)<br>
   音声入力アプリのペット機能が出す透明ウィンドウを、全画面扱いされる既知の不具合と比べて追った

10. [AI がターミナルの画面を予測して描く「WorldTUI」](https://gigazine.net/news/20261023-worldtui/) (GIGAZINE)<br>
    約3.6億パラメーターのモデルが打鍵に応じて画面を描く仕組みで、ブラウザから無料で試せる
