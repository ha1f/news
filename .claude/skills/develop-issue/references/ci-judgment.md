# CI judgment mandate (Phase 6.2)

<context>
orchestrator が Phase 6.2 (CI fail 発生時) に Read して判定する mandate。`repo-profile.ci.fail_classifiers[]` を真とし、本 mandate は分類戦略 / 自動修正可否 / flaky 判別 / escape 条件を提供する。
</context>

## Table of Contents

- [入力ファイル](#入力ファイル)
- [出力ファイル](#出力ファイル)
- [自動修正は最小限](#大原則-自動修正は最小限)
- [flaky 判別 (FLAKY_RETRY)](#flaky-判別-flaky_retry)
- [timeout (TIMEOUT_UNKNOWN)](#timeout-timeout_unknown)
- [fix 後の挙動](#fix-後の挙動-verdictauto_fix-時)
- [escape 時の open_concerns](#escape-時の-open_concerns-必須フィールド)
- [アンチパターン](#アンチパターン)

## 入力ファイル

- `<state_dir>/ci-run-<sub_plan_index>-r<round>.log` (`gh run download <run_id> -D <state_dir>/ci-runs/`)
- `<state_dir>/ci-run-<sub_plan_index>-r<round-1>.log` (前 round、flaky 判別用)
- `<repo-profile>.ci.fail_classifiers[]` (repo 抽出済み、なければ language default)
- 該当 `sub-plan-<N>.md` (Approach / Changes / Test plan)
- 該当 `code-judgment-<N>-*.md` (前 round の verdict)

## 出力ファイル

`<state_dir>/ci-judgment-<sub_plan_index>-r<round>.md` (orchestrator 自身が書く):

```markdown
# CI judgment (sub_plan_index=N, round=R)

## CI run summary
- run_id: <id>, url: <url>, conclusion: <success/failure/cancelled/timed_out>
- duration: <min> (expected: <min>)
- failed jobs: [<name>, ...]

## Classification
- classifier_hits: [<classifier_id>, ...]   # repo-profile.ci.fail_classifiers から
- category: lint | format | typecheck | test_simple | test_logic | integration | build | security | unknown
- fix_strategy: auto | handoff | ask
- flaky_suspected: true | false
- evidence: <log excerpt 3-5 行>

## Verdict
- verdict: AUTO_FIX | HANDOFF | FLAKY_RETRY | TIMEOUT_UNKNOWN
- fix_constraints (verdict=AUTO_FIX 時): {max_lines: 5, max_files: 1, allowed_kinds: [lint, format, import_order]}
- escape_reason (verdict=HANDOFF 時): <1 行>
```

## 大原則: 自動修正は最小限

<constraints>
- 自動修正の confidence は本来低い (remote container で build 不能、修正後の self-verify は次の CI run でしか確認できない、cross-file 影響は読みきれない)
- 誤修正 → regression → さらなる修正 loop で round 消費の最悪 case を避けるため、自動修正可カテゴリは大幅縮小
- Strategy file のため Blocker/Suggestion/Nits 3 階層は使わない。verdict は AUTO_FIX / HANDOFF / FLAKY_RETRY / TIMEOUT_UNKNOWN の 4 値
- 詳細は `references/judgment-conventions.md` 参照
</constraints>

### 自動修正可 (AUTO_FIX) の必要条件 (AND)

- 変更が **`≤ 5 行` かつ `≤ 1 file`** で完結 (mandate "small_fix_only")
- 該当カテゴリが下記 allowlist に含まれる
- 該当 fail の root cause が log の **decisive な 1 箇所** に集約されている (fanned-out symptom は handoff)

### Allowlist (確実に自動修正可)

| カテゴリ | 例 | 修正方針 |
|---|---|---|
| `lint` | `no-unused-vars`, `prefer-const`, `quotes` | linter の autofix (`--fix`) を信頼、diff が ≤ 5 lines で済むか確認 |
| `format` | `prettier` / `gofmt` / `rustfmt` diff | formatter 実行、diff が ≤ 5 lines で済むか確認 |
| `import_order` | `eslint-plugin-import` 系 | sort 規約に従い並べ替え |
| `unused_import` | unused symbol | import 削除 (export 経路に影響なければ) |
| `typecheck_local` | **single-file 内** で完結する型注釈追加 (`: string` / `as Foo` cast) | cross-file 依存があれば handoff |

上記 allowlist 以外は HANDOFF が default、特に以下のカテゴリは明示的に HANDOFF。

### Handoff (HANDOFF) のカテゴリ

| カテゴリ | 理由 |
|---|---|
| `test_logic` (heavy logic test fail) | 表面 fix が別 test 壊す regression リスク高 |
| `integration` / `e2e` | flaky 多発、root cause が遠い (external service / network) |
| `build_error` (依存問題 / network) | environment 起因、コード fix では直らない |
| `security_scan` (SAST / dependency vuln) | 人間 review 必須、勝手に依存更新しない |
| `dependency_drift` (lock file 不整合) | 上記同様、`pnpm install` / `cargo update` は影響範囲広い |
| `accessibility` / `perf_regression` | domain 知識 + 設計判断必要 |
| `infra` (docker pull fail / runner OOM) | コード fix で直らない、retry でなければ handoff |
| `codeowners` / `license` | 制度の問題、コード fix の範疇外 |
| `unknown` (classifier_hits が空) | 安全側で handoff |

## flaky 判別 (FLAKY_RETRY)

CI fail が真の bug か flaky か判別する手順:

1. 前 round の `<state_dir>/ci-run-<N>-r<round-1>.log` を Read
2. 今回 fail と前回 fail を比較:
   - **同一 test name + 同一 error message** → 真の bug (AUTO_FIX or HANDOFF へ)
   - **異 test / 同 test 異 error / time-of-day-dependent pattern** → flaky 疑い
3. flaky 疑い時は **`FLAKY_RETRY` verdict** で push 無し空 retry (`consume_round=false`、`MAX_TEND_ROUNDS_FLAKY_RETRY=2` 上限、`state.tend.summaries[sp.index].rounds_flaky_retry` をインクリメント)
4. 3 連続 flaky 疑い → `HANDOFF` + `open_concerns.ci_flaky_suspected`

## timeout (TIMEOUT_UNKNOWN)

`CI_WATCH_TIMEOUT_MIN = repo-profile.ci.expected_duration_min * 1.5` 超過時:
- `verdict: TIMEOUT_UNKNOWN` (CI fail とは別カテゴリ)
- `open_concerns.ci_unknown` で escape (PR は green/red 不明のまま DRAFT で残す、最新 run URL を PR body に記載)
- `repo-profile.ci.expected_duration_min` が無い repo は default 30 分

## fix 後の挙動 (verdict=AUTO_FIX 時)

orchestrator は `implement-agent` を以下引数で起動:
```
phase=fix_ci_failure
sub_plan_index=N
ci_judgment_path=<state_dir>/ci-judgment-N-rR.md
fix_constraints={"max_lines": 5, "max_files": 1, "allowed_kinds": ["lint", "format", "import_order"]}
```

implement-agent は変更制約 (≤ 5 lines / 1 file) を遵守し、超過したら `status: ci_handoff` を return (orchestrator が `HANDOFF` 扱いに転換)。

注: `fix_constraints` field 名は全 phase で統一 (`max_lines` / `max_files` / `allowed_kinds`)。Phase 7 (`apply_reviewer_feedback`) の `max_lines: 100 / max_files: 5` より厳しい (Phase 6.2 は lint/format 等の小修正に限定)。詳細は `references/return-schemas.md` の `fix_constraints` 参照。

## escape 時の `open_concerns` 必須フィールド

```json
{
  "kind": "ci_persistent_failure | ci_unknown | ci_flaky_suspected",
  "run_id": "...",
  "run_url": "...",
  "classifier_hits": ["..."],
  "attempted_fixes": [{"round": 1, "fix": "...", "result": "still_failing"}],
  "last_log_excerpt": "<最後の 10-20 行>"
}
```

これらは PR body の `Local verification` セクションに転記され reviewer の trace 材料になる。

## アンチパターン

- log 全文を orchestrator context に取り込む → 巨大化、judgment 圧迫。`gh run view --log` ではなく `gh run download` で file 化、関連箇所のみ Read
- 「typecheck = 全て auto」と分類する → cross-file semantic bug の handoff 漏れ。**single-file 内完結のみ auto**
- flaky 判別を端折って即 AUTO_FIX に進む → 無駄 round 消費。**必ず前 round log と diff**
- escape 時 `open_concerns` を空配列で出す → reviewer が trace できない。**必須フィールド全部埋める**
- TS/JS の log pattern を他言語にも適用 → 言語別 default classifier (TS / Python / Go / Rust / Swift) を `repo-profile.ci.fail_classifiers[]` から読む。本 mandate に inline で書かない (D4 repo-agnostic 違反)
