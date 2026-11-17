---
layout: post
title: "AWS が手元で動く「AWS Emulator」公開、GitHub Agentic Workflows も正式版（ソフトウェアエンジニア）"
date: 2026-11-12
profile: engineer
tags: [AI, 開発, セキュリティ]
serendipity: [9]
article_tags:
  - [開発]
  - [開発, AI]
  - [開発, AI]
  - [開発]
  - [開発, AI]
  - [開発]
  - [開発]
  - [開発]
  - [セキュリティ]
  - [開発]
---

AWS が200超のサービスを手元で再現する「AWS Emulator」を公開し、GitHub は Agentic Workflows を正式版に。エージェントにコードを書かせる前提で、検証と権限の足場づくりが一気に進んだ一日。Python の礎を築いた Tim Peters 氏の訃報も届いた。

1. [AWS、200超のサービスを手元で再現する「AWS Emulator」](https://github.com/aws/aws-emulator) (HN・英語)<br>
   アカウント不要で CI にも置け、実装とテストはすべてエージェントが担ったと Vogels CTO が明かす

2. [GitHub Agentic Workflows が正式版、Actions 上でエージェントを動かす](https://www.infoq.com/news/2026/11/github-agentic-workflows-ga/) (InfoQ・英語)<br>
   エージェントは読み取り専用で動き、書き込みは別ジョブが担う。ただし独自ジョブは保護の対象外

3. [Chrome、エージェント向けの Web 知識集「Modern Web Guidance 1.0」](https://developer.chrome.com/blog/modern-web-guidance-v1?hl=ja) (はてブ)<br>
   既存コードを走査して古い書き方の置き換え先を探す手順を追加し、各ガイドは専門家が査読

4. [Playwright v1.65、テストランナーが Bun で正式に動作](https://www.publickey1.jp/blog/26/playwrightbun.html) (Publickey)<br>
   Bun が TypeScript を変換するので Babel が不要に。Watch Mode 非対応などの差は残る

5. [過去の審査指摘を先に渡したら、Claude Code 製 iPhone アプリが一発通過](https://zenn.dev/api_iota/articles/claude-code-swift-app-store-review) (Zenn)<br>
   Web 版の紙飛行機ゲームを Swift 5,505行で書き直し、Claude Code の稼働は約1時間10分

6. [iOS アプリをインストールせずに動かすランチャー「LiveContainer」](https://github.com/LiveContainer/LiveContainer) (GitHub Trending・英語)<br>
   無料開発者アカウントの3アプリ制限を受けず、1つの App ID の中で複数のアプリを動かせる

7. [Swift.org 11月号、CocoaPods は12月2日で新規 pod の受付を終了](https://www.reddit.com/r/swift/comments/1xtnx6w/whats_new_in_swift_november_2026_edition/) (Reddit・英語)<br>
   既存のビルドはすぐには壊れないが、Swift Package Index の Verwer 氏が期日前に注意を促す

8. [夏時間で1日が25時間になる日に起きた Chromium のバグ](https://www.reddit.com/r/programming/comments/1xsvulu/a_chromium_bug_caused_by_a_25hour_day/) (Reddit・英語)<br>
   カナダなどで年1回ある25時間の日を、UTC と時差の基本から順に解きほぐす個人ブログの解説

9. [JPCERT/CC、インシデント調査報告書のチェックリストを公開](https://www.jpcert.or.jp/ir_report_checklist_20261111.html) (はてブ)<br>
   調査を外部の会社に委託した被害組織が、報告書の妥当性や収束の判断に迷わないよう GitHub で公開

10. [Zen of Python の作者 Tim Peters 氏が死去](https://discuss.python.org/t/in-memoriam-tim-peters-1952-2026/110028) (HN・英語)<br>
   7月に亡くなっていたことを Guido 氏が公表。int と float の混在演算を最初に説いた言語の共同設計者
