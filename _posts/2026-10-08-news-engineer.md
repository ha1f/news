---
layout: post
title: "Claude Haiku 5.5が登場、IDCFクラウドはランサム被害（ソフトウェアエンジニア）"
date: 2026-10-08
profile: engineer
tags: [AI, 開発, セキュリティ, 社会]
article_tags:
  - [AI]
  - [セキュリティ]
  - [開発]
  - [開発]
  - [セキュリティ, AI]
  - [AI, 開発]
  - [開発]
  - [AI]
  - [開発]
  - [社会]
---

Anthropic が最小モデル「Claude Haiku 5.5」を投入し、Sonnet 5.5 のキャッシュ読み取りも半額にした。一方で国内では IDCF クラウドがランサムウェア被害を受け、復旧の見通しが焦点になっている。開発現場ではコーディングエージェントの運用ノウハウと、Chrome の JPEG XL 対応のような足回りの話題が並ぶ。

1. [Anthropic、最小モデル「Claude Haiku 5.5」を公開](https://www.anthropic.com/claude-haiku-5-5) (HN・英語)<br>
   前世代 Haiku 4.5 より平均で約75%安く、要約や分類、サブエージェント用途を想定している。

2. [IDCFクラウドにランサムウェア攻撃、障害が続く](https://piyolog.hatenadiary.jp/entry/2026/10/08/070606) (はてブ)<br>
   10月7日に公表された攻撃で、東日本リージョンへの影響から第1報以降の経過までを時系列で追える。

3. [Chrome 155 から JPEG XL の表示に対応](https://developer.chrome.com/blog/jpeg-xl-in-chrome) (HN・英語)<br>
   デコーダを Rust で書き直して安全性を確保した経緯と、AVIF との使い分けの指針が載っている。

4. [AWS、Aurora PostgreSQL に DuckDB を統合](https://www.publickey1.jp/blog/26/awsduckdbaurora_postgresqletl.html) (Publickey)<br>
   Iceberg 形式のデータレイクを ETL なしで直接読めるようになり、分析用の二重構成を減らせる。

5. [Cloudflare、AI で自社 WAF を攻撃して穴を探す](https://www.infoq.com/news/2026/10/cloudflare-sec-harness/) (InfoQ・英語)<br>
   45シナリオで1,107回試行し、人手の選別後に残った49件から3件のルール修正につながった。

6. [AI生成コードでデバッグ工数が増える、300人調査](https://www.infoq.com/news/2026/10/survey-complex-codebases-agents/) (InfoQ・英語)<br>
   C/C++ 中心の重要システムでは、生成速度より理解と保守が新たな詰まりどころになるという結果。

7. [Git Worktree でも Xcode のコンパイルキャッシュを効かせる](https://zenn.dev/sryu/articles/worktree-compilation-cache) (Zenn)<br>
   Xcode 26 のキャッシュ設定だけでは worktree 間で効かない理由と、効かせる手順を解説している。

8. [最近の LLM は「黙って」考えられるようになっている](https://joisino.hatenablog.com/entry/filler) (はてブ)<br>
   「.」の羅列を付けるだけで正答率が上がるフィラートークンの仕組みを、算数の例題で説明する。

9. [「ifは上へ、forは下へ」の設計指針を検証](https://debasishg.github.io/blog/push-ifs-up-fors-down/) (HN・英語)<br>
   TigerBeetle の流儀として知られる指針を、クエリ最適化や関数型の代数に結び付け、効かない場面も示す。

10. [アポロ計画のソフト開発を率いた Margaret Hamilton 氏が90歳で死去](https://news.mit.edu/2026/margaret-hamilton-computing-pioneer-dies-1007) (HN・英語)<br>
    MIT で月面着陸機のコンピュータを動かすチームを率い、ソフトウェア工学の先駆者となった人物の評伝。
