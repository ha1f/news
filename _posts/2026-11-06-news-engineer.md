---
layout: post
title: "musl版OpenSSHに10年越しの侵入口、Zig libcでSQLite激遅（ソフトウェアエンジニア）"
date: 2026-11-06
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, 科学]
serendipity: [10]
article_tags:
  - [セキュリティ, 開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発, 科学]
  - [AI, 開発]
  - [開発, セキュリティ]
  - [開発]
  - [ビジネス]
---

musl の上で動く OpenSSH が、2016年からパスワードのないアカウントへの侵入を許していた。Zig の libc 書き換えで SQLite が1万2000倍遅くなった話と並び、libc の小さな挙動が大きく響いた1日。後半は AI エージェントの作り方と、Swift・iOS の新しい API を拾う。

1. [musl 版 OpenSSH、2016年からパスワードなしで侵入できた](https://sshhole.com) (HN・英語)<br>
   1980年の Unix で使われた「*」から、musl が2012年に変えた crypt() の挙動まで、穴ができた経緯を順に追う

2. [Zig の libc 書き換えで SQLite が1万2000倍遅く](https://www.reddit.com/r/programming/comments/1xnq1xx/shlemiel_the_painter_is_back_how_zigs_libc/) (Reddit・英語)<br>
   Rust と SQLite で作ったチェス解析サービスで、ミリ秒で済むはずの保存が詰まった原因を掘る

3. [1973年の Unix V4 に残る malloc を読む](https://www.reddit.com/r/programming/comments/1xni70o/the_lost_malloc/) (Reddit・英語)<br>
   昨年倉庫で見つかった V4 のテープのソースから、初期の C でのメモリ確保の仕組みをたどる

4. [2.78兆パラメータの Kimi K3 を CPU だけで動かす C 実装](https://github.com/FareedKhan-dev/kimi-k3-in-c) (GitHub Trending・英語)<br>
   Moonshot AI のモデルを、メモリ8.24GB・BLAS も GPU も使わない C99 だけで推論させる

5. [自作の AI エージェント開発をやめた理由](https://blog.mudatobunka.org/entry/2026/11/05/100000) (はてブ)<br>
   データ分析用にスクラッチで作っていたエージェントを6月で打ち切り、MCP として作り直すまでの振り返り

6. [freee、税法を Lean で書いて税計算を全入力で検証](https://developers.freee.co.jp/entry/lean-formal-verification-tax-law-qa) (はてブ)<br>
   会計 SaaS の freee が定理証明支援系と AI エージェントを組み合わせ、テストで漏れる計算を確かめた

7. [iOS 27.3 beta の「Siri AI」にアプリをつなぎ、振る舞いを評価する](https://zenn.dev/d_date/articles/e8e2c5d53b424e) (Zenn)<br>
   既存の App Intent に @AppIntent(.tool) を足す接続手順と、Siri の動きをテストに書く Siri Evaluations の使い方

8. [Swift からターミナルへ文字を打ち込むときの落とし穴](https://www.reddit.com/r/swift/comments/1xor1bp/typing_untrusted_text_into_a_terminal_from_swift/) (Reddit・英語)<br>
   macOS アプリの作者が、送信しない設定でも PTY の行エディタが届いたバイトを即座に解釈する危険を検証

9. [AWS の Amazon ECS Gateway、独自ドメインに未対応で登場](https://www.infoq.com/news/2026/11/introducing-amazon-ecs-gateway/) (InfoQ・英語)<br>
   アカウント単位の入口を基盤チームが一度定義し、各サービスはコネクタで参加して自動のホスト名を受け取る

10. [有料検索の Kagi、アカウントなしで50回まで検索可能に](https://kagi.com/changelog#11820) (HN・英語)<br>
   広告を出さない Kagi は、Google が2027年から学校アカウントで AI ツールと一緒に検索も止める方針に、公開書簡で反論

