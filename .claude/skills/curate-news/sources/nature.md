# Nature

- **ソースID**: nature
- **TTL**: 1440分
- **説明**: 世界最高峰の学術ジャーナル。最新の科学研究論文・ニュースを掲載

## 仕様リンク

- https://www.nature.com/nature/articles?type=rss

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| Nature本誌 | `https://www.nature.com/nature.rss` | 全分野の最新研究・ニュース |
| Nature Physics | `https://www.nature.com/nphys.rss` | 物理学 |
| Nature Materials | `https://www.nature.com/nmat.rss` | 材料科学 |
| Nature Machine Intelligence | `https://www.nature.com/natmachintell.rss` | AI、機械学習、ロボティクス |

## フィード形式と取得上の注意

- RSS 1.0 (RDF) 形式 + Dublin Core拡張 + PRISM拡張（名前空間: `http://prismstandard.org/namespaces/basic/2.0/`）
- 著者が複数の場合、`dc:creator` が複数出現する

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `content:encoded` | description | HTML形式 |
| `dc:date` | published_at | ISO 8601形式 |
| `dc:creator` | meta.authors | 複数あり、配列で保持 |
| `prism:doi` | meta.doi | DOI識別子 |
| `prism:publicationName` | meta.journal | ジャーナル名 |

## 表示名

`Nature`
