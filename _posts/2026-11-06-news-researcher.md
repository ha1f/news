---
layout: post
title: "国勢調査の差分プライバシー雑音を後処理で6割減、子ども1人ずつの言語モデルも（研究者）"
date: 2026-11-06
profile: researcher
tags: [AI, 開発, 科学, 経済, ハードウェア, 社会]
serendipity: [7, 8]
article_tags:
  - [科学]
  - [科学, AI]
  - [AI, 科学]
  - [AI, 科学]
  - [AI]
  - [AI, ハードウェア]
  - [開発, 科学]
  - [社会, 経済]
---

2020年米国勢調査の差分プライバシーの雑音を、後処理だけで大きく減らす手法が Science に。同じ号では、8人の子どもの家庭録音から子ども1人ずつの言語モデルを育てた研究も。投稿上限や論文の整理をめぐって、ML 研究の回し方そのものを問い直す議論が続きます。

1. [米国勢調査の差分プライバシー雑音、後処理で最大6割減](https://www.science.org/doi/abs/10.1126/science.aej1765?af=R) (Science・英語/一部会員限定)<br>
   新手法 BlueDown は秘匿性を落とさず、人種別の郡集計で誤差を21〜36%減らした

2. [8人の子の家庭録音で、子ども1人ずつの言語モデル](https://www.science.org/doi/abs/10.1126/science.aeh9311?af=R) (Science・英語/一部会員限定)<br>
   生後1000日の発話を順に学ばせると、学習には毎日の密な記録と直近の入力の反復が要った

3. [主要5学会の論文10万本超を、トピック別の1ページに](https://www.reddit.com/r/MachineLearning/comments/1xmk8rx/we_turned_10_years_of_ml_papers_into_one_page_per/) (Reddit・英語)<br>
   2016年以降の約10.9万本を約1260トピックに分け、7.9万本の本文から結果表を抜き出した

4. [CVPR 2027 も1人25本まで、投稿上限は緩すぎるか](https://www.reddit.com/r/MachineLearning/comments/1xnscvr/why_cant_conferences_just_reasonably_reduce_the/) (Reddit・英語)<br>
   上限25本では粗製論文の「数撃ちゃ当たる」を防げないと、r/MachineLearning の投稿者が問題提起

5. [2人のラボ Linum、2.1万ドルで画像生成モデルを学習](https://www.linum.ai/field-notes/pjit-21k) (HN・英語)<br>
   20億パラメータの P-JiT を Apache 2.0 で公開、本命は次の動画モデルに向けた試作

6. [Google と Meta、TPU で PyTorch を直接動かす TorchTPU](https://www.infoq.com/news/2026/11/torchtpu-native-pythorch-tpu/) (InfoQ・英語)<br>
   既存の PyTorch コードをほぼそのまま TPU に載せられ、コンパイル実行と分散学習も扱える

7. [freee、税法を Lean で形式化し本番の税計算を全入力で検証](https://developers.freee.co.jp/entry/lean-formal-verification-tax-law-qa) (はてブ)<br>
   所得税・法人税・消費税や減価償却が対象で、選び方次第で税額が変わる箇所も洗い出した

8. [米上院、エネルギー施設の許認可改革法案を11月9日に採決へ](https://www.technologyreview.com/2026/11/05/1148062/permitting-reform/) (MIT TR・英語/一部会員限定)<br>
   417ページの BAAJA は審査対象の絞り込みと期限設定が柱で、温室効果ガス排出への影響が争点

