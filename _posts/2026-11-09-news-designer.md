---
layout: post
title: "UIST 最優秀はドラッグ操作を状態の指定で作る手法（デザイナー）"
date: 2026-11-09
profile: designer
tags: [AI, 開発, デザイン, 社会]
serendipity: [9, 10]
article_tags:
  - [デザイン, 開発]
  - [デザイン, 開発]
  - [AI, デザイン]
  - [開発]
  - [デザイン]
  - [デザイン]
  - [AI, 社会]
  - [社会, デザイン]
  - [デザイン, AI]
  - [社会]
---

UIST 2026 の最優秀論文は、ドラッグ操作を「行き先の状態」を並べるだけで作る仕組み。Rust と WebGPU で作った家具設計向けの 3D モデラーや、お手本の画面と見比べながら似たものを作る AI ツールも出てきた。作る道具が軽くなる一方で、透かしの追跡や会議での聞き方など、人の側の振る舞いを問い直す話題も並ぶ。

1. [ドラッグ操作を「行き先の状態」の指定だけで作る Declarative Dragging](https://declarative-dragging.github.io/) (HN・英語)<br>
   Horowitz、Blinn、Heer の3人による UIST 2026 最優秀論文で、候補の状態を先読みで描画して動きを合成する

2. [SketchUp 代わりのオープンソース 3D モデラー「KetchUp」](https://ketchup3d.github.io/app/) (HN・英語)<br>
   棚や机など木工家具の設計向けで、ブラウザでも動き、SketchUp の形状を読み込んで OBJ で書き出せる

3. [お手本のサイトやゲームを解析し、AI が似たものを作る「Craft Anything」](https://www.techno-edge.net/article/2026/11/09/5686.html) (はてブ)<br>
   完成品を元の対象と3つの画面幅で見比べて手直しを重ね、作る部分はまず Claude Code が担う

4. [React のアンマウントはいつ起きるか、位置と種類で整理](https://qiita.com/shun123/items/586906ea13bc03bfcea6) (Qiita)<br>
   key や返す要素の種類が変わると状態が消え、閉じるアニメーションが再生されない原因にもなる

5. [生年月日だけで一生を年表にする「人生タイムライン」](https://ltimeline.com/ja/) (はてブ)<br>
   寿命の目安と残り日数を出し、その年の出来事や家族の年齢を1年ごとの帯に並べる無料サービス

6. [自分のカメラロールで撮影地と時期を当て合う「Where Were We」](https://wherewerewe.app/) (HN・英語)<br>
   写真の位置と日付を読み取ってリンクで共有でき、作ったロールは30日で自動的に消える

7. [AI 画像の透かしは利用者を追う「スパイマーク」だ、という問題提起](https://gigazine.net/news/20261108-spymarks-not-watermarks/) (GIGAZINE)<br>
   画像・動画制作ソフト ArtCraft の創業者が、見えない追跡信号を真正性の印と呼び分けるよう訴える

8. [ドゥームスクロールから気をそらすアプリ集](https://techcrunch.com/2026/11/08/apps-to-distract-you-from-the-endless-cycle-of-doomscrolling/) (TechCrunch・英語)<br>
   米国人の64%がドゥームスクロールをするという調査を起点に、代わりに時間を使えるアプリを紹介

9. [米津玄師に学ぶ、一人で全部作れる時代に人と作る理由](https://zenn.dev/tokium_dev/articles/yonezu-kenshi-why-create-with-others) (Zenn)<br>
   作詞からアートワークまで一人で手がけた米津氏が、メジャーデビュー後にバンド録音へ移った経緯を追う

10. [会議でリーダーは質問するだけでなく、答えを聞かないと逆効果](https://gigazine.net/news/20261108-bosses-should-avoid-speaking-during-meetings/) (GIGAZINE)<br>
   ハンブルク大学などが88人・22チームにパイロットの採用を議論させ、聞き方で判断の質が変わるかを調べた
