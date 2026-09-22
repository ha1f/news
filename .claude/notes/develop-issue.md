# repo ノート（環境・検証・この repo の癖）

この repo で作業するときの環境メモ。develop-issue が正本として読むが、「この repo の癖」は review など他のステージも対象。手順は各スキルの SKILL.md 側、ここには this repo・この実行環境でしか通用しない事実だけ書く。CLAUDE.md からここを指しているので、毎回調べ直さずにここを読む。

書いてある内容が実際と違っていたら、その run で直す（古いまま残すと次の run を誤導する）。**ここに載せる検証コマンドは main に実在するものだけにする。** 未マージの PR にしかないスクリプトを載せると、次の run がそのまま叩いて `No such file or directory` を踏む。

## 環境

- Jekyll ベースの静的サイト (`_config.yml`, `_posts/`, `index.md`)。GitHub Pages で公開
- CI は `.github/workflows/jekyll-build-check.yml`（PR の base が `main` のときだけ走る）。ビルド + Playwright のスクリーンショット取得までを行い、artifact に残す
  - **base が main でない PR（スタックした PR）には CI が付かない**。base の付け替えだけでは workflow は起動しない（`edited` は既定の trigger 外）ので、base ブランチのマージ後に rebase して push（`synchronize`）すると走る
- `.gitignore` は toptal の macOS テンプレート + `.claude/` 用セクションで構成済み
- theme は `minima` を指定しているが、GitHub Pages が実際にビルドに使うバージョンは 2.5.1 に固定 ([pages.github.com/versions](https://pages.github.com/versions/) で確認)。minima 3.x系の設定書式 (`minima.social_links` の配列、`author:` のハッシュ形式等) は 2.5.1 では無視されるかそのまま文字列化されて壊れる。`_config.yml` の `minima.*` / theme依存の設定を変更するときは [2.5.1 のテンプレ実物](https://github.com/jekyll/minima/tree/v2.5.1) と照合してから進める
- `gh` CLI は無い。GitHub の操作は MCP ツール（`mcp__github__*`）で行う
  - ただし cloud proxy が素の HTTPS にも GitHub 認証を注入するので、**REST の読み取りは `curl` / Python `urllib` で `https://api.github.com/...` を直接叩ける**（実測 2026-09-20: `X-RateLimit-Limit: 15000`、`Link` ヘッダのページネーション有効。status issue のコメント 500件超も `per_page=100` で辿れる）。MCP のレスポンス上限や `--stdin` の往復を避けたい大量取得はこちら。`/repos/{owner}/{repo}/collaborators`・`/repos/{owner}/{repo}/pages`・GraphQL は proxy が 403 を返すので MCP を使う。書き込みは MCP に統一する
    - **`Link` ヘッダの `next` URL をそのまま辿らない。** GitHub が返す URL は `/repositories/{id}/...` 形式で、proxy がこの形を 403 で弾く（実測 2026-09-20: `Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy`）。ページ番号だけ次に進め、`/repos/{owner}/{repo}/...&page=N` の形で自分で組み立て直す
  - `check_state.py` と `select_issues.py` はこの実測を踏まえ、引数なし実行時に `gh` があれば `gh`、無ければこの REST 直叩きを自動で使う（#356）。`repos/{owner}/{repo}/` の `owner`/`repo` は `git config --get remote.origin.url` から解決する（gh の `gh api repos/{owner}/{repo}/...` が内部でやっている補完を手動で行う）

## ローカルでビルド・描画確認する（Gemfile は無い）

`gem install` で数分。GitHub Pages のビルドを十分に再現でき、UI 変更は必ずここまでやる。`_config.yml` の `plugins` に並ぶのは `jekyll-sitemap` だけだが、`jekyll-feed` と `jekyll-seo-tag` は minima 2.5.1 の依存なので欠けると `Dependency Error` で落ちる。まとめて入れる:

```bash
gem install --no-document jekyll:3.9.5 minima:2.5.1 jekyll-feed jekyll-seo-tag \
    jekyll-sitemap jekyll-paginate kramdown-parser-gfm
```

**`gem install` した実行ファイルは PATH に現れないので、必ず PATH を足す。** rbenv の shim 経由でも動かない（shim は作られるが `rbenv version` が `system` なので system ruby を見にいき `rbenv: <cmd>: command not found` になる）。`bash -lc` で回り道しても同じ。`export` は次の Bash 呼び出しに引き継がれないので、**使うコマンドと同じ行に置く**:

```bash
export PATH="$(gem env | awk '/EXECUTABLE DIRECTORY/{print $NF}'):$PATH" && jekyll build -d _site
```

描画確認は Playwright。**グローバルに入っている `playwright` をそのまま使う**（`/opt/pw-browsers` の chromium と組み合わせで動く）:

```bash
playwright screenshot --browser chromium --full-page \
  --viewport-size 375,812 --color-scheme dark <URL> out.png
```

`npx playwright@<CI のバージョン>` は使えない。CI がピンしている版は `/opt/pw-browsers` にあるものと違う build 番号を要求し、`Executable doesn't exist at /opt/pw-browsers/chromium_headless_shell-<別番号>/...` で落ちる。

- 配信は `python3 -m http.server <port> --directory <dir>` で。`baseurl: /news` を再現するため `<dir>/news/` に `_site` の中身を置く（CI の workflow と同じやり方）
- Node の API を直接使う場合、dark mode は `browser.newContext({ colorScheme })` か `browser.newPage({ colorScheme })` で。`context.newPage({ colorScheme })` は**黙って無視される**（実測）
- Node の API で幅を指定するキーは `viewport`。**`viewportSize` は黙って無視され 1280 幅になる**（Python 版のキー名。実測 2026-09-22: `newContext({viewportSize:{width:375,...}})` → `window.innerWidth` 1280 / `newContext({viewport:{width:375,...}})` → 375）。同じ `newContext` で `colorScheme` のほうは効くので、dark だけ合っていて幅が違う絵を撮ってしまう

### CI の screenshot artifact を取る

push 後はこちらも見る。ローカルで撮るのは1〜2枚だが、CI は6ページ × light/dark をデスクトップ幅とモバイル幅で撮っている。MCP 経由なら認証込みで取得できる（実測）:

```
mcp__github__actions_list(method=list_workflow_run_artifacts, resource_id=<run id>)
mcp__github__actions_get(method=download_workflow_run_artifact, resource_id=<artifact id>)
  → 期限付きの署名 URL が返る。curl でそのまま落として unzip
```

ローカルの Chromium は CI と同じ版ではない（実測 2026-09-22: ローカル 1.56.1 / `chromium-1194`、CI は `PLAYWRIGHT_VERSION: 1.63.0` ピン。Renovate が上げるので CI 側は workflow の値を見る）ので、最終確認は artifact のほうが CI の見え方に近い。

artifact に写るのは、その branch の `_posts/` をビルドした結果だけ。「これから生成される記事」の見え方を変える変更（publish-pages のタイトル生成ルール等）は `_posts/` を1件も触らないので、**artifact は main と同じ絵のままで、変更後の姿を1件も確認できない**（実走で PR #365 がこれに当たった）。この種の変更は、当日分の front matter を新形式に差し替えたローカルビルドで補う。

## 検証コマンド

- 保護パス判定: `python3 .claude/scripts/check_protected_paths.py --diff origin/main`（`ui_changes` が出たら `.claude/rules/ui-changes.md` に従う）
  - **判定前に `origin/main` を取り込む。** `--diff` は2点 diff なので、branch が main より遅れていると *main 側で進んだ* ファイルまで自分の変更として並ぶ。実測 2026-09-21: branch が #369（Renovate の playwright 更新）の分だけ遅れていて `.github/workflows/jekyll-build-check.yml` が `protected: true` で出たが、`git diff --name-only origin/main...HEAD -- .github/workflows/` は 0 件。main をマージしたら `protected: false` になった
- 見出しリンクの着地点: `python3 .claude/scripts/check_article_anchors.py <_site>`
- 読みどころの欠落: `python3 .claude/scripts/check_article_notes.py`
- ソース表記の不一致: `python3 .claude/scripts/check_source_hints.py`
  （上の2つは引数なしで当日 JST 分を検査。`_posts/{YYYY-MM-DD}-*.md` を渡せば日付を固定できる）
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
- レビュー stage で PR を調べるときは、取得元を **git → 素の REST → MCP** の順で選ぶ（MCP は往復が重く、返り値がトークン上限を超えるとファイルに退避される）。実測で迷ったのは次の3つ:
  - **conflict の有無**: git で完結する。`git fetch origin` のうえ `git merge-tree --write-tree origin/<先にマージする head> origin/<次の head>`（exit 0 なら clean）。この loop の PR head は repo 内ブランチなのでローカルで完結し、候補同士のマージ順も先に当てられる（マージ後に初めて conflict を知る順序にならない）。`pull_request_read(minimal_output=true)` は **PR body を削らない**ので、`mergeable_state` を見るためだけに呼ぶと PR body 全文（実測 約20k トークン）が返る。`behind` 等の値が要るときだけ MCP に落とす
  - **checks**: 素の REST で `actions/workflows/jekyll-build-check.yml/runs?per_page=100` を1回引けば head_sha ごとの conclusion がまとめて取れる（PR ごとに引かない）。MCP なら `actions_list(method=list_workflow_runs, resource_id=jekyll-build-check.yml)` が同じもの。1ページ100件に収まらない古い head は落ちるので、見つからない PR だけ `?head_sha=<40桁>` で個別に引く（実測 2026-09-22: 1ページ目の最古の run は 9/11 で、9/9 に push された PR #292 の run は入らない）
  - **分類スクリプトへの入力**: 素の REST だけで組める。`.claude/skills/review-and-merge/scripts/classify_prs.py` は `gh` 不在の環境では `--stdin` のみだが、渡す JSON は `pulls?state=open&per_page=100` 1回 + PR ごとの `pulls/{n}/files` と `pulls/{n}/commits` で揃う（同スクリプトの `fetch_prs_via_gh()` がそのまま仕様。実測 2026-09-22: open PR 3件 = 7 リクエスト / 2.8 秒）。`fetch_prs_via_gh()` は `--paginate` なので、`files` / `commits` が100件を超える PR では `per_page=100` の次ページも辿る（`commits[-1]` が最終 commit でないと quiescence 判定が狂う）
    - **`patches` を `git diff` の出力で組まない。** `version_bump_only()` は GitHub files API の patch 形式（`@@` 始まり・ファイルヘッダなし）を前提にしており、`git diff` は `---` / `+++` 行が削除・追加行として数えられて判定が壊れる。壊れると保護パスのバージョン置換が通常レビューに回らず `protected`（hold + 人間）に落ちる。実測 2026-09-22、PR #369 の `PLAYWRIGHT_VERSION` 更新で同じ1行の変更を両形式に通した: files API の patch → `True` / `git diff` の出力 → `False`
- マージ後の branch 削除は repo 設定で自動（実測 2026-09-22 `GET /repos/{owner}/{repo}` → `delete_branch_on_merge: true`）。`gh pr merge --delete-branch` 相当の後始末は不要で、明示的に消しにいくと `remote ref does not exist` で失敗する
- マージすると `pages.yml` の main ビルドが**数秒後に現れ、1分前後で completed** になる（実測 2026-09-22、直近のマージ済み PR 12件: run の出現がマージ後 2〜19 秒、completed まで 47〜77 秒、いずれも success）。run が現れるのを待つループで `?head_sha=` を使うなら **完全な40桁 SHA** を渡す。短縮 SHA は HTTP 200 / `total_count: 0` を返すだけなので永久に待つ（実測: 7桁・12桁とも 0件、40桁で1件）
- **1件の所要（select stage が残り時間を見積もるための実測）**: 2026-09-22 の12時 run で3件完走し、docs のみ（#380）約16分 / UI 1ファイル（#381）約15分 / UI で設計案の比較を要するもの（#386）約25分。いずれも実装 + fresh context のレビュー1〜2周とその反映 + CI green まで含む。run 内の2件目以降は jekyll と gem のインストール（数分）が済んでいる分だけ速い
- **CI は base が main の PR にしか走らない**ため、in-flight の branch と同じファイルを触る issue を同じ run で拾うと、スタックさせた側は base のマージまで検証できない。次の1件は in-flight が触ったファイルと重ならないものから選ぶ（2026-09-22 の run で #367 を見送った理由。#388 と同じ `.claude/notes/develop-issue.md` を触るため）
- squash マージされた PR にスタックしたブランチは `git rebase --onto origin/main <スタック元の最後の commit>` で自分の commit だけ載せ替える（素直な rebase は squash 済みの内容と全面衝突する）
