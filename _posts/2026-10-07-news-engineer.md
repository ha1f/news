---
layout: post
title: "AI経由の脆弱性報告増でOpenSSHがリリース頻度を上げる（ソフトウェアエンジニア）"
date: 2026-10-07
profile: engineer
tags: [AI, 開発, セキュリティ, ビジネス]
article_tags:
  - [AI]
  - [AI]
  - [セキュリティ, AI]
  - [開発, セキュリティ]
  - [AI]
  - [AI, ビジネス]
  - [開発]
  - [開発]
---

Mistral が1兆パラメータの新モデル「Large 4」のプレビューを公開した。OpenSSH は AI 経由の脆弱性報告の急増を受けてリリース頻度を上げ、Google は gVisor を CNCF に寄贈。AI がインフラと開発の前提を動かす一方、ガートナーや安いモデルの落とし穴を示す調査が熱気に水を差す。

1. [Mistral、1兆パラメータの「Large 4」をプレビュー公開](https://mistral.ai/news/mistral-large-4/) (HN・英語)<br>
   活性パラメータは490億で、API は即日利用可能。オープンウェイトの配布は月末の予定。

2. [Google、軽量マルチモーダル埋め込み「EmbeddingGemma 2」公開](https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/) (HN・英語)<br>
   テキスト・画像・音声・動画を同じ埋め込み空間に写せる、端末上で動かす前提のオープンモデル。

3. [OpenSSH 10.6 公開、AI 経由の脆弱性報告増でリリース頻度を上げる方針](https://www.openssh.org/releasenotes.html#10.6) (HN・英語)<br>
   AI が見つけたバグを別の研究者が後から再発見する例が続いており、攻撃側も同じ穴に届くと開発チームは見ている。

4. [Google、サンドボックス型ランタイム gVisor を CNCF に寄贈](https://www.publickey1.jp/blog/26/googlegvisorcncf.html) (Publickey)<br>
   Go 製で、システムコールを仮想カーネルが処理する構造のため、通常のコンテナより隔離が強い。

5. [安いAIモデルの方が総コスト高になる利用が32％](https://gigazine.net/news/20261006-ai-cheaper-model-more-cost/) (GIGAZINE)<br>
   単価の低いモデルを選んでも、タスクによっては高性能モデルの方が最終的に安く済むという料金比較の調査。

6. [ガートナー予測、FDE 製 AI エージェントの7割は2028年までに放棄](https://www.publickey1.jp/blog/26/fdeai7fde.html) (Publickey)<br>
   ベンダー技術者が顧客に常駐して作る形態が、名ばかりのコンサルに変わる危険も指摘している。

7. [Python 3.15 は速いのか、rc3 で3.10まで遡って比較](https://blog.miguelgrinberg.com/post/how-fast-is-python-3-15) (HN・英語)<br>
   フィボナッチとバブルソートの2本を各バージョンで走らせる、毎年恒例の非公式ベンチマーク。

8. [マイクロベンチは300ミリ秒に揃えるのがよい、という経験則](https://matklad.github.io/2026/10/05/benchmark-milliseconds.html) (HN・英語)<br>
   筆者の matklad が、1〜999の整数で読める単位と反復の速さを理由に挙げる。
