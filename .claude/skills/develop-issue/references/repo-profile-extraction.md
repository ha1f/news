# `repo-profile.md` 抽出ヒューリスティック

<context>
gather-agent が対象リポジトリを scan して `repo-profile.md` を作る時の手順。
未検出のフィールドは omit (推測でなく明示的に空) する。
</context>

## Table of Contents

- [抽出順序](#抽出順序)
- [1. repo メタデータ](#1-repo-メタデータ)
- [2. 規約ファイル](#2-規約ファイル)
- [3. CI workflows](#3-ci-workflows)
- [4. コマンド定義ファイル](#4-コマンド定義ファイル)
- [5. PR テンプレート](#5-pr-テンプレート)
- [6. git log 分析](#6-git-log-分析)
- [7. Codebase map / noise paths / LSP](#7-codebase-map--noise-paths--directory-specific-conventions--lsp-availability)
- [8. detection 構造の組み立て](#8-detection-構造の組み立て)
- [出力](#出力)

## 抽出順序

優先順位の高い source から読み、後段で見つかった値で上書きしない。
**規約ファイルの明示記述 > CI で実際に走る command > 設定ファイルの推測 > skill デフォルト**。

```
1. repo.root / default_branch / remote / host
2. 規約ファイル (CLAUDE.md, AGENTS.md, .claude/rules/*, .cursorrules, CONTRIBUTING.md)
3. CI workflows (.github/workflows/*.yml)
4. コマンド定義ファイル (package.json, Makefile, Justfile, Taskfile.yml)
5. 言語特有ファイル (Cargo.toml, pyproject.toml, go.mod, Gemfile, Package.swift)
6. PR テンプレート (.github/PULL_REQUEST_TEMPLATE.md)
7. git log 分析 (branch 命名 / commit 規約)
8. Review bots 抽出 (.github/workflows/* で動く bot account を検知、`uses: anthropics/claude-code-action@*` 等から populate)
9. Worktree gitignored 大型依存検知 (L43、`.gitignore` + 共通 pattern `Pods/` / `dependencies/Arkana*` / `*.xcframework` 等を `notes.worktree_gitignored_deps[]` に集約)
```

## 1. repo メタデータ

| フィールド | 取得方法 | フォールバック |
|---|---|---|
| `repo.root` | `git rev-parse --show-toplevel` | 必須、なければ catastrophic |
| `repo.default_branch` | `gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'` | `git symbolic-ref refs/remotes/origin/HEAD` → `main` |
| `repo.remote` | `git remote` の最初の行 | `origin` |
| `repo.host` | `gh repo view --json url` から判定 | `github` |
| `repo.primary_languages` | 拡張子分布 + 設定ファイル存在から推測 | omit |

## 2. 規約ファイル

### 探索パス (存在するものを全部読む)
- `<root>/CLAUDE.md`
- `<root>/AGENTS.md`
- `<root>/.claude/rules/*.md`
- `<root>/.cursorrules`
- `<root>/.cursor/rules/*`
- `<root>/CONTRIBUTING.md` / `<root>/.github/CONTRIBUTING.md` / `<root>/docs/CONTRIBUTING.md`
- `<root>/README.md` の "Development" / "Contributing" / "Getting started" セクション

### 規約から抽出する key
| 規約に書かれていたら | repo-profile のどこに |
|---|---|
| 「TDD で進める」「テストを書いてから実装」 | `testing.tdd_required: true` |
| 「unit / integration / e2e すべて必要」 | `testing.required_levels` |
| 「DRAFT で作成」「draft PR」 | `conventions.pr_must_be_draft: true` |
| 「commit メッセージは Conventional Commits」 | `conventions.commit_message.style: "conventional-commits"` |
| 「ブランチ命名」 | `conventions.branch_naming` |
| 「重複確認」「dedupe-check」 | `conventions.dedupe_check` |
| 「migration は人間が作る」「人間が生成」 | `conventions.human_owned` に追加 |
| 「main に commit しない」「force push しない」 | `conventions.forbidden` に追加 |
| 「変更時は X を実行」「Y を更新時は Z」 | `commands.codegen[]` に追加 |
| spec / 仕様書のルール | `spec_docs` |
| ファイル/ディレクトリ命名規則 | repo-profile 本文の Markdown 部分に記録 |

**抽出時の注意**:
- 規約ファイルの **要約** ではなく **引用** ベースで抽出する (`source` フィールドに必ず元ファイルを書く)
- 矛盾する規約があった場合は、より特定的なもの (rule ファイル) > より一般的なもの (README) を優先
- 規約に書いてないことは推測で書かない (omit)

## 3. CI workflows

`.github/workflows/*.yml` を全て読む (`gitlab-ci.yml`, `bitbucket-pipelines.yml`, `.circleci/config.yml` も同様)。

**コマンド推定** (`commands.*` 用):
- `pnpm test`, `npm run lint`, `cargo test`, `make test` 等の **実際に CI で走らせている command** をそのまま `commands.*` の値とする
- 複数 workflow に異なる command があれば、PR (`on: pull_request`) の workflow を優先
- matrix で複数走る場合は最も「全体的」なものを採用

**`ci` セクション抽出** (ローカル verify skip 判定の前提):
- `ci.has_workflows`: workflow ファイルが 1 つ以上あれば `true`、無ければ `false`
- `ci.workflow_files`: 検出した workflow ファイルの相対パス一覧
- `ci.covered_actions`: workflow が PR / push trigger で走らせている action を `format` / `lint` / `test` / `build` のいずれにマップ:
  - `pnpm lint` / `eslint` / `ruff check` / `cargo clippy` 等 → `lint`
  - `pnpm test` / `jest` / `pytest` / `cargo test` / `go test` 等 → `test`
  - `pnpm build` / `tsc` / `cargo build` / `go build` / `webpack` 等 → `build`
  - `pnpm format --check` / `prettier --check` / `ruff format --check` 等 → `format`
- `ci.trigger_events`: `on:` セクションから抽出 (`pull_request`, `push`, `schedule` 等)
- 注意: `format` は CI で `--check` (差分チェック) として走らせている場合のみ `covered_actions` に含める。CI で auto-fix する設計の repo は稀なので、検出できなければ `format` を含めない (= ローカル format skip 不可)

これらは R36 / R38 (ローカル verify skip) の判定に必須。`ci.covered_actions` に含まれない action は CI でも走らないため、ローカルで実行不能でも skip せず `stuck` で人間に渡す必要がある。

## 4. コマンド定義ファイル

### `package.json` (npm/yarn/pnpm/bun)
- `packageManager` フィールドからパッケージマネージャを判定
- なければ lockfile (`pnpm-lock.yaml` / `yarn.lock` / `bun.lockb` / `package-lock.json`) から判定
- `scripts` の中で以下に該当するキーがあれば候補:
  - `format` / `fmt` / `prettier` → `commands.format`
  - `lint` / `lint:check` / `eslint` → `commands.lint`
  - `test` / `test:unit` → `commands.test`
  - `build` / `compile` → `commands.build`
  - `install` → `commands.install` (なければ `<pm> install`)
  - `codegen` / `gen` / `generate` → 規約ファイルの codegen trigger と紐付け

### `Makefile`
- target 名から類似マッチ (`format`, `lint`, `test`, `build`, `generate`, `gen-*`)
- 複数候補があれば CI で実際に呼ばれている target を優先

### `Justfile` / `Taskfile.yml`
- 同様

### 言語特有

| ファイル | コマンド推測 |
|---|---|
| `Cargo.toml` | `cargo fmt`, `cargo clippy`, `cargo test`, `cargo build` |
| `pyproject.toml` (poetry) | `[tool.poetry.scripts]` / `[tool.ruff]` / `[tool.black]` |
| `pyproject.toml` (uv/pip) | `uv run` / `pip install -e .` |
| `go.mod` | `go fmt`, `go vet`, `go test ./...`, `go build ./...` |
| `Gemfile` | `bundle exec rake test` / `rspec` |
| `Package.swift` | `swift build`, `swift test` |
| `Podfile` / iOS の `Makefile -C ios` | `commands.platform_specific.ios.*` に格納、`include_by_default: false` (重いため) |

## 5. PR テンプレート

`.github/PULL_REQUEST_TEMPLATE.md` または `.github/PULL_REQUEST_TEMPLATE/<name>.md` を `conventions.pr_template_path` に格納。
内容は読まない (PR 作成時に実 file を `gh pr create --body-file` で渡す)。

## 6. git log 分析

```bash
git log --all --pretty=format:'%D|%s' -100
```

### Branch 命名
- `origin/<prefix>/<rest>` パターンの prefix 分布を集計
- 最頻出 prefix を `conventions.branch_naming.pattern` に格納 (例: `claude/<descriptive>`)
- 分布が散らばっていれば skill デフォルト `claude/<issue-slug>`

### Commit メッセージ
- `<type>(<scope>): <subject>` 形式が >70% なら `conventions.commit_message.style: "conventional-commits"`
- それ以外なら `"free-form"`
- 観測された `<type>` 一覧を `conventions.pr_title.allowed` に流用 (PR title prefix の根拠)

## 7. Codebase map / noise paths / directory-specific conventions / LSP availability

Anthropic blog "How Claude Code works in large codebases" の prescription を反映。

### `codebase_map.directories`
- `ls -d */` で top-level folder 列挙
- 各 folder の README.md (root or `<folder>/README.md`) の先頭 100 文字、もしくは `package.json.description` / `Cargo.toml.description` から 1 行 description を抽出
- 検出できなければ `desc: "purpose unknown"`、本文 Markdown 部分に注記

### `codebase_map.noise_paths`
- `.gitignore` の **大項目** (file-specific ではなく directory level の pattern) を抽出
- 共通 noise patterns を補完: `node_modules/`, `dist/`, `build/`, `target/`, `vendor/`, `.next/`, `.turbo/`, `.cache/`, `coverage/`
- 重複は dedupe

### `directory_specific_conventions`
- gather-agent **Step 4** で issue 関連 file を特定した後、それらの親 directory (root を除く) を抽出
- 各 directory に `CLAUDE.md` / `AGENTS.md` / `.claude/rules/*.md` があれば Read
- root の規約と異なる / 補完する rule だけを抽出 (root と同じ rule は重複なので omit)
- 形式: `{path, source, rules: [...]}` の配列

理由: 大規模 mono-repo では root CLAUDE.md だけでは subdir 固有規約 (例: `ios/CLAUDE.md` の「iOS test runs are heavy」) を取りこぼす。blog 曰く「root file for the big picture, subdirectory files for local conventions、each layer loading additively」。

### `tooling.lsp_available`
- gather-agent が起動時に LSP tool が available か確認 (`mcp__lsp__*` 系の tool 名が手元にあるか、もしくは IDE integration の signal を検知)
- `true` の場合、`tooling.lsp_languages` に対応言語を記録 (検出: lsp tool の supported languages、もしくは repo の primary languages から推測)
- implement-agent / plan-agent はこの flag を見て、symbol-level navigation (find_references / goto_definition) を Grep より優先する

理由: blog 曰く「LSP integrations give Claude symbol-level precision: it can follow a function call to its definition, trace references across files, and distinguish between identically named functions. Without LSP, Claude pattern-matches on text and can land on the wrong symbol」。

## 8. detection 構造の組み立て

### `human_owned` の detection 抽出

規約に「migration files は人間が作る」とあれば、ファイルパスのヒントを規約本文や repo 構造から探す:
- `migrations/` ディレクトリの存在 → `path_glob: "**/migrations/*"`
- ORM 設定ファイルから migration ディレクトリの場所を読む (TypeORM `migrations` config, Prisma `migrations/` 等)
- 推測が難しければ `path_glob` ではなく `command_check` (例: `grep -r "@Migration" --include='*.ts' src/`) を使う

## 出力

最終的に **2 つのファイル**を `<state-dir>/` に書き出す:

1. `repo-profile.md` — YAML frontmatter + Markdown 本文 (人間 / agent 用)
2. `repo-profile.json` — 同じ frontmatter を JSON 化したもの (scripts 用)

JSON は `frontmatter のみ`を `python3 -c 'import sys,yaml,json; print(json.dumps(yaml.safe_load(sys.stdin)))'` などで変換し、md と内容が常に同期するようにする (Python が無い環境なら `yq -o=json '.' repo-profile.md` 等で代替)。

出力後、orchestrator が `references/gather-judgment.md` mandate を読んで、この `repo-profile.md` の「充足度」を判定する (v2 では reviewer sub-agent を廃止し、orchestrator が直接 judge する)。
