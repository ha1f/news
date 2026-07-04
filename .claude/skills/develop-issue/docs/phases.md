# Phase 仕様

各 Phase の責務・入出力・終了条件・判定主体を統一フォーマットで記述。実装 pseudocode と定数値は [references/orchestration.md](../references/orchestration.md) を真とする。

姉妹 docs: [overview.md](./overview.md) / [design-decisions.md](./design-decisions.md) / [sources.md](./sources.md)

---

## Pre-flight (Phase 1 開始前)

orchestrator 起動時の最初の処理。Phase 番号は持たない (SKILL.md 上は Phase 1 から)。

- **責務**: state dir 確保、`LESSONS.md` の `Status: pending` 最新 20 件 Read (過去の mistake を文脈化)、対象 issue の labels / 既存 PR / 重複 issue を 1 回確認
- **判定主体**: orchestrator。重複 / closed / 他者作業中なら `stop_recommended` で AskUserQuestion
- **対応 mandate**: `references/gather-judgment.md` §1 "Pre-flight"

---

## Phase 1: Gather

実装可能な状態に文脈を揃える。

- **責務**: issue 取得、`repo-profile` 抽出 (`CLAUDE.md` / `directory_specific_conventions` / `codebase_map` / `noise_paths` / `commands` / LSP availability)、関連コード特定、不足情報の質問生成
- **入力**: issue ID、qa-trail (前 round の答え)
- **出力**: `repo-profile.{md,json}` / `context.md` / `qa-trail.md`
- **judgment 主体**: orchestrator が `references/gather-judgment.md` を Read して判定。verdict は `ready` / `needs_input` / `stop_recommended` / `investigation_recommended`
- **終了条件**: `ready` で Phase 2 へ
- **Q&A round 上限**: `MAX_GATHER_ROUNDS` 以降は毎回「進むか」の meta question を強制
- **Self-fillable gap**: orchestrator が追加 file Read で埋められる gap は user に聞かず自分で埋めて再 judge

---

## Phase 2: Plan

実装単位への分解と妥当性確認。

- **責務**: `plan.md` draft (各 sub-plan に `Approach` / `Changes` / `Impact` / `Test plan` / `Rollout` / `depends_on` / `Codegen artifacts` / `Per-dir Conventions` / `Existing tests`)
- **入力**: `context.md` / `qa-trail.md` / `repo-profile.md`
- **出力**: `plan.md` / `sub-plan-N.md`
- **judgment 主体**: orchestrator が `references/plan-judgment.md` を Read。verdict は `ready` / `needs_revise` / `split_needed` / `recursive_split` / `blocked_by_dependency` / `no_op`
- **Revise round 上限**: `MAX_PLAN_ROUNDS` を超えると Open concerns 記録して進む

### 分解モードの 1 行 discriminator
- 全 sub-plan が `depends_on: null` (互いに独立) → **`recursive_split`** (Phase 2.5 へ、sub-issue 化 + 並列実行)
- 1 つでも `depends_on` がある → **`split_needed`** (in-memory chained PR、順次)
- sub-plan が 1 つ → **`ready`** (single PR)

独立性が確認できた時だけ sub-issue 化のオーバーヘッドを払う、が原則。

---

## Phase 2.5: Recursive split

`recursive_split` 判定時のみ実行。

