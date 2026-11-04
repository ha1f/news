---
layout: post
title: "ノートPCのQwenが重みを読み解く、AIの中身に迫る（研究者）"
date: 2026-11-04
profile: researcher
tags: [AI, 開発, 科学, 社会]
article_tags:
  - [AI, 科学]
  - [AI, 社会]
  - [科学]
  - [AI, 科学]
  - [AI]
  - [AI, 開発]
  - [AI, 社会]
  - [科学]
  - [科学]
  - [開発]
---

ノート PC の Qwen 3.8 27B が、ニューラルネットの生の重みを読み解いた。AI を「規則で縛る」から「規則に従うほうが得な仕組み」で導く発想も出てきた。重みや損得勘定から AI の中身と振る舞いに迫る話題を軸に、早産児の小脳やミズナギドリの太陽コンパスまで並べた。

1. [ノート PC の Qwen 3.8 27B も、モデルの重みを読み解けた](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/) (HN・英語)<br>
   続報（11/3掲載）。Simon Willison 氏が論文の例題を手元のローカルモデルで再現した

2. [「逆ゲーム理論」で AI エージェントに規則を守らせる](https://www.technologyreview.com/2026/11/03/1147934/reverse-game-theory-mechanism-design-ai-alignment/) (MIT TR・英語/一部会員限定)<br>
   メカニズムデザインをアライメントに使う構想で、ケーキの切り分け方の例から入る

3. [ラグランジュ視点とオイラー視点をつなぐ、流体向けの物理情報 ML](https://www.nature.com/articles/s42256-026-01319-4) (Nature・英語/一部会員限定)<br>
   Fukami・Maulik 両氏が、同誌掲載の Wan らによる流れ場の再構成手法を論評

4. [生成 AI の数学を PCA から拡散モデルまで導く入門書](https://arxiv.org/abs/2605.29713) (HN・英語)<br>
   Tianhua Chen 氏の195ページの arXiv 原稿で、VAE や GAN、エネルギーベースモデルまで導出で追う

5. [InfoQ の AI・ML トレンド報告 2026年版](https://www.infoq.com/articles/ai-ml-data-engineering-trends-2026/) (InfoQ・英語)<br>
   Chip Huyen 氏らが執筆陣に入り、小型モデル・推論モデル・評価の比重の高まりを挙げる

6. [Netflix、GPU の故障を分散システムの問題として扱う](https://www.infoq.com/news/2026/10/netflix-gpu-distributed-systems/) (InfoQ・英語)<br>
   数百 GPU で数週間回る学習を、Kubernetes 上の多層ヘルスチェックと自動復旧で止めない設計

7. [トランプ政権の「Super Intelligence」改称、誰が従っているか](https://www.technologyreview.com/2026/11/02/1147932/heres-who-is-falling-in-line-for-trumps-super-intelligence-loyalty-test/) (MIT TR・英語/一部会員限定)<br>
   9月の大統領令で政府機関に AI の呼び替えを命じてから1カ月、言葉が忠誠の踏み絵になりつつある

8. [早産で小脳の発達がずれる、在胎期間に沿った内在プログラム](https://www.science.org/doi/abs/10.1126/science.aeb9095?af=R) (Science・英語/一部会員限定)<br>
   脳画像と死後組織の空間トランスクリプトームを突き合わせ、顆粒細胞とプルキンエ細胞の成熟不全を示す

9. [東西に速く飛ぶと体内時計がずれ、太陽コンパスが狂う](https://www.science.org/doi/abs/10.1126/science.adz2542?af=R) (Science・英語/一部会員限定)<br>
   マンクスミズナギドリの帰巣を GPS で追い、時差から予測どおりの方位誤差が出ると確かめた

10. [インターネットの通信をパケット単位で見せる「Protocol Explorer」](https://protocol-explorer-alpha.vercel.app/) (はてブ)<br>
    HTTP から TLS まで14種のプロトコルをバイト単位で分解して学べ、日本語表示もある
