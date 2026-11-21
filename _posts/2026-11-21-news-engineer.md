---
layout: post
title: "自分の重みを書き換える LLM、PostgreSQL 19 も正式リリース（ソフトウェアエンジニア）"
date: 2026-11-21
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
serendipity: [10]
article_tags:
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発, セキュリティ]
  - [開発]
  - [AI, 科学]
---

27B のモデルが自分の重みを書き換えて正答率を6.6ポイント上げた、という論文が話題の中心。AI に任せる範囲が広がる一方で、まつもとゆきひろ氏は OSS 文化の持続に危機感を示す。PostgreSQL 19 と TypeScript 7.1 も届いた週末です。

1. [LLM が自分の重みを書き換えて賢くなる、追加学習なしで](https://gigazine.net/news/20261120-large-language-model-can-rewrite-itself/) (GIGAZINE)<br>
   公開 27B モデルが勾配を使わず自ら編集し、未見の問題で6.6ポイント向上

2. [Claude Code と Codex で作る、自分の代わりに動く自律改善ハーネス](https://zenn.dev/nttdata_tech/articles/9562962cc181a1) (Zenn)<br>
   NTT データの筆者が約4か月運用した構成を、実際の MD ファイルや設定つきで紹介

3. [開発者は知らないうちにアーキテクトへ昇格していた](https://manidoraisamy.com/developer-to-architect.html) (HN・英語)<br>
   AI が書いたログ処理で歓迎画面の表示に15秒かかった実例から、設計判断の責任を説く

4. [まつもとゆきひろ氏「OSS 文化はあと10年もたないかもしれない」](https://type.jp/et/feature/32219/) (はてブ)<br>
   Ruby の生みの親が、PHP の脆弱性騒動を「明日は我が身」と語り、企業支援の難しさに触れる

5. [PostgreSQL 19 が正式リリース](https://www.postgresql.org/about/news/postgresql-19-released-3449/) (はてブ)<br>
   続報（11/16掲載）。無停止で表を再編成する REPACK (CONCURRENTLY) や pg_plan_advice 拡張が入った

6. [TypeScript 7.1 の Content Mapper で型の生成コマンドをなくす](https://zenn.dev/toiroakr/articles/typescript-content-mapper-codegen) (Zenn)<br>
   wrangler types や prisma generate のような生成手順を、型チェック側の変換で置き換える方法

7. [Uber、Go 製の翻訳キャッシュのメモリを最大9割削減](https://www.infoq.com/news/2026/11/uber-go-translation-cache/) (InfoQ・英語)<br>
   頻出の値だけメモリに置きディスクと組み合わせ、GC 負荷を減らしつつヒット率99.9%超を維持

8. [iOS アプリの個人情報を CryptoKit で暗号化するまで](https://qiita.com/naormt/items/4ee21370f85f28c28185) (Qiita)<br>
   ディップの求人アプリで、KMP と Room の構成のまま AES.GCM と鍵のキーチェーン保存を選んだ経緯

9. [Android の開発者認証、2027年1月から世界で展開](https://gigazine.net/news/20261120-android-developer-verification-expanding/) (GIGAZINE)<br>
   Google は趣味や学生向けの配信限定アカウントを用意し、共有先の上限も50台に引き上げた

10. [スコット・アーロンソン氏、Anthropic のモデルによる一般化リーマン予想の証明を論評](https://scottaaronson.blog/?p=10344) (HN・英語)<br>
   数学者アルポゲ氏が主張する証明は、Lean のコードで1740万行に及ぶという
