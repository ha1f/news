# Product Hunt

- **ソースID**: producthunt
- **TTL**: 12時間
- **説明**: 新しいプロダクト・ツールの発見に特化。開発者向けツールやAI系プロダクトが多い

## 仕様リンク

- https://help.producthunt.com/en/articles/484970-does-product-hunt-have-an-rss-feed
- https://api.producthunt.com/v2/docs

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://www.producthunt.com/feed` | 全カテゴリの最新プロダクト |

## フィード形式と取得上の注意

- Atom 形式
- フィードにはupvote数が含まれない（APIなら取得可能だが認証が必要）
- 認証不要
- プロダクトの tagline が title や summary に含まれる

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link[@rel="alternate"]` | url | Atom形式のリンク |
| `summary` | description | |
| `published` | published_at | ISO 8601形式 |
| `author > name` | meta.author | |

## 表示名

`PH`
