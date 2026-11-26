---
layout: post
title: "OpenJDK に認証不要の RCE「Java4Shell」、GPT-6.2 も公開（ソフトウェアエンジニア）"
date: 2026-11-18
profile: engineer
tags: [AI, 開発, セキュリティ, 社会]
serendipity: [11]
article_tags:
  - [開発, セキュリティ]
  - [セキュリティ]
  - [AI]
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [社会]
---

OpenJDK の Base64 デコーダに、認証なしでリモートからコードを実行できる脆弱性「Java4Shell」。同じ日に OpenAI の GPT-6.2 と Microsoft の MAI Code 2 が出て、コーディング向けモデルの値下げ競争が進んだ。モデルを替えるならハーネスも選び直せ、という2.7万回の比較も届いている。

1. [OpenJDK の Base64 デコーダに認証不要の RCE「Java4Shell」](https://calif.io/java4shell/) (HN・英語)<br>
   発見者は Calif。高速化のために x86-64 命令で書いた処理に欠陥があり、細工した入力で隣のメモリを上書きできる。CVSS 4.0 では9.2

2. [楽天証券、テスト環境から最大1125万口座の情報が漏えいか](https://www.itmedia.co.jp/news/article/2611/17/2000003275/) (ITmedia)<br>
   検知は16日だが、流出の恐れは11日のテスト環境から。447万口座分は年収や出金先口座の情報まで含む

3. [OpenAI、「GPT-6.2」の Astra と Sol を公開](https://www.itmedia.co.jp/news/article/2611/18/2000003279/) (ITmedia)<br>
   API は Astra が100万トークンあたり入力8ドル・出力40ドルと2割下げ、Sol はコード変更の評価で Astra に0.5ポイント差まで迫る

4. [Microsoft、コーディング専用モデル「MAI Code 2」と Flash を発表](https://www.publickey1.jp/blog/26/aimai_code_2mai_code_2_flash.html) (Publickey)<br>
   Ignite 2026 での発表。Microsoft の比較では Claude Opus 5.5 に対して性能96%、コストは5%

5. [RUNTA、22のハーネスを5モデルで2.7万回走らせて比較](https://runta.com/blog/introducing-frontierharness-eval-v1-1/) (HN・英語)<br>
   最も得なハーネスはモデルごとに違い、Codex CLI はタスク単価の順位が GLM-5.3 で1位、Kimi-K3 では16位

6. [mizchi 氏「Mutation Test をやれ」、AI 時代のテスト品質の測り方](https://zenn.dev/mizchi/articles/mutation-test-quality) (はてブ)<br>
   分岐カバレッジは85%あたりで効き目が鈍るという経験則から、コードをわざと壊して検出できるかを見る自作ツール mutator を勧める

7. [Rust 製リンター Oxlint、型を使う lint に Rust 版 TypeScript「tsrs」](https://oxc.rs/blog/2026-11-17-faster-type-aware-linting-with-tsrs) (はてブ・英語)<br>
   型検査と lint を1回の解析で済ませ、typescript-eslint と tsc を別々に回すより最大122倍速いと Oxc は計測

8. [Shopify、AI エージェントにアプリを作らせるリモート環境「Remote Dev」](https://www.infoq.com/news/2026/11/shopify-remote-ai-dev/) (InfoQ・英語)<br>
   エージェントを3〜4本並べるとノート PC が限界、蓋を閉じれば作業も止まる、という社内の困りごとから iOS と Android 向けに作った

9. [翻訳字幕で「right?」が「右」に、原因は句読点を削るキャッシュ](https://zenn.dev/yui/articles/8f2454253c848b) (Zenn)<br>
   Mac の字幕翻訳アプリ Wakaru の作者が報告。Apple のオンデバイス翻訳では「Nice」がニース、「Nice.」が「いいね。」と句読点で訳が変わる

10. [macOS で「ビットパーフェクト」と表示してよい条件](https://zenn.dev/vespertineapp/articles/619b3d99fd628b) (Zenn)<br>
   Mac 用音楽プレーヤー Vespertine の作者が、Core Audio から再生経路を読み戻す判定と、BlackHole で全サンプルを照合する試験を解説

11. [米南西部の水力発電、干ばつで記録的な落ち込み](https://www.technologyreview.com/2026/11/17/1148742/hydropower-drought-colorado-river/) (MIT TR・英語/一部会員限定)<br>
   9月末のパウエル湖は、グレンキャニオン発電所のタービンを回せる下限まで1%未満の余裕しかなかった
