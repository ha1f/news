---
layout: post
title: "2026年8月17日（ソフトウェアエンジニア）"
date: 2026-08-17
profile: engineer
tags: [AI, 開発, セキュリティ]
---

Anthropicがシステムプロンプトを全文公開し、HNで500ポイント超の反響。Lobstersでは「バグの数は自分で選べるようになった」とAI時代のソフトウェア品質論が盛り上がり、ProtobufへのLSP対応やCloudflareのアナリティクス無断注入など、開発者の道具と環境に直結するニュースが並ぶ。

1. [Claude、システムプロンプトを全文公開](https://platform.claude.com/docs/en/release-notes/system-prompts) (Hacker News)<br>
   モデルの振る舞いを規定するプロンプトの全容が読める

2. [AIモデルは意図的に劣化させられている](https://w4g1.dev/blog/models-are-getting-dumber-on-purpose) (Hacker News)<br>
   蒸留・量子化によるコスト削減が推論能力を削る構造を分析

3. [Kitesurf: CloudflareのAI専用超軽量ヘッドレスブラウザ](https://www.publickey1.jp/blog/26/aikitesurfcloudflare.html) (Publickey)<br>
   Rust+WasmでタブもUIもないエージェント向けブラウザを実現

4. [Protobufに公式LSPサポート](https://buf.build/blog/protobuf-lsp) (Hacker News)<br>
   補完・定義ジャンプ・リント連携がエディタ上で動く

5. [Cloudflare、ネームサーバー切替時にアナリティクスを無断注入](https://news.ycombinator.com/item?id=49322107) (Hacker News)<br>
   同意なくトラッキングスクリプトが埋め込まれると報告が相次ぐ

6. [Rust標準ライブラリを破壊的変更から守る仕組み](https://predr.ag/blog/protecting-the-rust-stdlib-from-breakage/) (Lobsters)<br>
   意図しないAPI変更を検出するテスト戦略の詳細

7. [C3言語の作者「C言語の代替を作っていたつもりが…」](https://c3-lang.org/blog/i_thought_i_was_building_a_c_replacement/) (Lobsters)<br>
   設計の方向転換と、既存言語との差別化に至った経緯

8. [「バグの数は自分で選べるようになった」](https://nolanlawson.com/2026/08/16/you-can-just-choose-how-many-bugs-you-want-now/) (Lobsters)<br>
   AIコード生成時代に品質をどう制御するかの考察

9. [Liquid GlassレンズティンティングをUISliderで実装](https://www.reddit.com/r/swift/comments/1vot164/i_made_a_liquid_glass_lens_tinting_control_for/) (Reddit)<br>
   iOS 26のLiquid Glassエフェクトを自前コントロールで再現

10. [Eigendrum — 図形を描いて音を聴く](https://baselashraf81.github.io/eigendrum/) (Hacker News)<br>
    描いた形状の固有振動を計算してドラムサウンドに変換するWebアプリ
