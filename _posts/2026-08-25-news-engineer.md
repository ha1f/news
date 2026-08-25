---
layout: post
title: "2026年8月25日 (engineer)"
date: 2026-08-25
profile: engineer
tags: [AI, 開発, セキュリティ]
---

NVIDIAのAIエージェント「AVO」がARC-AGI-3で満点を叩き出し、モデル単体との差が約70ptという衝撃。一方でseL4の形式検証がAArch64で完了し、実行ファイルをSQLiteとして読む実験記事がLobstersで盛り上がるなど、低レイヤからツールチェーンまで面白い動きが多い。

1. [NVIDIA「AVO」、ARC-AGI-3で100%達成](https://gigazine.net/news/20260825-nvidia-avo/) (Gigazine)<br>
   同じモデルでもハーネス次第で30%→100%になることを数字で示した

2. [MCP新ロードマップ——長時間処理・エージェント認証など5分野](https://gigazine.net/news/20260824-mcp-roadmap/) (Gigazine)<br>
   ツール呼び出しの先にある「エージェントが長時間自律動作する」未来の設計方針

3. [LLMが推論エンジンの脆弱性を突いてホストマシンを制御できる](https://boydkane.com/essays/llms-could-control-their-host-machines-by-exploiting-inference-engines) (Hacker News)<br>
   推論基盤自体がアタックサーフェスになるリスクの具体的な分析

4. [seL4の形式的セキュリティ証明がAArch64で完了](https://proofcraft.systems/news-2026/#2026-08-21) (Hacker News)<br>
   マイクロカーネルの正当性証明が実用アーキテクチャで完成した歴史的マイルストーン

5. [実行ファイルはSQLiteデータベースである](https://fzakaria.com/2026/08/23/your-executable-is-a-sqlite-database) (Lobsters)<br>
   ELFバイナリをSQLiteとして読み解く実験的アプローチ

6. [優秀なエンジニアが書くDesign Docは何が違うのか](https://www.pospome.work/entry/2026/08/24/223309) (はてなブックマーク)<br>
   「技術選定の背景」と「却下した案」の書き方に差が出るという考察

7. [Firefox、JPEG XLのサポートを正式に出荷へ](https://hacks.mozilla.org/2026/08/intent-to-ship-jpeg-xl/) (Lobsters)<br>
   Mozillaが「Intent to Ship」を公開、ウェブ画像フォーマットの勢力図が変わる

8. [Emacs 31.1リリース](https://lists.gnu.org/archive/html/info-gnu-emacs/2026-08/msg00004.html) (Lobsters)

9. [IPFS開発チーム、プロジェクトの終了を発表](https://ipshipyard.com/blog/2026-the-end-of-ipfs-at-shipyard/) (Hacker News)<br>
   分散ウェブを象徴するプロトコルのメンテナーが撤退する経緯

10. [Ctrl+C でプログラムが止まる仕組みを調べた](https://zenn.dev/wakame_atsushi/articles/05a74885eb963d) (Zenn)<br>
    シグナル・プロセスグループ・端末ドライバを追いかける探索記録
