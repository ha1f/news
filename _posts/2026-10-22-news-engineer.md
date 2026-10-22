---
layout: post
title: "PHPにRCE脆弱性2件、LiteLLMにもバックドア（ソフトウェアエンジニア）"
date: 2026-10-22
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [セキュリティ, 開発]
  - [セキュリティ, 開発]
  - [開発]
  - [AI]
  - [AI, 開発]
  - [セキュリティ, 開発]
  - [開発]
  - [AI]
  - [開発]
---

PHP に認証なしでサーバー上のコードを実行されかねない重大な脆弱性が2件見つかり、PHP 8.5.12 など4系統の修正版が出た。同じ日、PyPI 上の LiteLLM 1.107.0 に認証情報を盗むバックドアが混入していたことも判明。一方で DuckDB 2.0 LTS や Chrome 156 など、足場になるツールの大型更新も重なった。

1. [PHP に深刻な RCE 脆弱性2件、修正版を公開](https://thephp.foundation/blog/2026/10/21/todays-php-security-release-and-how-were-strengthening-php-security/) (Hacker News・英語)<br>
   メモリ上限に達した瞬間の状態破壊が原因で、Apache の mod_php では認証前に突かれる。PHP Foundation が発見から修正までの経緯と体制強化を説明。

2. [PyPI の LiteLLM 1.107.0 に認証情報窃取のバックドア](https://safedep.io/litellm-pypi-compromise-credential-stealer-backdoor/) (Hacker News・英語)<br>
   .pth 経由で Python の起動ごとに実行され、litellm を import しない環境でも動く。1.106.2 は無事で、PyPI からは削除済み。

3. [DuckDB 2.0.0 LTS 公開、VARIANT 型やトリガーを搭載](https://duckdb.org/2026/10/21/announcing-duckdb-200) (Hacker News・英語)<br>
   1.5 から約2万コミットを経た初のメジャー更新で、非同期 I/O や agent mode も加わる。移行時の破壊的変更の章もある。

4. [Anthropic が個人向けエージェント「Claude Duet」を発表](https://claude.com/product/claude-duet) (Hacker News・英語)<br>
   メールや予定を見張り、朝にまとめを出して、判断が要る場面だけ知らせる。Opus 5.5 で動き、米国の Pro・Max 向けリサーチプレビュー。

5. [claude -p を cron で回すと「ok」だけで4万トークン](https://zenn.dev/yosiki/articles/claude-p-cron-token-diet) (Zenn)<br>
   --safe-mode と --tools "" などの組み合わせを実測し、1回あたり39,968から737トークンまで落とした記録。

6. [GitHub CLI、期限付きで自動更新される OAuth トークンを試験提供](https://github.blog/changelog/2026-10-21-github-cli-opt-in-to-expiring-auto-refreshing-oauth-tokens/) (はてブ)<br>
   v2.103.0 の gh auth login --expiring で有効化。トークンが漏れても数時間で失効し、git 連携には gh auth setup-git を勧める。

7. [Google Chrome 156 安定版、CSS だけで乱数が使える](https://gigazine.net/news/20261021-google-chrome-156/) (GIGAZINE)<br>
   IndexedDB の内部実装が SQLite ベースになった点と、モジュール読み込み失敗時の再試行が入った点も、実装者には見逃せない変更。

8. [同じ層を回すモデル「Looped Transformer」入門](https://zenn.dev/acrosstudioblog/articles/895e38a8893223) (Zenn)<br>
   層を足さず共有重みを繰り返して使う仕組みを、推論時のループ回数と計算量の関係で解説。節約できるものと残るコストの整理が軸。

9. [Windows 11 に残る Windows 95 時代のヒープ管理](https://www.windowslatest.com/2026/10/19/why-windows-11-still-ships-with-windows-95s-memory-manager-hidden-inside-i) (Hacker News・英語)<br>
   古いアプリ向けに再コンパイルされた EmulateHeap を、Raymond Chen の解説で追う。自分の環境で見つける手順つき。
