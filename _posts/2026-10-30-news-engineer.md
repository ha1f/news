---
layout: post
title: "Mistral Large 4 の重み公開、Copilot は Rust 基盤に（ソフトウェアエンジニア）"
date: 2026-10-30
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
article_tags:
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発, セキュリティ]
  - [セキュリティ, AI]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [科学]
---

Mistral が1兆パラメータの「Mistral Large 4」の重みを公開し、Microsoft は Copilot の実行基盤を Rust で作り直して全社共通に。Linux カーネルでは、AI が書いたエクスプロイトが CVSS 9.8 の穴を突いた。AI が書き、AI が見張る開発の足元を点検する一日。

1. [Mistral、1兆パラメータの「Mistral Large 4」の重みを公開](https://mistral.ai/news/mistral-large-4-oss/) (HN・英語)<br>
   今月出したプレビュー版を強化学習で鍛え直した版で、推論の深さを3段階から選べる

2. [Microsoft、Copilot の実行基盤を全社共通化した「Copilot harness」](https://forest.watch.impress.co.jp/docs/news/2152248.html) (はてブ)<br>
   ランタイムを Rust に移し、20超のモデルと持ち込みの API キーに対応。Foundry でプレビュー提供

3. [Anthropic「Claude Code の全体像は誰も把握しなくていい」、実務家が検証](https://www.infoq.com/news/2026/10/anthropic-code-review/) (InfoQ・英語)<br>
   コードの約9割を Claude が書く同チームのレビュー体制と、まだ持てていない歯止めの話まで追う

4. [Claude Code で「AI の QA チーム」を1か月回した結果](https://zenn.dev/sre_holdings/articles/d4acb079680a79) (Zenn)<br>
   SREホールディングスが社内の業務 SaaS で試し、懐疑役の検証エージェントで AI の誤指摘をふるい落とした

5. [GitHub Actions の「@v7」指定をやめて actions.lock へ](https://zenn.dev/progate/articles/24b1140180300c) (Zenn)<br>
   3月の trivy-action 事件ではタグが force push で差し替えられ、パッチ番号まで固定しても防げなかった

6. [Linux カーネルの TCP に CVSS 9.8 の欠陥、Ubuntu・RHEL は未修正](https://www.reddit.com/r/programming/comments/1xiq8we/linux_kernel_tcp_flaw_with_98_cvss_score_affects/) (Reddit・英語)<br>
   Anthropic の AI がエクスプロイトを書き、MPTCP を待ち受けるサーバーで root 権限を奪えたと報告

7. [ElementaryUI、SwiftUI 風に書いてブラウザで動く Swift](https://elementary.codes) (HN・英語)<br>
   Embedded Swift で WebAssembly の出力を kB 単位に抑え、開発サーバーには Vite を使う

8. [llama.cpp の ggml-org、ローカル LLM を動かす Mac アプリ「Llama」](https://github.com/ggml-org/Llama-macOS) (GitHub Trending・英語)<br>
   Swift 製のメニューバー常駐アプリで、llama.cpp を抱える開発元自身が GUI まで手がけた

9. [サンドボックスの Mac アプリで、権限なしに他アプリのウインドウを動かす](https://qiita.com/bednarekpawell/items/7cc5cc4ceb58e1be1405) (Qiita)<br>
   個人開発の「Panebird」が、App Intents で作った操作をショートカット経由で呼んで移動させる方式

10. [気候モデルが見落とす、温暖化が温暖化を呼ぶ連鎖](https://www.technologyreview.com/2026/10/29/1147735/climate-models-blind-spot/) (MIT TR・英語/一部会員限定)<br>
   永久凍土や山火事などからの排出だけで、今世紀の気温上昇に0.2〜0.4℃が上乗せされうるとの9月の研究を紹介
