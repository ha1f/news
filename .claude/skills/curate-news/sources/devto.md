# dev.to

- **ソースID**: devto
- **TTL**: 12時間
- **説明**: 開発者コミュニティプラットフォーム。チュートリアル、技術記事、キャリア系の投稿が多い

## 仕様リンク

- https://dev.to/feed

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://dev.to/feed` | 全カテゴリの最新記事 |
| JavaScript | `https://dev.to/feed/tag/javascript` | JavaScript、フロントエンド |
| Python | `https://dev.to/feed/tag/python` | Python、データサイエンス |
| AI | `https://dev.to/feed/tag/ai` | AI、機械学習 |
| iOS | `https://dev.to/feed/tag/ios` | iOS、Swift |
| DevOps | `https://dev.to/feed/tag/devops` | CI/CD、インフラ、コンテナ |

## フィード形式と取得上の注意

- RSS 2.0 + Dublin Core拡張
- 認証不要、レート制限は緩い
- 1記事に複数の `category` タグが付く
- 記事は英語が中心

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:creator` | meta.author | |
| `category` | meta.categories | 複数あり、配列で保持 |

## 表示名

`dev.to`
