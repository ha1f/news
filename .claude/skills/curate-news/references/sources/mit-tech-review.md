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

## 利用条件

- **AI利用**: 可（規定なし。robots.txt は AI クローラを拒否）
- **商用利用（課金）**: 不可（再利用は有償ライセンスとして販売。窓口 licensing@technologyreview.com）
- **広告掲載での利用**: 不可（同上）
- **義務**: 規定なし（許諾自体が個別契約）
- **制約**: 書面許可なき複製・再配信の禁止（ToS が RSS に適用と明記）
- **根拠**: https://www.technologyreview.com/terms-of-service/ （確認日 2026-08-28）

## 実装

[`feed_sources/mit_tech_review.py`](../../scripts/feed_sources/mit_tech_review.py)
