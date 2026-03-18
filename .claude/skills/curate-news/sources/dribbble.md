# Dribbble

- **ソースID**: dribbble
- **TTL**: 24時間
- **説明**: デザイナー向けコミュニティ。Stories（記事）のRSSフィードを提供

## 仕様リンク

- https://dribbble.com/stories

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| Stories | `https://dribbble.com/stories.rss` | デザイントレンド、インタビュー、チュートリアル |

## フィード形式と取得上の注意

- RSS 2.0 形式
- 認証不要
- ショット（作品投稿）のRSSは提供されていない。Stories記事のみ
- 記事は全て英語

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `category` | meta.categories | 複数あり、配列で保持 |

## 表示名

`Dribbble`
