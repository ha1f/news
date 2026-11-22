---
layout: post
title: "リーマン予想の証明を Lean コミュニティが認定、課題を任せる andon も（ソフトウェアエンジニア）"
date: 2026-11-22
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, 科学, 社会]
serendipity: [11]
article_tags:
  - [AI, 科学]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, ビジネス]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [AI, セキュリティ]
  - [開発, 社会]
---

1700万行の Lean ライブラリが一晩で検証され、Lean と Mathlib のコミュニティがリーマン予想の証明を「正しい」と認めた。手元では、エージェントに課題の実装からマージまで任せる仕組みや、エージェント用のスキル集が GitHub で伸びている。Xcode 27.3 beta に入った Copilot、GKE を止めたカーネルのバグまで、開発の現場の話も揃った。

1. [Lean コミュニティ、Anthropic のアルポゲ氏によるリーマン予想の証明を認定](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/) (HN・英語)<br>
   続報（11/21掲載）。1700万行の証明を有志が1日がかりで確かめ、定理の述べ方と証明の両方にお墨付き

2. [エージェントに課題を流し、人は判断だけ担う「andon」](https://github.com/mitaku/andon) (はてブ・英語)<br>
   台帳の課題を実装・レビュー・マージまでエージェントが進め、人を呼ぶのは本人にしか決められない場面だけ

3. [コーディングエージェントに開発手順ごと覚えさせる「Superpowers」](https://github.com/obra/superpowers) (GitHub Trending・英語)<br>
   組み合わせて使うスキル群と最初の指示文で、エージェントの進め方そのものを一つの開発手法として揃える

4. [Gemini の定額プラン、他社ハーネスでも使える方向か](https://smhn.info/202611-gemini-subscription-third-party-harness-december-2) (はてブ)<br>
   Google の Gemini 担当者が「12月2日に最初の一歩」と返信、Antigravity の不評で乗り換えが鈍い事情も

5. [Xcode 27.3 beta、iPhone Duo のヒンジを UI テストで操る XCUIHinge と Copilot](https://zenn.dev/mochiai/articles/651c873a60b958) (Zenn)<br>
   ヒンジ角度の設定はシミュレータで実際に動かして確認、組み込みの GitHub Copilot はサインイン手前まで調査

6. [アプリ本体を TEST_HOST にしたら、テストが本物の設定と API を触っていた](https://zenn.dev/yskms/articles/71556f5ca02f88) (Zenn)<br>
   メニューバーアプリ「Claude Meters」で、テストが普段使いの UserDefaults を書き換えた2つの落とし穴

7. [App Store と Google Play の審査落ちを防ぐ「app-store-compliance」](https://github.com/mjmirza/app-store-compliance) (GitHub Trending・英語)<br>
   117通りの却下例と直し方に、EU AI Act など95件の期限一覧とエージェント用スキルまで付いた提出前チェック集

8. [ランタイムも GC も無しで C# を動かす「Zero C#」](https://onurgumus.github.io/zero-csharp/index.html) (HN・英語)<br>
   bflat の派生版で、メモリはアリーナでまとめて解放、同じソースが WebAssembly や 386 の DOS でも動く

9. [Google、GKE の API タイムアウトを Linux カーネルの TCP バグまで追跡](https://www.infoq.com/news/2026/11/gke-kernel-network-bug/) (InfoQ・英語)<br>
   GKE・Private Service Connect・カーネルの3つのバグが重なり、約800人の開発者が本番デプロイできなくなった

10. [日本語のプロンプトインジェクションを見分ける小型モデルを無料公開](https://zenn.dev/jpopendata/articles/2cc6a3888fc645) (Zenn)<br>
    Japan Open Data Lab の「ja-injection-guard-v1」で、LLM に渡す前の1層目の検査として使う想定

11. [ブラジル国税庁、税額計算ツールを MIT ライセンスで GitHub に公開](https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/novembro/receita-federal-publica-primeiro-codigo-fonte-aberto-no-github-e-amplia-transparencia-da-reforma-tributaria) (HN・英語)<br>
    消費税制改革の新税を計算する仕組みで、同庁が公式にソフトウェアを公開するのはこれが初めて
