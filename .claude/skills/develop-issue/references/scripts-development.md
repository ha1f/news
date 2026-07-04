# Scripts development guide

`scripts/*.sh` を改修する時の規約。develop-issue 実行時には参照不要、skill 自体の開発時のみ Read する。

## smoke test 規約

`scripts/*.sh` を変更したら、commit 前に主要シナリオで smoke test を実行する (silent bug の再発防止)。

### `detect_secrets.sh`

clean 状態 + AWS key / PAT / Slack / Private key を含む staged file + `.env` / `id_rsa` file name の 6 ケースで exit code 確認。期待: clean=0、secret 系=1。

### `diff_summary.sh`

1000 行未満 + 2000 行超 diff の 2 ケースで full/summarized モード切り替え確認。

### `run_command.sh`

`check_human_owned` の path_glob ヒット + 全 action (format / lint / test / build) で「tool 不在 + CI cover あり / なし」の 4 ケースで exit 0 / 5 / 127 区別確認。

### `fetch_issue.sh`

usage error + 数値 ID + URL 形式 + Linear ID (fail) の 4 ケース。
