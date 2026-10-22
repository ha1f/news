---
layout: post
title: "AIが見つけたPHP脆弱性とAI設計ウイルスの初投与（研究者）"
date: 2026-10-22
profile: researcher
tags: [AI, 開発, セキュリティ, 科学]
article_tags:
  - [AI, セキュリティ]
  - [科学]
  - [セキュリティ]
  - [AI]
  - [AI]
  - [AI]
  - [AI]
  - [AI]
  - [開発]
  - [科学]
---

PHP の中核に見つかった重大脆弱性「PHP2Shell」が、AI の手で見つかり AI 枠組みで調整された話として世界を駆け巡った。AI 設計のウイルスを人に投与した初の治療報告、AI 開発基盤 LiteLLM の PyPI 汚染、Google の AI 生成物検出ツール拡張と、AI が攻守両面で現実に踏み込む一日。研究側は、層を使い回す Transformer や、ベンチマーク表の読み方をめぐる議論が並ぶ。

1. [PHP の重大脆弱性「PHP2Shell」、AI で発見](https://gigazine.net/news/20261022-php2shell-wiz-openai-calif/) (はてブ)<br>
   セキュリティ企業の Calif と Wiz が2026年8月に別々に見つけ、認証なしのコード実行や処理中メモリの漏えいにつながる。

2. [AI が設計したウイルスを初めて患者に投与](https://www.asahi.com/articles/ASVBP1QR9VBPUHBI00RM.html) (はてブ)<br>
   米ラディカルニューメリクスが、抗生物質の効かない耐性菌の患者に、自社設計のファージを人道的使用の枠で使ったと発表。

3. [LiteLLM 1.107.0 が PyPI で汚染、認証情報を窃取](https://safedep.io/litellm-pypi-compromise-credential-stealer-backdoor/) (HN・英語)<br>
   Python 起動のたびに SSH 鍵やクラウドの認証情報を盗む仕掛けが入り、リリースは削除済み。GitHub のソースは無傷。

4. [同じ層を回す「Looped Transformer」入門](https://zenn.dev/acrosstudioblog/articles/895e38a8893223) (Zenn)<br>
   パラメータを増やさず計算の深さを稼ぐ仕組みと、規模を示す数字と実際の計算量が別の話になりつつある点を整理。

5. [Google DeepMind、AI 生成物検出「SynthID Detector」を世界公開](https://www.infoq.com/news/2026/10/synthid-watermarking-detector/) (InfoQ・英語)<br>
   OpenAI や NVIDIA、Kakao の生成物も一か所で判定でき、Apple は近日対応の予定。

6. [ベンチマークで8システムが首位タイのとき、表はどう見せるか](https://www.reddit.com/r/MachineLearning/comments/1xayxs1/when_eight_systems_share_a_benchmark_top_score/) (Reddit・英語)<br>
   エージェント記憶の公開ボードで43システムが150課題を競い、8つが52.67%で並ぶ例から、結果表の読まれ方を問う。

7. [Anthropic が先回りで動く新アプリ「Claude Duet」を試験公開](https://claude.com/product/claude-duet) (HN・英語)<br>
   朝に要点をまとめ、重要な連絡だけ知らせ、実行前に確認を挟む。米国の Pro・Max 向けに待機リスト制。

8. [実行中のバイナリを書き換えて高速化するモデル「Maxwell」](https://www.reddit.com/r/MachineLearning/comments/1xa2rrh/maxwell_a_new_model_that_speeds_up_ai_models_like/) (Reddit・英語)<br>
   Whisper などをソース無改変で速くし、最適化後も動作が同じことを形式検証で示すという触れ込み。

9. [DuckDB 2.0 LTS 公開、VARIANT 型やトリガーを追加](https://duckdb.org/2026/10/21/announcing-duckdb-200) (HN・英語)<br>
   1.5 から約2万コミットの大型機能更新で、非同期 I/O や拡張可能な SQL パーサーも入り、移行時の互換性変更も解説。

10. [サンゴ礫にプラスチックが溶け込んだ「プラスチコーラル」](https://www.oist.jp/news-center/news/2026/9/18/new-form-plastic-pollution-discovered-shores-vulnerable-coral-reefs) (HN・英語)<br>
    沖縄の海岸調査で見つかり、家庭用プラの溶融物が死んだサンゴ片の孔に染み込んでいた。沖縄科技大らの報告。
