# Qiita

- **ソースID**: qiita
- **TTL**: 12時間
- **説明**: 日本最大級のエンジニア向け技術記事共有プラットフォーム

## 仕様リンク

- https://qiita.com/

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
- 認証不要
- タグ別フィードのURLは `https://qiita.com/tags/{タグ名}/feed`
- 日本語記事が中心

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
