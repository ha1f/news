---
layout: post
title: "Linux KVM脱出の脆弱性PwnEscapeとAmazonのDuckLabs買収（ソフトウェアエンジニア）"
date: 2026-10-18
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, ハードウェア, 社会]
article_tags:
  - [セキュリティ, 開発]
  - [AI]
  - [ビジネス, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [セキュリティ, 開発]
  - [セキュリティ, ハードウェア]
  - [セキュリティ, 社会]
  - [開発]
---

Linux カーネルに、仮想マシンからホスト OS へ抜けられる深刻度 9.3 の脆弱性「PwnEscape」。一方で DeepSeek は新モデルを MIT ライセンスで公開し、Amazon は DuckDB の開発元 DuckLabs を買収した。エージェント基盤の隔離や、小型マイコンの物理攻撃といった守りの話題も並ぶ日。

1. [Linux の KVM 脱出脆弱性「PwnEscape」、深刻度 9.3](https://www.publickey1.jp/blog/26/linuxpwnescapecve-2026-99999linux_os.html) (Publickey)<br>
   原因は検証済み IPv4 ヘッダーのチェックサム関連データが書き換え可能だった点で、ネットワーク処理の欠陥。

2. [DeepSeek、新モデル V4.1 Flash を MIT ライセンスで公開](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) (HN・英語)<br>
   重みは FP8 形式で Hugging Face に置かれ、画像とテキストの入力に対応する。

3. [Amazon が DuckDB 開発元の DuckLabs を買収](https://www.infoq.com/news/2026/10/amazon-acquires-ducklabs/) (InfoQ・英語)<br>
   創業者 2 人は AWS 傘下でも開発を率い、OSS のまま続くと説明。Aurora PostgreSQL が最初の対応先。

4. [Perplexity、エージェント用サンドボックス「SPACE」をオープンソース化](https://gigazine.net/news/20261016-perplexity-space/) (GIGAZINE)<br>
   同社の Computer 機能の土台を公開し、開発者が安全なエージェントを組む基盤にしてもらう狙い。

5. [Google、エージェントの弱点に合わせ訓練環境を変える EnvHarness を公開](https://www.infoq.com/news/2026/10/envharness-self-evolving-agents/) (InfoQ・英語)<br>
   エージェント本体も評価系も触らず、訓練側の環境だけを動的に調整する枠組み。

6. [Python のバイナリ wheel がサプライチェーン攻撃の弱点になる理由](https://www.reddit.com/r/programming/comments/1x8eqt6/pythons_binary_wheels_and_supply_chain_attacks/) (Reddit・英語)<br>
   PyPI の悪意あるパッケージを調べてきた著者が、事前コンパイル済み配布物の穴を論じる。

7. [RP2350 のセキュアブートを、手作りのレーザー装置で破る](https://courk.cc/rp2350-challenge-laser) (HN・英語)<br>
   Raspberry Pi の新マイコンを開封し、赤外レーザーで命令スキップなどを起こす手順を FPGA 制御の自作基盤とともに解説。

8. [勤務先の管理者アカウントを閉め出し、約1億円を要求した元エンジニアが有罪に](https://gigazine.net/news/20261017-cyberattack-engineer-sentenced/) (GIGAZINE)<br>
   匿名で脅迫していたが、監視カメラの映像から身元が割り出された。

9. [Haskell の Kind 体系を、型付き設定の実装から学び直す](https://thunk.blog/posts/types-of-types-haskell-kind-system/) (HN・英語)<br>
   Haskell で Redis サーバーのクローンを作る中で見つけた、値・型・Kind の三層の使い方。
