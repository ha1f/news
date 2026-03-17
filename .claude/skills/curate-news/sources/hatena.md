# はてなブックマーク

- **ソースID**: hatena
- **TTL**: 12時間
- **説明**: 日本最大のソーシャルブックマークサービス。ブックマーク数で記事の注目度がわかる

## 仕様リンク

- https://b.hatena.ne.jp/help/entry/rss

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| テクノロジー | `https://b.hatena.ne.jp/hotentry/it.rss` | プログラミング、AI、インフラ、開発ツール、テック企業 |
| 総合 | `https://b.hatena.ne.jp/hotentry.rss` | 全カテゴリの人気記事 |
| 世の中 | `https://b.hatena.ne.jp/hotentry/social.rss` | 社会問題、事件、働き方 |
| 政治経済 | `https://b.hatena.ne.jp/hotentry/economics.rss` | 政治、経済、ビジネス、スタートアップ |
| 暮らし | `https://b.hatena.ne.jp/hotentry/life.rss` | 生活、健康、料理、住居 |
| 学び | `https://b.hatena.ne.jp/hotentry/knowledge.rss` | 教育、科学、歴史、語学、研究 |
| エンタメ | `https://b.hatena.ne.jp/hotentry/entertainment.rss` | ゲーム、アニメ、映画、音楽、マンガ |

## フィード形式と取得上の注意

- RSS 1.0 (RDF) 形式
- XML名前空間の指定が必須（`rss`, `dc`, `hatena`）
- 認証不要、レート制限なし

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `rss:title` | title | |
| `rss:link` | url | |
| `rss:description` | description | |
| `dc:date` | published_at | ISO 8601 |
| `hatena:bookmarkcount` | meta.bookmarks | 整数に変換 |

## 表示名

`はてブ`
