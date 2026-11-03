---
layout: post
title: "AIが重みを直接編集、数学の正答率が6倍に（研究者）"
date: 2026-11-03
profile: researcher
tags: [AI, 開発, 科学, 社会]
article_tags:
  - [AI]
  - [AI, 科学]
  - [AI, 社会]
  - [AI, 社会]
  - [AI, 開発]
  - [AI, 開発]
  - [科学]
  - [科学]
  - [開発, 社会]
  - [社会, 開発]
---

GPT-6 Astra が Qwen の重みのわずか0.016%を書き換え、数学ベンチマークの正答率を7.9%から48.1%へ。凍結した LLM 同士が言葉を使わずに考えを渡す手法も出て、モデルの「中身」を直接扱う研究が続く。一方で、名前を変えずに更新されるモデルや透かしの導入など、AI の出力をどう追跡するかも問われている。

1. [GPT-6 Astra、ニューラルネットの重みを直接読み書きして Qwen を改善](https://rikiyat.github.io/blog/weight-space-programming/) (HN・英語)<br>
   MIT CSAIL の研究で、勾配を使わず重みの0.016%を直して MATH-500 が7.9%から48.1%に上がった

2. [凍結した LLM 同士がテキスト抜きで考えを渡す「J-Comm」](https://zenn.dev/lixian/articles/jcomm-jacobian-guided-latent-communication) (Zenn)<br>
   Qwen3-8B から4B への受け渡しで、生成トークンを最大74.8%減らし GPQA でも8.59pt 伸びた論文の解説

3. [AI モデルには意味のある版管理が要る](https://www.nature.com/articles/s42256-026-01323-8) (Nature・英語/一部会員限定)<br>
   Mavroudis ら4人が、同じ名前のまま中身が変わるモデルでは規制も論文の再現も立ち行かないと論じる

4. [Anthropic、旧版の Claude にも11月3日から文章の透かしを導入](https://gigazine.net/news/20261102-anthropic-expands-text-watermarking-older-claude-november-3/) (GIGAZINE)<br>
   EU の AI 法を受けて8月以降のモデルに入れた不可視の透かしを、Opus 4.6 や Sonnet 4.6 にも広げる

5. [東北大 NLP、日本語で LLM を一から作れる「nanochat-jp」を公開](https://gigazine.net/news/20261102-nanochat-jp/) (GIGAZINE)<br>
   Karpathy の nanochat に日本語トークナイザや学習データ、日本語ベンチマークを足し、学習から評価まで1リポジトリで回せる

6. [エージェントが動き回るウェブはもう来ている](https://www.technologyreview.com/2026/11/02/1147846/the-agentic-web-is-here/) (MIT TR・英語/一部会員限定)<br>
   Berners-Lee が2001年に描いたセマンティックウェブの構想を起点に、サンドボックスを抜け出したエージェントの事故まで見渡す

7. [機械学習で文献を掘り直し、見落とされていた MXene 33種を発見](https://www.science.org/doi/abs/10.1126/science.aeh5957?af=R) (Science・英語/一部会員限定)<br>
   外部加熱のいらない数分の合成法で7種を作り、ネオジムやガドリニウムなど希土類を含む11種も初めて実現した

8. [ストレス応答の酵素を活性化し、神経を傷める複数のタンパク質をまとめて分解](https://www.science.org/doi/abs/10.1126/science.aed2525?af=R) (Science・英語/一部会員限定)<br>
   E3 リガーゼ CUL2-FEM1B の活性化剤で、フリードライヒ失調症のモデルでもミトコンドリアと神経細胞が保たれた

9. [日本の全法令を git の履歴にしてみた](https://zenn.dev/koheiwada/articles/houritsu-japanese-laws-as-git) (はてブ)<br>
   改正を1コミットにまとめ、日本学術会議の法人化で個人情報保護法の別表に1行増えたことまで diff で見える

10. [好きなウェブサイトがあるなら、自分でバックアップを](https://blog.mistys-internet.website/post/2026/10/29/if-you-love-a-website-back-it-up/) (HN・英語)<br>
    2004年からあったファンサイトを失ったウェブアーカイブの専門家が、個人でもできる保存の手順を教える
