# 日経新聞

- **ソースID**: nikkei
- **TTL**: 720分
- **説明**: 日本最大の経済紙。速報ニュースのRSSフィードを提供（全文は有料購読が必要）

## 仕様リンク

- https://www.nikkei.com/telecom/sitemap/rss/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 速報 | `https://assets.wor.jp/rss/rdf/nikkei/news.rdf` | 経済、政治、国際、社会の速報ニュース |

## フィード形式と取得上の注意

- RSS 1.0 (RDF) 形式 + Dublin Core拡張
- `description` が空の場合がある（タイトルとリンクのみの速報）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | 空の場合あり |
| `dc:date` | published_at | ISO 8601形式 |

## 表示名

`日経`
