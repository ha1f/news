# Publickey

- **ソースID**: publickey
- **TTL**: 12時間
- **説明**: 日本のエンタープライズIT・クラウド・開発ツール系ニュースサイト。更新頻度は低めだが質が高い

## 仕様リンク

- https://www.publickey1.jp/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://www.publickey1.jp/atom.xml` | クラウド、開発ツール、DB、コンテナ、サーバレス |

## フィード形式と取得上の注意

- Atom 形式（RSS 2.0 ではない）
- `category` タグでカテゴリとタグの2種類の分類あり（`scheme="#category"` と `scheme="#tag"`）
- 認証不要
- 更新頻度が低い（1日数本程度）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link[@rel="alternate"]` | url | Atom形式のリンク |
| `summary` | description | |
| `published` | published_at | ISO 8601形式 |
| `author > name` | meta.author | |
| `category[@scheme="#category"]` | meta.categories | 複数あり |

## 表示名

`Publickey`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 規定なし（個人運営。収益化時は直接確認が現実的）
- **広告掲載での利用**: 規定なし
- **義務**: 規定なし
- **制約**: なし
- **根拠**: https://www.publickey1.jp/about-us.html （確認日 2026-08-28、規約不存在を確認）

## 実装

[`feed_sources/publickey.py`](../../scripts/feed_sources/publickey.py)
