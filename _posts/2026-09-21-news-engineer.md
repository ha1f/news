---
layout: post
title: "AIエージェント運用基盤「AX」が登場（ソフトウェアエンジニア）"
date: 2026-09-21
profile: engineer
tags: [AI, 開発]
---

AIエージェントをどう大量に安全運用するか——タスクをYAMLで宣言してサンドボックス実行する新基盤「AX」と、Googleの開発規範をコマンド化した「agent-skills」が同じ日にトレンド入り。国内ではLLM統合のアーキテクチャ論とSwift/iOSの地道なデバッグ記事が肩を並べ、締めくくりはGameCube版『バイオハザード4』を当時の3種のコンパイラで丸ごと再現した執念のデコンパイル。

1. [AIエージェントをYAMLで宣言・隔離実行する新基盤「AX」](https://agentexecutor.io) (HN・英語)<br>
   タスクをYAML宣言→ネットワーク制限付きサンドボックスで実行、1クラスタで数十億タスク規模の運用を想定した設計。

2. [Google流エンジニア規範をコマンド化した「agent-skills」](https://github.com/addyosmani/agent-skills) (GitHub Trending・英語)<br>
   25種のスキルを9つのスラッシュコマンドに集約、Hyrum's LawなどGoogleの開発規範をAIコーディングエージェントに強制する仕組み。

3. [プロンプトを返すだけでは終わらない、LLM統合の3層](https://qiita.com/ryucciarati/items/62d7e9fc4c873fdaac20) (Qiita)<br>
   res.textをそのまま画面に出すだけでは実アプリで破綻する箇所を、統合の3層に分けて整理した実装論。

4. [App Store10回リジェクトから生まれた、個人開発者のAIプロンプト全文](https://zenn.dev/papaeng/articles/ios-dev-ai-prompts) (Zenn)<br>
   審査対応を重ねる中で標準化した、Claude Code向け指示文を共通ルールから出力形式まで実物公開。

5. [XCFrameworkを毎回フルビルドしない構成術](https://qiita.com/RIKI_2525/items/8d6c90e6ab838146ab58) (Qiita)<br>
   配布のたびに全体を再ビルドしていた無駄を避け、開発しやすいFramework構成に組み替える具体策。

6. [watchOSのアラームが鳴らない原因は、ARCによるコールバック解放](https://zenn.dev/papaeng/articles/wkextendedruntimesession-arc-release) (Zenn)<br>
   3つの原因が重なっていたが、登録直後にスケジューラのインスタンスがARCで解放される問題を中心に解説。

7. [KV Cacheをtensor形状から見積もる](https://zenn.dev/kas_blog/articles/20260509-llm-17-kv-cache) (Zenn)<br>
   「cacheを有効にする」で済ませず、各層のtensorが持つ軸とdecode時のメモリ予算を数式で整理。

8. [Rustで自作メモリアロケータを書く](https://www.reddit.com/r/programming/comments/1wlho4z/writing_your_own_allocator_in_rust_and_why_you/) (Reddit・英語)<br>
   トイ実装から実用版まで、bump allocationの設計判断とベンチマーク結果を追った実装記。

9. [『Xcodeをほぼ開かなくなった』という開発者の告白](https://www.reddit.com/r/swift/comments/1wi26mi/anyone_else_barely_opening_xcode_anymore/) (Reddit・英語)<br>
   主戦場はVS Code+xcodebuild+ターミナルのAIエージェントに移行、Xcodeは署名とシミュレータ起動だけに。

10. [GameCube版『バイオハザード4』を完全バイト一致で逆コンパイル](https://github.com/adonis-singh/re4) (HN・英語)<br>
    2004年11月のデバッグ版を対象に約55万行のC/C++を復元、当時の3種のコンパイラでmain.dolを完全再現。
