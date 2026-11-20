---
layout: post
title: "Ruby に認証不要の RCE、標準構成の Rails で到達（ソフトウェアエンジニア）"
date: 2026-11-20
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
serendipity: [11]
article_tags:
  - [セキュリティ, 開発]
  - [セキュリティ, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [科学]
---

Ruby の文字列変換に1バイトのヒープオーバーフロー。標準構成の Rails が認証なしで RCE に届き、PHP も17件の修正版を出した。脆弱性の週が続くなか、エージェントに PR を出させる現場の実数と、そのスキルを測る道具も揃ってきた。

1. [Ruby に認証不要の RCE「Ruby2Shell」、標準の Rails で到達](https://verialabs.com/ruby2shell/) (HN・英語)<br>
   修正版は Ruby 3.3.14・3.4.13・4.0.10。GitLab や GitHub Enterprise Server は同梱 Ruby のため未修正のまま

2. [「PHP」で17件の脆弱性を修正、Critical は7件](https://forest.watch.impress.co.jp/docs/news/2158039.html) (はてブ)<br>
   続報（11/19掲載）。予告どおり8.2〜8.5の4系統に修正版、セッション処理の不備による RCE は PoC も公開済み

3. [Mastra、自社の保守に使う「Mastra Factory」を OSS 化](https://news.ycombinator.com/item?id=50548660) (HN・英語)<br>
   TypeScript のエージェント基盤 Mastra のチームが公開。先週は人の630本に対し Factory 自身が238本の PR をマージ

4. [NVIDIA、エージェントのスキルを評価する「SkillEvaluator」](https://github.com/NVIDIA/SkillEvaluator) (GitHub Trending・英語)<br>
   スキルやプラグインが挙動をどう変えるかを実エージェントで測り、他リポジトリの CI に組み込むテンプレートも付属

5. [Rust を AI と書く、Niko Matsakis 氏の「RIIIR」](https://www.infoq.com/presentations/rust-ai-symposium-agent-client-protocol/) (InfoQ・英語)<br>
   Rust Foundation の OSS ツールチェーン「Symposium」と、エージェントとツールをつなぐ ACP を QCon で実演

6. [Google、Mac 版 Gemini に「コンピューター操作」を搭載](https://techcrunch.com/2026/11/19/google-gives-gemini-the-ability-to-use-your-mac-for-you/) (TechCrunch・英語)<br>
   ネイティブの Mac アプリやブラウザを裏で操作する機能で、OpenAI や Anthropic、Meta の後を追う形の投入

7. [iOS 1〜7 時代のアプリを Mac で動かす「Light Touch」](https://github.com/samhenrigold/LightTouchMac) (GitHub Trending・英語)<br>
   初期の iPhone・iPod touch・iPad 向けアプリが対象で、作者はコーディングエージェントを使って開発したと明記

8. [App Intents でアラームを「1時間だけオフ」にする](https://zenn.dev/lightning_llc/articles/b3559f8b7fe400) (Zenn)<br>
   AlarmKit を使うアプリに Siri やアクションボタンからの一時停止を追加、画面操作と結果を揃える線引きが中心

9. [ブラウザで Node.js と npm を動かす「OpenVessel」、神戸ソフトが公開](https://www.publickey1.jp/blog/26/nodejsnpmwebopenvessel.html) (Publickey)<br>
   サーバーなしで Astro など Node.js 対応のフレームワークまでブラウザ内で実行できるオープンソース

10. [LinkedIn、Spark のシャッフル失敗を1日750件から20件に](https://www.infoq.com/news/2026/11/linkedin-celeborn-remote-shuffle/) (InfoQ・英語)<br>
    共有のリモートシャッフル基盤に Apache Celeborn を採用し、Spark と Flink の大半で計算コストも1割削減

11. [ウイルス注射で膵臓がんの進行が3人で止まる](https://www.newscientist.com/article/2528235-pancreatic-cancer-halted-by-virus-injection-in-three-patients/) (HN・英語)<br>
    ミネソタ大が開発したウイルスの初期安全性試験で、目標の10分の1の投与量でも腫瘍の増大と転移が止まった
