# MIT Technology Review

- **ソースID**: mit-tech-review
- **TTL**: 12時間
- **説明**: MITが発行する先端技術メディア。AI・バイオ・量子コンピューティング等の深い分析記事

## 仕様リンク

- https://www.technologyreview.com/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://www.technologyreview.com/feed/` | 全カテゴリの最新記事 |

## フィード形式と取得上の注意

- RSS 2.0 形式
- `dc:creator` に著者名
- `content:encoded` にフル記事HTML（description より詳細）
- 認証不要
- カテゴリ別フィードURLは未確認のため全体フィードを使用

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:creator` | meta.author | |
| `category` | meta.categories | 複数あり |

## 表示名

`MIT TR`
