---
layout: post
title: "AppleがMacのディスク権限を制限、Dockerはエージェント用仕様を提案（ソフトウェアエンジニア）"
date: 2026-10-04
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
---

AppleがmacOSの「フルディスクアクセス」に新たな制限を設けると発表した。背景にはAIエージェントが私的メッセージを読んだとされる騒動がある。Dockerはエージェントの権限をOCIイメージに詰める仕様をCNCFに持ち込み、現場ではレビューの自動化やリミット消費の実測が進む。モデル、IDE、OSまで、手作りの新顔も並ぶ。

1. [AppleがmacOSのフルディスクアクセスを制限へ、AIエージェントを警戒](https://techcrunch.com/2026/10/02/apple-says-its-tightening-macos-full-disk-access-controls-due-to-new-risks-from-ai-agents/) (TechCrunch・英語)<br>
   もとはバックアップ用の権限で、Metaのアプリが私的メッセージを読んだとの報道が引き金になった。

2. [DockerがエージェントのSandbox Kit仕様をCNCFへ](https://www.infoq.com/news/2026/10/docker-sandbox-ai-agent/) (InfoQ・英語)<br>
   エージェント本体と要求する接続先・認証情報・ボリュームを、1つのOCIイメージにまとめて持ち運べる仕様（Apache 2.0、v3）。

3. [AIコードレビューの「敵対的レビュー」は実務で効くのか](https://zenn.dev/edash_tech_blog/articles/4577f7d4780bef) (Zenn)<br>
   通常レビューに加え、誤動作を招く入力を探す別エージェントを走らせる手法を、自チームで回した結果と時間・token負担の話。

4. [Claude Code・Codexの週間リミットが急減する原因を調べた](https://zenn.dev/tokium_dev/articles/ai-agent-usage-limit-long-sessions) (Zenn)<br>
   一晩の長時間セッションで自動compactが何十回も走り、上限を食っていた事例から対処を探る。

5. [Aleph Alpha、78BのOSSモデル「Kolibri」を公開](https://aleph-alpha.com/en/blog/kolibri-has-landed-a-sovereign-open-weight-model/) (HN・英語)<br>
   独英対応のMoEで、有効パラメータ3B、最大1Mトークン。行政や航空宇宙向けの用途を想定し、重みはHugging Faceにある。

6. [CloudflareのPython Workersが正式サービスに](https://www.publickey1.jp/blog/26/cloudflarepython_wrokerspythonweb.html) (Publickey)<br>
   サーバレス基盤のWorkers上でPythonを動かし、DBやオブジェクトストレージも扱える。JavaScript以外の選択肢が公式になった。

7. [Go製の高速IDE「Rune」、Unstablebuildがオープンソース化](https://www.publickey1.jp/blog/26/goiderune.html) (Publickey)<br>
   GPU描画のネイティブIDEで、端末操作を中心に据え、複数のリモートノードをローカルのように扱える。

8. [AWSをローカルで再現する無料エミュレーター「MiniStack」](https://gigazine.net/news/20261003-ministack/) (GIGAZINE)<br>
   60超のサービスを単一ポートで提供し、マルチアカウント・マルチリージョンにも対応する。AWS CLIやTerraformから動作確認できる。

9. [ValveのKristófが旧世代AMD GPUをLinuxで蘇らせた仕事](https://www.phoronix.com/news/XDC-2026-Valve-Timur-AMDGPU) (HN・英語)<br>
   約10年前のGCN 1.0/1.1世代を旧Radeonドライバから現行AMDGPUへ移し、RADVでVulkanを使えるようにした経緯。

10. [Linuxバイナリも動くクラウド向けOS「FTL」](https://ftl-os.org/) (HN・英語)<br>
    OS機能を共有ライブラリとして各コンテナに載せ、カーネルはハイパーバイザー風の最小インターフェースだけを持つ設計。
