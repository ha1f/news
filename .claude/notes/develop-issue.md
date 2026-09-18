# develop-issue 向け repo ノート

develop-issue スキルが参照する repo 固有の情報。手順は SKILL.md 側、ここには this repo でしか通用しない事実だけ書く。

## 環境

- Jekyll ベースの静的サイト (`_config.yml`, `_posts/`, `index.md`)。GitHub Pages で公開
- CI は `.github/workflows/jekyll-build-check.yml`（PR の base が `main` のときだけ走る）。ビルド + Playwright のスクリーンショット取得までを行い、artifact に残す
  - **base が main でない PR（スタックした PR）には CI が付かない**。base の付け替えだけでは workflow は起動しない（`edited` は既定の trigger 外）ので、base ブランチのマージ後に rebase して push（`synchronize`）すると走る
- `.gitignore` は toptal の macOS テンプレート + `.claude/` 用セクションで構成済み
- theme は `minima` を指定しているが、GitHub Pages が実際にビルドに使うバージョンは 2.5.1 に固定 ([pages.github.com/versions](https://pages.github.com/versions/) で確認)。minima 3.x系の設定書式 (`minima.social_links` の配列、`author:` のハッシュ形式等) は 2.5.1 では無視されるかそのまま文字列化されて壊れる。`_config.yml` の `minima.*` / theme依存の設定を変更するときは [2.5.1 のテンプレ実物](https://github.com/jekyll/minima/tree/v2.5.1) と照合してから進める
- `gh` CLI は無い。GitHub の操作は MCP ツール（`mcp__github__*`）で行う

## ローカルでビルド・描画確認する（Gemfile は無い）

`gem install` で数分。GitHub Pages のビルドを十分に再現でき、UI 変更は必ずここまでやる:

```bash
gem install --no-document 'jekyll:3.9.5' 'minima:2.5.1' 'jekyll-sitemap' 'kramdown-parser-gfm'
export PATH="/opt/rbenv/versions/3.3.6/bin:$PATH"   # gem の EXECUTABLE DIRECTORY
jekyll build -d /tmp/_site
```

描画確認は Playwright。ブラウザは導入済み（`/opt/pw-browsers`）だが npm の playwright が要求する build 番号と違うので、`executablePath` で明示する:

```bash
npm install playwright@1.62.1          # CI がピンしているバージョン
# chromium.launch({ executablePath: '/opt/pw-browsers/chromium' })
```

- 配信は `python3 -m http.server <port> --directory <dir>` で。`baseurl: /news` を再現するため `<dir>/news/` に `_site` の中身を置く（CI の workflow と同じやり方）
- dark mode は `browser.newContext({ colorScheme: 'dark' })` で。`newPage({ colorScheme })` は効かない
- CI の screenshot artifact は認証なしでは取得できない。ローカルで同じ Chromium・同じ viewport で撮れば代用になる（`.claude/rules/ui-changes.md` の「artifact が取得できない場合」に該当する）

## 検証コマンド

- 保護パス判定: `python3 .claude/scripts/check_protected_paths.py --diff origin/main`（`ui_changes` が出たら `.claude/rules/ui-changes.md` に従う）
- 見出しリンクの着地点: `python3 .claude/scripts/check_article_anchors.py <_site>`
- 読みどころの欠落: `python3 .claude/scripts/check_article_notes.py`
- ソース表記と定義の一致: `python3 .claude/scripts/check_source_hints.py`
- gitignore が効いているか: `git check-ignore -v <path>`
- 意図しないファイルの混入: `git ls-files | grep <pattern>`

## この repo の癖

- `.claude/skills/` 配下のスキルは repo 自身に置かれている。branch を切り替えても開始時に読んだ版に従う
- スキルのスクリプトは「エージェントの Bash から起動すると stdin が非 tty」を踏まえた分岐になっているか確認する（`not sys.stdin.isatty()` で stdin モードに入る実装は必ず壊れる）
