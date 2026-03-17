# Lobsters

- **ソースID**: lobsters
- **TTL**: 12時間
- **説明**: 招待制のテック系リンク集約サイト。HNより技術寄りでタグベースの分類が特徴

## 仕様リンク

- https://lobste.rs/about
- https://github.com/lobsters/lobsters

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://lobste.rs/rss` | 全タグの最新記事 |
| プログラミング | `https://lobste.rs/t/programming.rss` | プログラミング全般 |
| AI | `https://lobste.rs/t/ai.rss` | AI、機械学習 |
| セキュリティ | `https://lobste.rs/t/security.rss` | セキュリティ、暗号 |
| devops | `https://lobste.rs/t/devops.rss` | DevOps、インフラ |
| Swift | `https://lobste.rs/t/swift.rss` | Swift言語 |

## フィード形式と取得上の注意

- RSS 2.0 形式
- 認証不要、レート制限は緩い
- スコア（投票数）はRSSに含まれない
- `.json` をURLに付けるとJSON表現も取得可能（例: `https://lobste.rs/newest.json`）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |

## 表示名

`Lobsters`
