---
layout: post
title: "Cloudflareが判断特化モデルClefをOSS公開（ソフトウェアエンジニア）"
date: 2026-10-02
profile: engineer
tags: [AI, 開発, セキュリティ]
article_tags:
  - [AI, 開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [開発]
  - [AI, 開発]
  - [開発]
  - [セキュリティ, AI]
  - [開発]
---

Cloudflareが判断特化の「決定モデル」Clefを公開し、Next.jsをVercel外で動かす「Vinext 1.0」も1.0に到達した。Git 3.0のSHA-256既定化への批判、turbopufferの「ベクトルDB」脱却宣言と、基盤の設計をめぐる議論も並ぶ。Claude CodeのAGENTS.md対応やOracle JDK 21のライセンス変更など、足元の運用に効く話題も多い。

1. [Cloudflare、決定モデル「Clef」をOSSで公開](https://blog.cloudflare.com/clef-decision-models/) (HN・英語)<br>
   TypeSafe の Jev 互換APIを備え、Jev Decision Index で首位。Apache 2.0 で、自社データでの強化学習による調整基盤も同時に出した。

2. [Git 3.0のSHA-256既定化は高くつく失敗になる](https://blog.gitbutler.com/git-3-sha-256) (HN・英語)<br>
   GitButler の Scott Chacon 氏が、移行コストに見合う実利がないと論じる長文。Git 3.0 の破壊的変更を先に知る材料になる。

3. [turbopuffer、ベクトルDBを主役にしない v3 へ](https://turbopuffer.com/blog/rip-vector-database) (HN・英語)<br>
   ANN索引を軸にした設計が GROUP BY や集計を縛っていたため、保存構造そのものを作り直す。Cursor や Notion が顧客。

4. [Claude Codeが「AGENTS.md」を読み込めるように](https://www.publickey1.jp/blog/26/claude_codeagentsmdclaudemd.html) (Publickey)<br>
   2.1.277 で、CLAUDE.md がないプロジェクトに限り AGENTS.md を読む。/config で切替でき、Bedrock・Vertex・Foundry では未対応。

5. [Cloudflare、Next.jsをVite上で動かす「Vinext 1.0」](https://www.publickey1.jp/blog/26/vercelnextjscloudflare_workersaws_lambdavercelvinext_10.html) (Publickey)<br>
   Turbopack の代わりに Vite でビルドし、Workers・Lambda・Netlify へ載せる。AI実験として始まった試みが製品版になった。

6. [SvelteKit 3 公開、設定は vite.config.ts へ集約](https://svelte.dev/blog/sveltekit-3-is-here) (HN・英語)<br>
   `$lib` が `#lib` に変わるなど破壊的変更の要点と、`sv migrate` による自動移行の手順がわかる。

7. [Claude Codeの使用量、Max 20xで実測した重み](https://zenn.dev/tksfjt1024/articles/25c0ab111c277c) (Zenn)<br>
   キャッシュ読み直しは input の 1/40 で計上される、など API 料金表と食い違う計算式を実験で割り出している。

8. [Oracle JDK 21、10月のCPU以降は無償ライセンス外に](https://forest.watch.impress.co.jp/docs/news/2144856.html) (はてブ)<br>
   10月20日以降の更新は Java SE OTN 扱い。商用本番で無償を保つには JDK 25 への移行が必要になる。

9. [ChatGPTのカスタムGPTを入口にしたマルウェア誘導](https://gigazine.net/news/20261001-custom-gpt-clickfix-rat/) (GIGAZINE)<br>
   Huntress の報告。正規の chatgpt.com 上のカスタムGPTが本物のモデルを装い、利用者に不正コマンドを実行させる手口。

10. [41年前のC64ゲーム「Mercenary」に新種の悪用バグ](https://gamesexplained.com/c64/mercenary/) (Reddit・英語)<br>
    ゲームの描画処理をルーチン単位で移植し、バイト単位で検証した解説ページ。街 Targ をブラウザ上で飛び回れる。
