# develop-issue 向け repo ノート

この repo で作業するときの環境メモ。手順は各スキルの SKILL.md 側、ここには this repo・この実行環境でしか通用しない事実だけ書く。CLAUDE.md からここを指しているので、毎回調べ直さずにここを読む。

書いてある内容が実際と違っていたら、その run で直す（古いまま残すと次の run を誤導する）。**ここに載せる検証コマンドは main に実在するものだけにする。** 未マージの PR にしかないスクリプトを載せると、次の run がそのまま叩いて `No such file or directory` を踏む。

## 環境

- Jekyll ベースの静的サイト (`_config.yml`, `_posts/`, `index.md`)。GitHub Pages で公開
- CI は `.github/workflows/jekyll-build-check.yml`（PR の base が `main` のときだけ走る）。ビルド + Playwright のスクリーンショット取得までを行い、artifact に残す
  - **base が main でない PR（スタックした PR）には CI が付かない**。base の付け替えだけでは workflow は起動しない（`edited` は既定の trigger 外）ので、base ブランチのマージ後に rebase して push（`synchronize`）すると走る
- `.gitignore` は toptal の macOS テンプレート + `.claude/` 用セクションで構成済み
- theme は `minima` を指定しているが、GitHub Pages が実際にビルドに使うバージョンは 2.5.1 に固定 ([pages.github.com/versions](https://pages.github.com/versions/) で確認)。minima 3.x系の設定書式 (`minima.social_links` の配列、`author:` のハッシュ形式等) は 2.5.1 では無視されるかそのまま文字列化されて壊れる。`_config.yml` の `minima.*` / theme依存の設定を変更するときは [2.5.1 のテンプレ実物](https://github.com/jekyll/minima/tree/v2.5.1) と照合してから進める
- `gh` CLI は無い。GitHub の操作は MCP ツール（`mcp__github__*`）で行う

## ローカルでビルド・描画確認する（Gemfile は無い）

`gem install` で数分。GitHub Pages のビルドを十分に再現でき、UI 変更は必ずここまでやる。`_config.yml` の `plugins` に並ぶ gem が1つでも欠けると `Dependency Error` で落ちるので、まとめて入れる:

```bash
gem install --no-document jekyll:3.9.5 minima:2.5.1 jekyll-feed jekyll-seo-tag \
    jekyll-sitemap jekyll-paginate kramdown-parser-gfm
jekyll build -d _site
```

ruby は 3.3.6 で、`jekyll` は既定の PATH（rbenv の shims）から引ける。`PATH` を足す必要はない。

描画確認は Playwright。**グローバルに入っている `playwright` をそのまま使う**（`/opt/pw-browsers` の chromium と組み合わせで動く）:

```bash
playwright screenshot --browser chromium --full-page \
  --viewport-size 375,812 --color-scheme dark <URL> out.png
```

`npx playwright@<CI のバージョン>` は使えない。CI がピンしている版は `/opt/pw-browsers` にあるものと違う build 番号を要求し、`Executable doesn't exist at /opt/pw-browsers/chromium_headless_shell-<別番号>/...` で落ちる。

- 配信は `python3 -m http.server <port> --directory <dir>` で。`baseurl: /news` を再現するため `<dir>/news/` に `_site` の中身を置く（CI の workflow と同じやり方）
- Node の API を直接使う場合、dark mode は `browser.newContext({ colorScheme })` か `browser.newPage({ colorScheme })` で。`context.newPage({ colorScheme })` は**黙って無視される**（実測）

### CI の screenshot artifact を取る

push 後はこちらも見る。ローカルで撮るのは1〜2枚だが、CI は6ページ × light/dark をデスクトップ幅とモバイル幅で撮っている。MCP 経由なら認証込みで取得できる（実測）:

```
mcp__github__actions_list(method=list_workflow_run_artifacts, resource_id=<run id>)
mcp__github__actions_get(method=download_workflow_run_artifact, resource_id=<artifact id>)
  → 期限付きの署名 URL が返る。curl でそのまま落として unzip
```

ローカルの Chromium は CI と同じ版ではない（ローカル 1.56.1 / `chromium-1194`、CI は 1.62.1 ピン）ので、最終確認は artifact のほうが CI の見え方に近い。

## 検証コマンド

- 保護パス判定: `python3 .claude/scripts/check_protected_paths.py --diff origin/main`（`ui_changes` が出たら `.claude/rules/ui-changes.md` に従う）
- 見出しリンクの着地点: `python3 .claude/scripts/check_article_anchors.py <_site>`
- 読みどころの欠落: `python3 .claude/scripts/check_article_notes.py`
- ユニットテスト: スクリプトと同じディレクトリで `python3 -m unittest discover -p 'test_*.py'`。
  置き場が分かれているので、触ったものを個別に回す（repo ルートからの discover は 0 件になる）:
  `.claude/scripts` / `.claude/skills/select-and-develop/scripts` /
  `.claude/skills/review-and-merge/scripts` / `.claude/skills/evaluate-and-triage/scripts` /
  `.claude/skills/curate-news/scripts`
- gitignore が効いているか: `git check-ignore -v <path>`
- 意図しないファイルの混入: `git ls-files | grep <pattern>`

## この repo の癖

- `.claude/skills/` 配下のスキルは repo 自身に置かれている。branch を切り替えても開始時に読んだ版に従う
- スキルのスクリプトは「エージェントの Bash から起動すると stdin が非 tty」を踏まえた分岐になっているか確認する（`not sys.stdin.isatty()` で stdin モードに入る実装は必ず壊れる）
- 毎朝9時のキュレーションで当日分の投稿が main に入る。`_posts/` の中身に関わるルールを足す PR は、rebase のたびに当日分を揃え直す必要がある
- squash マージされた PR にスタックしたブランチは `git rebase --onto origin/main <スタック元の最後の commit>` で自分の commit だけ載せ替える（素直な rebase は squash 済みの内容と全面衝突する）
