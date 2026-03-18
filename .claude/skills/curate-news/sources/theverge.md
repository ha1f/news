# The Verge

- **ソースID**: theverge
- **TTL**: 12時間
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

- フィード形式は取得時に判定すること（RSS 2.0 または Atom）
- 認証不要
- Bot制限がある場合はUser-Agentヘッダを設定すること
- 記事は全て英語

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` / `summary` | description | |
| `pubDate` / `published` | published_at | |
| `author` / `dc:creator` | meta.author | |
| `category` | meta.categories | 複数あり、配列で保持 |

## 表示名

`The Verge`
