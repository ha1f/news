---
layout: post
title: "DevDayでdotsとGPT-6.1 Sol登場、npmではワームが拡散（ソフトウェアエンジニア）"
date: 2026-09-30
profile: engineer
tags: [AI, 開発, セキュリティ, ハードウェア]
---

OpenAI が開発者会議 DevDay 2026 で20件超を発表し、24時間稼働のエージェント「dots」と新モデル「GPT-6.1 Sol」を投入した。開発現場では WSL containers の一般提供や Git 3.0 に向けた動きなど土台の更新が続き、npm では Express を装う9パッケージがワームを広めている。

1. [OpenAI の DevDay 2026、dots と GPT-6.1 Sol など20件超](https://www.itmedia.co.jp/news/article/2609/30/2000001868/) (ITmedia)<br>
   常時稼働エージェント、最大8倍高速な有料枠「Ultrafast」、Codex のクラウド実行まで一度に把握できる。

2. [Express を装う npm パッケージ9件、SSH で広がるワーム](https://www.reddit.com/r/programming/comments/1wt8odk/nine_npm_packages_shipping_worm_that_spread_by/) (Reddit・英語)<br>
   9/29 に33分で公開され、インストール時のフックから Tor 経由のバックドアを仕込み、手元の SSH 鍵で他ホストへ感染する。

3. [Devin に macOS の仮想環境、Mac 実機なしでベータ公開まで](https://www.publickey1.jp/blog/26/devinmacosmacdevinappstore.html) (Publickey)<br>
   Ubuntu と Windows に続き macOS が加わり、コード生成からテスト、実行、App Store 配信前のベータ公開まで Devin が行う。

4. [WSL containers が一般提供に、Microsoft が発表](https://blogs.windows.com/windowsdeveloper/2026/09/29/wsl-containers-now-generally-available/) (はてブ)<br>
   Windows 上で Linux のコンテナを動かす WSL の新機能が GA になり、AI やクラウドネイティブ開発の作業を Windows 側で完結させる位置づけ。

5. [Git 2.56.0 の新機能と Git 3.0 リリース計画](https://about.gitlab.com/ja-jp/blog/whats-new-in-git-2-56-0/) (はてブ)<br>
   GitLab の Git チームが、git-history の drop やマージ済みブランチの削除など追加機能と Git 3.0 の計画を整理する。

6. [15年使った Git から Jujutsu へ乗り換えた理由](https://zenn.dev/oukayuka/articles/15years-git-then-jujutsu) (Zenn)<br>
   会社指定の VCS を使ってきた筆者が、2026年に初めて自分で選んだバージョン管理として Jujutsu を挙げた経緯。

7. [Go 1.28 で string(int) 変換が制限される見込み](https://zenn.dev/aqyuki/articles/go-proposal-3939) (Zenn)<br>
   9/23 に承認された提案で、整数から文字列への直接変換は rune と byte を基底型に持つ場合などに限られる。

8. [MCP の新仕様でセッションが不要に、AWS が解説](https://www.infoq.com/news/2026/09/aws-stateless-mcp/) (InfoQ・英語)<br>
   リモート MCP サーバーでスティッキーセッションが要らなくなりスケールしやすくなる一方、状態管理や冪等性はアプリ側の課題になる。

9. [Cloudflare Workers で Rust の Emscripten ターゲットを実験提供](https://www.reddit.com/r/programming/comments/1wsv1tt/supporting_native_rust_in_workers_with_the_new/) (Reddit・英語)<br>
   wasm-bindgen の新ターゲットで Rust ライブラリの互換性が上がり、Tokio 製の Minecraft サーバー Pumpkin が Durable Object 上で動いた。

10. [Android、パスキーをパスワードマネージャ間で転送可能に](https://www.publickey1.jp/blog/26/androidgoogle1passwordbitwardendashlane.html) (Publickey)<br>
    Google パスワードマネージャに登録したパスキーを 1Password や Bitwarden など別の管理アプリへ移せる。

11. [27万個超の NAND ゲートだけで作った16ビットPC「NAND-16」](https://somethingbig.ai/computer) (HN・英語)<br>
    CPU、メモリ、OS、テトリスまでゲート上で動き、ブラウザで信号の流れを拡大して追える。
