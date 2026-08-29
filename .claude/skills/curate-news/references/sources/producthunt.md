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

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 要連絡（ToS は非商用限定、API は「商用は hello@producthunt.com へ」）
- **広告掲載での利用**: 要連絡（同上）
- **義務**: 帰属表示＋Product Hunt へのリンクバック（要請ベース）
- **制約**: ToS はクロール禁止（/feed の位置付けは規約上不明確）
- **根拠**: https://www.producthunt.com/legal?section=terms-of-service （確認日 2026-08-28）

## 実装

[`feed_sources/producthunt.py`](../../scripts/feed_sources/producthunt.py)
