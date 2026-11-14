---
layout: post
title: "Claude Code のサンドボックス確認が既定に、OpenAI は Codex Security 公開（ソフトウェアエンジニア）"
date: 2026-11-14
profile: engineer
tags: [AI, 開発, セキュリティ, デザイン, ハードウェア, 科学]
serendipity: [11]
article_tags:
  - [AI, 開発]
  - [AI, セキュリティ]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [デザイン]
  - [ハードウェア]
  - [科学]
---

Claude Code v2.1.325 で、サンドボックス内の Bash が既定で許可確認を求めるように変わった。無人で回している CI は設定を見直したい。ほかに、OpenAI の脆弱性スキャン CLI、Google によるエージェント障害の診断、Stripe が2500万行の Ruby を一晩で整形した話と、開発の足回りの話題が並ぶ一日。

1. [Claude Code v2.1.325、サンドボックスと無人実行の確認を強化](https://qiita.com/picnic/items/9c8095450eb2b79ac3d8) (Qiita)<br>
   /loop やスケジュールタスクでもスキル実行前に確認が入るようになり、無人運用が止まりうる。permissions.allow の見直し点を整理

2. [OpenAI、脆弱性を探して直す「Codex Security」の CLI と SDK を公開](https://github.com/openai/codex-security) (GitHub Trending・英語)<br>
   リポジトリや Git の差分をスキャンし、修正パッチを作って結果を Linear・Jira・GitHub に起票する。SARIF 出力と GitHub Action も用意されている

3. [Google、本番 AI エージェントの失敗を診断する「AQuA」をオープンソース化](https://www.infoq.com/news/2026/11/google-ambient-agent-prod/) (InfoQ・英語)<br>
   失敗パターンをデプロイ時点のソースと照らし合わせる。32セッションの再生では、座席指定の手順飛ばしが15件から2件に減った

4. [Stripe、2500万行の Ruby を一晩で自動整形した「rubyfmt」の舞台裏](https://www.reddit.com/r/programming/comments/1xv8oe9/formatting_an_entire_25_million_line_codebase/) (Reddit・英語)<br>
   Rust 製で設定不要のフォーマッターを個人 OSS から始め、6年がかりで世界最大級の Ruby コードベースに展開した経緯

5. [Cloudflare、実運用例のない合意アルゴリズム「QuePaxa」を選んだ理由](https://www.reddit.com/r/programming/comments/1xuv4ux/how_cloudflare_uses_quepaxaa_leaderless/) (Reddit・英語)<br>
   リーダーが遅れると全体が詰まる Raft や Paxos を避け、制御プレーン用の合意サービス「Meerkat」をリーダーなしの方式で組んでいる

6. [FreeBSD の bhyve、仮想マシンのライブマイグレーションが動き始めた](https://gyptazy.com/blog/freebsd-bhyve-live-migration-support-rfc/) (HN・英語)<br>
   FreeBSD 15.1 で、カーネルの vmm にダーティページ追跡を足して実装した。TCP で別ホストへ移し、止まるのは最後のコピーの間だけ

7. [Microsoft、Sysinternals の「Process Explorer」を Mac 向けに公開](https://github.com/microsoft/Procexp-Mac) (GitHub Trending・英語)<br>
   Swift・SwiftUI・AppKit で書かれたネイティブアプリ。プロセスツリーやスレッドに加え、macOS ならではのコード署名も調べられる

8. [DuckDB を Swift らしく使う「Duck」が1.0に](https://www.reddit.com/r/swift/comments/1xuswu5/i_built_duck_a_swiftnative_layer_over_duckdb_for/) (Reddit・英語)<br>
   中身は DuckDB 2.0 エンジンで、iOS 15・macOS 12 から使える。Codable のモデル、マイグレーション、SwiftUI に反映されるクエリまで揃う

9. [閉じた iPhone Duo の「右端84pt」に、各アプリはどう対応しているか](https://zenn.dev/mochiai/articles/5551e6a3d8555e) (Zenn)<br>
   外側画面は 466×678pt と横に広い。ステータスバーやタブバーが縦に並ぶ右端の列を、各アプリがどう扱っているかを比べている

10. [Coway の空気清浄機を解析し、クラウドなしで Apple Home につないだ](https://scottjg.com/posts/2026-11-11-reverse-engineering-my-coway-air-purifier-to-ditch-the-cloud/) (HN・英語)<br>
   就寝時の「おやすみ」ボタンで照明を消し、同時にファンをホワイトノイズの強さまで上げたい、という家庭の事情から始まった解析記

11. [AI がゲーデルのノートを読み解く、数百の証明済み定理が眠っていたか](https://www.theguardian.com/science/2026/nov/13/kurt-godel-notebooks-ai-helps-unlock-hidden-discoveries-man-who-transformed-maths) (HN・英語)<br>
   1940年代初めの16冊・1009ページは、当時すでに廃れていたドイツ語速記で書かれていた。ヘルシンキ大学が2017年から解読を進めている
