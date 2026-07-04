# `repo-profile.md` / `repo-profile.json` schema

<context>
`repo-profile.md` は対象リポジトリの「規約」と「実行可能コマンド」を skill に提供するための単一の参照ファイル。
gather-agent が最初に作成し、後続フェーズはこれを source of truth として参照する。
</context>

## Table of Contents

- [ファイル構造](#ファイル構造)
- [フィールド規約 (Required / Optional)](#フィールド規約)
- [値の出典 (source フィールド)](#値の出典-source-フィールドの書き方)
- [human_owned の detection 構造](#human_owned-の-detection-構造)
- [codegen エントリの trigger](#codegen-エントリの-trigger)
- [バージョン / 互換性](#バージョン--互換性)

**gather-agent は同じ内容を 2 つの形式で書き出す**:

- `repo-profile.md` — YAML frontmatter + Markdown 本文。**reviewer / phase agent が読む** (人間にも読める)
- `repo-profile.json` — 同じ内容を JSON で表現。**`scripts/run_command.sh` 等が `jq` で読む**

2 つの内容は常に同期する。`md` を真と扱い、書き出し時に `json` を派生として生成する。

## ファイル構造

YAML frontmatter + Markdown 本文。

```markdown
---
repo:
  root: <絶対パス>
  default_branch: main
  remote: origin
  host: github                       # github / gitlab / bitbucket
  primary_languages: [typescript, swift]
commands:
  install: "pnpm install"
  format: "pnpm format"
  lint: "pnpm lint"
  test: "pnpm test"
  build: "pnpm build"
  codegen:
    - trigger: "**/*.gql"
      command: "pnpm studio codegen && (cd ios && make generate)"
      owned_by_pattern:                # 生成物の出力先 glob (R68、artifact ownership)
        - "typescript/apps/studio/src/types/__generated__/**"
        - "ios/Packages/Dependencies/Sources/API/**"
      source: ".claude/rules/graphql-codegen.md"
  platform_specific:
    ios:
      test: "make -C ios test"
      build: "make -C ios build"
      include_by_default: false
conventions:
  branch_naming:
    pattern: "claude/<descriptive>"
    source: "git log analysis"
  commit_message:
    style: "conventional-commits"
    examples:
      - "feat(ios): ..."
      - "refactor(api): ..."
    source: "git log analysis"
  pr_title:
    prefix_required: true
    allowed: ["feat", "fix", "refactor", "chore", "style", "test", "docs", "build", "ci"]
    max_length: 70
  pr_must_be_draft: true
  pr_template_path: ".github/PULL_REQUEST_TEMPLATE.md"
  locale: "en"                       # en / ja。Phase 7 reply template の言語選択に使う (default: en)
  dedupe_check:
    required: true
    source: ".claude/rules/dedupe-check.md"
    keywords_min: 2
  human_owned:
    # ✅ 推奨: detection は具体的、source 明示
    - kind: "migration_files"
      detection:
        path_glob: "typescript/apps/app/migrations/*.ts"
      reason: "Migration files must be created by a human"
      source: "CLAUDE.md L34"

    # ❌ 非推奨: detection が曖昧、source 欠落
    # - kind: "migrations"
    #   detection: {content_match: "migration"}   # 過剰マッチで false positive
    #   reason: "migration"                       # なぜ human owned かが不明
  forbidden:
    - "direct commit to main"
    - "git push --force"
    - "--no-verify"
    - "gh pr merge"
testing:
  tdd_required: true
  required_levels: ["unit", "integration", "e2e"]
  skip_test_authorization_phrase: "I AUTHORIZE YOU TO SKIP WRITING TESTS THIS TIME"
  source: "CLAUDE.md"
ci:
  has_workflows: true
  workflow_files: [".github/workflows/ci.yml", ".github/workflows/pr.yml"]
  covered_actions: ["lint", "test", "build"]   # ローカル verify が skip 可能な action 集合
  trigger_events: ["pull_request", "push"]
  expected_duration_min: 12                    # Phase 6 CI watch timeout の計算根拠 (× 1.5、default 30)
  fail_classifiers:                            # Phase 6.2 CI fail 分類 (ci-judgment.md が参照)
    # action_name: workflow job 名 / 用途
    # log_pattern: 一致判定用 regex
    # fix_strategy: auto (自動修正) | handoff (人間) | ask (orchestrator が判断)
    # max_lines / max_files: auto 時の変更制約 (超過したら handoff へ転換)
    # category: lint | format | typecheck | test_simple | test_logic | integration | build | security | unknown
    - action_name: "lint"
      log_pattern: '\d+ problems? \(\d+ errors?'
      fix_strategy: auto
      max_lines: 5
      max_files: 1
      category: lint
    - action_name: "format"
      log_pattern: '(prettier|gofmt|rustfmt).* (Code style issues|diff)'
      fix_strategy: auto
      max_lines: 5
      max_files: 1
      category: format
    - action_name: "typecheck"
      log_pattern: 'TS\d+: '
      fix_strategy: ask   # single-file 完結なら auto、cross-file なら handoff (orchestrator が judge)
      max_lines: 5
      max_files: 1
      category: typecheck
    - action_name: "test"
      log_pattern: '(FAIL|✗) .*\.test\.(ts|tsx)'
      fix_strategy: handoff
      category: test_logic
    - action_name: "build"
      log_pattern: 'error\[E\d+\]|cannot find module'
      fix_strategy: handoff
      category: build
  source: ".github/workflows/ + 言語別 default classifier set"
codebase_map:
  # top-level directory の 1 行 description (blog "lightweight markdown file ...
  # a table of contents Claude can scan before opening files" 相当)
  directories:
    - path: "typescript/apps/app"
      desc: "API server (GraphQL)"
    - path: "typescript/apps/studio"
      desc: "admin panel (React)"
    - path: "ios"
      desc: "iOS app (Swift + TCA)"
  noise_paths:
    # 探索時に skip する path (生成物・third-party・build artifacts)
    # `.gitignore` 大項目 + 共通 noise pattern (`node_modules`, `dist`, `vendor`,
    # `target`, `.next`, `.turbo`, `build` 等) から抽出
    - "node_modules/"
    - "dist/"
    - ".turbo/"
    - "ios/build/"
directory_specific_conventions:
  # issue 関連 directory の CLAUDE.md / .claude/rules/*.md から抽出した
  # 局所規約 (root の規約と並列ではなく、root を上書き or 補完するもの)
  # ✅ 推奨: priority_reason 明示
  - path: "ios/"
    source: "ios/CLAUDE.md"
    priority_reason: "subdir > root for iOS-specific testing rules"
    rules:
      - "iOS test runs are heavy; gated behind --include-ios"
  - path: "typescript/apps/app/migrations/"
    source: "typescript/apps/app/CLAUDE.md"
    rules:
      - "Migration files must be created by a human (already in conventions.human_owned)"
tooling:
  lsp_available: true   # Claude Code 環境で LSP tool が available か (gather-agent が確認)
  lsp_languages: ["typescript", "swift"]   # LSP 対応言語
review_bots: []                             # Phase 7 (Review-loop) で bot 識別を補助する account allowlist。
                                            # 主たる判定は `comment.user.type == "Bot"` (GitHub API 標準)。
                                            # 動的抽出: gather-agent が .github/workflows/*.yml の `uses:` から bot account を検知して append。
                                            # default は [] (固有名 hardcode を避け、D4 repo-agnostic を維持)
  source: ".github/workflows/* 内の uses: ... を検知"
spec_docs:
  required: false
  location: "docs/spec/"
  template: "docs/spec/_template.md"
  prohibited_content: ["code snippets", "implementation details", "file paths"]
  source: ".claude/rules/spec-document.md"
notes:
  - "iOS test runs are heavy; gated behind --include-ios"
  - "schema.gql changes require both studio and ios codegen"
---

# Repo Profile

## Conventions (full text references)
- CLAUDE.md (root): ...
- .claude/rules/graphql-codegen.md: ...
- .claude/rules/dedupe-check.md: ...
- .claude/rules/spec-document.md: ...

## CI workflows (relevant excerpts)
- .github/workflows/ci.yml: runs `pnpm lint`, `pnpm test`, ...

## Notable patterns from `git log`
- Conventional Commits dominant
- Branch prefix `claude/...` for ai-generated work
```

## フィールド規約

### Required
- `repo.root` — `git rev-parse --show-toplevel` の出力
- `repo.default_branch` — `gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'`
- `repo.remote` — `git remote` の最初のもの (通常 `origin`)
- `conventions.pr_must_be_draft` — bool (規約に明記がなければ true を推奨デフォルト)

### Optional (検出できなければ omit)
- `commands.*` — 個別 command が検出できなければそのキーごと omit
- `commands.codegen` — 検出できなければ空配列 `[]`
- `commands.platform_specific` — 検出できなければ omit
- `conventions.commit_message.style` — 検出できなければ `"free-form"`
- `conventions.dedupe_check` — 規約になければ omit (skill デフォルトは「重複確認を簡易実行」)
- `conventions.human_owned` — 検出できなければ空配列 `[]`
- `conventions.locale` — `en` / `ja`、default は `en` (international friendly)。Phase 7 reply template の言語選択に使用。リポジトリの主言語を git log / README から推定 (日本語 commit が >50% なら `ja`)
- `testing.tdd_required` — 検出できなければ `false`
- `spec_docs` — 検出できなければ omit
- `ci.*` — `.github/workflows/` が無ければ `{has_workflows: false, covered_actions: [], fail_classifiers: []}` を明示。ローカル verify skip 判定 (R36-R39) + Phase 6 (Tending) で CI fail 分類に使う
- `ci.expected_duration_min` — 既存 workflow の `gh run list --json conclusion,createdAt,updatedAt` で過去 N 件の duration 中央値を計算 (default 12 分)。Phase 6 の `CI_WATCH_TIMEOUT_MIN = expected_duration_min * 1.5` 算出根拠
- `ci.fail_classifiers[]` — 言語別 default classifier set を base (TS / Python / Go / Rust / Swift)、repo 固有の workflow / linter / test runner を反映して上書き。Phase 6.2 で orchestrator が `ci-judgment.md` mandate と合わせて参照
- `codebase_map.directories` — `ls -d */` で top-level folder 列挙 + README から 1 行 description (検出できなければ「purpose unknown」)
- `codebase_map.noise_paths` — `.gitignore` + 共通 noise pattern。gather-agent / implement-agent が探索時に skip
- `directory_specific_conventions` — Step 4 で issue 関連 directory を特定後に各 CLAUDE.md を Read して抽出。無ければ空配列
- `tooling.lsp_available` — Claude Code 環境で LSP tool が available か gather-agent が確認 (Read tool で `mcp__lsp__*` 等を検知)。`true` なら implement-agent / plan-agent が `find_references` / `goto_definition` を優先
- `review_bots[]` — Phase 7 で bot 識別を補助する account allowlist。**主たる判定基準は `comment.user.type == "Bot"` (GitHub API 標準)** で、固有 bot account 名は本 field に依存しない。default は `[]` (D4 repo-agnostic 維持、固有名 hardcode を避ける)。動的抽出: gather-agent が `.github/workflows/*.yml` の `uses:` 行を読んで bot account を append

## 値の出典 (`source` フィールドの書き方)

各規則の出典を必ず明記する。これがあると reviewer がトレース可能で、規約変更時にどのファイルを見れば良いか分かる。

- `source: "<相対パス>"` — 規約ファイルから読み取った場合
- `source: "git log analysis"` — git 履歴から推測した場合
- `source: "package.json scripts"` — package.json から
- `source: "CI workflow: .github/workflows/<name>.yml"` — CI から
- `source: "skill default"` — 何も見つからずデフォルト適用

## human_owned の `detection` 構造

```yaml
human_owned:
  - kind: "<short name>"
    detection:
      path_glob: "..."            # ファイルパス glob
      # または
      content_match: "..."         # ファイル内容の regex
      # または
      command_check: "..."         # 実行して exit 0/1 で判定する command
    reason: "<人間の言葉で説明>"
    source: "<出典>"
```

`detection` は **いずれか 1 つ以上**。複数定義した場合は OR 条件 (どれか 1 つでもヒットしたら catastrophic)。

### 検知タイミングと verdict matrix (gather/plan/code 3 段階)

| timing | verdict | mandate |
|---|---|---|
| gather (issue 解析) | `investigation_recommended` (handoff signal) | `gather-judgment.md` §2c |
| plan (sub-plan 設計) | `blocker` (needs_revise) | `plan-judgment.md` §7 |
| implement (実装中) | `catastrophic` (止まる) | implement-agent 内 |
| code-judgment (post-implement) | `blocker` (needs_fix) | `code-judgment.md` §8 |

## codegen エントリの `trigger`

- glob (`**/*.gql`, `proto/**/*.proto`, `openapi.yaml`)
- 複数 trigger があれば配列にせず、別エントリとして列挙する (command が異なる可能性のため)

## バージョン / 互換性

frontmatter 先頭に `schema_version: 1` を入れない方針 (skill が常に最新スキーマで上書きする)。
スキーマを変更した場合は本ドキュメントを更新し、gather-agent の prompt を追従させる。
