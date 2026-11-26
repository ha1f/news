---
layout: post
title: "Lovable 製アプリ15.9万件に情報露出、Cursor は侵害の経緯を公表（ソフトウェアエンジニア）"
date: 2026-11-15
profile: engineer
tags: [AI, 開発, セキュリティ]
serendipity: [13]
article_tags:
  - [AI, セキュリティ]
  - [セキュリティ]
  - [セキュリティ]
  - [開発, セキュリティ]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
---

Lovable で作られた15.9万件のアプリからログインなしで読めるデータが見つかり、Cursor は偽の Claude Code 拡張が出回った侵害の経緯を公表。Google Project Zero も LLM による攻撃の高速化を理由に開示方針を改めた。後半は XCUITest の空振りや Neovim GUI など、手を動かす人向けの記事を揃えた。

1. [Lovable 製アプリ、旅券情報や20万件超の私信が丸見え](https://www.crissyfield.de/research/lovable-en/) (HN・英語)<br>
   AI でアプリを作るスウェーデン企業の15.9万件を調べ、ログイン不要で読める事例が多数

2. [Cursor、偽の Claude Code 拡張が出回った侵害の経緯を公表](https://cursor.com/blog/security-incident-update) (はてブ・英語)<br>
   発端は Fireworks に渡したアクセスキーの流出で、API 認証情報が漏れた顧客は0.01%未満

3. [Google Project Zero、報告から90日で脆弱性を開示する方針に](https://projectzero.google/2026/11/disclosure-policy.html) (HN・英語)<br>
   2021年からの「90+30日」を改め、パッチ後の猶予期間は LLM 時代には意味を失ったと説明

4. [Java のコメントが Unicode エスケープで実行コードに化ける](https://www.reddit.com/r/programming/comments/1xw63wj/a_unicode_escape_can_turn_a_java_comment_into/) (Reddit・英語)<br>
   コメント判定より先に \u000a が改行になる仕様で、SDK 生成器は PHP・Ruby でも要注意

5. [AI 同士の敵対的レビューより、動かして検証にトークンを](https://zenn.dev/karamage/articles/5c3f8370b2b370) (Zenn)<br>
   差分だけ渡された AI は揚げ足取りに流れる、と本番バグを出した筆者が振り返る

6. [JioHotstar、コーディングエージェント向けのコード検索6方式を比較](https://www.infoq.com/news/2026/11/jiohotstar-codingagent-retrieval/) (InfoQ・英語)<br>
   インドの動画配信大手の検証で、具体的な課題には構造検索、曖昧な要件には意味検索が効いた

7. [エージェントの計画とコードに注釈を付ける「Plannotator」](https://github.com/backnotprop/plannotator) (GitHub Trending・英語)<br>
   計画づくりやコードレビューの指摘をチームで共有し、ワンクリックでエージェントへ返せる作業場

8. [XCUITest、isHittable が true でも tap() が空振りする理由](https://zenn.dev/d_aiba1/articles/xcuitest-ishittable-tap-bottom-edge) (Zenn)<br>
   ボタンの上端29ptだけが画面に出ていても true になり、2周目のテストだけ画面が開かなかった

9. [macOS の eslogger と Endpoint Security クライアントを負荷計測で比較](https://zenn.dev/lafine/articles/9d9293b75dd254) (Zenn)<br>
   全力の open 連打で eslogger は1コアを使い切り約25%しか出力できず、ES クライアントは欠番0

10. [作らない機能を先に決めた Neovim GUI「ng」](https://zenn.dev/shougo/articles/ng-nvim-simple-gui) (Zenn)<br>
   Go 製で Linux の X11・Wayland 専用、アニメや独自タブを省き端末と同じ画面と日本語入力を優先

11. [Google Cloud、Compute Engine API を日付で固定する版管理に](https://www.infoq.com/news/2026/11/compute-engine-api-versioning/) (InfoQ・英語)<br>
   変わり続ける /v1 に代わり、四半期ごとの不変スナップショットをヘッダで選ぶ。Stripe と同じ発想

12. [国際送金で二重払いを防ぐ、タイムアウトと「不明」状態の設計](https://www.reddit.com/r/programming/comments/1xw8tdv/designing_payouts_that_never_payout_twice/) (Reddit・英語)<br>
   送金基盤の開発者が、応答のない相手先には再試行せず同じ参照番号で状態を照会する手法を紹介

13. [1940年代から今まで、ソフトウェア職種名104個の系統図](https://zwischenzugs.com/2026/11/03/a-family-tree-of-software-job-titles/) (HN・英語)<br>
   元 Head of DevOps の筆者が、人間の「Computer」から「Context Engineer」までを Graphviz で図にした
