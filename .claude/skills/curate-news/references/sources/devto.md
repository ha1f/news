# dev.to

- **ソースID**: devto
- **TTL**: 720分
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
- 1記事に複数の `category` タグが付く

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

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 不可（personal, non-commercial 限定の明文）
- **広告掲載での利用**: 規定なし（商用禁止の文言に含まれるおそれ）
- **義務**: 規定なし（著作権は投稿者にあるため原文直リンクを維持）
- **制約**: 複製・public display 禁止の文言あり（現行形態への適用は要判断）
- **根拠**: https://dev.to/terms （確認日 2026-08-28）

## 実装

[`feed_sources/devto.py`](../../scripts/feed_sources/devto.py)
