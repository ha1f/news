# ITmedia

- **ソースID**: itmedia
- **TTL**: 720分
- **説明**: 日本の大手IT系ニュースサイト。エンタープライズIT、AI、セキュリティなど幅広い

## 仕様リンク

- https://corp.itmedia.co.jp/media/

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| 全体 | `https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml` | ITmedia全媒体の最新記事 |

## フィード形式と取得上の注意

- RSS 2.0 形式
- 記事数が多い（約50件）

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |

## 表示名

`ITmedia`

## 利用条件

- **AI利用**: 可（規定なし）
- **商用利用（課金）**: 要許諾（私的利用のみ無償、商用は基本有償）
- **広告掲載での利用**: 要許諾（同上）
- **義務**: 発信元（配信元媒体）の表示
- **制約**: 改変・一部削除・抜粋転載・翻案の禁止（見出しリライトの該当性は要判断 → #241）
- **根拠**: https://corp.itmedia.co.jp/media/rss_condition/ （確認日 2026-08-28）

## 実装

[`feed_sources/itmedia.py`](../../scripts/feed_sources/itmedia.py)
