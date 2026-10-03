---
layout: post
title: "macOSのフルディスクアクセスをApple制限、AIエージェント拡大が背景（ソフトウェアエンジニア）"
date: 2026-10-03
profile: engineer
tags: [開発, AI, セキュリティ]
---

Apple が macOS の「フルディスクアクセス」に追加の制限を設けると開発者向けに告知した。背景にあるのは自律型AIエージェントの広がり。一方で Zig は5か月ぶりの 0.17.0、Redis 作者は DeepSeek をローカルで動かす推論エンジンを公開し、道具まわりも動いている。

1. [macOS のフルディスクアクセス、明示操作を必須に](https://developer.apple.com/news/?id=p6zjojqw) (HN・英語)<br>
   バックアップ用の強い権限が悪用されうるとして Apple が絞る方針で、AIエージェントのリスクにも言及している。

2. [Redis 作者の推論エンジン「ds4」、DeepSeek V4 をローカルで](https://dwarfstar.sh/) (HN・英語)<br>
   C 実装で Metal・CUDA・ROCm に対応し、専門部分だけを2ビットに圧縮して KV キャッシュを SSD に退避する設計。

3. [Zig 0.17.0 リリース、ビルドシステムを刷新](https://ziglang.org/download/0.17.0/release-notes.html) (HN・英語)<br>
   206人が925コミットを重ねた5か月分で、Build Server Protocol 導入と x86_64-linux の増分コンパイル対応が柱。

4. [Wagtail、GLM 5.3 Flash だけで1か月コーディングしてみた](https://wagtail.org/blog/one-month-on-glm-53-flash/) (HN・英語)<br>
   CMS の Wagtail チームが20億トークンを使った記録。前半は68ドルに収まったが、後半は他モデルに頼った。

5. [vCPU を減らして VM を速くする「Steal Governor」](https://gihyo.jp/article/2026/10/daily-linux-261001) (はてブ)<br>
   IBM 製の仕組みで、vCPU がハイパーバイザに奪われている間は使用数を絞る。Linux 7.4 で取り込まれる見込み。

6. [glibc の strlen はなぜ範囲外まで読んで速いのか](https://zenn.dev/peloeil/articles/glibc-strlen-2023) (Zenn)<br>
   複数バイトを整数として一括で調べる実装を、範囲外読み込みが許される理由まで含めて読み解く。

7. [テストは35件全部通ったのに、本番コードを1行も通っていなかった](https://zenn.dev/dhubplus/articles/tests-that-verify-nothing) (Zenn)<br>
   iOS アプリ開発者が実際に踏んだ、モックが検証を空洞化させる3パターンを出力付きで紹介。

8. [terraform apply で1か月半前のコンテナが本番に出た](https://zenn.dev/gonta_ganbareyo/articles/6256bf2008b2ef) (Zenn)<br>
   環境変数を消しただけで Cloud Run の本番が落ちた事例で、原因はコンテナを Terraform で扱う構造にある。

9. [「SaaS はすべてモデルを包むハーネスになる」という主張](https://blog.sshh.io/p/the-harness-is-the-company) (HN・英語)<br>
   ハーネスをインフラ・文脈・状態の総体と広く定義し、ソフトウェア受託の事業がエージェント中心に移る道筋を描く。

10. [Stratego で人間の最強プレイヤーに勝ったAI「Ataraxos」](https://arstechnica.com/science/2026/10/ai-finally-beat-the-best-stratego-player-in-history-and-did-it-on-a-budget/) (HN・英語)<br>
    隠れた駒の正体を推測する第2のネットワークが鍵で、16 GPU・数千ドルの学習で15勝1敗4分。
