# Gigazine

- **ソースID**: gigazine
- **TTL**: 720分
- **説明**: 日本の老舗ニュースサイト。テック、科学、食、エンタメまで幅広くカバー

## 仕様リンク

- https://gigazine.net/news/rss_2.0/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://gigazine.net/news/rss_2.0/` | 全カテゴリの最新記事 |

## フィード形式と取得上の注意

- RSS 2.0 形式 + Dublin Core拡張
- `dc:subject` にカテゴリ情報が含まれる
- User-Agentヘッダを設定する（未設定だと403エラー）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:subject` | meta.categories | カテゴリ |

## 表示名

`GIGAZINE`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 規定なし（規約ページ不存在。収益化時は要問い合わせ）
- **広告掲載での利用**: 規定なし（同上）
- **義務**: 規定なし
- **制約**: robots.txt に Crawl-delay 100（日次取得は問題なし）
- **根拠**: https://gigazine.net/news/about/ （確認日 2026-08-28、規約不存在を確認）

## 実装

[`feed_sources/gigazine.py`](../../scripts/feed_sources/gigazine.py)
