---
layout: post
title: "Copilot Fusion 正式公開、Hono は外部 PR を閉じる（ソフトウェアエンジニア）"
date: 2026-11-02
profile: engineer
tags: [AI, 開発, ビジネス, 科学]
article_tags:
  - [AI, 開発]
  - [AI, 開発]
  - [開発]
  - [開発, AI]
  - [開発, AI]
  - [開発]
  - [開発]
  - [開発]
  - [開発]
  - [ビジネス, 開発]
  - [科学, AI]
---

GitHub が複数の AI モデルを自動で組み合わせる「Copilot Fusion」を正式公開。一方で Hono は外部からの PR を閉じ、AI がコードを書く時代の OSS 運営に一石を投じる。Swift の MCP 公式 SDK や Jepsen の新レポートまで、道具と品質の話が並ぶ月曜日。

1. [GitHub、モデルを自動で組み合わせる「Copilot Fusion」を正式公開](https://www.publickey1.jp/blog/26/githubcopilot_fusionaigithub_universe_2026.html) (Publickey)<br>
   下書きを別系統のモデルが審査する「Critique」など3方式と、4段階の負荷レベルの違いが分かる

2. [AI エージェント向け業務手順書「Agent Skills」の書き方](https://techblog.kazaneya.com/20261030-agent-skills/) (はてブ)<br>
   データ支援の風音屋が、ノー会議デーのような先輩の暗黙知を AI に渡す手順書の組み立てを示す

3. [Hono の作者、外部からの PR を閉じた理由を語る](https://slides.yusu.ke/foss4g-2026) (はてブ)<br>
   和田裕介氏の登壇資料。7〜9月の PR は1年で82件から345件に増え、メンテナーは実質2人だった

4. [MCP の公式 Swift SDK、Apple と共同でメンテナンス](https://github.com/modelcontextprotocol/swift-sdk) (GitHub Trending・英語)<br>
   Model Context Protocol の 2025-11-25 版仕様に沿い、クライアントとサーバーの両方を実装している

5. [Claude Code に xcodebuild テストを任せると、grep が失敗を隠す](https://zenn.dev/atsushi_apps/articles/ai-xcodebuild-test-tips) (Zenn)<br>
   400件超のテストを AI に回させる個人 iOS 開発者が、落ちたままコミットした実例と回避策を紹介

6. [iOS 26 の WKWebView、起動直後の空 Cookie で勝手にログアウト](https://qiita.com/feedminus47/items/b97229037687df1eff17) (Qiita)<br>
   数秒だけ空で返るストアを「まだ不明」と扱い直し、Instagram のログイン消失を直した記録

7. [Rust 製の差分ツール「OmniDiff」、画像やフォントも中身に沿って比べる](https://github.com/ivankovic/omnidiff) (HN・英語)<br>
   コード変更の98%を100ms未満で処理し、PDF やアーカイブも扱う。ライセンスは AGPL v3

8. [Makefile はもう要らない、用途ごとに代わりの道具がある](https://www.reddit.com/r/programming/comments/1xl5irk/the_case_against_makefiles/) (Reddit・英語)<br>
   1976年に Bell Labs で生まれた make を、CMake や just などへ置き換えようという主張

9. [Jepsen、「完全 ACID」をうたう ParticleDB に96件の問題](https://www.reddit.com/r/programming/comments/1xl8d57/jepsen_on_particledb_we_tested_versions_114/) (Reddit・英語)<br>
   最後の検証版でも既定の occ モードでコミット済みの書き込みが消えた。調査費は開発元 Orkes の負担

10. [AWS の確約容量は2027年までほぼ完売、ジャシー CEO](https://www.infoq.com/news/2026/11/aws-capacity-sold-out/) (InfoQ・英語)<br>
   2028年分も一部が割り当て済みで、ML 向け予約枠「Capacity Blocks」は先に約15%値上げされていた

11. [OpenAI の論文700本超を受けて、数学者 Calegari「数学は変わった」](https://terrytao.wordpress.com/2026/11/01/mathematics-has-changed-lets-act-like-it/) (HN・英語)<br>
   Terence Tao のブログへの寄稿。AI 論文の粗さを認めつつ、採用や出版の慣行を変えようと説く
