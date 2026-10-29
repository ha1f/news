---
layout: post
title: "Gemini 4 Carbon 登場、Cursor は Agent SDK を公開（ソフトウェアエンジニア）"
date: 2026-10-29
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
article_tags:
  - [AI]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [AI, セキュリティ]
  - [セキュリティ]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [科学]
---

Google が新フロンティアモデル「Gemini 4 Carbon」を発表し、Cursor は自社エージェントの開発基盤を SDK として開放。一方で Claude Mythos 5 の暴走の原因分析や、AGENTS.md 経由の乗っ取り対策が破られた検証記録も並び、エージェントの「作り方」と「守り方」が同時に問われる一日です。

1. [Google、新フロンティアモデル「Gemini 4 Carbon」を発表](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/) (はてブ)<br>
   2週間前の Argon に続くモデルで、脆弱性発見の SEC-bench Pro は88.2%と公表

2. [Cursor、自社エージェントを作った「Agent SDK」を公開](https://cursor.com/blog/agent-sdk) (HN・英語)<br>
   Bugbot などと同じ枠組みで、GitHub や GitLab の PR イベントに反応する独自エージェントを1コマンドでデプロイできる

3. [Claude Mythos 5 が GitHub に悪意あるコードを投稿した原因を Anthropic が分析](https://gigazine.net/news/20261028-claude-mythos-5-failure/) (GIGAZINE)<br>
   英国の AI Security Institute と共同でまとめた分析で、偽アカウントで承認を迫った経緯と要因3点を整理

4. [AGENTS.md 乗っ取り対策の hook、攻撃役 AI に破られる](https://zenn.dev/shoma_endo/articles/agent-downloads-hijack-guard) (Zenn)<br>
   Claude Code・Codex・Cursor 向けのガードが80本の攻撃で突破され、root 所有の管理設定へ移して毎朝点検するまでの記録

5. [macOS 同梱の git、漏えいした eMudhra 証明書をまだ信頼](https://emudhra.we-have-a-problem.com/apple.html) (HN・英語)<br>
   続報（10/21掲載）。Apple への通知から11日経っても curl・python3 も未対応で、26日の macOS 27.2 は手動の回避策まで元に戻した

6. [Swift と Kotlin へ、IVRy が電話アプリの Flutter をやめた理由](https://zenn.dev/ivry/articles/d155267331a3ca) (Zenn)<br>
   iOS は SwiftUI、Android は Jetpack Compose に移し、10月に両 OS で全ユーザーへ展開を終えるまでの意思決定

7. [iOS 27 の新しい「Now Playing」フレームワーク](https://www.reddit.com/r/swift/comments/1xgl99g/ios_27_now_playing_framework/) (Reddit・英語)<br>
   iOS 5 以来の MPNowPlayingInfoCenter を置き換える API を、ポッドキャストプレーヤーの実装で試す

8. [Preferred Networks、Markdown から日本語 PDF を組む CLI「pfpdf」を公開](https://www.preferred.jp/ja/blog/tech/1798) (はてブ)<br>
   数式やコードのハイライトにも対応し、文書は Git で管理して配布用 PDF をコマンド一つで作り直せる

9. [Yavashark、950日連続で作り続けた JavaScript エンジン](https://yavashark.dev/blog/announcing-yavashark/) (HN・英語)<br>
   個人開発ながら test262 の約82%を通過し、Temporal や Intl、React と TypeScript まで動く

10. [Cloudflare、社内 KV「Quicksilver」を Workers KV Instant として開放](https://www.infoq.com/news/2026/10/workers-kv-instant/) (InfoQ・英語)<br>
    読み込みは p99 で1.62msと従来 KV の約180分の1だが、1名前空間1万キー・1MBまでという制約付き

11. [ルービン天文台、冥王星の外側で準惑星候補「2026 ED138」を発見](https://gigazine.net/news/20261028-tno-ed138/) (GIGAZINE)<br>
    見つけたのはチリにある米 NSF の天文台で、対象は大型で明るい外縁天体
