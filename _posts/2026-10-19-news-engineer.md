---
layout: post
title: "Broadcom製WiFiの脆弱性とDeepSeekの検索API公開（ソフトウェアエンジニア）"
date: 2026-10-19
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [セキュリティ, ハードウェア]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア]
---

Broadcom 製 WiFi 実装の 2010 年からの脆弱性が、数百万台のルーターで放置されたまま公表された。一方で DeepSeek は検索・取得 API を投入し、エージェントの足回りを固める動きが続く。AI に任せる開発の測り方と節約術、LLM が苦手な言語の実験、80 年代チップの解剖まで、手を動かす話が並ぶ。

1. [Broadcom 製 WiFi の脆弱性、数百万台のルーターが「永遠のバグ」に](https://quentinkaiser.be/security/2026/10/16/one-parser-two-bugs/) (HN・英語)<br>
   WPS の実装バグが 2018 年の不完全なパッチ後も残り、CVE も付かないまま。エージェントでの発見経緯と悪用手順を解説

2. [DeepSeek、検索と Web 取得の API を提供開始](https://api-docs.deepseek.com/guides/search/) (HN・英語)<br>
   自社検索エンジンが基盤で、取得ページは Markdown で返る。エンドポイントは 2 本、認証は既存 API キーと共通

3. [Grafana が AI エージェントに SLO とエラーバジェットを適用](https://www.infoq.com/news/2026/10/grafana-slo-ai-agent/) (InfoQ・英語)<br>
   エージェントが「うまく動いているか」を信頼性工学の物差しで測る提案

4. [iOS シミュレーターの画面を画像で読ませるのをやめ、Claude のコンテキストを 43% 削減](https://zenn.dev/eai/articles/dont-let-agents-see-the-ios-sim-screen) (Zenn)<br>
   セッションログ 99 件の集計から無駄を洗い出し、画面を文字で読む道具を足した実測記録

5. [LLM に使えないことを狙った言語「KillSwitch」を作って各モデルで検証](https://blog.picheta.me/post/killswitch-lang/) (HN・英語)<br>
   仕様書に紛れた嘘や文字数を数える規則で、コード生成が暗記頼みかを試した

6. [Valen の借用チェッカーは関数を逆向きに歩く](https://verdagon.dev/blog/reverse-borrow-checking) (HN・英語)<br>
   最適化では定番の逆順走査を、メモリ安全性の検査に持ち込む発想の内側を解説

7. [Free Pascal と Lazarus が動的パッケージに対応](https://www.getlazarus.org/dynamic/) (HN・英語)<br>
   IDE を再ビルドせずに部品を入れられ、自作プログラムのプラグイン機構にも使える

8. [Microsoft、.NET のツールチェーン管理ツール「dotnetup」をプレビュー公開](https://www.publickey1.jp/blog/26/netdotnetupnet.html) (Publickey)<br>
   CLI・コンパイラ・ランタイムをまとめて入れ、複数バージョンを切り替えられる

9. [Intel 8087 の浮動小数点の加減算を、マイクロコードと回路から読み解く](https://www.righto.com/2026/10/8087-addition-subtraction-microcode.html) (HN・英語)<br>
   1648 命令のマイクロコードと 80 ビット演算回路が、無限大などの特殊値をどう扱うか
