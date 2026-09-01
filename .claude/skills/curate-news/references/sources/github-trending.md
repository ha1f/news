# GitHub Trending

- **ソースID**: github-trending
- **TTL**: 1440分
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

- RSS 2.0 + Media RSS拡張（名前空間: `http://search.yahoo.com/mrss/`）
- GitHub Pages経由のため安定性はリポジトリに依存

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | `owner/repo` 形式 |
| `link` | url | GitHubリポジトリURL |
| `description` | description | HTML形式（リポジトリ説明・スター数等を含む） |
| `pubDate` | published_at | |
| `media:content/@url` | meta.image_url | リポジトリのOGP画像 |

## 表示名

`GitHub Trending`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 要判断（GitHub AUP の利用目的列挙は研究・アーカイブのみ）
- **広告掲載での利用**: 要判断（同上）
- **義務**: リポジトリへのリンク維持（説明文は各リポジトリオーナーの著作物）
- **制約**: 経由サービス（GitHubTrendingRSS、個人運営・MIT）依存。停止時はフォーク自前ホストか GitHub API へ切替
- **根拠**: https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies （確認日 2026-08-28）

## 実装

[`feed_sources/github_trending.py`](../../scripts/feed_sources/github_trending.py)
