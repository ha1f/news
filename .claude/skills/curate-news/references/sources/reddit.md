# Reddit

- **ソースID**: reddit
- **TTL**: 12時間
- **説明**: 世界最大のフォーラム型SNS。サブレディットごとに専門コミュニティがある

## 仕様リンク

- https://www.reddit.com/wiki/rss/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| programming | `https://www.reddit.com/r/programming/hot/.rss` | プログラミング全般 |
| swift | `https://www.reddit.com/r/swift/hot/.rss` | Swift言語、iOS開発 |
| MachineLearning | `https://www.reddit.com/r/MachineLearning/hot/.rss` | 機械学習、AI研究 |
| devops | `https://www.reddit.com/r/devops/hot/.rss` | DevOps、CI/CD、インフラ |
| ExperiencedDevs | `https://www.reddit.com/r/ExperiencedDevs/hot/.rss` | シニアエンジニア向け議論 |

## フィード形式と取得上の注意

- Atom 形式（RSS 2.0 ではない）
- **User-Agent ヘッダが必須**（汎用UA `curl` だとレート制限が厳しい）。ブラウザUAを指定する:
  ```
  curl -s -H "User-Agent: Mozilla/5.0" '{フィードURL}'
  ```
- 非認証で10リクエスト/分の制限あり。キャッシュを活用すること
- スコア（upvote数）はAtomフィードに含まれない

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link[@rel="alternate"]` | url | Atom形式のリンク |
| `updated` | published_at | ISO 8601形式 |
| `author > name` | meta.author | |
| `content` | description | HTML含む場合あり、テキスト抽出推奨 |

## 表示名

`Reddit`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 不可（書面合意なき商用利用を禁止）
- **広告掲載での利用**: 不可（同上）
- **義務**: Data API 利用時は Reddit 指定の帰属表示
- **制約**: robots.txt が全面 Disallow で自動取得の許諾根拠が曖昧（要判断）。UGC の改変禁止（表示整形を除く）
- **根拠**: https://redditinc.com/policies/user-agreement （確認日 2026-08-28）

## 実装

[`feed_sources/reddit.py`](../../scripts/feed_sources/reddit.py)
