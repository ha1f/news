---
layout: post
title: "Windows 11 がコーディングエージェント名を送信、llama.cpp と Jiff は 1.0（ソフトウェアエンジニア）"
date: 2026-11-17
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
serendipity: [12]
article_tags:
  - [セキュリティ, AI]
  - [開発, AI]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [ハードウェア]
---

Windows 11 が、使っているコーディングエージェントの名前を記録して送っていた。llama.cpp と Rust の日付ライブラリ Jiff は、そろって 1.0 に到達。エージェントとの付き合い方が、OS からリポジトリの規約にまで及んできた一日。

1. [Windows 11、使ったコーディングエージェントを記録して送信](https://xusheng.dev/posts/windows-coding-agent-telemetry/) (HN・英語)<br>
   MissionControlAggregator.dll に codex.exe や claude.exe の名前があり、既定で有効な任意の診断データに載って送られる

2. [Zed、AI を使った貢献に注文、PR は同時に3本まで](https://scrapbox.io/keroxp/Zed%E3%81%AE%E3%82%B3%E3%83%B3%E3%83%88%E3%83%AA%E3%83%93%E3%83%A5%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%83%9D%E3%83%AA%E3%82%B7%E3%83%BC%E3%81%8CAI%E6%BF%80%E3%81%8A%E3%81%93%E3%81%AA%E4%BB%B6) (はてブ)<br>
   Atom の作者たちが Rust で作り直したエディタ Zed の CONTRIBUTING.md を、11/14時点の版で1節ずつ和訳して読み解く

3. [GitHub Issue に HTML と Markdown を Artifact として添付](https://zenn.dev/kesin11/articles/20261114_github_issue_artifact) (はてブ)<br>
   10月28日に Public Preview となった機能で、エージェントが gh から上げた設計案を Issue 右側のパネルで開ける

4. [llama.cpp と ggml、2023年の公開から3年半で 1.0 に](https://gigazine.net/news/20261116-llama-cpp-ggml-milestone/) (GIGAZINE)<br>
   リリースは11月13日。今後は API や ABI の互換性を壊す変更のときにメジャー番号を上げる方針

5. [Rust の日付ライブラリ「Jiff」が 1.0](https://burntsushi.net/jiff/) (HN・英語)<br>
   ripgrep の作者による発表で、uv や Cargo、Jujutsu がすでに採用し、作者は 1.0 の API を維持し続けると約束

6. [Go 1.27 のジェネリックメソッドで、列名を構造体フィールドのポインタに](https://www.reddit.com/r/programming/comments/1xwtfmr/what_go_127s_generic_methods_made_possible_for/) (Reddit・英語)<br>
   ORM「ant」の作者が GORM・Bun・ent と同じクエリを並べ、コード生成なしで型を検査する仕組みと限界を示す

7. [CNCF、Linux アプリを無改変で microVM にする「Hyperlight-Unikraft」](https://www.publickey1.jp/blog/26/vmhyperlight-unikraft.html) (Publickey)<br>
   Python や Node.js、.NET、Java などに対応し、ウォームアップ後のスナップショットから起動して立ち上がりを速める

8. [AWS「Nitro Sandboxes」、EKS の Pod ごとに専用の microVM](https://www.infoq.com/news/2026/11/aws-nitro-sandboxes-eks/) (InfoQ・英語)<br>
   Firecracker で Pod ごとにカーネルを分けられ、ECS や EC2 でも使えて追加料金はかからない

9. [Microsoft 365 の世界障害、7月の修正に潜んだロック競合が原因](https://www.itmedia.co.jp/news/article/2611/17/2000003245/) (ITmedia)<br>
   続報（11/16掲載）。負荷テストはコア数の少ない旧型機が中心で、2時間足らずでゲートウェイの8割超が止まった

10. [「圏外テスト」のつもりが、作れていたのは「応答が遅い」状態](https://zenn.dev/shinsei99/articles/offline-test-was-not-offline) (Zenn)<br>
   鍵の貸出を記録する iOS アプリで、サーバーを22秒止めても失敗しなかった理由と、二重送信を防ぐ操作 ID の設計

11. [Apple Pencil の複数筆を草稿に溜め、まとめて確定する設計](https://zenn.dev/sponge841841/articles/2026-11-08-pencil-multistroke-atomic-undo) (Zenn)<br>
   刺しゅう図案アプリで、入力中・草稿・正本の3状態を分け、Undo で中途半端な線が残らないようにした

12. [ネットも携帯網もない地域を HF 帯でつなぐ「HERMES」](https://gigazine.net/news/20261116-open-source-hf-communications-hermes/) (GIGAZINE)<br>
   非営利団体 Rhizomatica が作ったオープンソースのシステムで、短波でメールやファイルを送受信できる
