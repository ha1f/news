---
layout: post
title: "公式 Claude Code 拡張に SSH バックドア発覚（ソフトウェアエンジニア）"
date: 2026-10-31
profile: engineer
tags: [AI, 開発, セキュリティ, 科学]
serendipity: [11]
article_tags:
  - [セキュリティ, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [セキュリティ, 開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [科学]
---

Cursor Marketplace に並んだ公式 Claude Code 拡張 2.1.313 に、SSH バックドアが仕込まれていた。エディタ拡張という「開発者の手元」が狙われた一日。一方で curl が9か月だけチューリング完全だった話や、NES を LLM の重みに焼き込む試みなど、手を動かす人の遊び心も光る。

1. [Cursor Marketplace の公式 Claude Code 拡張にバックドア](https://phorion.io/blog/offical-claude-code-vsx-compromise/) (HN・英語)<br>
   該当は 2.1.313 で、macOS・Linux・Windows に常駐する SSH 侵入口を設置。npm と VS Code 側の同版も取り下げ済み

2. [AI 時代の開発者体験、週10時間以上の時短は68%から26%へ](https://www.infoq.com/news/2026/10/atlassian-devex-2026/) (InfoQ・英語)<br>
   Atlassian の年次調査で、AI 以前より摩擦が減ったと答えた開発者は28%どまりという結果

3. [楽楽請求の開発チーム、ERROR ログ1行から障害の初動を整える Claude Code スキル](https://tech-blog.rakus.co.jp/entry/20261030/errorlog) (はてブ)<br>
   Grafana のアラート起点で、既知か新規かの判定から障害対応シートの複製・記入までを gws CLI で自動化した設計

4. [個人情報を自社の DB に持たない設計は、どこまでできるか](https://tech.every.tv/entry/2026/10/30/124255) (はてブ)<br>
   every が IDaaS や決済代行に任せた場合を検討、DB に残る sub も自社では個人情報になりうると指摘

5. [Swift 6.4 の Span や InlineArray、使うには macOS 26 以上が必要](https://www.reddit.com/r/swift/comments/1xjacvb/upgrading_to_swift_64_the_stdlib_gate/) (Reddit・英語)<br>
   標準ライブラリが OS 同梱のため、Windows や Linux では使えるのに Mac だけ古い機種を切る羽目になった開発者の報告

6. [SwiftUI の図形エディタで、ドラッグ吸着とズーム・Undo を両立する設計](https://zenn.dev/sponge841841/articles/2026-10-18-swiftui-snap-drag-undo) (Zenn)<br>
   図面の mm 座標と画面上の距離を分け、操作を確定する時点を決めて吸着先の飛びや Undo の残骸を防ぐ

7. [macOS の「ローカルネットワーク許可」ダイアログを自動で断る「dontallow」](https://github.com/johncassil/dontallow) (HN・英語)<br>
   Chromium 系ブラウザは起動ごとに一時フォルダへ自分をコピーするため選択が記憶されない、という原因の解説つき。本体は Swift 2ファイル

8. [AT Protocol で動く、連合型のコードフォージ「Tangled」](https://tangled.org/blog/forge/) (HN・英語)<br>
   Git ホスティングや CI ランナーだけ自前で持つこともでき、他サーバーの利用者ともそのまま共同作業できる構成

9. [curl の設定ファイル、9か月間だけチューリング完全だった](https://www.reddit.com/r/programming/comments/1xjiofl/how_curl_was_accidentally_turingcomplete_for_nine/) (Reddit・英語)<br>
   8.12〜8.16 の変数切り出しと設定の入れ子読み込みで2カウンタ機械を再現、8.17.0 の5段上限で塞がれた

10. [学習なしで Qwen3.5 の重みに NES の CPU を焼き込んだ「nesformer」](https://github.com/dbreunig/nesformer) (HN・英語)<br>
    コンパイラが全重みを計算し、Gated DeltaNet の状態をメモリに使ってスーパーマリオのワールド1-1が動く

11. [摂食障害が増加、GLP-1 薬が拍車をかける懸念](https://www.technologyreview.com/2026/10/30/1147838/eating-disorders-rise-glp-1s-weight-loss-drugs/) (MIT TR・英語/一部会員限定)<br>
    拒食症と過食症の世界の発症数は1990〜2023年で71%増えたという報告を起点に、臨床心理士が新薬のリスクを語る
