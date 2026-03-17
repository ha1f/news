# Zenn

- **ソースID**: zenn
- **TTL**: 24時間
- **説明**: 日本のエンジニア向け技術記事プラットフォーム。トピック別フィードが充実

## 仕様リンク

- https://zenn.dev/faq（フィード仕様の公式情報）

## カテゴリとフィードURL

| カテゴリ | フィードURL | 含まれるトピック |
|---------|-----------|----------------|
| トレンド（全体） | `https://zenn.dev/feed` | 全トピックのトレンド記事 |
| Swift | `https://zenn.dev/topics/swift/feed` | Swift言語、iOS/macOS開発 |
| iOS | `https://zenn.dev/topics/ios/feed` | iOSアプリ開発、UIKit、SwiftUI |
| TypeScript | `https://zenn.dev/topics/typescript/feed` | TypeScript、型システム |
| React | `https://zenn.dev/topics/react/feed` | React、Next.js、フロントエンド |
| Python | `https://zenn.dev/topics/python/feed` | Python、データ分析、スクリプト |
| AI/機械学習 | `https://zenn.dev/topics/machinelearning/feed` | 機械学習、LLM、生成AI |
| インフラ | `https://zenn.dev/topics/infrastructure/feed` | AWS、Docker、Kubernetes、CI/CD |

## フィード形式と取得上の注意

- RSS 2.0 形式
- `dc:` 名前空間あり（`dc:creator` に著者名）
- 認証不要、レート制限なし

## フィールドマッピング

| ソースのフィールド | キャッシュのフィールド | 備考 |
|---|---|---|
| `title` | title | |
| `link` | url | |
| `description` | description | |
| `pubDate` | published_at | RFC 2822形式 |
| `dc:creator` | meta.author | |

## 表示名

`Zenn`
