# Science (AAAS)

- **ソースID**: science
- **TTL**: 24時間
- **説明**: AAASが発行する世界トップクラスの学術ジャーナル群

## 仕様リンク

- https://www.science.org/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| Science本誌 | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science` | 全分野の最新研究 |
| Science Advances | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv` | オープンアクセス論文 |
| Science Robotics | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=scirobotics` | ロボティクス |
| Science Immunology | `https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciimmunol` | 免疫学 |

## フィード形式と取得上の注意

- RSS 1.0 (RDF) 形式 + Dublin Core拡張 + PRISM拡張
- 認証不要（メタデータは公開。全文は要購読）
- `dc:type` で記事種別（Research Article, Perspective等）が判別可能
- 記事は全て英語

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `dc:date` | published_at | ISO 8601形式 |
| `dc:creator` | meta.authors | 複数あり、配列で保持 |
| `dc:type` | meta.article_type | Research Article, Perspective等 |
| `prism:doi` | meta.doi | DOI識別子 |
| `prism:publicationName` | meta.journal | ジャーナル名 |

## 表示名

`Science`
