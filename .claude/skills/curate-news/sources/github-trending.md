# GitHub Trending

- **ソースID**: github-trending
- **TTL**: 24時間
- **説明**: GitHubでトレンドのリポジトリ。サードパーティRSS（mshibanami/GitHubTrendingRSS）経由で取得

## 仕様リンク

- https://github.com/mshibanami/GitHubTrendingRSS

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 日次・全言語 | `https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml` | 全言語のデイリートレンド |
| 週次・全言語 | `https://mshibanami.github.io/GitHubTrendingRSS/weekly/all.xml` | 全言語のウィークリートレンド |
| 日次・Swift | `https://mshibanami.github.io/GitHubTrendingRSS/daily/swift.xml` | Swiftのデイリートレンド |
| 日次・Python | `https://mshibanami.github.io/GitHubTrendingRSS/daily/python.xml` | Pythonのデイリートレンド |
| 日次・TypeScript | `https://mshibanami.github.io/GitHubTrendingRSS/daily/typescript.xml` | TypeScriptのデイリートレンド |

## フィード形式と取得上の注意

- RSS 2.0 + Media RSS拡張
- 認証不要
- GitHub Pages経由のため安定性はリポジトリに依存
- `description` はHTML形式でリポジトリの説明・スター数等を含む

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | `owner/repo` 形式 |
| `link` | url | GitHubリポジトリURL |
| `description` | description | HTML形式、テキスト抽出が必要 |
| `pubDate` | published_at | |
| `media:content` | meta.image_url | リポジトリのOGP画像 |

## 表示名

`GitHub Trending`
