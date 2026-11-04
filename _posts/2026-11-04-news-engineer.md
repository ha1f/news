---
layout: post
title: "GitHubがエージェント前提へ、書き込み性能180倍（ソフトウェアエンジニア）"
date: 2026-11-04
profile: engineer
tags: [AI, 開発, デザイン, ハードウェア, 社会]
article_tags:
  - [開発, AI]
  - [AI, 開発]
  - [開発, AI]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [開発, デザイン]
  - [開発, ハードウェア]
  - [開発]
  - [ハードウェア, AI]
  - [社会]
---

5000体の AI エージェントが1つのリポジトリに毎秒7200回書き込む。GitHub Universe 2026 で示されたのは、エージェントが並列で働く前提への作り替えだった。手元では worktree 管理やデスクトップ操作の道具が伸び、Apple 側では Safari と macOS 27 に開発者が気にすべき変化が出ている。

1. [GitHub、エージェント時代に向けスループット180倍へ](https://www.publickey1.jp/blog/26/github180aigithub_universe_2026.html) (Publickey)<br>
   書き込みロックをブランチ単位に細かくし、ストレージと計算を分ける新構成で実現

2. [GitHub、複数モデルで査読する「Copilot Code Review Max」](https://www.publickey1.jp/blog/26/githubcopilot_code_review_maxgithub_universe_2026.html) (Publickey)<br>
   Lite・Balanced の上に加わる段階で、複数モデルの指摘を集約役が突き合わせる

3. [並列エージェント向けの git worktree 管理 CLI「Worktrunk」](https://github.com/max-sixty/worktrunk) (GitHub Trending・英語)<br>
   ブランチ名だけで worktree を作って移動でき、ローカル作業を自動化するフックやビルドキャッシュの複製も備える

4. [Vercel Labs、AI がデスクトップアプリを操る CLI「agent-desktop」](https://github.com/vercel-labs/agent-desktop) (GitHub Trending・英語)<br>
   画面画像でなく OS のアクセシビリティツリーを読み、要素の ref を指定して操作させる

5. [E2E テスト大全、脆さと遅さを理論から整理](https://blog.kuniwak.com/entry/e2ebok) (はてブ)<br>
   Kuniwak 氏が長年の自動化経験をまとめた長編で、グラフベースの手法や実装パターン、生成 AI へのテスト指示まで扱う

6. [Uber、リトライの連鎖障害を「エラーの持ち主」で断つ](https://gigazine.net/news/20261103-protecting-against-retry-storms/) (GIGAZINE)<br>
   サービス間で再試行が雪だるま式に増える問題に、どの層が失敗を引き受けるかを決める設計で臨んだ Uber の事例

7. [Safari 27.3 ベータ、明るいサイトを自動で暗くする「Adaptive Dark Mode」](https://webkit.org/blog/18541/introducing-adaptive-dark-mode/) (HN・英語)<br>
   color-scheme を宣言済みのサイトは変えない。ダーク利用4割に対し対応は1割という数字も

8. [macOS 27、CoreStorage の暗号化 HFS+ ボリュームが使えなくなる](https://wadetregaskis.com/macos-27-golden-gate-does-not-actually-support-corestorage-or-hfs-volumes/) (HN・英語)<br>
   Wade Tregaskis 氏の報告。マウントも APFS 変換も消去もできず、起動時の警告は「macOS 28 で非対応」と食い違う

9. [Xcode 27 で Expo アプリが起動直後に落ちる、原因は UIScene 必須化](https://zenn.dev/yskms/articles/817f8e9526aaf4) (Zenn)<br>
   iOS 27 SDK ではシーン対応のない UIKit アプリがアサートで止まる。SDK 57 のまま直す道と 58 に上げる道を比べる

10. [富士フイルム、データ保存用の磁気テープ生産を約5倍に](https://qiita.com/quotidia/items/03266d4dfecacb0dc989) (Qiita)<br>
    小田原の工場に約100億円を投じる計画で、生成 AI が生む大量データの長期保管需要を見込む

11. [ドメイン更新料が1年で6.8倍、判断の猶予は約45時間](https://anond.hatelabo.jp/20261103160506) (はてブ)<br>
    お名前.com で .cyou が「レジストリプレミアム」扱いになり、サービス維持調整費も487円から3,800円に上がった経緯
