---
layout: post
title: "Claude Code の生みの親は「もうプロンプトを書かない」（ソフトウェアエンジニア）"
date: 2026-10-26
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス, 科学]
article_tags:
  - [開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, ビジネス]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [開発, AI]
  - [開発]
  - [開発]
  - [開発]
  - [科学]
---

Claude Code の生みの親が「もうプロンプトは書かない」と語り、Anthropic は AI 前提の開発工程を6段階にまとめた。LLM の料金は数カ月で最大8割安に。コードを書く手間が減ったぶん、レビューと設計、そして何を作るかに目が向く一日。

1. [Dan Luu「作るソフトウェアにもっと野心を」](https://danluu.com/ambitious/) (HN・英語)<br>
   Rust で Postgres を作り直す pgrust のテストが、本家 Postgres の実バグを複数掘り当てた経緯が軸

2. [Claude Code 生みの親「もうプロンプトは書かない」](https://www.itmedia.co.jp/business/articles/2610/24/news009.html) (はてブ)<br>
   Anthropic のボリス・チェルニー氏の働き方の変化を追い、トークン消費や暴走リスクといった代償にも触れる

3. [Anthropic、AI 前提の開発工程「SDLC プレイブック」](https://claude.com/ja/resources/articles/the-ai-native-sdlc-playbook) (はてブ)<br>
   コードを書く速さに周りの工程が追いつかない前提で、開発の流れを6段階に分け具体例付きで示す

4. [OpenAI と Anthropic、数カ月で LLM 料金を最大80%値下げ](https://minimaxir.com/2026/10/cheap-llms/) (HN・英語)<br>
   Max Woolf 氏が6月以降の発表を時系列に並べ、GPT-5.6 Luna の8割値下げなどの背景を探る

5. [本番の AI エージェントをアクターモデルで組む](https://www.infoq.com/presentations/actors-for-production-ai-agents/) (InfoQ・英語)<br>
   QCon AI Boston 2026 の講演。状態の持ち主や障害時の監督境界をエージェントのどこに置くかを扱う

6. [AI エージェントの多くが hCaptcha や Turnstile を通過](https://gigazine.net/news/20261026-ai-bot-detection-benchmark/) (GIGAZINE)<br>
   検出製品を作る Proof of Human が、Browser Use・Comet・Grok の3種で5方式を試した比較

7. [AI が書いたコードを読むため、Mac アプリに LSP を組み込む](https://zenn.dev/yenpodev/articles/96e7a3da3f26a4) (Zenn)<br>
   Claude Code や Codex の差分を追うレビュー用アプリで、外部の言語サーバーを安全に動かす設計の考え方

8. [Apple Silicon で CI 用の macOS VM を回す「Tart」](https://github.com/openai/tart) (GitHub Trending・英語)<br>
   Apple の Virtualization.Framework を使い、VM イメージを OCI レジストリで push/pull できる。リポジトリは openai 配下

9. [純粋関数型の Roc は C の libdeflate にどこまで迫れるか](https://www.reddit.com/r/programming/comments/1xdjru9/how_close_can_pure_fp_get_to_c/) (Reddit・英語)<br>
   Lean 製の DEFLATE 実装が届かなかった C の本命を相手に、0.1.0 前の Roc で挑んだ検証

10. [税抜と税を別々に切り捨てたら、請求の90.9%が1円不足](https://zenn.dev/shinsei99/articles/rounded-the-parts-not-the-whole) (Zenn)<br>
   親子メーターで水道光熱費を各戸に配る Swift アプリで、「端数は最後に1回」の方針がなぜ破れたか

11. [活火山の熱で海底発電、水深約1.6kmで実証](https://gigazine.net/news/20261026-underwater-volcano-energy/) (GIGAZINE)<br>
   シアトルの新興企業 Endurance Energy の試験。発電は10秒足らずでも、水中で電気を取り出せることを示した
