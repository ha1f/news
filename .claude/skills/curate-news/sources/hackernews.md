# Hacker News

- **ソースID**: hackernews
- **TTL**: 12時間
- **説明**: Y Combinator運営のテック系ニュースサイト。英語圏のテックトレンドの最前線

## 仕様リンク

- https://github.com/HackerNewsAPI/HN-API（公式 Firebase API ドキュメント）

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| トップ | `https://hacker-news.firebaseio.com/v0/topstories.json` | 全ジャンルの人気記事（投票数順） |
| 最新 | `https://hacker-news.firebaseio.com/v0/newstories.json` | 全ジャンルの最新投稿 |
| ベスト | `https://hacker-news.firebaseio.com/v0/beststories.json` | 長期的に高評価の記事 |
| Ask HN | `https://hacker-news.firebaseio.com/v0/askstories.json` | コミュニティへの質問・相談、キャリア、技術選定 |
| Show HN | `https://hacker-news.firebaseio.com/v0/showstories.json` | 個人開発、プロダクト紹介、OSS |

## フィード形式と取得上の注意

- JSON API（RSS ではない）
- **2段階取得が必要**: 一覧APIはID配列のみ返すため、各アイテムを個別に取得する（上位20件）
- 個別取得URL: `https://hacker-news.firebaseio.com/v0/item/{id}.json`
- 個別取得は並列化推奨（python3 の `ThreadPoolExecutor` や `subprocess` 等）
- 認証不要、レート制限は緩い

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `url` | url | 未設定時は `https://news.ycombinator.com/item?id={id}` |
| `time` | published_at | UNIXタイムスタンプ → ISO 8601 に変換 |
| `score` | meta.score | |
| `descendants` | meta.comments | |

## 表示名

`HN`
