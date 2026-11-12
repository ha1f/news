---
layout: post
title: "Chrome らの「Modern Web Guidance」1.0、エージェントに今の CSS を教える（デザイナー）"
date: 2026-11-12
profile: designer
tags: [AI, 開発, 科学, デザイン, ハードウェア]
serendipity: [10]
article_tags:
  - [開発, AI]
  - [開発, デザイン]
  - [デザイン, AI]
  - [AI]
  - [デザイン, 開発]
  - [開発]
  - [デザイン]
  - [AI]
  - [ハードウェア, デザイン]
  - [科学, ハードウェア]
---

Chrome・Edge・Firefox・MDN のチームが手がける「Modern Web Guidance」が1.0に。エージェントが書くフロントエンドを今の CSS に寄せる動きと、人と AI が同じキャンバスや編集画面を共有する道具が並んだ一日。後半は折りたたみ iPhone への UI 対応から、33万円のキーボード、宇宙の DOOM まで。

1. [Chrome チーム、エージェントに今の Web 作法を教える「Modern Web Guidance」](https://github.com/GoogleChrome/modern-web-guidance) (HN・英語)<br>
   View Transitions や subgrid、oklch などの手引きを CLI でエージェントに渡し、古い書き方も検出する

2. [2026年に全主要ブラウザで使えるようになった CSS 機能5選](https://sterfield.co.jp/blog/blog-44/) (はてブ)<br>
   入力欄を文字量に合わせて伸ばす field-sizing など、JS で書いていた処理が CSS 1行になる例を前後で比較

3. [コーディングエージェントと同じ絵を描くペイントアプリ「klad」](https://github.com/klad-app/klad) (HN・英語)<br>
   画像生成モデルは使わず、筆跡を筆圧や色ごとデータで残すので、AI が描いた線も後から一本ずつ直せる

4. [Anthropic の Claude、画面内で Adobe 製品や Notion を直接操作可能に](https://gigazine.net/news/20261111-claude-interactive-connectors-full-tool/) (はてブ)<br>
   アプリの編集画面をチャットの横や全画面で開き、写真のレタッチや PDF の黒塗りを会話しながら頼める

5. [mixi2、Apple の折りたたみ「iPhone Duo」に初日から対応できた理由](https://zenn.dev/mixi/articles/b0ea64fded9503) (Zenn)<br>
   独自実装だったボトムタブを縦に並べ替え、分割した右ペインに新機能「みんなの今」を置いた設計判断

6. [Expo の新ランタイム「Exact」で天気アプリを作ってみた](https://zenn.dev/tellernovel_inc/articles/expo-exact-first-impression) (Zenn)<br>
   WebView を使わず UIKit・AppKit・DOM で描く仕組みを、SwiftUI 版とアプリサイズや起動時間で比べている

7. [Matter のチーム、赤ちゃん写真を振り返る iPhone アプリ「Sundrop」](https://techcrunch.com/2026/11/10/sundrop-turns-your-endless-baby-photos-into-recaps-time-lapses-and-more-without-ai/) (TechCrunch・英語)<br>
   Apple の Vision と Core ML で端末内だけで処理し、週ごとのまとめや成長のタイムラプスを作る

8. [Spotify の AI DJ、声と性格を選べて曲間のおしゃべりも減らせるように](https://techcrunch.com/2026/11/10/spotifys-ai-dj-gets-new-voices-personalities-and-an-option-for-less-chatter/) (TechCrunch・英語)<br>
   Premium 会員のうち9400万人超が使う機能で、英語では7種類の声から選べるようになった

9. [PFU、33万円・限定300台のアルミ削り出し「HHKB Professional Elite」](https://gigazine.net/news/20261111-hhkb-professional-elite-appearance/) (GIGAZINE)<br>
   実測970gの筐体やブラスト加工とアルマイト染色の質感、裏蓋の外し方まで写真で細部を追う

10. [ESA の衛星に声で命じて、宇宙で『DOOM』を起動](https://gigazine.net/news/20261111-doom-satelite-ops-sat/) (GIGAZINE)<br>
   4〜7月に7回試行。音声機能のない衛星に、書き換え可能なソフトウェア無線で後から機能を足した
