---
layout: post
title: "Bun が TS 7 超えの型チェッカー、Meta は816B公開（ソフトウェアエンジニア）"
date: 2026-10-16
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [開発]
  - [AI]
  - [AI, 開発]
  - [セキュリティ, 開発]
  - [セキュリティ]
  - [AI]
  - [開発]
  - [AI, 開発]
  - [開発]
---

Anthropic 傘下の Bun が v1.4.3 で、TypeScript 7 の3倍超という型チェッカーを載せた。Meta は 816B パラメータのオープンウェイト「Muse Spark Open」を公開し、Linus Torvalds 氏は Claude Code でカーネル改善に取り組む。AI が開発の道具からインフラの中核へ入り込む一方、curl の24件の脆弱性修正や国内の連続不正アクセスなど、足元の守りも待ったなしだ。

1. [Bun、TS 7 の3倍超速い型チェッカーを搭載](https://www.publickey1.jp/blog/26/anthropicbuntypescript_73typescriptbun143.html) (Publickey)<br>
   v1.4.3 の `bun check` は TS 7.0.2 の適合性テストを全通過し、メモリ消費は2分の1以下という。

2. [Meta が816Bのオープンウェイト「Muse Spark Open」公開](https://research.meta.ai/blog/muse-spark-open) (HN・英語)<br>
   アクティブ42B・100万トークン文脈で、Mac Studio 2台のローカル実行を売りにする。

3. [トーバルズ氏、Claude Code で Linux カーネルを改修中](https://gigazine.net/news/20261016-linus-torvalds-claude-code/) (GIGAZINE)<br>
   Phoronix の報道を受けた記事で、カーネルツリー内でも AI 活用が進んでいる様子を伝える。

4. [curl 8.23.0、HTTP/2 の解放後使用を含む24件を修正](https://forest.watch.impress.co.jp/docs/news/2148495.html) (はてブ)<br>
   深刻度 High は v8.12.0〜8.22.0 に影響し、悪意あるサーバー次第で任意コード実行もありうる。

5. [JPCERT/CC、AI を使う連続不正アクセスの手口を分析](https://blogs.jpcert.or.jp/ja/2026/10/web_api_attacks.html) (はてブ)<br>
   攻撃者が APK を解析して API の SSRF を探していた痕跡を、攻撃元サーバーから確認した。

6. [Goodfire「ニューラルネットは最初から整理されている」](https://already-clean.goodfire.com/) (HN・英語)<br>
   多義性の原因を重ね合わせでなく再帰的な汎化とみなし、解釈研究の見通しは明るいと論じる。

7. [xcrun xcodeproj で .xcodeproj をCLI編集](https://zenn.dev/d_date/articles/xcrun-xcodeproj-xcode27-2) (Zenn)<br>
   Xcode 27.2 Beta 3 の全サブコマンドを実際に試し、JSON 形式のプロジェクトでの挙動と注意点をまとめる。

8. [Claude Code で非対応スキャナの Linux ドライバを動かした話](https://blogs.gnome.org/uraeus/2026/10/15/aiandreverseengineerhardware/) (HN・英語)<br>
   Windows VM で USB 通信を採取させたことで、数か月詰まった解析が数時間で初スキャンに届いた。

9. [Fortran が誕生70周年、12月に記念ワークショップ](https://fortran-lang.org/news/2026/09-15-Fortran-birthday/) (HN・英語)<br>
   初のマニュアルから70年。気候予測や核工学を支え続け、12月1日にマンチェスターで催しがある。
