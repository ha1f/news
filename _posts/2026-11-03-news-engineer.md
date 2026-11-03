---
layout: post
title: "GPT-6 Astra、Qwenの重み0.016%で正答率6倍に（ソフトウェアエンジニア）"
date: 2026-11-03
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア, 社会]
article_tags:
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発, AI]
  - [開発]
  - [開発]
  - [セキュリティ, 開発]
  - [開発, 社会]
  - [ハードウェア, AI]
---

MIT CSAIL の実験で、GPT-6 Astra が Qwen の重みをわずか0.016%書き換えただけで、数学ベンチマークの正答率が7.9%から48.1%に跳ね上がった。Uber は800超の MCP サーバーを1つのゲートウェイにまとめ、Hono は「AI にとって使いやすいフレームワークか」を測り始めた。エージェントが道具を使うだけでなく、道具の形まで変えつつある。

1. [LLM がニューラルネットの重みを直接読み書き、MIT CSAIL の実験](https://rikiyat.github.io/blog/weight-space-programming/) (HN・英語)<br>
   GPT-6 Astra が勾配を使わずに Qwen3.5-0.8B の重みを編集し、推論ループの原因を直して MATH-500 を大きく伸ばした

2. [Hono の作者、AI 向けの開発者体験「Agent DX」を測る](https://zenn.dev/yusukebe/articles/3d3dc6605ca1b1) (Zenn)<br>
   エージェントにアプリを作らせ、採点は LLM ではなくテストと静的解析で行う。指示なしで Hono を選ぶかも検証

3. [Uber、800超の MCP サーバーを束ねるゲートウェイを構築](https://www.infoq.com/news/2026/11/uber-mcp-gateway-ai-agents/) (InfoQ・英語)<br>
   登録を担うレジストリと実行を担うプロキシを分け、既存 API を改修せずに5000超のツールとして公開する

4. [手元の Claude Code や Codex をスマホから操る「T3 Code」](https://github.com/pingdotgg/t3code) (GitHub Trending・英語)<br>
   iOS・Android・Web・デスクトップの各版があり、Cursor や Grok Build など7種のエージェント CLI をそのまま使える

5. [project.pbxproj のコンフリクトを Tuist で構造的になくす](https://zenn.dev/digitalio/articles/eliminate-pbxproj-conflicts) (Zenn)<br>
   ECナビのアプリチームが XcodeGen・Bazel と比べ、型で定義ミスを防げて CocoaPods と併用できる点で選んだ

6. [Mac の検索アプリ「AnswerSearch」がオープンソースに](https://www.reddit.com/r/swift/comments/1xmajfe/answersearch_is_opensourced/) (Reddit・英語)<br>
   Mac App Store で配布中の個人開発アプリで、クラウドを呼ぶかどうかの判断を端末内の Foundation Model に任せる作り

7. [ブラウザで Java を動かす CheerpJ 5.0、Java 21と25に対応](https://www.reddit.com/r/programming/comments/1xlutld/cheerpj_50_java_2125_in_the_browser_full_openjdk/) (Reddit・英語)<br>
   Leaning Technologies の WebAssembly 版 OpenJDK で、JRE でなく JDK 一式を同梱し、ブラウザ内でコンパイルまでできる

8. [27アーキテクチャの Linux システムコール表「syscall.sh」](https://syscall.sh/) (HN・英語)<br>
   x86_64 から RISC-V、SuperH まで、番号・引数・レジスタを Linux 3.3〜7.3 の範囲で引ける。API も更新

9. [Ubuntu、CVSS 9.8 のカーネル欠陥を2週間以上未修正](https://chalmovsky.com/posts/wtf-ubuntu) (HN・英語)<br>
   続報（10/30掲載）。Debian は10月16日に修正済みだが、Ubuntu は 22.04〜26.04 の LTS がいまも「Vulnerable」のまま

10. [日本の全法令を git の履歴にした「houritsu」](https://zenn.dev/koheiwada/articles/houritsu-japanese-laws-as-git) (Zenn)<br>
    e-Gov の8982法令を、改正法の施行1件につき1コミットで記録。git diff で条文のどこが変わったかが見える

11. [声を出さずにパソコンと話すメガネ「Subvocal」](https://news.ycombinator.com/item?id=50340088) (HN・英語)<br>
    YC 採択のスタートアップで、ジョージア工科大の元学生2人が開発。電波で口の中の動きを捉え、唇を閉じたまま言葉を形づくるだけで文字に変換する
