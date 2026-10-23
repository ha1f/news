---
layout: post
title: "Claude が OSS 100件超を形式検証、バグも発見（ソフトウェアエンジニア）"
date: 2026-10-23
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [セキュリティ, ハードウェア]
  - [セキュリティ, 開発]
  - [セキュリティ, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
---

Anthropic が Claude に OSS ライブラリ100件超のアセンブリ級の証明を書かせ、長年見つからなかったバグまで掘り当てた。AI でコードが増えた現場では、レビューの待ち時間や生産性の伸び悩みが数字で語られ始めている。一方で Node.js と GitLab はパッチ適用の期限が迫る。

1. [Claude が OSS 100件超のアセンブリ級コードを形式検証](https://www.anthropic.com/research/formal-verification) (Hacker News・英語)<br>
   Theorem との共同研究で、RISC-V 上のセキュリティ特性を証明。数兆回のテストをすり抜けたバグも出たという。

2. [AI コード増でも成果が増えない、718社調査](https://www.infoq.com/news/2026/10/jellyfish-ai-productivity/) (InfoQ・英語)<br>
   Jellyfish の分析基盤を使った Harvard の研究で、コード量は増えても完了した仕事は比例しなかった。

3. [PR 数4倍でレビューが77分に、Imprint の「small-change」](https://lethain.com/small-changes/) (Hacker News・英語)<br>
   決済系企業 Imprint では2年でレビュー中央値が33分から77分に延び、その対策として small-change を試している。

4. [Switch 2 の初のソフト脱獄「ns2jb」、最新ファームで成立](https://pepsipu.com/blog/2026-10-switch2-jailbreak-ns2jb/) (Hacker News・英語)<br>
   作者によると約2週間かけた成果で、Codex には Mario Kart World の改造を1日で書かせたという。

5. [GitLab が CVSS 10 の RCE を含む12件を緊急修正](https://gigazine.net/news/20261022-gitlab-critical-patch/) (GIGAZINE)<br>
   未認証でサーバー上のコードを実行できる欠陥が対象。19.0 から 19.5 の各系列と 18.11 に修正版がある。

6. [Node.js が脆弱性10件を修正、22.23.4・24.22.1・26.12.1](https://gigazine.net/news/20261022-node-js-security-releases/) (GIGAZINE)<br>
   深刻度は「高」が4件、「中」が3件、「低」が3件。定例のスケジュール通りの公開。

7. [Vercel Labs、Zig 製の組み込み型コーディングエージェント「fx」を公開](https://www.infoq.com/news/2026/10/vercel-zig-fx-agent/) (InfoQ・英語)<br>
   CLI にもライブラリにも WebAssembly にもなる実験的な OSS。モデル非依存という主張には疑問の声も出ている。

8. [Foundation Models と Gemini Nano、同じ機能で設計思想が正反対](https://zenn.dev/reinf0rce/articles/2c4fc900473565) (Zenn)<br>
   出欠連絡アプリの案内文生成を、iOS と Android の端末内 AI で実装して比べた個人開発の記録。

9. [Interop 2027 で注目の CSS 機能トップ10](https://gigazine.net/news/20261023-future-of-css/) (GIGAZINE)<br>
   Josh Comeau 氏がブラウザ互換性プロジェクトの対象から、これから使えるようになる CSS を10件選んで解説。

10. [地図ポリゴン370万件を489msで三角形分割、earcut より速い「earstrip」](https://globus.software/blog/2026/10/16/cutting-map-polygons/) (Hacker News・英語)<br>
    耳切り法を1工夫ずつ作り直して計測。C++ 版は earcut.hpp より14%、ブラウザ版は1.4〜2.1倍速い。
