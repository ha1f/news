---
layout: post
title: "Rust 1.100 で never 型が安定化、GitHub Actions に供給網攻撃（ソフトウェアエンジニア）"
date: 2026-11-13
profile: engineer
tags: [AI, 開発, セキュリティ]
serendipity: [8]
article_tags:
  - [開発]
  - [AI, 開発]
  - [セキュリティ]
  - [セキュリティ]
  - [AI, 開発]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
---

Rust 1.100 で never 型がついに安定化。GitHub Actions には11月10日から3日間、悪性コミットでシークレットを抜く攻撃が広がった。エージェントに任せる範囲が広がるほど、権限の切り方と検証の仕組みが問われる一日。

1. [Rust 1.100 公開、never 型がついに安定版に](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/) (HN・英語)<br>
   安定化の試みは10年で5回失敗していた。Allocator API や Cargo の未使用依存の報告も入る

2. [Apple の Foundation Models、任意の LLM を Swift から](https://developer.apple.com/foundation-models-framework/) (HN・英語)<br>
   Apple 純正の LLM 用 Swift API が画像入力に対応し、Vision の OCR やバーコード読み取りもモデルのツールとして使える

3. [GitHub Actions に広域サプライチェーン攻撃、11/10〜12](https://blog.flatt.tech/entry/github_actions_widespread_supply_chain_attack) (はてブ)<br>
   「docs: dependency audit notes」という PR などが痕跡。GMO Flatt Security が確認手順とローテーション対象を整理

4. [PostgreSQL に22年潜んだ型混同、RCE まで到達](https://www.reddit.com/r/programming/comments/1xuk4d5/exploit_a_22_years_old_postgresql_compositetype/) (Reddit・英語)<br>
   複合型の列の型を後から変えて値を読み戻すだけで起きる。マネージド PostgreSQL の調査から見つかった CVE-2026-6460

5. [shadcn の「improve」、強いモデルが計画し安いモデルが実装](https://github.com/shadcn/improve) (GitHub Trending・英語)<br>
   コードベースを監査して実装計画だけを書き出すエージェント用スキルで、自分では一行も実装しない設計

6. [Xcode の index store を読み、呼び出し元を一発で返す CLI](https://www.reddit.com/r/swift/comments/1xtj1xr/i_built_a_cli_that_reads_xcodes_index_store_so_ai/) (Reddit・英語)<br>
   作者の実験では grep で辿るエージェントより入力トークンが約3分の1に。NotificationCenter や KVO は拾えない

7. [AI エージェントのコード劣化を測る「SlopCodeBench」](https://gigazine.net/news/20261112-slopcodebench/) (GIGAZINE)<br>
    同じコードに仕様変更を何度も重ねさせ、チェックポイントごとに動作と品質の崩れ方を追う仕組みを紹介

8. [数KBで数十億人を数える「HyperLogLog」の仕組み](https://gigazine.net/news/20261112-hyperloglog-with-coin-toss/) (GIGAZINE)<br>
    INRIA のフィリップ・フラジョレが関わり2007年に発表された推定法を、Scientific American の解説をもとにコイン投げの比喩でたどる
