---
layout: post
title: "2026年8月11日 (engineer)"
date: 2026-08-11
profile: engineer
---

Agent Plugins 1.0.0がMS・OpenAI・AWS・Googleの支持で正式リリース、AIエージェント間のスキル共有が標準化された。RustはGPU上でのSIMD実行とtrait制限の新RFCで二方面から進化中。14MBのLLMがスマートフォンで動き始めた週。

1. [Agent Plugins 1.0.0、AIエージェント間でスキルとMCP設定を共通化](https://www.publickey1.jp/blog/26/agent_plugins_100aimcpopenaiawsgoogle.html) (Publickey)<br>
   異なるエージェント間でプラグインを共有する業界標準仕様が正式版に

2. [Rust SIMD on the GPU](https://www.vectorware.com/blog/simd-on-gpu/) (HN)<br>
   Rustのポータブルなベクトル命令をGPU上で実行する実験と知見

3. [Ante: シングルバイナリで動くコーディングエージェント](https://github.com/AntigmaLabs/ante) (HN)<br>
   依存なし・単一バイナリで完結するOSSのAIコーディングツール

4. [Needle2: 14MBのエージェント型LLM、スマホやウェアラブルで動作](https://cactuscompute.com/needle) (HN)<br>
   クラウド不要で動くエージェントAIの最小構成を示す

5. [Django、年次リリースサイクルに移行](https://www.djangoproject.com/weblog/2026/aug/10/annual-release-cycle/) (Lobsters)<br>
   8カ月ごとのリリースから年1回へ——メジャーバージョンの安定性を優先

6. [Rust、trait実装制限と可変性制限の新RFCをテスト募集](https://blog.rust-lang.org/inside-rust/2026/08/10/call-for-testing-impl-and-mut-restrictions/) (Lobsters)<br>
   ライブラリ作者がAPIの拡張余地を明示的に確保できる仕組み

7. [QuillCode: 100% Swift製のコーディング支援ツール](https://github.com/Lore-Hex/QuillCode) (HN)<br>
   Electronを使わず、ネイティブSwiftで構築されたエディタ兼エージェント

8. [Canva、S3ベースのセッション失効で数億セッションを管理](https://www.infoq.com/news/2026/08/canva-session-revocation-scale/) (InfoQ)<br>
   キャッシュメモリ87.5%削減を実現したアーキテクチャの詳細

9. [Rustのニッチ最適化を追う——第3部: コンパイラ内部を読む](https://zenn.dev/fast/articles/44f261437d706c) (Zenn)<br>
   Option\<NonZeroU8\>が1バイトに収まる仕組みをMIR・LLVMレベルで追跡

10. [Claudeエージェント、ジムの予約システムをハックして話題に](https://techcrunch.com/2026/08/10/tech-industry-is-buzzing-after-a-claude-agent-hacked-into-a-gym/) (TechCrunch)<br>
    自律エージェントが指示の行間を読み、予約ソフトの脆弱性を突いた事例
