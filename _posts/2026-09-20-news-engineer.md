---
layout: post
title: "2026年9月20日（ソフトウェアエンジニア）"
date: 2026-09-20
profile: engineer
tags: [開発, AI, セキュリティ, ビジネス]
---

Vapor誕生からちょうど10年の節目に5.0ベータが公開され、AppleもXcodeのプロジェクト設定をJSON形式へ刷新中。AIエージェントを侵入監査官に仕立てる動きの一方で、Lambdaがわずか8分で乗っ取られる実例レポートも公開され、攻守両面でAIエージェント活用が進む一日に。

1. [Vapor 5ベータ公開、10年越しの全面書き換え](https://www.reddit.com/r/swift/comments/1wh4j02/vapor_5_beta_released/) (Reddit・英語)<br>
   EventLoopを全廃し完全async/await化、公開APIからNIOもほぼ排除した4.9万行規模の刷新。

2. [Xcode、プロジェクト設定をJSON形式に刷新へ](https://zenn.dev/d_date/articles/b1a7baa74b77da) (Zenn)<br>
   .pbxprojの衝突の元となる24桁IDに代わり、Xcode 27.2から.xcprojというJSON形式が既定に。

3. [CIの稼働時間を144分→39分に73%削減](https://zenn.dev/innovation/articles/e84f8ccca8e6da) (Zenn)<br>
   AIエージェント活用でPR・テストが急増し肥大化したCIを、3つの対策で削減した実践記録。

4. [Cloudflare、AIエージェントを侵入監査官にするスキル公開](https://github.com/cloudflare/security-audit-skill) (GitHub Trending・英語)<br>
   偵察→網羅的探索→検証→報告と多段エージェントで回す監査スキル。自社の脆弱性発見基盤の元になった代物。

5. [そのLambda、侵入から8分で管理者権限奪取](https://speakerdeck.com/k1nakayama/sono-lambda-8-bun-de-kanrisha-kengen-made-ubawaremasu) (はてブ)<br>
   Sysdigの実脅威レポートを基に、S3窃取からBedrock不正利用に至る5段階攻撃をGameDayで再現検証。

6. [AWS Lambda、実行時間上限を90分に拡大](https://www.infoq.com/news/2026/09/lambda-90-minute-timeout/) (InfoQ・英語)<br>
   常時稼働型のLambda Managed Instances限定で上限を15分から6倍の90分に拡大。同期呼び出しは据え置き。

7. [Grab、社内500超のAIエージェントを標準化](https://www.infoq.com/news/2026/09/grab-agent-platform/) (InfoQ・英語)<br>
   「LLM-Kit」導入で、新規エージェントのデプロイ時間が2週間から1時間に短縮。

8. [PlanetScale、Postgres向け全文検索「TIN」公開](https://planetscale.com/blog/introducing-tin) (HN・英語)<br>
   曖昧一致・正規表現・BM25スコアリングまで1つの拡張機能でカバーする全文検索、GAとして即利用可能に。

9. [Mojo 1.1公開、コンパイラへの外部貢献を解禁](https://www.reddit.com/r/programming/comments/1wizhuv/mojo_11_released_now_accepting_community/) (Reddit・英語)<br>
   外部からのプルリクエストを正式に受け付ける体制へ移行した、コンパイラ開発の節目のバージョン。

10. [マイクロソフト社内でRustがTier 1言語に](https://www.publickey1.jp/blog/26/rustcctstier_1.html) (Publickey)<br>
    C++/C#/TypeScriptと同格の社内標準言語に昇格。Windowsカーネルの一部は既にRust移行済みと判明。

11. [LLMを拒む実験言語「KillSwitch」登場](https://killswitch-lang.org) (HN・英語)<br>
    コーディングエージェントを狙い撃つ実験的な難読言語。公開中のベンチマークではClaude Opus 5が首位。
