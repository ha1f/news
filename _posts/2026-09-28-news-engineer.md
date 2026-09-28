---
layout: post
title: "Apple新カメラ、真正性巡り論争（ソフトウェアエンジニア）"
date: 2026-09-28
profile: engineer
tags: [開発, AI, セキュリティ, ハードウェア]
---

Appleが「撮影の瞬間にセンサー側で署名する」新カメラモードを発表し、真正性の証明を巡る論争が起きている。GoogleはGKEでモデル起動を9割近く高速化、PlanetScaleはPostgreSQLで1億1800万QPSの新記録を出すなど、基盤の足回りを削る話が目立つ一日。言語仕様の進化から個人開発の設計判断、AIエージェント向けツールまで、規模の大小が入り混じる。

1. [Apple、iPhone18 Proでセンサー時点の写真に署名](https://www.infoq.com/news/2026/09/apple-reference-image-provenance/) (InfoQ・英語)<br>
   写真を撮った画面ごと再撮影されたら防げるのか、HNで疑問の声。

2. [Google、GKEのPodスナップショットで起動最大89%短縮](https://www.infoq.com/news/2026/09/gke-pod-snapshots-benchmarks/) (InfoQ・英語)<br>
   700億パラメータモデルの読み込みが37秒に短縮、実務者は無効化の判定基準に注目。

3. [PlanetScale、Postgresで1.18億QPSを達成](https://www.publickey1.jp/blog/26/planetscalepostgresql11800qpsdbneki.html) (Publickey)<br>
   シャーディングを自動化した新サービス「Neki」としてプレビュー公開。

4. [「Java 27」正式リリース、G1 GCが全環境デフォルトに](https://www.publickey1.jp/blog/26/java_27g1_gctls_13.html) (Publickey)<br>
   TLS 1.3向けに耐量子暗号のハイブリッド鍵交換も追加。

5. [Rust SIMDライブラリ保守者が2026年の状況を総括](https://shnatsel.github.io/state-of-simd-rust-2026/) (HN・英語)<br>
   std::simdやwide、pulpなど主要ライブラリの設計を横断比較。

6. [2FAアプリ開発者が考えた「依存を選ぶ」自由](https://zenn.dev/satoh_yoshiharu/articles/hiken-dependency-boundary) (Zenn)<br>
   Authy Desktop終了でTOTPを持ち出せなくなった経験がきっかけ。

7. [配置を自分で決める図表用DSL「Reladraw」公開](https://github.com/reladraw/reladraw) (HN・英語)<br>
   MermaidとdrawIOの中間を狙う設計で、Show HNで389点。

8. [Anthropic、GitHub用Claude Codeアクションが急上昇](https://github.com/anthropics/claude-code-action) (GitHub Trending・英語)<br>
   @claudeメンションやissue割当てで自動的にPR対応する仕組み。

9. [FlutterからApple Foundation Modelsを呼ぶ最小構成](https://qiita.com/TechStudioLab/items/1d08c21fd53cecaff4c4) (Qiita)<br>
   Swift越しにiOSのオンデバイスAIをFlutterアプリから呼ぶ橋渡しを解説。

10. [LoRA適用モデル、llama.cppでだけ壊れた原因を調査中](https://zenn.dev/atemoya/articles/5032fc34095c5d) (Zenn)<br>
    学習率を半分にすると崩れが消えたが、原因はまだ特定できず。

11. [開発者が自分のブログをTorの隠しサービス化](https://david.alvarezrosa.com/posts/self-hosting-on-the-dark-web/) (HN・英語)<br>
    証明書もDNSも無く、公開鍵から.onionアドレスを生成する仕組み。
