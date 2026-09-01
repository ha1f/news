# Qiita

- **ソースID**: qiita
- **TTL**: 720分
- **説明**: 日本最大級のエンジニア向け技術記事共有プラットフォーム

## 仕様リンク

- https://qiita.com/about#feed

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 人気記事 | `https://qiita.com/popular-items/feed` | 全タグの人気記事 |
| Python | `https://qiita.com/tags/python/feed` | Python全般 |
| JavaScript | `https://qiita.com/tags/javascript/feed` | JavaScript、フロントエンド |
| Swift | `https://qiita.com/tags/swift/feed` | Swift、iOS開発 |
| AI | `https://qiita.com/tags/ai/feed` | AI、機械学習 |
| LLM | `https://qiita.com/tags/llm/feed` | LLM、生成AI |
| Docker | `https://qiita.com/tags/docker/feed` | コンテナ、DevOps |
| AWS | `https://qiita.com/tags/aws/feed` | AWS、クラウド |

## フィード形式と取得上の注意

- Atom 1.0 形式
- タグ別フィードのURLパターン: `https://qiita.com/tags/{タグ名}/feed`
- `content` はHTML形式

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link[rel="alternate"]/@href` | url | |
| `content` | description | HTML形式 |
| `published` | published_at | ISO 8601形式 |
| `author > name` | meta.author | |

## 表示名

`Qiita`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 要許諾（「転用・売却・再販」禁止に該当のおそれ）
- **広告掲載での利用**: 不可（データを元にしたサービスへの広告設置収益化は規約違反と公式ヘルプが明言）
- **義務**: 規定なし（著作権は投稿者に留保のため原文直リンクを維持）
- **制約**: スクレイピング不許可（フィード/API は提供）
- **根拠**: https://qiita.com/terms / https://help.qiita.com/ja/articles/points-when-creating-application-using-qiita-data （確認日 2026-08-28）

## 実装

[`feed_sources/qiita.py`](../../scripts/feed_sources/qiita.py)
