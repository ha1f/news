---
layout: post
title: "24KB の LLM 専用 OS が llama.cpp 超え、推論を自前で削る流れ（ソフトウェアエンジニア）"
date: 2026-11-27
profile: engineer
tags: [AI, 開発, 科学]
serendipity: [11]
article_tags:
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [AI, 科学]
---

全編アセンブリで書いた 24KB の OS が、Linux 上の llama.cpp より速く LLM を動かした。AMD 向けフォークや 2 時間で学習できる 64M モデルも並び、推論エンジンを自分で削る流れが強い。Claude Code の使いこなしや iOS のアーキテクチャの話も揃った朝。

1. [24KBの「LLM専用OS」、llama.cppより最大54%高速](https://www.techno-edge.net/article/2026/11/26/5824.html) (はてブ)<br>
   Alexey Fateev 氏が NASM だけで書き、起動は100ミリ秒未満でディスク不要

2. [AMD の GPU 専用に削った llama.cpp のフォーク](https://devnull.land/amd-specific-llama-cpp) (HN・英語)<br>
   筆者の環境では生成が毎秒35から55トークンに伸び、汎用エンジン離れの背景も解説

3. [2時間・約3元で64Mの言語モデルを一から学習「minimind」](https://github.com/jingyaogong/minimind) (GitHub Trending・英語)<br>
   事前学習から SFT・DPO・蒸留までの全工程のコードを公開し、個人の GPU で再現できる

4. [Cognition、Kimi K3 ベースのコーディングモデル「SWE-2.1」](https://gigazine.net/news/20261126-swe-2-1-coding-ai/) (GIGAZINE)<br>
   長いワークフロー向けに学習し、前版の SWE-2 からベンチマークの数値を大きく伸ばした

5. [Claude Code の /btw・/fork・/rewind をどう使い分けるか](https://zenn.dev/nextbeat/articles/b0ccca979da06b) (Zenn)<br>
   名前の似たコマンドを、作業を止めずに横から質問・分岐する場面ごとに整理

6. [CLAUDE.md を Claude Code 自身に毎週書き直させる](https://anond.hatelabo.jp/20261126144022) (はてブ)<br>
   理想の出力例を基準に claude -p で調整させる運用で、ファイルは回すほど短くなるという

7. [型チェックが重い原因は1つのクエリの型推論だった](https://zenn.dev/dress_code/articles/88b55221eea4e0) (Zenn)<br>
   Dress Code の開発者が、全体の約3分の1を占めた推論を手放してメモリ不足を解消

8. [LinkedIn、UIKit の階層に依存しない iOS の計測基盤](https://www.infoq.com/news/2026/11/linkedin-view-agnostic-analytics/) (InfoQ・英語)<br>
   SwiftUI 時代に論理構造と View がずれる問題を、共通の MeasurableNode 契約で吸収した

9. [起動中の iOS シミュレータを Finder のサイドバーに出す「SimDrop」](https://github.com/rxliuli/sim-drop) (HN・英語)<br>
   File Provider 経由で写真やダウンロードへドラッグでき、macOS 15 以降・Homebrew で導入可能

10. [DHH 氏の Linux「Omarchy 4.5」、フローティング型ウィンドウに対応](https://www.publickey1.jp/blog/26/dhhomarchy_457applewebms_office.html) (Publickey)<br>
   タイル型が売りだった OS に切り替えを用意し、Apple シリコンにも対応した

11. [OpenAI、行列乗算の指数 ω が「9/4」だと示す論文](https://gigazine.net/news/20261126-openai-matrix-multiplication/) (GIGAZINE)<br>
   1969年から続く計算量の未解決問題に、上界の更新を経て決着をつけたと主張する
