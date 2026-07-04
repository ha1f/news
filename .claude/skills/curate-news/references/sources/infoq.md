# InfoQ

- **ソースID**: infoq
- **TTL**: 12時間
- **説明**: ソフトウェアアーキテクチャ・エンジニアリングプラクティスに特化した技術メディア

## 仕様リンク

- https://www.infoq.com/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://feed.infoq.com/` | 全トピックの最新記事 |
| AI/ML | `https://feed.infoq.com/ai-ml-data-eng/` | AI、機械学習、データエンジニアリング |
| Architecture | `https://feed.infoq.com/architecture-design/` | ソフトウェアアーキテクチャ、設計パターン |
| DevOps | `https://feed.infoq.com/devops/` | DevOps、CI/CD |
| Development | `https://feed.infoq.com/development/` | 開発全般 |

> **注意**: InfoQ のフィードはパスベースで指定する必要がある。`?topic=` や `?tag=` のクエリパラメータはサーバ側で無視され、グローバルフィードと同じ内容が返るため使ってはいけない。

## フィード形式と取得上の注意

- RSS 2.0 形式（Dublin Core拡張）
- `dc:creator` に著者名、`dc:date` に日付
- 認証不要
- ニュース記事のほかプレゼンテーション、ポッドキャストも含まれる

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | UTMパラメータ付き、除去推奨 |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:creator` | meta.author | |
| `category` | meta.categories | 複数あり |

## 表示名

`InfoQ`

## 実装

[`feed_sources/infoq.py`](../../scripts/feed_sources/infoq.py)
