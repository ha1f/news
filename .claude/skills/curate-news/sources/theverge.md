# The Verge

- **ソースID**: theverge
- **TTL**: 720分
- **説明**: テック・科学・エンタメを幅広くカバーする米国大手メディア。深掘りレビューやオピニオンにも強い

## 仕様リンク

- https://www.theverge.com/rss/index.xml

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://www.theverge.com/rss/index.xml` | 全カテゴリの最新記事 |
| テック | `https://www.theverge.com/rss/tech/index.xml` | ガジェット、ソフトウェア、プラットフォーム |
| エンタメ | `https://www.theverge.com/rss/entertainment/index.xml` | 映画、ゲーム、ストリーミング |
| 環境 | `https://www.theverge.com/rss/environment/index.xml` | 気候変動、エネルギー |
| 特集 | `https://www.theverge.com/rss/features/index.xml` | 長文記事、深掘り分析 |
| 車 | `https://www.theverge.com/rss/cars/index.xml` | EV、自動運転、モビリティ |

## フィード形式と取得上の注意

- Atom 形式
- User-Agentヘッダを設定する（Bot制限あり）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link[@rel="alternate"]` | url | Atom形式のリンク |
| `summary` | description | |
| `published` | published_at | ISO 8601形式 |
| `author > name` | meta.author | |
| `category` | meta.categories | 複数あり、配列で保持 |

## 表示名

`The Verge`
