# TechCrunch

- **ソースID**: techcrunch
- **TTL**: 12時間
- **説明**: 米国最大級のテック系メディア。スタートアップ・AI・VC情報に強い

## 仕様リンク

- https://techcrunch.com/feed/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://techcrunch.com/feed/` | 全カテゴリの最新記事 |
| AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | AI、機械学習、生成AI |
| スタートアップ | `https://techcrunch.com/category/startups/feed/` | スタートアップ、資金調達 |
| Apps | `https://techcrunch.com/category/apps/feed/` | アプリ、モバイル |
| セキュリティ | `https://techcrunch.com/category/security/feed/` | サイバーセキュリティ |
| ベンチャー | `https://techcrunch.com/category/venture/feed/` | VC、投資、M&A |

## フィード形式と取得上の注意

- RSS 2.0 形式
- `dc:creator` に著者名
- 1記事に複数の `category` タグが付く
- 認証不要、レート制限は緩い
- 記事は全て英語

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

`TechCrunch`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 要判断（RSS 規約に規定なし、一般 ToS は非商用限定）
- **広告掲載での利用**: 要判断（フィードへの広告組込みは明示禁止。サイト上の広告併置の可否は不明確）
- **義務**: TechCrunch への帰属表示＋原文への直リンク（明文義務）
- **制約**: フィード内容の改変禁止（見出しリライトの該当性は要判断 → #241）
- **根拠**: https://techcrunch.com/rss-terms-of-use/ （確認日 2026-08-28）

## 実装

[`feed_sources/techcrunch.py`](../../scripts/feed_sources/techcrunch.py)
