---
layout: post
title: "独自エンジンの Ladybird がアルファ版、AArch64 参照サイトは閉鎖へ（ソフトウェアエンジニア）"
date: 2026-11-24
profile: engineer
tags: [AI, 開発, セキュリティ, 科学, ハードウェア]
serendipity: [11]
article_tags:
  - [開発]
  - [開発, ハードウェア]
  - [開発, セキュリティ]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [AI, セキュリティ]
  - [AI, 開発]
  - [開発]
  - [開発, セキュリティ]
  - [開発]
  - [科学]
---

フォークではない自前エンジンのブラウザ Ladybird が、ついにアルファ版に。一方で Arm の法務部門からの通知を受け、愛用者の多い AArch64 リファレンスサイトが12月4日で閉鎖へ。形式検証で Rust 製 OSS の脆弱性が見つかった話や、エージェント時代のテストとセキュリティの話題も厚い一日。

1. [自前エンジンのブラウザ「Ladybird」がアルファ版に](https://ladybird.org/posts/alpha/) (HN・英語)<br>
   macOS と Linux 向けに配布が始まり、WebDriver と Firefox DevTools プロトコルにも対応した

2. [Arm の要請で、AArch64 命令リファレンスサイトが閉鎖へ](https://arm.jonpalmisc.com/) (HN・英語)<br>
   Armv8-A・v9-A の命令とシステムレジスタを検索できた個人サイトに、Arm の弁護士から削除の通知

3. [Rust 製 OSS を Lean 4 で形式検証したら、実際の脆弱性が次々見つかった](https://zenn.dev/koukyosyumei/articles/31c8fcf4da45b7) (はてブ)<br>
   CalDAV サーバー RustiCal では、所有者を WHERE 句に入れ忘れた SQL で他人の予定を消せた

4. [AI がテストに合わせて実装していないか、仕様テストを隠して確かめる](https://zenn.dev/h_aso/articles/isolated-spec-tests-claude-code) (Zenn)<br>
   codecentric の記事が紹介した「Isolated Specification Tests」を Claude Code で試した記録

5. [バグハント用の Claude Code スキル集「Claude-BugHunter」](https://github.com/elementalsouls/Claude-BugHunter) (GitHub Trending・英語)<br>
   82のスキルと15のスラッシュコマンドに、24の脆弱性分類で整理した過去の報告681件分のパターン

6. [QCon SF、本番環境の AI エージェントをどう守るか](https://www.infoq.com/news/2026/11/qcon-ai-agent-security/) (InfoQ・英語)<br>
   Google のアマンダ・ウォーカー氏は、エージェントを「機械の速さで動く内部犯行リスク」として扱った

7. [コーディングエージェントが変えた OSS 開発のプロセスと喜び](https://zenn.dev/cybergarage/articles/5ee7ac6b3b0565) (Zenn)<br>
   止まっていた保守が再び動き出した一方、判断を次々迫られる疲れで楽しさの質が変わったという実感

8. [Agoda、モジュラーモノリス化で API のコードレビュー時間を64%短縮](https://www.infoq.com/news/2026/11/agoda-modular-monolith-framework/) (InfoQ・英語)<br>
   予約後 API を作り直さずに、Data Mapper と ArchUnit のテストでドメインの境界を守らせた事例

9. [iOS エンジニアのための OAuth 2.0 + PKCE 入門](https://zenn.dev/mobile_app_tec/articles/ios-oauth2-pkce-native-app) (Zenn)<br>
   SwiftUI アプリで外部ライブラリを使わずに実装した経験から、state と PKCE の違いなど誤解しやすい点を整理

10. [Mac の任意のウィンドウを iPhone・iPad で操作できる OSS「Sill」](https://github.com/Saffsanity/sill) (GitHub Trending・英語)<br>
    タッチや Apple Pencil、トラックパッドで操作でき、サーバーを介さず無料で動く Swift 製アプリ

11. [岩石を畑にまく炭素除去、やりすぎると作物の収量を下げるおそれ](https://www.technologyreview.com/2026/11/23/1149392/why-using-rocks-for-carbon-removal-could-eventually-reduce-crop-growth/) (MIT TR・英語/一部会員限定)<br>
    Google や Microsoft が出資する手法で、CarbonPlan の試算では除去量の上限が年10億トン未満に
