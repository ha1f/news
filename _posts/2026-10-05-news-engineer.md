---
layout: post
title: "GoogleがOSS脆弱性報奨金を停止、AI報告の急増で（ソフトウェアエンジニア）"
date: 2026-10-05
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス]
article_tags:
  - [セキュリティ, AI]
  - [セキュリティ, AI]
  - [ビジネス, 開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [AI, 開発]
  - [セキュリティ]
  - [開発]
---

Googleがオープンソース向けの脆弱報奨金プログラムを10月1日から停止した。AIが量産する無効な報告に、運営側が耐えきれなくなった形だ。同じ「AIエージェントのリスク」を巡り、Appleもmacの権限制御に動く。一方で、Go 1.27のJSON刷新やSupabaseのTurso買収など、足元の技術選択も動いている。

1. [Google、OSS向け脆弱性報奨金を一時停止](https://techcrunch.com/2026/10/04/google-froze-its-open-source-bug-bounty-program-due-to-a-significant-rise-in-ai-submissions/) (TechCrunch・英語)<br>
   AI由来の自動投稿の大半が無効だったためで、再開の見通しは2027年第1四半期に更新される予定。

2. [Apple、macOSのフルディスクアクセスに追加制御](https://www.kobonemi.com/entry/2026/10/03/macOS-27-Full-Disk-Access-Additional-Controls) (はてブ)<br>
   常時稼働のAIエージェント普及を受け、許可にはっきりした操作を要求する方向だとAppleが開発者向けに説明した。

3. [Supabase、SQLite基盤のTursoを買収](https://www.publickey1.jp/blog/26/supabase1sqlitetursoaidb.html) (Publickey)<br>
   Tursoは1台のサーバで数百万のDBを持て、未使用時はストレージ料金のみという構造が売りで、エージェント向けDB需要が買収の理由。

4. [Go 1.27のJSON v2、移行で何が壊れるか](https://importstatic.com/go/go-json-v2-migration) (Reddit・英語)<br>
   encoding/jsonは既にv2エンジン上で動いており、v2をimportした瞬間にnilスライスが[]になるなど既定値が変わる。

5. [なぜ開発者は「プラットフォームを使え」に従わないのか](https://nolanlawson.com/2026/10/03/why-dont-more-developers-use-the-platform/) (HN・英語)<br>
   Web標準の推進側だった筆者が、あえて懐疑派の側に立ち、jQuery時代の経緯や慣れから理由を整理する。

6. [AI時代に、次のベテランエンジニアは育つのか](https://note.com/yoshiki_shibata/n/n185f3d9e13bc) (はてブ)<br>
   1978年からプログラミングを続ける筆者が、48年の変化を振り返りつつ今回のAIによる変化を論じる。

7. [開発者5463人の実態調査「State of Devs 2026」](https://www.publickey1.jp/blog/26/state_of_devs_2026_ai.html) (Publickey)<br>
   回答者の年齢中央値は36歳、経験年数は12年、日本からの回答は21位の50人。AI利用度合いも集計されている。

8. [Google Cloud、コーディングエージェント向けプラグインを発表](https://www.publickey1.jp/blog/26/google_cloudgoogle_cloud_developer_plugin_for_ai_coding_agents.html) (Publickey)<br>
   Claude CodeなどにGoogle Cloudの専門知識とツールを組み込める拡張で、公式提供。

9. [Xiaomi端末の広告が、導入済みアプリのアイコンを偽装](https://www.reddit.com/r/programming/comments/1wxr63h/your_xiaomi_phone_may_be_sending_you_phishing/) (Reddit・英語)<br>
   投稿者の端末では、偽の「Spotify」通知としてカジノ系アプリの広告が表示された。

10. [ページテーブルのメモリ消費を巡るカーネル開発の議論史](https://frn.sh/pagetables/) (HN・英語)<br>
    Torvaldsが1997年の修士論文以来ツリー型を選んだ背景と、2020年にメモリ効率が問題になった経緯を追う。
