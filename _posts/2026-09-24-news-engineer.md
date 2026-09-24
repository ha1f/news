---
layout: post
title: "Claude Code、AGENTS.md読込に対応（ソフトウェアエンジニア）"
date: 2026-09-24
profile: engineer
tags: [AI, 開発, セキュリティ, 科学, ハードウェア]
---

Anthropicの新設バイオラボで、Claudeが人間の大枠指示だけを頼りに未知の酵素系を見つけた。同じタイミングでClaude CodeがAGENTS.md対応を明かし、コーディングエージェントを手元環境からどう隔離するかを巡る議論もHackerNewsで熱を帯びた。足元にはB+ツリーやRailway指向設計といった定番の設計論、締めにはDoomをSQLへ移植する酔狂な実験まで、振れ幅の大きい一日。

1. [Claude、CRISPR類似の未知酵素系を発見](https://www.anthropic.com/news/claude-discovers-novel-enzyme-system) (HN・英語)<br>
   Anthropic新設の生命科学ラボ、大枠の指示だけで機能未知の酵素系をClaudeが特定。

2. [Claude Code、AGENTS.mdを自動読み込みに対応](https://www.publickey1.jp/blog/26/claude_codeagentsmdclaudemd.html) (Publickey)<br>
   9/18更新のv2.1.277、CLAUDE.mdが無いプロジェクトで自動的に読み込む仕様に。

3. [Fly.io、VSCodeのリモートSSH実装を酷評](https://fly.io/blog/vscode-ssh-wtf/) (HN・英語)<br>
   AIコーディングエージェントの実行環境が誤って手元PCに混ざる設計の危うさを指摘。

4. [rm -rf対策のLinuxサンドボックス「Drop」](https://droprun.sh/) (HN・英語)<br>
   Docker不要のrootless実行で、エージェントの暴走コマンドをOSレベルで遮断。

5. [iPhone Duo開閉でSwiftUIレイアウトが崩れる原因](https://qiita.com/tsuzuki817/items/57b2d318427820713657) (Qiita)<br>
   Xcode 27.1のDevice Hubで実機確認、原因はUIViewRepresentableの状態管理漏れ。

6. [macOS27の新コマンド`fm`をM1 Macで実機検証](https://zenn.dev/dannchu/articles/macos27-fm-command-guide) (Zenn)<br>
   Apple Foundation Models CLI、8GBのM1でもクラウド接続せず日本語対話まで完結。

7. [FlashAttention、確認すべきはkernelとデータ移動](https://zenn.dev/kas_blog/articles/20260509-llm-19-flashattention) (Zenn)<br>
   API名でなく、GPU・dtype・shape次第で変わる実際の処理経路を実装者向けに整理。

8. [B+ツリーが速いのはディスクI/O単位に合わせたから](https://zenn.dev/ippe1/articles/why-db-uses-bplus-tree) (Zenn)<br>
   探索アルゴリズムの優劣ではなく、リーフノード到達までのI/O削減が速さの正体。

9. [エラー処理を「線路」に例えるRailway指向設計](https://kciter.so/posts/railway-oriented-programming/en/) (Reddit・英語)<br>
   F#発の手法、FunctorとMonadで正常系・異常系を2本のレールとして合成する考え方。

10. [Cloudflare、Python Workersが正式サービスに](https://www.publickey1.jp/blog/26/cloudflarepython_wrokerspythonweb.html) (Publickey)<br>
    サーバレスのCloudflare Workers上で、PythonからDB接続やストレージ操作が可能に。

11. [1993年版Doomを丸ごとSQLに移植](https://cedardb.com/blog/sqldoom/) (Reddit・英語)<br>
    CedarDB開発陣が移植、ゲームロジックがDB内で35FPS駆動しマルチプレイも動作。
</content>
