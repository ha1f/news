---
layout: post
title: "Anthropic の脆弱性探索、報告3万8000件に修正は217件（ソフトウェアエンジニア）"
date: 2026-11-11
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア, 社会]
serendipity: [10]
article_tags:
  - [セキュリティ, AI]
  - [AI]
  - [AI, セキュリティ]
  - [開発, AI]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア, 社会]
---

Anthropic の脆弱性探索「Glasswing」は7カ月で報告3万7966件、修正済みは217件。AI が見つける速さに、直す側が追いつかない。DeepMind は Signal の暗号コードを AI エージェントで形式検証し、Google はコーディングエージェントに最新の Web 作法を教え込む。AI とコードの距離がまた一段縮まった朝。

1. [Anthropic の「Glasswing」、7カ月で保守者を報告の山に埋める](https://www.vulncheck.com/blog/anthropic-glasswing-november-update) (HN・英語)<br>
   VulnCheck の集計で、報告約3万8000件のうち公開は19.4%、修正済みは217件どまり

2. [Claude Opus 5.5 の推論が11月3日から急低下、との指摘](https://gigazine.net/news/20261110-claude-opus-nerf/) (はてブ)<br>
   開発者が Claude Code の利用履歴約1400件を分析し、モデル名が同じまま思考の書き方が変わったと主張

3. [DeepMind「AlphaProof Code」、Signal の暗号コードを AI で形式検証](https://deepmind.google/blog/introducing-alphaproof-code/) (HN・英語)<br>
   人の知見と AI エージェントを組み合わせ、プロトコルの仕様でなく実装コードの安全性を証明

4. [エージェントを古い JS 作法から離す「Modern Web Guidance」](https://github.com/GoogleChrome/modern-web-guidance) (HN・英語)<br>
   Chrome・Edge・Firefox・MDN のチームが手がけるスキル集で、既存コードの古い書き方を洗い出す legacy-scan も付く

5. [Pinterest、ユーザー行動のクラスタリングを 4B の Qwen3 に置き換え](https://www.infoq.com/news/2026/11/pinterest-journey/) (InfoQ・英語)<br>
   多段のパイプラインを微調整した小型 LLM 1つにまとめ、メールのクリック率は1.1%改善

6. [TCA の Effect と Dependency で保存処理を Reducer から切り離す](https://zenn.dev/sakurainohirune/articles/tca-effect-dependency) (Zenn)<br>
   Swift の設計ライブラリ TCA 1.26.2 で、UserDefaults に書かずに保存の成否をテストする手順

7. [mixi2 が iPhone Duo の発売初日から最適化できた理由](https://zenn.dev/mixi/articles/b0ea64fded9503) (Zenn)<br>
   ボトムタブを自前で実装していたので、縦向きの配置へすぐ組み替えられたことが効いた

8. [「.NET MAUI 11」、Xamarin 由来の Mono を捨てて CoreCLR に統一](https://www.publickey1.jp/blog/26/net_maui_11xamarinmonocoreclr.html) (Publickey)<br>
   iOS や Android も1つのコードで書く Microsoft の UI フレームワークで、内部ランタイムが一本化

9. [1日が25時間になる日に Chromium で起きたバグ](https://www.reddit.com/r/programming/comments/1xsvulu/a_chromium_bug_caused_by_a_25hour_day/) (Reddit・英語)<br>
   カナダなどで夏時間が終わる日は25時間あり、日付計算の前提が崩れる仕組みを UTC の基礎から追う

10. [Suica のウォークスルー改札、iPhone と Android は27年後半に UWB で対応へ](https://japan.cnet.com/article/35254664/) (はてブ)<br>
   JR東日本は2028年春に首都圏の主要40駅へ広げる計画で、その前の27年春には14駅でモニター体験
