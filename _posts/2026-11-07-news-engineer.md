---
layout: post
title: "Firecrackerの仮想マシンを破りroot奪取、AIエージェントの安全性も問われる（ソフトウェアエンジニア）"
date: 2026-11-07
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
serendipity: [11]
article_tags:
  - [セキュリティ, 開発]
  - [セキュリティ, 開発]
  - [AI, セキュリティ]
  - [AI, セキュリティ]
  - [AI]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア]
---

Firecracker の microVM から抜け出し、ホストで root 権限のコード実行に成功した報告が HN の上位に。AWS は実際に攻撃コードを動かして脆弱性を確かめるサービスを一般提供し、Claude Code ではメールアドレスの外部送信が見つかった。エージェントとサンドボックスの安全性が問われた一日。

1. [Firecracker の microVM を破り、ホストで root を奪取](https://pwn.ai/blog/firecracker-escape) (HN・英語)<br>
   Linux のネットワーク処理の欠陥を足がかりに、vCPU スレッドの復帰先を書き換える手順を追う連載の第2回

2. [AWS「Continuum」、攻撃を実際に試してから修正 PR を出す](https://www.infoq.com/news/2026/11/aws-continuum-ga/) (InfoQ・英語)<br>
   コードの脆弱性をサンドボックスで実証する新サービスで、提供は2リージョン、料金は検出件数とコード行数の両方で決まる

3. [Claude Code、User-Agent にユーザーのメールアドレスを入れて送信](https://gigazine.net/news/20261106-claude-code-mail-address/) (はてブ)<br>
   curl で外部 API を呼ぶ際に起きる問題で、7月と8月にも GitHub に報告が上がっていた

4. [コーディングエージェントの行動を手元で監査する「Stroq」](https://github.com/AGGIB/Stroq) (HN・英語)<br>
   Claude Code と Codex の直近30日の履歴から、エージェントが読んだ文章由来のコマンドと外に出た鍵の名前を洗い出す

5. [安い判定モデル Jev が迷ったら Opus に聞く、コスト4分の1で同等精度](https://hightouch.com/blog/llm-judges-identity-resolution) (HN・英語)<br>
   TypeSafe の判定モデル Jev は自信の低いときに誤りが集中するため、その分だけ Claude Opus に回せるという Hightouch の検証

6. [ubuntu-latest が 26.04 になり、明治の開始日が変わってテストが落ちた](https://zenn.dev/xin9le/articles/9a1cf8e10494d6) (はてブ)<br>
   同梱の ICU で明治元年が1868年10月23日始まりに直り、.NET の和暦変換が例外を投げるようになった

7. [Rust 製の Firebase エミュレーター「Firenook」、書き込み40倍速](https://firenook.dev/) (HN・英語)<br>
   firebase.json や SDK はそのままで Java も不要、再起動後もデータが残り、ピーク時のメモリは10分の1

8. [Postgres 19 の REPACK、テーブルの肥大をロックなしで解消](https://www.reddit.com/r/programming/comments/1xn9jr2/postgres_19_repack_builtin_online_table_bloat/) (Reddit・英語)<br>
   これまで VACUUM FULL か外部拡張に頼っていた領域回収が、CONCURRENTLY 指定で本体だけで済むようになる

9. [Xcode のシミュレーターを軽くする Mac アプリ「NeoSimulator」](https://github.com/lynnswap/NeoSimulator) (GitHub Trending・英語)<br>
   iPhone から Vision Pro までのシミュレーターを扱い、止めても安全な裏のサービスを停止できる。Xcode 27 以降が必要

10. [SwiftUI の状態管理「MV State パターン」の解説と事例集](https://zenn.dev/fumiyasac/articles/792e32d3c8ec51) (Zenn)<br>
   MVVM のように画面ごとのクラスを増やさず、状態の持ち主と参照先を先に決める設計を実装例で示す

11. [人型ロボットの家事代行を頼んでみたら](https://www.technologyreview.com/2026/11/06/1148090/i-watched-a-humanoid-robot-clean-my-apartment-it-felt-like-a-taste-of-the-future/) (MIT TR・英語/一部会員限定)<br>
   サンフランシスコの Tau Robotics の清掃ロボットは今のところ人が遠隔で操作しており、作業の記録を自律化の学習に回している
