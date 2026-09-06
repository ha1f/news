---
layout: post
title: "2026年8月23日（ソフトウェアエンジニア）"
date: 2026-08-23
profile: engineer
tags: [AI, 開発, 科学]
---

LinkedInが自社PRレビューにマルチエージェントAIを実戦投入し、エンジニアリングの現場でAIは「補助」から「基盤」へ着実に格上げされている。Rustは次世代トレイトソルバーをnightlyで有効化、macOS 27ではhdiutilが非推奨入りと、開発者の足元も静かに動く。形式手法でDenoのバグを見つけた記事やiOS向けネットワークデバッグOSSなど、手を動かす人向けの実践ネタが揃った週末。

1. [LinkedIn、AIコードレビューをマルチエージェント構成で本番化](https://www.infoq.com/news/2026/08/linkedin-ai-code-review/) (InfoQ)<br>
   組織のコーディング文脈を理解しつつ低シグナルなフィードバックを減らす設計

2. [Claude Code/Codexの大規模開発向けタスク管理術](https://qiita.com/Y-Y-dev/items/d526fb7cdbe35a3f9384) (はてなブックマーク)<br>
   数十〜数百件規模で破綻しない指示の切り方を実例で解説

3. [ローカルLLMが「思ったより馬鹿に見える」理由](https://forum.level1techs.com/t/why-your-local-llm-feels-dumber-than-it-is/253917) (Hacker News)<br>
   プロンプトやサンプリング設定の見直しで性能差が縮まる理由

4. [Quintの形式仕様でdeno/celldの二重writerバグを発見](https://zenn.dev/mizchi/articles/quint-application-modeling) (Zenn)<br>
   形式手法とClaude 5 Opusを組み合わせた実践的なバグ検出記録

5. [Rust、次世代トレイトソルバーをnightlyで有効化](https://blog.rust-lang.org/2026/08/21/enabling-next-solver-on-nightly/) (Lobsters)<br>
   型推論の精度と一貫性が向上する大型リファクタの第一歩

6. [hdiutil、macOS 27 Golden Gateで非推奨に](https://lapcatsoftware.com/articles/2026/8/7.html) (Hacker News)<br>
   DMGの作成・マウントに使っていたツールの移行先を確認

7. [apple/container: Apple SiliconでLinuxコンテナ実行](https://github.com/apple/container) (GitHub Trending)<br>
   Swiftで書かれたmacOS向け軽量VMコンテナ管理ツール

8. [Trace: iOSネイティブのネットワークデバッグOSS](https://www.reddit.com/r/swift/comments/1vvhh50/i_opensourced_trace_a_native_ios_network/) (Reddit)<br>
   Network Extension APIでHTTPS・WebSocket・SSEを端末上でキャプチャ

9. [三人寄ればチューリング完全](https://speakerdeck.com/puhitaku/sannin-yore-ba-churingu-kanzen) (はてなブックマーク)<br>
   Kernel/VM探検隊の発表、計算可能性の意外な構成

10. [レタスに「肉のタンパク質」を作らせることに成功](https://gigazine.net/news/20260822-meat-protein-grown-lettuce-plant/) (Gigazine)<br>
    畜産に頼らず植物に動物性タンパク質を生産させる新手法
