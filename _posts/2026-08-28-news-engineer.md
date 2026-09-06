---
layout: post
title: "2026年8月28日（ソフトウェアエンジニア）"
date: 2026-08-28
profile: engineer
tags: [開発, AI]
---

Cloudflareが1.1.1.1のDNSキャッシュを再設計し100TBのメモリを削減、FFmpegではバイブコーディングで書いたファザーがゼロ除算バグを発見。開発ツール・OSS・AI開発環境まわりで読み応えのある技術記事が揃った一日。

1. [Cloudflare、DNSキャッシュ最適化で100TBのメモリ削減](https://blog.cloudflare.com/dns-cache-memory-optimization-1111/) (Hacker News)<br>
   1.1.1.1のキャッシュ構造をゼロから再設計した技術詳解

2. [FFmpegのゼロ除算バグをバイブコーディングしたファザーで発見](https://code.ffmpeg.org/FFmpeg/FFmpeg/issues/24290) (Hacker News)<br>
   LLMに書かせたファザーが既存ツールの見逃していたバグを検出

3. [DuckDB 2.0プレビュー——クライアント/サーバ機能でOLAPの新領域へ](https://www.publickey1.jp/blog/26/olap_dbduckdb_20variantio.html) (Publickey)<br>
   シングルバイナリの組込みDBが分散対応に踏み出す設計の全容

4. [Rust、初の「Maintainers in Residence」を発表](https://blog.rust-lang.org/2026/08/26/announcing-our-first-maintainers-in-residence/) (Lobsters)<br>
   OSSメンテナの持続可能性に向けた新しい試み

5. [Float Bloat——ベクトルのシリアライゼーションが生むムダ](https://bonsai.io/blog/float-bloat/) (Lobsters)<br>
   float64の不要な精度がストレージと帯域を数倍に膨らませる問題

6. [SwiftからCの関数を呼び出す](https://zenn.dev/keeki/articles/705e3edf8a8ac5) (Zenn)<br>
   C interopの実装パターンとハマりどころを整理

7. [AI10並列で事故りかけた——worktreeの正しい使い方](https://zenn.dev/ceres_tech_blog/articles/8cb3ce7bc4c937) (Zenn)<br>
   並行AI開発でgitが壊れる原因と具体的な回避策

8. [anthropics/claude-plugins-officialがGitHub Trendingに浮上](https://github.com/anthropics/claude-plugins-official) (GitHub Trending)

9. [Backlogの値上げ、月1.6万→3.6万に——SNSで悲鳴](https://www.itmedia.co.jp/news/article/2608/27/2000000862/) (はてなブックマーク)<br>
   ユーザー無制限プランの大幅改定が開発チームに波紋

10. [AIを使ったナレッジ中心設計を試してみた](https://future-architect.github.io/articles/20260827b/) (はてなブックマーク)<br>
    設計判断をAIに委ねるのではなくナレッジを軸に協働する手法
