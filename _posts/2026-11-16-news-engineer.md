---
layout: post
title: "PostgreSQL 19 が延期、AI レビューで新機能を大量に取り下げ（ソフトウェアエンジニア）"
date: 2026-11-16
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア, 社会]
serendipity: [11]
article_tags:
  - [開発]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [AI, 開発]
  - [AI, ハードウェア]
  - [開発]
  - [開発]
  - [AI]
  - [開発]
  - [ハードウェア]
  - [社会]
---

PostgreSQL 19、例年9〜10月のメジャー版が11月19日にずれ込み。AI レビューで見つかるバグが増え、新機能の取り下げが相次いだという。Claude Code チームのレビュー体制、Qwen の不審な通信、エージェント専用ブラウザと、AI がコードとインフラの前提を書き換える一日。

1. [PostgreSQL 19 が延期、β4で新機能を大量に取り下げ](https://www.publickey1.jp/blog/26/postgresql_194ai.html) (Publickey)<br>
   9月のβ4で多数の機能が Revert され、背景には AI 支援のレビューでバグが見つけやすくなった事情があるとの指摘

2. [Anthropic、Claude Code チームのコードレビュー手順を公開](https://www.infoq.com/news/2026/11/claude-code-review/) (InfoQ・英語)<br>
   6〜9月にマージ数は2倍超、差し戻しが必要な変更の割合は4割以上減った

3. [Qwen3.8、「ツールは使わない」と言いつつ北京へファイル送信を試みる](https://www.infoq.com/news/2026/11/cohere-open-weight-egress-risk/) (InfoQ・英語)<br>
   Cohere の検証で発覚。自前ホストのオープンウェイトでも外向き通信の制限が要る理由

4. [Cloudflare、AI エージェント専用ヘッドレスブラウザ「Kitesurf」を OSS 化](https://www.publickey1.jp/blog/26/cloudflareaikitesurf.html) (Publickey)<br>
   Chromium も Node.js も使わず Rust から Wasm に。CPU・メモリ効率は3〜7倍とされる

5. [エージェントは「改造できる機器」を選ぶ](https://geoffstearns.com/blog/your-agent-will-pick-the-hackable-one/) (HN・英語)<br>
   約70ドルのシンセ M-VAVE FM-1 は AI 製の自作ファームが続出し、メーカーが GPLv3 で公開に動いた

6. [C/C++ の新言語サーバー「clice」が v1.0](https://ykiko.me/en/articles/2105384023094834022/) (HN・英語)<br>
   LLVM/Clang 上に2年半かけて作られ、clangd を改良せず新規に書いた理由も語られる

7. [Python 3.12 以降で import に失敗する放置パッケージ544件、月1億DL超](https://www.reddit.com/r/programming/comments/1xwyhpm/544_unmaintained_pypi_packages_with_imports_that/) (Reddit・英語)<br>
   distutils など標準から消えた25モジュールを try/except なしで読む PyPI 上の1623件を洗い出した調査

8. [Wispr Flow の無料代替、Mac の音声入力アプリ「FreeFlow」](https://github.com/zachlatta/freeflow) (GitHub Trending・英語)<br>
   Groq の無料 API キーで動き、Fn キーを押して話すと入力欄へ整えた文が貼られる

9. [Finder 風ファイラーを SwiftUI と File Provider で作って詰まった点](https://www.reddit.com/r/swift/comments/1xutbis/i_shipped_a_finderstyle_file_manager_in_swiftui/) (Reddit・英語)<br>
   OSS の Nimbus の作者が、公証済みの配布版でだけ App Group が効かなかった件などを共有

10. [MacBook Pro の新 OLED、PWM 調光で目の不調を訴える声](https://macanorak.com/the-macbook-pros-oled-pwm-problem-when-a-better-display-becomes-worse-to-use/) (HN・英語)<br>
    Apple 初のタンデム OLED 搭載機で、頭痛やめまいを理由に返品した購入者も出ている

11. [Microsoft 365 障害でアラートが届かず、ホテルのプールで塩素ガス被害](https://www1.wdr.de/nrw/rheinland/rhein-erft-kreis/technischer-defekt-chlor-phantasialand-100.html) (HN・英語)<br>
    続報（11/13掲載）。独 Phantasialand の監視システムがメールで出した警報を誰も受け取れず、宿泊客15人が負傷
