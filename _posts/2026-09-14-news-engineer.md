---
layout: post
title: "AppleがCore AIモデル群をOSS公開（ソフトウェアエンジニア）"
date: 2026-09-14
profile: engineer
tags: [AI, 開発, 科学]
---

AppleがCore AIのモデルツールキットをOSSで公開、Swift開発者がオンデバイスで自前モデルを動かす道が整った。Homebrew 7.0.0はサンドボックス強化とIntel Mac Tier 3移行を含むメジャーリリース。AIエージェントの欺瞞行動を問うBengioの論文が大きな議論を呼んでいる。

1. [AIエージェントはなぜ嘘をつき協調するのか](https://yoshuabengio.org/en/publication/why-are-ai-agents-lying-cheating-and-coordinating) (Hacker News)<br>
   Bengio共著、自律エージェントの欺瞞行動を体系的に分析

2. [Apple、Core AIモデルツールキットをOSS公開](https://github.com/apple/coreai-models) (GitHub Trending)<br>
   PyTorchモデルをApple Siliconへエクスポートし、Swiftで推論するまでの一式

3. [Tinycast――Swift製の軽量macOSランチャー](https://github.com/abue-ammar/tinycast) (GitHub Trending)<br>
   Raycast拡張をネイティブSwiftUIで実行。RAM 100MB未満、依存ゼロ

4. [Homebrew 7.0.0リリース](https://brew.sh/2026/09/13/homebrew-7.0.0/) (はてなブックマーク)<br>
   サンドボックス強化、ネイティブmacOSアプリ追加、Intel MacはTier 3へ

5. [Julia 1.13の主な変更点](https://julialang.org/blog/2026/09/julia-1.13-highlights/) (Hacker News)<br>
   科学計算言語の最新版、パフォーマンスと型システムの改善

6. [Tailscale「Aperture」正式リリース](https://www.publickey1.jp/blog/26/tailscalevpnaiapertureaitailscale.html) (Publickey)<br>
   VPNにAIエージェントを組み込めるゲートウェイ

7. [AI生成日本語の頻出語を検出するtextlintプリセット](https://blog.p1ass.com/posts/textlint-rule-preset-ai-words-ja/) (はてなブックマーク)<br>
   Claude Code hooksに組み込む使い方も紹介

8. [Wasmコンパイラに並行処理を載せたら1.46KBに縮んだ話](https://qiita.com/kanryu/items/a031d4928ddb7caa0784) (Qiita)<br>
   libcフリー、Goライク構文でWasm生成。前作2.56KBからさらに圧縮

9. [OpenTelemetry eBPF計装の舞台裏](https://zenn.dev/ymotongpoo/books/go-ebpf-primer) (Zenn)<br>
   Go Conference 2026登壇資料。GoバイナリならではのeBPF計装の4つの難所

10. [光速が時速5kmだったら？ 相対論的効果を体験できるWebアプリ](https://gigazine.net/news/20260913-walking-speed-light/) (GIGAZINE)<br>
    ブラウザ上で色のシフトや形状の歪みを視覚体験
