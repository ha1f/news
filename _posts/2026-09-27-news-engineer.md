---
layout: post
title: "AI時代、言語とコード生成の変わり目（ソフトウェアエンジニア）"
date: 2026-09-27
profile: engineer
tags: [AI, 開発, セキュリティ]
---

GitHub Copilot for XcodeがSwiftトレンド上位に浮上し、YC発のOSS設計ツール「Whiteboard」も410ポイントを集めるなど、AIとコードを書く現場の話題が目立つ一日。ElixirのJosé Valim氏はAIが大半のコードを書く時代に言語コミュニティがどう変わるかを問い、SupabaseではAI生成アプリの設定ミスによるデータ流出も報告された。Swiftの並行処理設計から分散DBの再設計、痛みを感じるAIの研究まで、視点の異なる技術記事が並ぶ。

1. [Elixir作者、AI時代の言語進化を考察](https://dashbit.co/blog/evolving-ai-era) (HN・英語)<br>
   PythonやRubyの文化基盤ごと、AIがどう変えるかを考察。

2. [Xcode向けCopilot、Agentモード強化](https://github.com/github/CopilotForXcode) (GitHub Trending・英語)<br>
   ターミナル操作やMCP連携までXcode内で完結する新機能。

3. [YC発のOSS設計キャンバス「Whiteboard」](https://github.com/devdotfast/whiteboard) (HN・英語)<br>
   Claude CodeやCodexの提案をキャンバス上の図で確認できる。

4. [本当に要るSendable、Region分離で判定](https://zenn.dev/d_date/articles/1768cc530b685e) (Zenn)<br>
   SE-0414のRegion-based isolationで要否を判定する。

5. [常駐監視アプリAirStats、待機時0.046%CPU](https://zenn.dev/airstats/articles/c94975e318122a) (Zenn)<br>
   Stats・iStat Menusと実機比較、11MBの軽さも検証。

6. [Vercelの「インポート可能」通知、条件を検証](https://zenn.dev/devuloper/articles/vercel_import_candidates_email) (Zenn)<br>
   検証用に61個のリポジトリを作り、送信条件を特定。

7. [Uber、時系列DB「M3DB」をサブクラスタ化](https://www.infoq.com/news/2026/09/uber-m3db-subcluster-sharding/) (InfoQ・英語)<br>
   固定サイズの分割で障害影響を局所化、リバランス省略も実現。

8. [AIエージェント基盤の作り方、AWSとLangChainで比較](https://www.infoq.com/articles/agent-harness-build-one/) (InfoQ・英語)<br>
   金融アシスタントを題材に、ツール・メモリ・コスト設計の差を比較。

9. [Supabase利用アプリ、個人データが公開状態に](https://techcrunch.com/2026/09/25/some-supabase-customers-are-publicly-exposing-reams-of-peoples-data-to-the-web/) (TechCrunch・英語)<br>
   AI生成・バイブコーディング製アプリの設定ミスが原因。

10. [AI製Goコードの品質を上げるLinter「declscope」](https://zenn.dev/yumemi_inc/articles/go-declscope-file-scoped-private) (はてブ)<br>
    フラットなGoパッケージにファイル単位の非公開を持ち込む。

11. [AI内部に「痛み」特有の活動パターンを発見](https://nazology.kusuguru.co.jp/archives/200119) (はてブ)<br>
    独ルール大学が25種のAIで検証、痛み回避へ人間を害す選択が最大7割に。
