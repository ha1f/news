---
layout: post
title: "Anthropic が自前の VCS へ移行、NICT は A2B 攻撃に警告（ソフトウェアエンジニア）"
date: 2026-10-14
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
article_tags:
  - [AI]
  - [開発, AI]
  - [セキュリティ]
  - [セキュリティ, AI]
  - [セキュリティ, ハードウェア]
  - [セキュリティ, 開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [開発]
---

Google が新モデル「Gemini 4 Argon」を一般提供に移した。一方、Anthropic は1日の統合数が3万件を超えて自前のバージョン管理に移行し、NICT は公開アプリ経由でバックエンドを突く「A2B攻撃」に警告を出した。AI がコードを書く速度に、インフラも防御も追われる1日。

1. [Google、最新モデル「Gemini 4 Argon」を公開](https://deepmind.google/models/gemini/) (HN・英語)<br>
   脆弱性修正の CWE-Bench で68%の首位タイ、間接プロンプトインジェクションへの耐性も売りにする。

2. [Anthropic、git から自社製 VCS「Scion」へ移行](https://www.anthropic.com/engineering/redesigning-source-control) (HN・英語)<br>
   モノレポへの統合が5月の日2,500件から9月は3万件超に増え、5か月で乗り換えた経緯を書く。

3. [NICT、アプリ解析から裏側サーバを狙う「A2B攻撃」を公表](https://www.itmedia.co.jp/news/article/2610/13/2000002230/) (はてブ)<br>
   アプリ自体に穴がなくても、サーバ側の認可不備で漏えいする。事業者向けの点検3項目も示された。

4. [AI 攻撃エージェントに「餌」の API を踏ませてみた](https://qiita.com/kumai_yu/items/84f7eaad15426da0a5b8) (Qiita)<br>
   自社デモアプリに怪しいダミーエンドポイントを置き、OSS の Strix が何に食いつくかを観察した実験。

5. [Ledger 製ウォレットに物理的な盗聴チップ、流通は東南アジアの販売店](https://www.bleepingcomputer.com/news/security/ledger-confirms-hardware-wallet-spy-implant-behind-crypto-thefts/) (HN・英語)<br>
   正規価格の約半額で売られた改造品から暗号資産が流出。Ledger が実装を認め、販売店に出荷停止を求めた。

6. [Windows Update の証明書が2027年に失効、更新が止まる端末も](https://pc.watch.impress.co.jp/docs/news/2147744.html) (はてブ)<br>
   最新の月例更新を当てていれば原則不要。古い版は2027年5月17日か6月19日までに対応する。

7. [SvelteKit 3 が正式リリース、設定は Vite に集約](https://www.publickey1.jp/blog/26/websveltekit_3vite.html) (Publickey)<br>
   大きな新機能はなく、環境変数やエラーメッセージの整理が中心。移行スクリプトで多くは自動で直る。

8. [SwiftData の rollback() が iOS 27 で挙動変更、残高が過剰に戻る](https://zenn.dev/kzq/articles/swiftdata-rollback-ios27) (Zenn)<br>
   iOS 26.5 では通っていたテストが、save 失敗後の巻き戻しで足した分より多く引かれて落ちた。

9. [Claude Opus 5.5 に替えたら強制ツール指定が全件 HTTP 400](https://qiita.com/charge0315/items/d82ebcd11d449ee761ff) (Qiita)<br>
   判定役のモデル交換で月曜朝のAIピックが0件になりかけた話。試し打ちと比較、元に戻す手順まで書く。

10. [「Recreational Programming」、仕事でも学習でもないプログラミングの勧め](https://www.cphiri.dev/presentations/recreational-programming) (HN・英語)<br>
    燃え尽きを防ぐ内発的動機の取り戻し方を、ライブ探索型や深掘り型など遊び方の類型で整理した発表資料。
