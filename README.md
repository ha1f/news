# news

Claude Code のスキル機能を使ったニュースキュレーションツール。複数のニュースソースから記事を自動取得し、ユーザーの好みに基づいてキュレーションする。

キュレーション結果の例は [GitHub Pages](https://ha1f.github.io/news/) で確認できる。

## 使い方

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) でこのリポジトリを開き、`/curate-news` を実行する。

```
$ claude
> /curate-news
```

好みに合った記事が日本語でキュレーションされる。

結果はローカルの `output/` に保存される。Webで公開したい場合は `/publish-pages` を使う。キュレーションの実行からPR作成まで自動で行われ、PRをマージすると [GitHub Pages](https://ha1f.github.io/news/) に反映される。

## 仕組み

```mermaid
flowchart LR
    sources["references/sources/*.md"] --> select["ソース選択"]
    prefs["preferences.md"] --> select
    select --> fetch["フィード取得\n（並列）"]
    fetch --> cache["キャッシュ"]
    cache --> curate["キュレーション"]
    prefs --> curate
    curate --> output["output/\n{YYYY-MM-DD}-{hash}.md"]
```

1. **ソース選択** — `preferences.md` の興味・関心と各ソースのトピックをマッチングし、取得対象を自動選択
2. **フィード取得** — `scripts/fetch_feeds.py` で対象フィードを並列取得。キャッシュが有効（TTL内）ならスキップ
3. **キュレーション** — 全記事を統合・重複排除し、興味との関連度とスコアで選定
4. **出力** — 日本語のマークダウン形式で表示し、`output/{YYYY-MM-DD}-{hash}.md` に保存（hashは好みファイルのMD5先頭8文字）

## 毎日の自動ループ

claude.ai のクラウド trigger が毎日のステージを実行し、キュレーション→評価→実装→マージまで自動で回る。スキル・プロンプトの改善 PR も自動マージされる自己改善ループ。実装→レビューは1日2周（12時→15時、16時→18時）。スキルの優先順（要対応の in_progress → backlog）により、15時に要修正で draft に戻った PR は16時の run が最優先で拾い、手戻りを翌日に持ち越さない。

週次（日曜11時）の `/audit-and-adopt` は、プロダクトでなくループ自身の環境を監査する: マージ済み資産の批評・エコシステム（Claude Code 新機能・公式スキル）の取り込み判断・スキル手順が守られているかのプロセス監査。見つかった改善は issue / PR として日次ループに流れ込む。

プロダクト・事業側のリスク監査（法務・収益化準備など）は `/audit` が担う。監査の観点は [.claude/skills/audit/audits/](.claude/skills/audit/audits/) にデータとして版管理され、実施のたびに履歴が残るため、同じ監査を誰でも再現できる。各定義の「再監査トリガー」の該当は週次の audit-and-adopt が確認して実行する。人間にしかできない判断を `hold` で依頼するときは、その観点を監査定義として資産化する（詳細は [.claude/GUARDRAILS.md](.claude/GUARDRAILS.md) の設計原則）— 監査能力自体がループとともに成長する。

```mermaid
flowchart LR
    publish["9:00 /publish-pages\nキュレーション→デプロイ"] --> evaluate["10:00 /evaluate-and-triage\nユーザ評価→issue化"]
    evaluate --> develop["12:00 /select-and-develop\nissue選定→実装"]
    develop --> review["15:00 /review-and-merge\nレビュー→マージ"]
    review --> develop2["16:00 /select-and-develop\nissue選定→実装（2周目）"]
    develop2 --> review2["18:00 /review-and-merge\nレビュー→マージ（2周目）"]
    review2 -.改善が翌日に反映.-> publish
```

状態は GitHub ネイティブのもので受け渡す: PR の **draft（作業中・ループは触らない）/ ready（レビュー・マージ候補）**、issue の open / closed、linked PR、作者。専用ラベルは `hold`（自動処理を止めて人間が見る）の1つだけ。数値上限・保護パス・auto-merge モードは [.claude/GUARDRAILS.md](.claude/GUARDRAILS.md) に集約されている。

### 介入方法（runbook）

- **PR を自動マージさせない** — draft のままにするか、`hold` ラベルを付ける（ready な PR はレビュー後にマージされ得る）
- **issue を自動実装させない** — `hold` ラベルを付ける
- **ループ全体を止める** — claude.ai の設定で該当 trigger を無効化する
- **悪い変更を巻き戻す** — `git revert` の PR を作ってマージする
- **自動マージの有効化 / 停止** — `.claude/GUARDRAILS.md` の mode を編集する（保護パスなので必ず人間がマージする）

### trigger 定義（claude.ai 上にあり repo 外のため記録）

| JST | cron (UTC) | メッセージ |
|-----|-----------|-----------|
| 9:00 | `0 0 * * *` | `/publish-pages` |
| 10:00 | `0 1 * * *` | `/evaluate-and-triage` |
| 12:00 | `0 3 * * *` | `/select-and-develop` |
| 15:00 | `0 6 * * *` | `/review-and-merge` |
| 16:00 | `0 7 * * *` | `/select-and-develop` |
| 18:00 | `0 9 * * *` | `/review-and-merge` |
| 日曜 11:00 | `0 2 * * 0` | `/audit-and-adopt` |

## 依存関係の更新

GitHub Actions と workflow 内でピン留めしているバージョン（Playwright・Python）は [Renovate](https://docs.renovatebot.com/) が更新する。設定は [.github/renovate.json5](.github/renovate.json5) で、Renovate 公式の `config:best-practices` をベースにしている。

- **digest 固定** — Actions は `@v7` のようなタグではなく commit SHA に固定される（タグは付け替え可能なため、サプライチェーン攻撃を受けにくくする）
- **実行タイミング** — 月曜早朝（JST）にまとめて PR を作る。日次ループのステージと重ならない時間帯
- **自動マージ** — digest / patch / minor は公開から3日経過し CI が green なら Renovate 自身がマージする。major と Renovate 設定自体の変更は人間がマージする
- **状況の確認** — Renovate が作る Dependency Dashboard issue で保留中の更新を一覧できる（bot の issue なのでループの実装対象・issue 上限には入らない）

有効化には [Renovate GitHub App](https://github.com/apps/renovate) のインストールが必要（リポジトリ設定のためリポジトリ外の作業）。Fork して使う場合も同様に、自分のリポジトリに App をインストールすると設定がそのまま効く。

## ニュースソース

18ソースが定義済み。各ソースは `references/sources/*.md` に独立したファイルとして管理され、規約・robots.txt を一次情報で確認した利用条件（AI利用・商用利用・広告・義務・制約）を各定義の「利用条件」セクションに保持している。

| ソース | カテゴリ | 説明 |
|--------|----------|------|
| [dev.to](https://dev.to/) | テック | 開発者コミュニティ。チュートリアル・技術記事 |
| [GitHub Trending](https://github.com/trending) | テック | GitHubのトレンドリポジトリ * |
| [Hacker News](https://news.ycombinator.com/) | テック | Y Combinator運営のテック系ニュース |
| [InfoQ](https://www.infoq.com/) | テック | ソフトウェアアーキテクチャ特化メディア |
| [MIT Technology Review](https://www.technologyreview.com/) | テック | AI・バイオ・量子等の先端技術 |
| [Product Hunt](https://www.producthunt.com/) | テック | 新プロダクト発見プラットフォーム |
| [Reddit](https://www.reddit.com/) | テック | テック系サブレディット |
| [TechCrunch](https://techcrunch.com/) | テック | 米国最大のテックメディア |
| [日経新聞](https://www.nikkei.com/) | 経済 | 日本最大の経済紙（速報フィード） |
| [Nature](https://www.nature.com/) | 科学 | 世界最高峰の学術ジャーナル |
| [Science](https://www.science.org/) | 科学 | AAAS発行のトップ学術ジャーナル群 |
| [Dribbble](https://dribbble.com/) | デザイン | デザイナー向けコミュニティ（Stories記事） |
| [GIGAZINE](https://gigazine.net/) | 日本語 | テック・科学・エンタメの老舗ニュースサイト |
| [ITmedia](https://www.itmedia.co.jp/) | 日本語 | エンタープライズIT・AI・セキュリティ |
| [Publickey](https://www.publickey1.jp/) | 日本語 | エンタープライズIT専門メディア |
| [Qiita](https://qiita.com/) | 日本語 | エンジニア向け技術記事共有プラットフォーム |
| [はてなブックマーク](https://b.hatena.ne.jp/) | 日本語 | 日本最大のソーシャルブックマーク |
| [Zenn](https://zenn.dev/) | 日本語 | エンジニア向け技術情報プラットフォーム |

\* GitHub Trending はサードパーティの [GitHubTrendingRSS](https://github.com/mshibanami/GitHubTrendingRSS) 経由で取得

**検討したが対応不可のソース**: Bloomberg（公開RSSフィード無し）、Designer News（サイト閉鎖済み）

**規約により除外したソース**（2026-08 の monetization 監査・#241 の方針）: Ars Technica・Wired（Condé Nast 規約が生成AI/RAG での利用を非商用からも除外）、The Verge（PMC 規約が AI ツールでの取得を明示禁止）、Lobsters（`Content-Signal: ai-input=no` を宣言）。AI 利用を明示的に制限するソースは採用しない

## カスタマイズ

### 好みの設定

[`.claude/skills/curate-news/preferences.md`](.claude/skills/curate-news/preferences.md) を編集する。
以下は例。

```markdown
# ニュースの好み

## 興味・関心

- iOS / Swift 開発
- ソフトウェアアーキテクチャ
- AI / LLM
- 開発ツール・生産性
- テック業界の動向
- 話題のサービス・プロダクト
- 経済・ビジネス

## 好みのメディア

- 日経
- TechCrunch

## 読みたくない記事

- 入門・チュートリアル系の記事
- 宣伝色の強い記事

```

興味・関心はソースのカテゴリ自動選択にも使われるため、具体的に書くとより精度が上がる。

### ソースの追加

`references/sources/` にマークダウンファイルを追加する。フォーマットは `STYLEGUIDE.md` を参照。

## Forkして使う

自分専用のニュースキュレーションを作りたい場合は、リポジトリをForkして使う。

1. **Fork** — GitHubで [Fork](https://github.com/ha1f/news/fork) を作成し、ローカルにcloneする
2. **好みの編集** — `preferences.md` を自分の興味・関心に書き換える（[書き方](#好みの設定)）
3. **ソースの調整** — 不要なソースを削除したり、読んでいるメディアを追加する（[追加方法](#ソースの追加)）
4. **GitHub Pagesの有効化** — リポジトリの **Settings → Pages** で Source を `main` ブランチに設定する。公開URLは `https://{ユーザー名}.github.io/news/` になる
5. **実行** — Claude Code で `/publish-pages` を実行し、PRをマージすれば公開される
6. **（任意）毎日の自動ループ** — [毎日の自動ループ](#毎日の自動ループ) を使う場合は、pinned の status issue（📊 daily-loop status）と `hold` ラベルを作成し、claude.ai で trigger を設定する（[trigger 定義](#trigger-定義claudeai-上にあり-repo-外のため記録)参照）。評価対象の URL は Pages API から自動解決される

## ファイル構成

```
.claude/skills/curate-news/
├── SKILL.md           # ワークフロー定義
├── STYLEGUIDE.md      # 設計方針・ファイル構成ガイド
├── preferences.md     # ユーザーの好み
├── scripts/           # フィード取得スクリプト
├── references/sources/ # ニュースソース定義
├── cache/             # フィード取得キャッシュ（git管理外）
└── output/            # キュレーション結果（git管理外）
```
