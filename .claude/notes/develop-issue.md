# develop-issue 向け repo ノート

develop-issue スキルが参照する repo 固有の情報。手順は SKILL.md 側、ここには this repo でしか通用しない事実だけ書く。

## 環境

- CI は無い。PR に checks が付かないことを確認できれば green 扱いでよい
- Jekyll ベースの静的サイト (`_config.yml`, `_posts/`, `index.md`)。GitHub Pages で公開
- `.gitignore` は toptal の macOS テンプレート + `.claude/` 用セクションで構成済み
- theme は `minima` を指定しているが、GitHub Pages が実際にビルドに使うバージョンは 2.5.1 に固定 ([pages.github.com/versions](https://pages.github.com/versions/) で確認)。minima 3.x系の設定書式 (`minima.social_links` の配列、`author:` のハッシュ形式等) は 2.5.1 では無視されるかそのまま文字列化されて壊れる。`_config.yml` の `minima.*` / theme依存の設定を変更するときは [2.5.1 のテンプレ実物](https://github.com/jekyll/minima/tree/v2.5.1) と照合してから進める。ローカルに Ruby/Jekyll/minima gem が無い環境ではビルド確認ができないため、テンプレ照合とライブサイト (https://ha1f.github.io/news/) の実HTML確認が実質的な green 条件になる

## 検証コマンド

- gitignore が効いているか: `git check-ignore -v <path>` (ネストしたパスでも試す)
- 過去に意図しないファイルが commit されていないか: `git ls-files | grep <pattern>` / `git log --all --oneline -- "**/<pattern>"`
