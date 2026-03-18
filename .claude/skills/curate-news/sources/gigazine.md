# Gigazine

- **ソースID**: gigazine
- **TTL**: 12時間
- **説明**: 日本の老舗ニュースサイト。テック、科学、食、エンタメまで幅広くカバー

## 仕様リンク

- https://gigazine.net/news/rss_2.0/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://gigazine.net/news/rss_2.0/` | 全カテゴリの最新記事 |

## フィード形式と取得上の注意

- RSS 2.0 形式 + Dublin Core拡張
- 認証不要
- `dc:subject` にカテゴリ情報が含まれる
- 日本語記事

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:subject` | meta.categories | カテゴリ |

## 表示名

`GIGAZINE`
