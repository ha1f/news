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

## 利用条件

- **AI利用**: 要確認（robots.txt が AI ボットを拒否し「機械学習利用は要連絡」と表明）
- **商用利用（課金）**: 不可（営利目的の記事利用リンク・事業者クリッピングを明示禁止）
- **広告掲載での利用**: 不可（同上）
- **義務**: 出典が日経である旨の明記
- **制約**: フィード自体が日経非公式の第三者（RSS愛好会）配信で予告なく停止されうる。継続可否は #241 論点（オーナー判断待ち）
- **根拠**: https://www.nikkei.com/info/link.html （確認日 2026-08-28）

## 実装

[`feed_sources/nikkei.py`](../../scripts/feed_sources/nikkei.py)
