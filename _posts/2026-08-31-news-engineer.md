---
layout: post
title: "2026年8月31日 (engineer)"
date: 2026-08-31
profile: engineer
tags: [AI, 開発, セキュリティ]
---

Linuxカーネルのメンテナがkernel.orgを食い尽くすAIクローラーの実態を告発、HNで今週最高スコアを記録。開発ツール側ではJetBrainsとAWSがそれぞれコーディングエージェント基盤をリリースし、AI時代の開発環境が急速に整備されている。

1. [Linuxカーネルに群がるAIクローラーの実態](https://people.kernel.org/monsieuricon/creepy-crawlies) (Hacker News)<br>
   kernel.orgの帯域を食い尽くすボットの正体と、開発者が講じた対抗策

2. [Swift×MetalでLLM推論エンジンを自作、16GB Macで61GBモデルを実行](https://www.reddit.com/r/swift/comments/1w2t0l0/built_a_custom_llm_inference_engine_in_swiftmetal/) (Reddit)<br>
   MoEエキスパートをSSDからストリーミングし、llama.cppに依存しない独自設計

3. [JetBrains「Junie Local」提供開始、Macでコーディングエージェント](https://www.publickey1.jp/blog/26/jetbrainsmacjunie_localclaude_sonnet_45rtx5909.html) (Publickey)<br>
   Claude Sonnet 4.5搭載、ローカルで動作するIDEネイティブのエージェント

4. [AWS、非同期コーディングエージェント基盤「Kiro Crew」をOSS化](https://www.infoq.com/news/2026/08/kiro-crew-coding-agents/) (InfoQ)<br>
   複数エージェントの並行実行と成果物統合を管理するフレームワーク

5. [自作npmパッケージにマルウェアを公開された——対応の全記録](https://zenn.dev/7nohe/articles/npm-malware-incident-response) (Zenn)<br>
   リリースワークフローの不備を突かれたサプライチェーン攻撃の発見から収束まで

6. [QubesOS、copy-to-VMで任意コード実行の脆弱性](https://www.qubes-os.org/news/2026/08/29/qsb-118/) (Hacker News)<br>
   VM間のファイルコピー機構を突く攻撃経路の詳細と緩和策

7. [XCTestのthrowに隠れたコスト——実行ファイルの40倍遅い](https://www.reddit.com/r/swift/comments/1w2f07n/the_hidden_cost_of_throw_in_xctest_40x_slower/) (Reddit)<br>
   グローバルオブザーバーが全throwを捕捉、try?でも回避不可

8. [nginxで502が稀に発生する原因はkeepalive接続](https://zenn.dev/shinagawa_web/articles/transient-502-keepalive-reuse) (はてなブックマーク)<br>
   バックエンドのログに何も残らない間欠的エラーの根本原因を特定するまで

9. [Zod v4.5、スキーマコンパイルでバリデーション3〜9倍高速化](https://www.reddit.com/r/programming/comments/1w1sl70/zod_v45_adds_schema_compilation_39x_faster/) (Reddit)<br>
   z.compile()で事前コンパイルし、ランタイムのオーバーヘッドを大幅に削減

10. [AIが作った架空の病名、研修医の44%が信用](https://www.itmedia.co.jp/news/article/2608/31/2000000865/) (ITmedia)<br>
    LLMの幻覚が専門家の判断をどう歪めるか、仏大学病院が定量検証
