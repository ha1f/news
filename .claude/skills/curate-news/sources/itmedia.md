# ITmedia

- **ソースID**: itmedia
- **TTL**: 720分
- **説明**: 日本の大手IT系ニュースサイト。エンタープライズIT、AI、セキュリティなど幅広い

## 仕様リンク

- https://corp.itmedia.co.jp/media/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml` | ITmedia全媒体の最新記事 |

## フィード形式と取得上の注意

- RSS 2.0 形式
- 記事数が多い（約50件）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |

## 表示名

`ITmedia`