- **責務**: sub-issue 作成 (`gh issue create`) / 親 issue body 更新 (`gh issue edit` で `### Sub-tasks` checklist 追加) / 並列 Task 起動 (1 message 内多重 Task call)
- **並列子の制約**: `recursion_depth=N+1` で同じ orchestrator role を再帰起動 (subagent_type: `general-purpose`)。各子は独立 state dir / 独立 git branch を持つ
- **Recursion depth 上限**: `MAX_DEPTH` 到達なら `recursive_split` が出ても `split_needed` (chained) で fallback
- **集約**: 全子 return を待ち、`needs_input` のものは [Q&A bubble up](#qa-bubble-up) で処理

---

## Phase 3: Implement (per sub-plan)

実装 → verify → PR body 判定 → PR 作成。

- **責務**: branch 作成 → TDD impl → self verify (`format` / `lint` / `test` / `build`) → secret check → human_owned check → codegen → commit → push → PR body draft → PR 作成
- **入力**: 該当 `sub-plan-N.md` / `repo-profile.json` / 前 round の `code-judgment-N-r<round>.md`
- **出力**: `diff-summary-N-r<round>.txt` / branch / PR URL
- **judgment 主体 (2 段)**:
  1. **Code review** (`references/code-judgment.md`): orchestrator が diff_summary を読んで判定。verdict は `ready` / `needs_fix` / `split_needed` / `stuck`
  2. **PR body** (`references/pr-body-judgment.md`): orchestrator が PR body draft + title 候補を判定。verdict は `ready` / `needs_fix`
- **Code review loop 上限**: `MAX_CODE_ROUNDS` 到達で残 blocker を `open_concerns` に記録し DRAFT PR は作る (escape_hatch)
- **PR body review 上限**: 2 round。3 round 目は escape_hatch_with_pr
- **phase 細分** (orchestrator が引数で制御): `default` (verify + commit) → `push_and_pr` (push + PR body draft) → `create_pr` (実 PR 作成) / `fix_pr_body` (修正) / `fix_blockers` (実装 fix)

### Verify skip の条件
`format` / `lint` / `test` / `build` のいずれかが「tool 不在」(`scripts/run_command.sh` が `rc=5` を返す = 元 exit 127 を wrapper が変換) で実行不能、かつ `repo-profile.ci.covered_actions` に該当 action があれば `open_concerns.verify_skipped` に記録して次の action に進む。「最大限ローカル、できないものは CI に委ねる」原則。command が走って exit 非0 で死んだ場合は failure として 5 round retry → stuck (skip 禁止)。

### Stuck の semantics
- **`blocked_no_pr`**: PR を作らず止まる (secret detected / 5 round verify failure / catastrophic)
- **`escape_hatch_with_pr`**: PR は作るが `open_concerns` に懸念を残す (code review 3 round で blocker 残)
- chained mode で upstream が `blocked_no_pr` / `catastrophic` の時、downstream は base branch が無く壊れるため `skipped_due_to_upstream` で cascade skip

---

## Phase 4: Report

成果の集約と判断 trail の永続化。

- **責務**: 全 PR URL を `pr-urls.md` に集約 / 自分の (sub-)issue に `gh issue comment` で判断 trail 投稿
- **comment の目的**: state dir は local にしか残らないため、issue が唯一の永続記録。**再現性** (同 orchestrator が同 issue を再処理して同結論) + **可読性** (人間が短時間で全体像把握)
- **comment フォーマット**: 6 セクション固定 (Acceptance/Scope/Decisions、Q&A、分解戦略、作成 PR、Local verification、再現性ノート)、各 5 行以内 / 合計 30 行目安。詳細は [orchestration.md "Phase 4 issue comment 仕様"](../references/orchestration.md)
- **depth>0** でも実行 (各子が自分の sub-issue にコメント)

---

## Phase 6: Tending (CI green + no-conflict 自律維持)

**設計 core**: skill は remote container (build 環境なし) で並列実行が前提。CI が verify の唯一手段。DRAFT PR 作成で終わらせず、CI green + no-conflict まで責任を持つ。`depth>=0` 全 instance で実行 (各子が自分の PR を tend、Phase 5 と違い depth>0 でも有効)。

- **責務**: 6.1 CI watch (`gh run watch` を **background + Monitor で multi-PR 並行 stream**) / 6.2 CI fail 自動修正 (lint/format/import のみ、≤5 行/1 file 制約) / 6.3 conflict 解消 (`gh pr update-branch` → 失敗時 `git rebase` + `--force-with-lease`)
- **入力**: `state.json.plan.sub_plans[].pr_url` / `repo-profile.ci.fail_classifiers[]` + `expected_duration_min` / `state.json.created_branches[]` (force-with-lease 2 条件 AND check 用)
- **出力**: `<state_dir>/ci-judgment-<N>-r<round>.md` / `conflict-judgment-<N>-r<round>.md` / `state.json.tend.summaries[]` / `state.json.tend.watch_processes[]` (Resume 対策) / `tend_summary` (子 return JSON)
- **判定主体**: orchestrator (`ci-judgment.md` / `conflict-judgment.md` mandate Read、verdict + 物理修正は implement-agent に委譲)
- **対応 mandate**: [references/ci-judgment.md](../references/ci-judgment.md) / [references/conflict-judgment.md](../references/conflict-judgment.md)
- **round 上限 (3 種独立カウント)**: `MAX_TEND_ROUNDS_CI_FIX=3` (自分の fix 起因) / `MAX_TEND_ROUNDS_CONFLICT=2` (upstream churn 起因) / `MAX_TEND_ROUNDS_FLAKY_RETRY=2` (flaky 空 retry、consume_round=false)
- **timeout**: `CI_WATCH_TIMEOUT_MIN = repo-profile.ci.expected_duration_min * 1.5` (default 30 分)
- **escape**: round 上限 / handoff カテゴリ / force-push reject → `escape_hatch_with_pr` + `open_concerns.{ci_persistent_failure / ci_flaky_suspected / ci_unknown / conflict_unresolvable / pr_branch_modified_by_human / force_push_blocked}`
- **並列性**: `MAX_PARALLEL_TEND=3` で同時 watch 数制限 (GitHub API rate limit 1h 5000 req 対策)、超過は queue
- **Monitor で multi-PR 並行 watch**: `gh run watch` を `Bash(run_in_background=true)` で起動、各 process を Monitor で並行 stream。foreground 同期 block の `N × 30min` を `~30min` に圧縮できる (特にローカル multi-PR tend で効く)。`state.json.tend.watch_processes[]` に `run_id` 記録 → session 死亡時の Resume も `gh run view <run_id>` で復元可能 (L39 part 1 解消)

### `--force-with-lease` 例外 (2 条件 AND)
Phase 6.3 のみ、(i) `state.json.created_branches[]` 登録 (自己作成 branch)、(ii) `target != default_branch`、+ branch protection が force 許可、を全て満たす場合のみ。reject 時は retry せず即 handoff (reviewer 直接 commit 上書き防止)。**branch 名 pattern は判定に使わない** (D4 repo-agnostic と整合)。詳細: [design-decisions.md D12](./design-decisions.md)

### Phase 順序: 4 → 6 → 5
Phase 5 retrospect が Phase 6 結果 (CI fail 自動修正の頻発 / conflict 連鎖 rebase 渋滞 / flaky 検出 pattern) を learning material として拾えるよう、Phase 4 (report) → 6 (tend) → 5 (retrospect) の順序。

---

## Phase 5: Retrospect (skill の自律成長)

**depth=0 (top-level orchestrator) のみ実行**。並列子が同時に `LESSONS.md` に append すると race condition で破損するため。

- **責務**: state_dir 全体分析 → 6 category (`script_bug` / `mandate_gap` / `q_a_overhead` / `verify_skipped_pattern` / `user_correction` / success patterns) で learning 抽出 → `<state_dir>/retrospect.md` 詳細 + `<skill_dir>/LESSONS.md` append (削除 / Status 遷移は orchestrator)
- **判定主体**: retrospect-agent (sub-agent) は分析と候補 return のみ。**削除 / Status 遷移は orchestrator** (effort:max、誤判定の最後の砦)
- **対応 mandate**: `references/retrospect.md`
- **次回への取り込み**: Pre-flight で `Status: pending` 最新 20 件 Read (`proposed` / `rejected` は skip)
- **LESSONS.md の運用モデル**: 未消化 learning queue。`pending` / `proposed (issue <URL>)` / `rejected (issue closed)` の 3 状態のみ保持。**`applied` 状態は存在しない** (mandate 反映と同時に entry 物理削除、`git log` が事実 trail を担う)。詳細は [design-decisions.md D11](./design-decisions.md)
- **applied 化削除サイクル**: retrospect-agent が `applied_candidates[]` return → orchestrator が `<skill_dir>` 内 mandate を Read して verdict → 物理削除 + commit (skill_dir 内、commit message に Summary を含めて git log trail 確保)
- **proposed のサイクル**: `gh issue view` で state 確認 → closed+merged なら物理削除、closed+not_planned なら `rejected` Status 遷移 (削除しない、dedupe signal として永続)
- **skill mandate ファイルの自動編集は禁止**: regression リスク回避。pending 20 件超で AskUserQuestion → 同意あれば skill repo に改善 issue 投稿、人間 review を挟む

---

## Phase 間データ受け渡し早見表

| ファイル | write | read |
|---|---|---|
| `repo-profile.{md,json}` | gather-agent | plan-agent / implement-agent / 各 judgment |
| `context.md` | gather-agent (orchestrator が追加 Read で update) | gather-judgment / plan-agent |
| `qa-trail.md` | orchestrator (AskUserQuestion 応答後) | 全 phase |
| `plan.md` / `sub-plan-N.md` | plan-agent | plan-judgment / implement-agent |
| `gather/plan/code/pr-body-judgment-*.md` | orchestrator | retrospect-agent |
| `diff-summary-N-r<round>.txt` | implement-agent | code-judgment (orchestrator) |
| `state.json` | orchestrator | Resume 時 / retrospect-agent |
| `pr-urls.md` | orchestrator (Phase 4) | retrospect-agent / 次回 dedupe-check |
| `retrospect.md` (state_dir) | retrospect-agent | (人間が必要時) |
| `<skill_dir>/LESSONS.md` | retrospect-agent (append のみ) / orchestrator (applied 物理削除 + Status 遷移 + skill_dir 内 commit) | Pre-flight (全 orchestrator、`Status: pending` のみ取り込み) |
| `ci-judgment-<N>-r<round>.md` / `conflict-judgment-<N>-r<round>.md` | orchestrator (Phase 6.2/6.3 で judge) | retrospect-agent (Phase 5 で learning 抽出) |
| `state.json.tend.summaries[]` | orchestrator (Phase 6 完了後 append) | retrospect-agent / 次回 orchestrator Resume |
| `state.json.created_branches[]` | implement-agent (return で append、orchestrator が記録) | orchestrator (Phase 6.3 force-with-lease 2 条件 AND check) |
| `<state_dir>/ci-runs/r<round>/` (`gh run download` 出力) | orchestrator (Phase 6.2 で取得) | ci-judgment.md mandate Read 時 (flaky 判別で前 round と diff) |

---

## Q&A bubble up

並列子 (depth>0) は `AskUserQuestion` を持たない (Task で起動された agent の制約)。代わりに以下のフロー:

1. 子が `status: needs_input` を return (questions 配列を含む)
2. 親 orchestrator が並列子全員の return を待つ
3. 親が `needs_input` のものを集約、1 回の AskUserQuestion で全質問提示 (max 4)
4. 答えを各子の `qa-trail.md` に reflect、子 orchestrator を再起動 (resume from gather Q&A reflection)

**前提**: 親 plan-judgment が sub-issue 化前に「実装可能な明確な単位」に分解する責務を持つ。受け入れ基準が明確なら子で Q&A は基本起こらない。連発するなら親 plan を作り直す signal。

---

## Resume

orchestrator 再起動時の戦略 (詳細 pseudocode: [orchestration.md "Resume 戦略"](../references/orchestration.md))。

1. `state.json` を読んでフェーズ判定
2. 各 sub_plan について `gh pr list --head <branch>` 照会、既存 PR あれば populate して Phase 3 skip (中断後の手動 PR 作成 / 別 session 完走済みで重複 PR 量産を防ぐ)
3. 並列実行で部分完了: `completed_sub_indices` を skip、`in_flight_sub_indices` の各 child state.json を読んで child orchestrator を再起動
4. truth ordering: git branch / filesystem / state.json の順で信頼
