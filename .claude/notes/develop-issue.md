# develop-issue 向け repo ノート

develop-issue スキルが参照する repo 固有の情報。手順は SKILL.md 側、ここには this repo でしか通用しない事実だけ書く。

## 環境

- CI は無い。PR に checks が付かないことを確認できれば green 扱いでよい
- Jekyll ベースの静的サイト (`_config.yml`, `_posts/`, `index.md`)。GitHub Pages で公開
- `.gitignore` は toptal の macOS テンプレート + `.claude/` 用セクションで構成済み

## 検証コマンド

- gitignore が効いているか: `git check-ignore -v <path>` (ネストしたパスでも試す)
- 過去に意図しないファイルが commit されていないか: `git ls-files | grep <pattern>` / `git log --all --oneline -- "**/<pattern>"`
