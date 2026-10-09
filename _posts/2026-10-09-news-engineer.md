---
layout: post
title: "GoogleがPyreflyへ移行、Polars2.0も登場（ソフトウェアエンジニア）"
date: 2026-10-09
profile: engineer
tags: [AI, 開発, デザイン]
article_tags:
  - [AI]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [AI]
  - [開発]
  - [デザイン]
---

Google が社内のモノレポで Python の型チェッカーを Meta 製 Pyrefly に切り替え、Polars は 2.0 に到達。開発基盤の世代交代が目立つ一日。Anthropic は Max と Team の契約者に毎月の API 枠を配り始め、AI が書いたコードの検証をどう担保するかという話題も並ぶ。

1. [Anthropic、Max と Team の契約者に API 利用枠を無償配布](https://pc.watch.impress.co.jp/docs/news/2146653.html) (はてブ)<br>
   Max 5x は月100ドル、Max 20x は月200ドル分。申請は課金設定ページで行い、Agent SDK にも使える。

2. [Google が Python 型チェッカーを Pyrefly に全面移行](https://www.reddit.com/r/programming/comments/1x0p1v8/adopting_pyrefly_as_the_python_type_checker_at/) (Reddit・英語)<br>
   10年以上使った自社製 Pytype をやめ、Meta 発の OSS を採用。差分ビルドの待ち時間は最大98%減った。

3. [Polars 2.0 公開、SQL を第一級に](https://www.reddit.com/r/programming/comments/1wzf37b/release_of_polars_20/) (Reddit・英語)<br>
   ディスクへの退避処理（out-of-core）に対応し、TPC-H では DataFusion と DuckDB を上回る結果を示す。

4. [AI が足したテストは緑でも、違う鍵に14バイト返していた](https://zenn.dev/ihsan/articles/ai-14-9200b641f6e6) (Zenn)<br>
   正しい鍵で一度つないだ後だと、拒否されるはずの別の鍵に応答が返る。違反入力で赤くなった実績のないテストは信用できない、という教訓。

5. [Ghostty 作者、プログラムの状態を端末に伝える OSC 7501 を提案](https://mitchellh.com/writing/program-status-osc7501) (HN・英語)<br>
   待機・実行中・入力待ち・失敗を端末に知らせるエスケープシーケンス。長時間動くコーディングエージェントの通知が主な用途。

6. [DMM、8兆レコード規模の取り込みを Embulk から dlt へ](https://zenn.dev/dmmdata/articles/embulk-to-dlt-migration) (はてブ)<br>
   Embulk のメンテナンスモード入りを受け、5人のチームが約3週間で選定から実装まで終えた移行記録。

7. [さくらのAI Engine に GPU 専有の定額プラン](https://www.publickey1.jp/blog/26/gpuai_engine.html) (Publickey)<br>
   GPU サーバ上の基盤モデルを企業が専有して使う形態で、トークン消費量を気にせず定額で回せる。

8. [Mac Catalyst で Mac だけ黙って動かない7つの落とし穴](https://zenn.dev/taska_ja/articles/7f29d28c5e1b5b) (Zenn)<br>
   iPhone では動く SwiftUI コードが、エラーも出ずに Mac で何も起きない。Taska の開発で見つけた事例集。

9. [DVD メニューの美学を技術面から振り返る](https://vale.rocks/posts/dvd-menus) (HN・英語)<br>
   720×480 という解像度の由来や、メニュー設計が凝っていき再び地味に戻るまでの流れを追う。
