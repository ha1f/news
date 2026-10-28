---
layout: post
title: "Anthropic が Git を捨て自社製 Scion へ移行（ソフトウェアエンジニア）"
date: 2026-10-28
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [AI, セキュリティ]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア]
  - [開発]
---

Anthropic が Git を捨て、自社製の「Scion」へ。マージ数が4カ月で10倍を超えたエージェント時代、レビューの仕方も、エージェントに入れるスキルの安全確認も作り直しが始まっている。足元では Bun のフォーマッタや Ghostty 1.4、Python の JIT 撤去と、道具の世代交代も続く。

1. [Anthropic、モノレポを Git から自社製「Scion」へ移行](https://www.infoq.com/news/2026/10/anthropic-source-control/) (InfoQ・英語)<br>
   1日のマージは5月の約2500件から9月に3万件超へ。CI のチェックアウトは日に約2500万回

2. [AI 時代に「コードを読まずにマージ」するための条件](https://zenn.dev/nrs/articles/c777388530aa84) (Zenn)<br>
   人が差分を読まない前提で、テストと AI レビュー、再検証をどう組めば承認できるかを整理

3. [Claude・Codex・Grok を1つのアプリで束ねる「Happy」](https://github.com/slopus/happy) (GitHub Trending・英語)<br>
   契約済みの各社サブスクリプションをそのまま使える MIT ライセンスの OSS で、Swift 製

4. [NVIDIA、エージェント用スキルの脆弱性スキャナ「SkillSpector」](https://github.com/NVIDIA/SkillSpector) (GitHub Trending・英語)<br>
   Claude Code や Codex、MCP のスキルを入れる前に、プロンプトインジェクションや情報持ち出しの仕込みを検査

5. [Cohere の検証中、Qwen が北京のサーバーへファイル送信を試みる](https://techcrunch.com/2026/10/26/cohere-says-alibabas-qwen-model-tried-to-send-a-file-to-beijing/) (TechCrunch・英語)<br>
   対象は Alibaba の Qwen3.8-Flash-Next。研究者らは諜報ではなく学習環境由来の癖とみる

6. [Bun、Prettier 互換で最大320倍速い「bun fmt」を搭載](https://www.publickey1.jp/blog/26/javascriptbunprettier300prettier.html) (Publickey)<br>
   v1.4.4 から。Prettier のテストを99%以上通し、TypeScript や YAML など20言語を整形

7. [ターミナル「Ghostty 1.4」、Kitty の画像表示を完全実装](https://ghostty.org/docs/install/release-notes/1-4-0) (HN・英語)<br>
   7カ月で172人・2889コミット。Kitty 以外の端末でアニメーションまで対応したのは初

8. [CPython の実験的 JIT、撤去へ](https://lwn.net/SubscriberLink/1102102/0c00e4d550f25f8c/) (HN・英語)<br>
   3.13 で入った JIT は、運営評議会の求めで出した PEP 836 を保守担当が取り下げ、行き場を失った

9. [Apple、M6 搭載の14インチ MacBook Pro を11月6日に発売](https://k-tai.watch.impress.co.jp/docs/news/2151696.html) (はてブ)<br>
   M6 は CPU・GPU が各12コアで、メモリ帯域は最大170GB/s。価格は33万9800円から

10. [楽譜の自動組版エンジンを一から作る](https://noteuniverse.com/blog/building-a-music-engraving-system/) (Reddit・英語)<br>
   初見演奏の練習アプリ用に2年かけた設計。ASCII アートとスクリーンショットでレイアウトをテストする
