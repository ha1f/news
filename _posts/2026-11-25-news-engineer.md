---
layout: post
title: "OpenAI が Git を拡張する Pando、Fable 5.2 の評価に癖（ソフトウェアエンジニア）"
date: 2026-11-25
profile: engineer
tags: [AI, 開発, ビジネス]
serendipity: [10]
article_tags:
  - [AI, 開発]
  - [AI]
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [ビジネス]
---

OpenAI が、コーディングエージェントの同時 push に耐える Git バックエンド「Pando」の中身を明かした。エージェントが開発の主役になるにつれ、Git も評価も、モデルの置き場所も作り直しが始まっている。足元では jQuery 4.1 と DynamoDB 互換の ExtendDB 1.0 という、地味だが効くリリースも並ぶ。

1. [OpenAI、エージェント向けに Git を拡張する「Pando」](https://www.infoq.com/news/2026/11/openai-git-pando/) (InfoQ・英語)<br>
   普段の Git の操作は変えずに、push の遅延の中央値を約8割縮めた。ブランチ更新を個別に調停する仕組みが効いている

2. [Fable 5.2、ズルできる課題ほど早くあきらめる](https://goodhartlabs.com/blog/fable-5-2-tries-less-on-some-hard-tasks-when-a-shortcut-is-available) (HN・英語)<br>
   Goodhart Labs が評価セット HoneyBench v0.2 で気づいた挙動。暗算課題の得点は Opus 5.5 を下回り、原因を手抜きでなく「解けない課題と思い込む」ことに求めている

3. [PrismML の3値量子化モデル「Ternary Bonsai 2.5 27B」](https://prismml.com/news/bonsai-2-5-27b) (HN・英語)<br>
   Qwen3.8 27B を元にしたモデルで、5.9GB のままツール呼び出しを何度も重ねるエージェント用途を鍛えた。手元の端末で動かす前提

4. [Cursor、プラグインの仕様と公式プラグイン集を公開](https://github.com/cursor/plugins) (GitHub Trending・英語)<br>
   1プラグイン1ディレクトリで manifest を置く構成。AGENTS.md を育てる記憶更新や、サブエージェントで回すブランチレビューが入っている

5. [AWS Lambda、GPU 推論に対応、1枚で48呼び出しを同時処理](https://www.infoq.com/news/2026/11/aws-lambda-gpu-managed-instances/) (InfoQ・英語)<br>
   vLLM と SGLang のイメージはハンドラを書かずに動く。料金は EC2 G 系インスタンス代に9.75%の手数料を足す形

6. [AWS、DynamoDB 互換 DB を手元で動かす「ExtendDB」が 1.0 に](https://www.publickey1.jp/blog/26/awsdynamodbextenddb10.html) (Publickey)<br>
   同じ SDK とコードのまま使え、裏側のエンジンは PostgreSQL・SQLite・Cassandra・MongoDB から選ぶ。npm とコンテナで配布

7. [jQuery 4.1 正式版、内部を querySelectorAll に統一](https://www.publickey1.jp/blog/26/jquery_41queryselectoralljquery_3xjquery_38.html) (Publickey)<br>
   リダイレクト後の URL を取れる responseURL を追加。3.x 系は 3.8 が最後で、セレクタの ReDoS を直して幕を引く

8. [エムスリー、Lean で始める契約プログラミング](https://www.m3tech.blog/entry/contract-programming-in-lean) (はてブ)<br>
   リストの最大値を返す関数を題材に、Java の interface で書く約束と Lean で証明まで付ける書き方を並べて見せる

9. [Skitch の代わりを Claude Code と10日で作った Mac アプリ](https://qiita.com/sumihiro3/items/cb6b62b3e880f2b57d1b) (Qiita)<br>
   Intel 版しかない Skitch は、Rosetta が限定される macOS 28 で使えなくなる。そこで AI からも呼べるスクショ注釈アプリを作った

10. [電力網を待てないデータセンター、自前のガス発電所へ](https://www.technologyreview.com/2026/11/24/1149622/data-centers-natural-gas/) (MIT TR・英語/一部会員限定)<br>
   系統への接続承認は最長10年待ちになることもあり、xAI などが送電網から切り離した自前のガス火力に向かっている
