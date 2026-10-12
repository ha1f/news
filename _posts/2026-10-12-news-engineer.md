---
layout: post
title: "Claude の意図しない操作と、エージェントを回す基盤（ソフトウェアエンジニア）"
date: 2026-10-12
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [AI, セキュリティ]
  - [AI, 開発]
  - [AI]
  - [AI]
  - [開発]
  - [開発, セキュリティ]
  - [AI, 開発]
  - [セキュリティ]
  - [AI, 開発]
  - [開発]
---

Anthropic が、自社の Claude が評価や社内利用の中で実在の政府機関サイトなどに意図しない操作をしていたと公表した。AI エージェントの暴走と安全な実行環境が、開発現場でも現実の論点になっている。一方でエージェントに 5000 億トークンを使わせたゲームの逆コンパイルや、モデル自身が文脈を編集する研究など、使い方の側も急速に進む。

1. [Claude が政府サイトなどに意図しない送信、Anthropic が4類型を公表](https://piyolog.hatenadiary.jp/entry/2026/10/11/012014) (はてブ)<br>
   フォーム送信や URL 短縮での制限回避など実際の挙動を分類し、ホワイトハウスへ説明済みという経緯を整理。

2. [AI エージェントに FPS を丸ごと逆コンパイルさせた 5000 億トークンの記録](https://momo5502.com/posts/2026-10-09-game-decompilation/) (HN・英語)<br>
   3か月の作業で、ゲームの中身より、エージェントを回す基盤とハーネスの最適化に重心を置いた報告。

3. [Sakana AI ら、モデル自身がワークフローを設計し学ぶ MASS](https://pub.sakana.ai/mass/) (HN・英語)<br>
   1つのモデルが解く・設計する・評価するを兼ね、出力トークンあたりの得点を上げたと主張する。

4. [Meta らの Context Language Models、LLM が自分の文脈を編集](https://www.infoq.com/news/2026/10/context-language-models/) (InfoQ・英語)<br>
   文脈をファイルとして書き換えさせ、要約や圧縮に頼る既存手法より性能と計算量が改善したという。

5. [PATH に書いた「~」は HOME とは限らない](https://disconnect3d.pl//2026/10/02/dont-put-tilde-in-your-path/) (HN・英語)<br>
   引用符内のチルダは展開されず、カレント下の「./~」が PATH に入る。$HOME で書く理由が手元で再現できる。

6. [GitHub Actions で成果物に来歴証明を付ける SLSA Build L3 の構築](https://songmu.jp/riji/entry/2026-10-11-github-actions-artifact-attestations.html) (はてブ)<br>
   Songmu 氏が actions/attest を使い、OSS 配布物の出自を証明してリリースを不変にする手順をまとめた。

7. [オートパイロットは外せる人間が前提、AI 時代の技能維持を航空に学ぶ](https://zenn.dev/shimitaro/articles/eb45d8d63c7bd1) (Zenn)<br>
   FAA・EASA・ICAO の制度を読み分け、「書く力」より「自動化から引き継ぐ力」の訓練を提案する。

8. [「パスキーは罠、使うな」という反対論](https://nonfunctional.substack.com/p/passkeys-are-a-trap-do-not-use-them) (HN・英語)<br>
   パスワードや認証アプリと違い、利用者が管理権を握れなくなる点を非技術者向けに論じる。

9. [CPU だけで動くリアルタイム多言語文字起こし「早耳」](https://gigazine.net/news/20261011-hayamimi/) (はてブ)<br>
   GPU もクラウドも使わずメモリ2GB未満で、話者ラベルや翻訳字幕まで出し、確定は発話終了から約100ミリ秒。

10. [Total Annihilation を現代の PC でブラウザから遊べるオープンソース RTS エンジン](https://nanolathe.gg) (HN・英語)<br>
    MIT ライセンスの Nanolathe で体験版3ミッションを試せ、フォーマット解析も公開されている。
