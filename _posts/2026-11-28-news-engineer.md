---
layout: post
title: "TCP 通信だけで Linux が止まる「TCPanic」、修正は 7.3.4 に（ソフトウェアエンジニア）"
date: 2026-11-28
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
serendipity: [11]
article_tags:
  - [セキュリティ]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [AI, 開発]
  - [セキュリティ, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [科学]
---

外から TCP 通信を送るだけで Linux ホストが止まる「TCPanic」が明らかに。証明支援系の健全性バグを集めた一覧も出て、「機械が確かめた」をどこまで信じるかが問われる一日。Netflix や価格.com の大規模コード改修の事例、Swift の実装記事も並ぶ。

1. [Linux カーネルに「TCPanic」、TCP 通信だけでホストが停止](https://ikotaslabs.com/news/2026-11-27) (はてブ)<br>
   Ikotas Labs が独自に見つけた CVE-2026-99288 で、認証不要のまま IPv4・IPv6 の両方に影響し、修正は Linux 7.3.4 に入った

2. [「機械が検査した証明」も間違う、証明支援系の健全性バグ一覧](https://cr.yp.to/proofs/falseccp.html) (HN・英語)<br>
   暗号学者のバーンスタイン氏が各検証器のバグ報告を件数順に並べ、400行しかない HOL Light のカーネルでもレビューの深さは測れないと説く

3. [Netflix、ライブラリの API 変更が誰に響くかを測る「Quasar」](https://www.infoq.com/news/2026/11/netflix-quasar-api-impact/) (InfoQ・英語)<br>
   依存グラフや文字列検索では漏れる継承・オーバーロード経由の呼び出しまで、SCIP の索引でリポジトリ横断に洗い出す仕組み

4. [価格.com、960万行の C# と Classic ASP を AI で全面刷新した半年](https://speakerdeck.com/tkyowa/kakaku-com-ai-driven-system-renewal-202611) (はてブ)<br>
   カカクコムの CTO らが、工程を固めたワークフロー型と自律エージェント型を品質・時間・費用で比べた結果をアーキテクチャConference で報告

5. [エージェント向けに検索とスクレイピングをまとめる「Firecrawl」](https://github.com/firecrawl/firecrawl) (GitHub Trending・英語)<br>
   550を超えるデータ提供元に1つの API でアクセスできる OSS で、LLM に渡すウェブの知識を集める基盤として伸びている

6. [パスキーは正しく実装してこそ強い、iOS とサーバーを Swift で](https://zenn.dev/kantacky/articles/b5a03eab70c7b1) (Zenn)<br>
   SMS の2段階認証も破るリアルタイムフィッシングへの備えとして、AuthenticationServices と Server-Side Swift の両側の実装例を載せる

7. [zip で配られる SDK を SPM で管理する3つの入れ方](https://zenn.dev/mochiai/articles/330ad178e4fc5e) (Zenn)<br>
   URL と checksum で取り寄せる binaryTarget、手元の XCFramework、ローカルパッケージで包む方法を、自作フレームワークで試した記録

8. [SwiftUI の Canvas で折り返した文字が重なる、行を自分で分けて解決](https://qiita.com/d_aiba1/items/c049b68bc2934b52fb0f) (Qiita)<br>
   音響アプリ「チェックワンツー」の作者が、審査前の AI のコード点検で見つかった重なりを draw(_:at:anchor:) で下から積んで直した手順

9. [Mac のメニューバーのアイコンを隠す軽量ツール「Hidden」](https://github.com/consolelabs/hidden) (GitHub Trending・英語)<br>
   メニューバーに並ぶアイコンを隠して表示を整理する Swift 製の OSS で、GitHub の Swift 日次トレンドに入った

10. [Vim の教本を4年かけて書き上げた、練習問題は170問](http://themouseless.dev/vim/) (HN・英語)<br>
    25年コードを書いてきた著者が、マウスに頼らず手を鍵盤に置いたまま編集する技を段階的に教える電子書籍で、紙版も近く出る

11. [小惑星を逸らした DART の衝突現場、欧州の Hera が初めて撮影](https://arstechnica.com/space/2026/11/europes-hera-mission-returns-to-the-chaotic-scene-of-a-cosmic-smashup/) (HN・英語)<br>
    2022年の NASA の体当たりで衛星 Dimorphos の公転が33分縮んだ現場を、ESA の探査機が4年後に訪れて見た「大混乱」の様子
