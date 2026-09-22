---
layout: post
title: "AI最前線とコーディング現場のひずみ（ソフトウェアエンジニア）"
date: 2026-09-22
profile: engineer
tags: [AI, 開発, セキュリティ]
---

xAIの新型「Grok 4.7」と、OpenAIが安全性「重大」区分に初めて分類した「GPT-6 Astra」――フロンティアAIの主導権争いが続く一方、現場ではAIコーディングの普及がCIやテスト運用を圧迫し始めている。アーキテクチャ設計とApple platform開発の現場からも、地に足のついたツールが並んだ一日。

1. [xAI、Grok 4.7公開。価格・速度据え置きで精度向上](https://x.ai/news/grok-4-7) (HN・英語)<br>
   価格・速度は前モデルと同じまま、長時間コーディング課題の評価CursorBenchで46.3%に上昇。

2. [GPT-6 Astra、OpenAI初のサイバー「重大」認定](https://www.infoq.com/news/2026/09/gpt-6-astra-critical-cyber/) (InfoQ・英語)<br>
   専門家テストでブラウザとOSカーネルの未知の脆弱性を自力発見し攻撃コードまで作成、一方で推論過程の可視性は低下。

3. [Quiet Grid Labs、AIエージェント向けC4設計図ツール公開](https://c4.quietgridlabs.com/) (HN・英語)<br>
   システム構成図をMCP経由でエージェントに読ませ、実装作業まで橋渡しする「Viaduct」。

4. [Uber、分散DB「M3DB」のシャーディングを再設計](https://www.infoq.com/news/2026/09/uber-m3db-subcluster-sharding/) (InfoQ・英語)<br>
   固定サイズの「サブクラスタ」に分割し、ノード障害や保守時の影響範囲とデータ移動量を抑制。

5. [mtx2s氏、「テックリード」呼称のズレを整理](https://mtx2s.hatenablog.com/entry/2026/09/21/182658) (はてブ)<br>
   同じ「テックリード」でもリーダー・マネージャー・アーキテクトのどれを指すか組織でバラバラな理由を解剖。

6. [Linear、AIコーディング急増でCIを再設計](https://linear.app/now/ci-bottleneck-reworked) (HN・英語)<br>
   テストスイートが4倍近くに増えてもPR待ち時間を短縮、1テストあたりの実行時間はほぼ半減。

7. [mizchi氏、diffから関連テストだけ抽出するCLI公開](https://zenn.dev/mizchi/articles/jev-test-filter-intro) (はてブ)<br>
   git diffを渡すと影響範囲を絞り込み、110件中3件など実行すべきテストだけに削減する「jev-test-filter」。

8. [Xcode不要、Claude Code使用率を常駐表示するMacアプリ](https://zenn.dev/ait/articles/hachibu-claude-code-usage-bar) (Zenn)<br>
   モデル・エフォート・週間使用率を色分けバーで表示するMIT公開の非公式ツール「Hachibu」。

9. [自作MacアプリのMCPサーバー、常駐サービスから分離](https://zenn.dev/labee/articles/4e2209e701dec8) (Zenn)<br>
   同じ実行ファイルでも起動元でEventKitの権限エラーが出る問題を、プロセス分離で解消した設計判断。

10. [NSHipsterのmattt氏、Mac標準アプリをMCPサーバー化](https://github.com/mattt/iMCP) (GitHub Trending・英語)<br>
    Messages・Contacts・RemindersなどMac標準アプリをAIエージェントから呼び出せるOSSサーバー「iMCP」。
