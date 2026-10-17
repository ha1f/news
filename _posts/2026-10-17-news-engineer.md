---
layout: post
title: "有名OSSが外部PRを閉じ始め、AIコードの洪水に（ソフトウェアエンジニア）"
date: 2026-10-17
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [開発]
  - [AI, 開発]
  - [AI, 開発]
  - [セキュリティ]
---

Hono、tldraw、Ladybird、Sindre Sorhus 氏と、有名 OSS が外部からの PR 受け付けを止める動きが広がっている。背景には AI が量産するコードと、それを読む人間の時間の奪い合いがある。Anthropic は自社のレビュー体制を公開し、個人開発者は ADR や会話履歴の検索で AI の記憶不足を補う。

1. [有名 OSS が外部 PR を閉じ始めた理由と向き合い方](https://zenn.dev/hand_dot/articles/ecb391d4322330) (Zenn)<br>
   tldraw や Ladybird など、閉じ方を「全面停止」「初回限定」などに分けて事例ごとに整理している。

2. [Claude Code チームのコードレビュー運用](https://claude.dev/blog/solving-code-review-at-anthropic/) (Hacker News・英語)<br>
   6〜9月でマージ数が2倍超、リバート率は4割超減。人の確認を減らしながら事故を抑えた手順の記録。

3. [Claude Code に任せる個人開発で、設計判断を64本の ADR に残す](https://zenn.dev/kam_labz/articles/ebbing-adr-with-claude-code) (Zenn)<br>
   iOS アプリ開発者が、何を書き、いつ誰が書き、覆すときどうするかを4か月半の運用から具体化。

4. [Claude Code に過去の会話を思い出させるツール](https://zenn.dev/babarot/articles/claude-code-session-recall) (はてブ)<br>
   JSONL は30日で消え、grep では読みにくい。Go と SQLite で会話を検索可能にする作りを説明。

5. [OpenRouter、危険なツール実行を別 AI で止める「Armor」](https://gigazine.net/news/20261016-openrouter-armor/) (はてブ)<br>
   エージェントが実行しようとする操作を事前に別モデルで判定し、ルール違反をブロックするベータ機能。

6. [Uber、サービス間の障害伝播を自動で分類](https://www.infoq.com/news/2026/10/uber-automated-dependency/) (InfoQ・英語)<br>
   RPC ミドルウェアで呼び出し元と先の失敗を突き合わせ、依存を fail-close か fail-open かに仕分ける。

7. [Codex と Xcode で SwiftUI を作るときの5つの工夫](https://zenn.dev/hiro322/articles/6a27c8d958de36) (Zenn)<br>
   依頼前の現状確認や変更範囲の絞り込みなど、個人開発で実践する AI への頼み方。

8. [AI エージェントが「頑張るのに進まない」Doom Loop](https://qiita.com/engchina/items/869c0630d80fe87b5ca9) (Qiita)<br>
   通信エラー向けの再試行と、同条件では直らない失敗を分け、止まる条件を先に設計する考え方。

9. [NIST の楕円曲線の種はタイムスタンプだった、Claude が解明](https://www.anthropic.com/research/ecdsa-curve-origins) (Hacker News・英語)<br>
   NSA 提供で出所不明だった ECDSA 曲線の seed 値の由来を Anthropic が説明。対応は不要という締め。
