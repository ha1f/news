# Ars Technica

- **ソースID**: arstechnica
- **TTL**: 12時間
- **説明**: 深掘り技術記事に定評のある老舗テックメディア。品質が安定して高い

## 仕様リンク

- https://arstechnica.com/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://arstechnica.com/feed/` | 全カテゴリの最新記事 |
| AI | `https://arstechnica.com/ai/feed/` | AI、機械学習 |
| Tech | `https://arstechnica.com/information-technology/feed/` | テクノロジー全般 |
| Security | `https://arstechnica.com/security/feed/` | セキュリティ |
| Science | `https://arstechnica.com/science/feed/` | 科学技術 |
| Gadgets | `https://arstechnica.com/gadgets/feed/` | ハードウェア、ガジェット |

## フィード形式と取得上の注意

- RSS 2.0 形式
- `dc:creator` に著者名、`slash:comments` にコメント数
- 1記事に複数の `category` タグ
- 認証不要

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:creator` | meta.author | |
| `slash:comments` | meta.comments | コメント数 |

## 表示名

`Ars`
