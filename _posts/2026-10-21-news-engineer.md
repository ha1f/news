---
layout: post
title: "CloudflareのRust製tsrsとeMudhra鍵漏えい（ソフトウェアエンジニア）"
date: 2026-10-21
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [開発]
  - [セキュリティ]
  - [セキュリティ,開発]
  - [セキュリティ,AI]
  - [AI,開発]
  - [開発]
  - [開発]
  - [開発]
  - [AI]
  - [開発]
---

Cloudflare が Rust 製の TypeScript コンパイラ「tsrs」を打ち出し、インド eMudhra の中間 CA 秘密鍵8本の漏えいで主要ブラウザが失効対応に追われた。AI まわりでは、エージェントを使った攻撃基盤の管理画面が公開されたまま見つかり、AWS と Cloudflare は業務向けプラットフォームの整備を進める。

1. [Cloudflare ら、TypeScript の Rust 移植「tsrs」を開発](https://blog.cloudflare.com/typescript-rust-port/) (Hacker News・英語)<br>
   TypeScript チーム協力の下、Oxc 傘下で育てる。初期計測は最大8倍速でメモリ7割減。

2. [eMudhra の中間 CA 8本で秘密鍵が漏えい、各ブラウザが遮断](https://emudhra.we-have-a-problem.com/) (Hacker News・英語)<br>
   署名による実証つきで10月17日に報告され、Firefox・Chrome は即日、Apple は19日に遮断した。

3. [nginx に脆弱性11件、3件は「クリティカル」評価](https://www.security-next.com/191645) (はてブ)<br>
   F5 が定例外で公表。DoS やコード実行、認証回避などにつながり得るため、利用中なら更新確認を。

4. [公開状態の AI ペンテスト基盤「Cairn」から見えた攻撃活動](https://piyolog.hatenadiary.jp/entry/2026/10/20/205855) (はてブ)<br>
   NorForge が管理画面を観測。エージェント型の攻撃がどう動くかを、公開情報から整理している。

5. [Cloudflare、業務 AI 基盤「Cloudflare OS」をマネージド提供へ](https://www.publickey1.jp/blog/26/cloudflare_osgithubgmail.html) (Publickey)<br>
   提供開始に先立ち、現在はウェイティングリストで利用希望を受け付けている。

6. [AWS Transform、Azure SDK の .NET コードを AWS 向けに変換](https://www.publickey1.jp/blog/26/aws_transformazure_functionsaws_lambdamicrosoft_azureaws.html) (Publickey)<br>
   Azure Functions から Lambda への書き換えも対象で、Azure から AWS への移行作業を自動化する。

7. [V8 の Array.prototype.fill を最大約7倍に高速化したパッチ](https://zenn.dev/dinii/articles/5b8edc7856c25b) (Zenn)<br>
   Smi と double の配列に fast path を足した実装の解説。V8 に貢献する入口としても読める。

8. [主要 OSS 23件のうち11件は、実質1〜2人が支える](https://gigazine.net/news/20261020-open-source-projects/) (GIGAZINE)<br>
   Reddit ユーザーが過去1年の履歴を調べ、スマホやブラウザ、サーバーの土台となるプロジェクトの保守体制を比べた。

9. [Mistral、音声エージェント用 SDK「Voxtral 3」を公開](https://mistral.ai/news/voxtral-3/) (Hacker News・英語)<br>
   50言語超で文字起こしから感情付き音声合成、ツール呼び出しまで通す。EU ホストか自前運用を選べる。

10. [Wine が OpenBSD Ports に追加へ、64ビット Windows アプリの実行も視野](https://gigazine.net/news/20261021-openbsd-ports-wine/) (GIGAZINE)<br>
    Ports への新規提案が出た段階で、OpenBSD 上で Windows アプリを動かせる道が開く。
