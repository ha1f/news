# Wired

- **ソースID**: wired
- **TTL**: 12時間
- **説明**: テクノロジーが文化・社会に与える影響を深掘りする老舗メディア

## 仕様リンク

- https://www.wired.com/about/rss-feeds/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://www.wired.com/feed/rss` | 全カテゴリの最新記事 |
| ビジネス | `https://www.wired.com/feed/category/business/latest/rss` | ビジネス、経済、スタートアップ |
| サイエンス | `https://www.wired.com/feed/category/science/latest/rss` | 科学、研究、宇宙 |
| ギア | `https://www.wired.com/feed/category/gear/latest/rss` | ガジェット、レビュー、製品 |
| セキュリティ | `https://www.wired.com/feed/category/security/latest/rss` | サイバーセキュリティ、プライバシー |
| AI | `https://www.wired.com/feed/tag/ai/latest/rss` | AI、機械学習、生成AI |

## フィード形式と取得上の注意

- RSS 2.0 形式
- 認証不要
- Bot制限がある場合はUser-Agentヘッダを設定すること
- 記事は全て英語

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

`Wired`
