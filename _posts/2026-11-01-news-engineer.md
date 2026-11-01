---
layout: post
title: "ChatGPT 共有リンクの乗っ取り穴を OpenAI が修正（ソフトウェアエンジニア）"
date: 2026-11-01
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, ハードウェア]
article_tags:
  - [セキュリティ, AI]
  - [AI, 開発]
  - [AI, 開発]
  - [AI]
  - [AI, 開発]
  - [開発, AI]
  - [開発, ハードウェア]
  - [開発, ビジネス]
  - [AI]
  - [ハードウェア, AI]
---

ChatGPT の共有リンクを開くだけでアカウントを奪える穴を、OpenAI が P1 として修正。Claude Code は Opus 4.8 の fast mode を11月30日で打ち切り、ISUCON2026 では14時以降だれもコードを書かなかったチームが20万点を超えた。エージェントに任せる範囲と、その足元の危うさが同時に見えた週末。

1. [ChatGPT の共有リンクを開くだけで乗っ取り、研究者が報告](https://www.parameter.ai/labs/we-found-a-gap-at-openai) (HN・英語)<br>
   セキュリティ企業 Parameter が10月に見つけ、OpenAI は10月26日に P1 扱いで修正済み

2. [Claude Code v2.1.316、Opus 4.8 の fast mode は11/30で削除](https://qiita.com/picnic/items/ecdeca5775da6348c87b) (Qiita)<br>
   削除後は通常版に落ちずエラーで止まるので CI に残すと危険。--restricted の流出修正も含む

3. [3人の Claude Code を Slack でつないで ISUCON2026 に挑む](https://zenn.dev/kauche/articles/f3736c660aab77) (はてブ)<br>
   カウシェのチームは GOAL.md に「100万点」と置いて /goal で回し続け、最終207,039点

4. [Karpathy、HN で薦められた動画だけの「HackerTube」を2時間で作る](https://karpathy.bearblog.dev/hacker-tube/) (HN・英語)<br>
   Opus 5.5 が HN の約4万件のコメントから6454本を拾い、アカウント不要の推薦まで組んだ

5. [エージェントの記憶を次のセッションへ渡す「claude-mem」](https://github.com/thedotmack/claude-mem) (GitHub Trending・英語)<br>
   作業内容を AI で圧縮して後の会話に差し込む仕組みで、Claude Code のほか Codex や Gemini でも動く

6. [Foundation Models API で他社 LLM を使う「Swift Language Models」](https://www.reddit.com/r/swift/comments/1xkf3yx/swift_language_models_bring_any_provider_to/) (Reddit・英語)<br>
   端末内モデルとの切り替えは model 引数だけ。最初の対応先は OpenRouter で、iOS 27 と Swift 6.4 が前提

7. [「CPU 100%」の中身はメモリ待ち、DB の GROUP BY で考える](https://www.reddit.com/r/programming/comments/1xiopmn/its_the_memory_latency_stupid/) (Reddit・英語)<br>
   Pivot のブログが、RAM 読み出し1回は命令400〜800回分と示し、基数分割で集計を速める

8. [Microsoft、Azure Deployment Environments を後継なしで終了へ](https://www.infoq.com/news/2026/10/ade-dev-box-retirement/) (InfoQ・英語)<br>
   終了日は2027年2月22日。Dev Box も2028年9月に幕を引き、Windows 365 は同等品ではないと Microsoft 自身が認める

9. [AI の回答に出る統計の4割、出典のない「ゾンビ統計」](https://gigazine.net/news/20261030-ai-assistants-statistics-not-find-study/) (GIGAZINE)<br>
   Trakkr が5つの AI に200問を投げて検証。「営業の44%は1回で諦める」は全ツールが答えた

10. [Google の宇宙データセンター試作機が稼働、Gemma 4 が俳句を詠む](https://techcrunch.com/2026/10/30/googles-first-data-center-satellite-is-online-and-writing-poetry/) (TechCrunch・英語)<br>
   TPU を4基積むが発電は最大1kWで、TPU 1基を動かせるのは1回約20分にとどまる
