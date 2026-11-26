---
layout: post
title: "1Password に GitHub 経由の侵入、NFS に12年物の root 穴（ソフトウェアエンジニア）"
date: 2026-11-26
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
serendipity: [11]
article_tags:
  - [セキュリティ]
  - [セキュリティ]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, セキュリティ]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア]
---

1Password が社員の GitHub アカウント経由で侵入され、CI/CD まで触られていたと公表。同じ日に Linux の NFS サーバーで12年潜んだ認証前 root の穴も明らかに。守りの話が続く一方、MCP は「スキル」を運ぶ段階へ進み、Anthropic は Messages API の Rust 移行を Claude のチームに検証させた舞台裏を明かした。

1. [1Password、社員の GitHub 経由で侵入され顧客の氏名とメールが流出](https://1password.com/blog/update-on-nov-2026-security-incident) (HN・英語)<br>
   攻撃者は私有リポジトリを複製し CI/CD にも到達、保管庫の中身には触れていないと同社は説明

2. [Linux の NFS サーバーに12年潜んだ認証前 root「Nfs2root」](https://opensec.in/blog/nfs2root-cve-2026-99362) (HN・英語)<br>
   2014年の Linux 3.16 から続く穴で、tcp/2049 に1回つなぐだけで届く。修正は 6.12.117 や 7.3.2 から

3. [Anthropic、Messages API を Python から Rust へ移した検証の手順](https://www.anthropic.com/research/migrating-api-to-rust) (はてブ)<br>
   API の通信量は2024年初めから約1800倍に、旧版との差分を Claude のエージェント群が追って直した

4. [MCP に「Skills over MCP」、ツールの使い方までサーバーから配る](https://www.publickey1.jp/blog/26/mcpskills_over_mcpmcp.html) (Publickey)<br>
   スキルを必要なときだけ最新版で読み込めてコンテキストも節約、Claude の Pro 以上では既定で有効

5. [Google Workspace の MCP サーバーと CLI が正式版に](https://www.publickey1.jp/blog/26/google_workspace_mcpgoogle_workspace_cli.html) (Publickey)<br>
   Gmail や Drive など8サービス対応で無料枠は1日5000回、REST API 経由のエージェントは2027年2月までに移行を

6. [Claude Code のセキュリティ設定、2026年11月版の手引き](https://zenn.dev/happy_elements/articles/27e14ff6754044) (Zenn)<br>
   権限ルール・Bash サンドボックス・MCP 設定をチェックリスト化し、ダミーファイルでの確認手順も付く

7. [性能が出ない原因は AI ゲートウェイかもしれない](https://zenn.dev/google_cloud_jp/articles/7e29a9acf06557) (Zenn)<br>
   Google Cloud の筆者が、HTTP 200 のまま思考やキャッシュが失われる事例と見分け方を整理

8. [AWS Lambda のタイムアウト上限、8年ぶりに15分から30分へ](https://www.infoq.com/news/2026/11/aws-lambda-30-minute-timeout/) (InfoQ・英語)<br>
   全商用リージョンで申請不要・追加料金なし、同時実行数の倍増など AWS 自身が挙げる代償も読める

9. [DoorDash、配車の基盤を分散化してスループット10倍に](https://www.infoq.com/news/2026/11/doordash-dispatch-redesign/) (InfoQ・英語)<br>
   一枚岩の最適化エンジンを「調整」と「計算」に分け、ピーク時も可用性99.99%超を保った設計

10. [押したキーとショートカット名を字幕で出す Mac アプリ「Keyray」](https://zenn.dev/s3onghyun/articles/3bb9e040a61778) (Zenn)<br>
   Xcode や VS Code、JetBrains 系6種に対応する MIT ライセンスの OSS で、作者が仕組みを解説

11. [1998〜2006年の 3dfx・NVIDIA・ATI の技術デモをブラウザで再び動かす](https://gpu-demo-gallery.pages.dev/) (HN・英語)<br>
   Voodoo2 の多重テクスチャから GeForce3 世代まで、当時のカードの見せ場を触って比べられる
