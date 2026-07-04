# Sub-agent return schemas

<context>
全 sub-agent の return JSON schema を集約。orchestrator が return JSON をパースして次の動作を決める参照表。
</context>

## Table of Contents

| Sub-agent / Phase | section |
|---|---|
| gather-agent | [gather-agent return](#gather-agent-return) |
| plan-agent | [plan-agent return](#plan-agent-return) |
| implement-agent (phase=implement / fix_blockers) | [phase=implement の return](#phaseimplement--fix_blockers-の-return) |
| implement-agent (phase=push_and_pr) | [phase=push_and_pr の return](#phasepush_and_pr-の-return) |
| implement-agent (phase=apply_reviewer_feedback) | [phase=apply_reviewer_feedback の return](#phaseapply_reviewer_feedback--reply_to_reviewer-の-return-phase-7) |
| implement-agent (phase=investigate) | [phase=investigate の return](#phaseinvestigate-の-return-phase-15) |
| open_concerns 構造 (kind enum) | [open_concerns の構造](#open_concerns-の構造) |
| retrospect-agent | [retrospect-agent return](#retrospect-agent-return) |
| Recursive sub-orchestrator | [Recursive sub-orchestrator return](#recursive-sub-orchestrator-return-depth0-で-task-起動された-orchestrator) |
| Error fallback | [エラー時の共通 fallback](#エラー時の共通-fallback) |

## 共通ルール

各 sub-agent は最後の出力に **単一の JSON code block** を含めて return する。
orchestrator はその最後の JSON block をパースして次の動作を決める。

- JSON は ` ```json` フェンスで囲む
- 1 response に複数 JSON block があっても、parse 対象は **最後のもの**
- パース失敗時は orchestrator が 1 回 retry を試み、それでも失敗なら catastrophic
- 「必須追加フィールド」以外のフィールドは、そのステータスでは意味を持たないので **`null` または空配列で出力しても、key ごと省略してもよい**

## 大原則: phase sub-agent は judgment しない

v2 設計では、**orchestrator が `references/{role}-judgment.md` を読んで判定する**。
各 phase sub-agent は探索 / draft / 実装の生データを return するだけで、`ready` / `needs_input` / `needs_revise` 等の judgment 結果は出さない。

例外: `catastrophic` (続行不可) のみ、sub-agent が自分の状況で判断して return できる (gh auth 失敗、ネットワーク断、root 解決不能 等)。

---

## gather-agent return

```json
{
  "status": "completed",
  "context_summary": "<1-3 行>",
  "state_dir": "<absolute path>",
  "files_written": ["repo-profile.md", "repo-profile.json", "context.md"],
  "rounds": 1,
  "pre_flight_observations": {
    "issue_state": "open",
    "labels_concerning": [],
    "assignee_status": "none",
    "bug_type": "reproducible"
  },
  "open_observations": [
    "<実装分岐に効く未確定事項 1>"
  ]
}
```

`pre_flight_observations.bug_type` (新、Problem 4/Group C): `null` (feature/refactor、default = bug 関連 mandate は全 skip) / `reproducible` / `intermittent` / `server_side` / `data_dependent` / `race_condition` / `perf_regression` / `repro_unknown`。orchestrator が gather-judgment §1b で判定 + `state.gather.bug_type` に persist。Phase 2 (plan) / Phase 3 (code) で bug-specific mandate を発火するための trigger。

### bug_type cross-phase matrix

| bug_type | gather (producer) | plan (consumer) | code (consumer) | implement (consumer) |
|---|---|---|---|---|
| `null` | feature / refactor | スキップ | スキップ | スキップ |
| `reproducible` | bug + 再現手順あり | Reproduction / Root cause / Verification 必須 | regression test 必須 (Blocker) | — |
| `intermittent` | bug + 間欠 | 上記 + AskUserQuestion 確認 | regression test suggestion | — |
| `server_side` | bug + サーバ side | plan に来るべきでない | `bug_repro_unavailable` 必須 | `INVESTIGATION_RECOMMENDED` |
| `data_dependent` | bug + データ依存 | plan に来るべきでない | `bug_repro_unavailable` 必須 | `INVESTIGATION_RECOMMENDED` |
| `race_condition` | bug + レース | 上記 + AskUserQuestion 確認 | regression test suggestion | — |
| `perf_regression` | パフォーマンス劣化 | benchmark gate 確認 | — | — |
| `repro_unknown` | 再現手順なし | plan に来るべきでない | `bug_repro_unavailable` 必須 | `INVESTIGATION_RECOMMENDED` |

enum 拡張時の同期: gather-judgment.md §1b / plan-judgment.md §12 / code-judgment.md §5e / return-schemas.md L43 の 4 箇所を本表更新で一括同期。

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `completed` | 探索終了。orchestrator が judge へ | `context_summary`, `files_written`, `pre_flight_observations`, `open_observations` |
| `catastrophic` | 続行不可 (gh auth / network / 等) | `reason` |

`pre_flight_observations` は orchestrator が Pre-flight 判定するための生データ:
- `issue_state`: `"open"` / `"closed"`
- `labels_concerning`: `question` / `discussion` / `duplicate` / `wontfix` 等の検出
- `assignee_status`: `"none"` / `"self"` / `"other_recent_active"` / `"other_inactive"`

---

## plan-agent return

```json
{
  "status": "completed",
  "files_written": ["plan.md", "sub-plan-1.md", "sub-plan-2.md"],
  "round": 1,
  "sub_plan_count": 2,
  "sub_plans_summary": [
    {"index": 1, "title": "...", "depends_on": null, "estimated_diff_lines": 150},
    {"index": 2, "title": "...", "depends_on": null, "estimated_diff_lines": 80}
  ]
}
```

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `completed` | draft 終了。orchestrator が judge へ | `files_written`, `sub_plans_summary` |
| `catastrophic` | draft 不能 (全部 human_owned / context 不足) | `reason` |

orchestrator は `plan.md` を Read + `plan-judgment.md` mandate で判定。verdict (`ready` / `needs_revise` / `split_needed` / `recursive_split` / `blocked_by_dependency` / `no_op` / `catastrophic`) を導出する。

---

## implement-agent return

implement-agent は **phase 引数で複数の実行モード**を持つ:
- `phase=implement` (default) または `phase=fix_blockers`: 実装+verify+diff_summary 生成 → review 用 return
- `phase=push_and_pr`: push + PR body draft 書き出し → body 判定待ち return
- `phase=fix_pr_body`: PR body のみ修正 → body 判定待ち return
- `phase=create_pr`: 実 PR create → 完了 return
- `phase=fix_ci_failure` (Phase 6.2): CI fail を constraint 内で自動修正 + push → CI 再 watch 待ち return
- `phase=resolve_conflict` (Phase 6.3): rebase + force-with-lease push → 解消結果 return
- **`phase=apply_reviewer_feedback`** (Phase 7、新): reviewer feedback の `scope_addition` 分類分を constraint 内で反映 + push → review-loop 続行 return
- **`phase=reply_to_reviewer`** (Phase 7、新): PR comment 返信のみ (commit なし) → review-loop 続行 return
- **`phase=investigate`** (Phase 1.5、新): `INVESTIGATION_RECOMMENDED` 時に bug 仮説 + 関連箇所収集 + issue comment 投稿 → 計測 trail return

### phase=implement / fix_blockers の return

```json
{
  "status": "ready_for_review",
  "sub_plan_index": 1,
  "branch": "claude/...",
  "implementation_notes_path": "<state_dir>/implementation-notes-1.md",
  "diff_summary_path": "<state_dir>/diff-summary-1-r1.txt",
  "verify_status": "passed",
  "round": 1,
  "open_concerns": []
}
```

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `ready_for_review` | 実装と verify 完了、orchestrator の code judgment 待ち | `diff_summary_path`, `verify_status`, `branch`, `implementation_notes_path` (Step 4.5 で running update した path、entry 0 件なら `null`)、`created_branch` (新規 branch なら、orchestrator が state.created_branches[] に append) |
| `stuck` | secret 検知 / verify 5 round 全 fail / 等で進めない | `open_concerns`, `branch`, `diff_summary_path` (あれば) |
| `ci_fix_pushed` | `phase=fix_ci_failure` 完了、fix commit + push 済み (CI 再 watch 待ち) | `new_head_sha`, `branch`, `changed_files`, `changed_lines` |
| `ci_handoff` | `phase=fix_ci_failure` で fix_constraints 超過、または handoff カテゴリ detect | `reason`, `branch`, `handoff_kind` (`ci_persistent_failure` 等) |
| `conflict_resolved` | `phase=resolve_conflict` 完了、rebase + force-with-lease push 済み (CI 再 watch 待ち) | `new_head_sha`, `branch` |
| `conflict_handoff` | `phase=resolve_conflict` で textual conflict / force-with-lease reject / 2 条件 AND 不成立 | `reason`, `branch`, `handoff_kind` (`conflict_unresolvable` / `pr_branch_modified_by_human` / `force_push_blocked`) |
| `catastrophic` | gh auth / human_owned 検知 / 等 | `reason`, `branch` (作成済みなら) |

### phase=push_and_pr の return

```json
{
  "status": "created",
  "sub_plan_index": 1,
  "branch": "claude/...",
  "pr_url": "https://github.com/.../pull/123",
  "rounds": {"verify": 1, "code_review": 2},
  "open_concerns": []
}
```

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `ready_for_body_review` | `phase=push_and_pr` or `fix_pr_body` 完了。push 済み + pr-body draft 書き出し済み、実 PR create はまだ | `pr_body_path`, `branch`, `dedupe_result` |
| `created` | `phase=create_pr` 完了。DRAFT PR 作成成功 | `pr_url`, `rounds` |
| `blocked_no_pr` | secret_detected / verify_failure (5 round retry 後) / catastrophic 等で **PR を作らずに止まる** | `open_concerns`, `branch` (作成済みなら) |
| `escape_hatch_with_pr` | code_review_blocker (3 round NEEDS_FIX 残) / diff_too_large 等で **DRAFT PR は作るが open_concerns 残置** | `pr_url`, `open_concerns` |
| `skipped_dedupe` | 重複 PR 既存 (sibling 除外後の真の重複) | `existing_pr_url`, `reason` |
| `catastrophic` | push 失敗 (ネットワーク等) | `reason`, `branch` |

**注 (`stuck` の semantic overload 解消)**: 旧来の `stuck` は「PR 作らず止まる」と「PR 作るが懸念付き」の 2 意味を持っていた。前者を `blocked_no_pr`、後者を `escape_hatch_with_pr` に分離 (集計時の bug 防止)。orchestrator pseudocode / pr-urls.md / Phase 4 report はすべてこの分離に従い、「N 件 created、M 件 escape_hatch_with_pr、K 件 blocked_no_pr」と明示する。

### phase=apply_reviewer_feedback / reply_to_reviewer の return (Phase 7)

```json
{
  "status": "review_fix_pushed",
  "sub_plan_index": 1,
  "branch": "claude/...",
  "new_head_sha": "abc1234",
  "applied_comment_ids": [4476406789, 4476410001],
  "reply_summaries": [
    {"comment_id": 4476420000, "classification": "preexisting_bug", "reply_url": "https://github.com/.../pull/.../comments/..."}
  ],
  "changed_files": 2,
  "changed_lines": 18
}
```

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `review_fix_pushed` | `phase=apply_reviewer_feedback` 完了、scope_addition 分の fix commit + push 済み (CI 再 watch 待ち)。同 round 内の `preexisting_bug` / `off_topic` への reply も実施済み | `new_head_sha`, `branch`, `applied_comment_ids[]`, `reply_summaries[]`, `changed_files`, `changed_lines` |
| `review_fix_handoff` | `phase=apply_reviewer_feedback` で fix_constraints (`MAX_REVIEW_LOOP_FIX_LINES=100` / `MAX_REVIEW_LOOP_FIX_FILES=5`) 超過、または fix 中の自己 verify 失敗 | `reason`, `branch`, `handoff_kind` (`reviewer_feedback_unresolved`), `partial_applied_comment_ids[]` |
| `review_no_actionable` | `phase=reply_to_reviewer` のみ、reply 完了 (commit なし、`preexisting_bug` / `off_topic` のみ) | `reply_summaries[]` |
| `catastrophic` | gh auth / network / human_owned 検知 / 等 | `reason`, `branch` |

`fix_constraints` 引数 (orchestrator が dispatch 時に渡す):
```json
{"max_lines": 100, "max_files": 5, "allowed_kinds": ["dead_code_removal", "simple_refactor", "typo_fix", "comment_update", "test_addition"]}
```

### Phase 別 fix_constraints 一覧

| Phase | max_lines | max_files | allowed_kinds |
|---|---|---|---|
| 6.2 (`fix_ci_failure`) | 5 | 1 | `lint`, `format`, `import_order` |
| 7 (`apply_reviewer_feedback`) | 100 | 5 | `dead_code_removal`, `simple_refactor`, `typo_fix`, `comment_update`, `test_addition` |

field 名は全 phase で統一 (`max_lines` / `max_files` / `allowed_kinds`)。超過時は `git reset HEAD` で取り消し + `status: review_fix_handoff` / `ci_handoff` で return。

Phase 6.2 (`fix_ci_failure`) の `max_lines: 5 / max_files: 1` よりは広いが、commit 前に必ず `git diff --stat HEAD` で制約 check、超過時は `git reset HEAD` で取り消し + `status: review_fix_handoff` で return。

### phase=investigate の return (Phase 1.5)

```json
{
  "status": "investigation_posted",
  "issue_comment_url": "https://github.com/.../issues/123#issuecomment-...",
  "investigation_summary": "<1-3 行>",
  "related_artifacts": {
    "prs": ["#456", "#789"],
    "commits": ["abc1234", "def5678"],
    "files": ["path/to/relevant.swift:42"]
  },
  "hypothesis": "<bug 原因仮説、actionable な形>"
}
```

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `investigation_posted` | bug 仮説 + 関連箇所収集 + issue comment 投稿完了。PR は作らず終了 | `issue_comment_url`, `investigation_summary`, `related_artifacts`, `hypothesis` |
| `catastrophic` | gh / network 等 | `reason` |

orchestrator は `state.report.issue_comments[]` に `{phase: "investigate", url, ts}` を append し、`state.gather.status = "ready"` + `state.gather.investigation_only = true` を set。Phase 2 以降は skip して終了 (skill 終了)。

### `open_concerns` の構造

```json
{
  "open_concerns": [
    {
      "kind": "code_review_blocker",
      "summary": "<1 行>",
      "details": "<必要なら詳細>"
    }
  ]
}
```

`kind` の例とその扱い (Phase 別 grouping):

#### Phase 3/4 関連 (旧来)

| kind | 意味 | orchestrator 動作 |
|---|---|---|
| `code_review_blocker` | code-judgment が出した blocker | needs_fix で再 dispatch |
| `verify_failure` | format/lint/test/build が exit 非0 で失敗 (5 round retry 後) | stuck DRAFT PR、PR body に記録 |
| `verify_skipped` | tool 不在 (exit 127) かつ CI が対応 action を cover (許容判定は `code-judgment.md` §5b が定義本体) | judgment 上は許容。PR body の "Local verification" に記録、reviewer が CI run を確認 |
| `diff_too_large` | 2000 行超 | split_needed、DRAFT PR は作成 |
| `secret_detected` | detect_secrets.sh ヒット | stuck、PR 作らず |

#### Phase 6.2 (CI fail) 関連

| kind | 意味 | orchestrator 動作 |
|---|---|---|
| `ci_persistent_failure` | Phase 6.2 MAX_TEND_ROUNDS_CI_FIX 超過 or HANDOFF カテゴリ | escape_hatch_with_pr、PR body に `run_url` / `classifier_hits` / `attempted_fixes` / `last_log_excerpt` 記録 |
| `ci_flaky_suspected` | Phase 6.2 で 3 連続 flaky 疑い (MAX_TEND_ROUNDS_FLAKY_RETRY 超過) | escape_hatch_with_pr、PR body に「flaky test の根本対応必要」明記 |
| `ci_unknown` | Phase 6.1 CI watch timeout or run trigger 未検出 | escape_hatch_with_pr、最終 run URL を PR body に記載 (reviewer が後で確認) |

#### Phase 6.3 (conflict) 関連

| kind | 意味 | orchestrator 動作 |
|---|---|---|
| `conflict_unresolvable` | Phase 6.3 で `gh pr update-branch` + `git rebase` 両方失敗、または textual conflict | escape_hatch_with_pr、`pr_url` / `attempted_strategies` 記録 |
| `pr_branch_modified_by_human` | Phase 6.3 で `--force-with-lease` reject (reviewer が直接 commit した可能性) | escape_hatch_with_pr、retry しない (reviewer commit を上書き禁止) |
| `force_push_blocked` | Phase 6.3 で 2 条件 AND 不成立 / branch protection block | escape_hatch_with_pr、`reason` 記録 |

#### Phase 7 / 1.5 / LSP fallback 関連 (新)

| kind | 意味 | orchestrator 動作 |
|---|---|---|
| `reviewer_feedback_unresolved` | Phase 7 MAX_REVIEW_LOOP_ROUNDS 超過、または fix_constraints 超過で actionable な scope_addition が残存 | escape_hatch_with_pr、`pr_url` / `unresolved_comment_ids[]` / `reason` 記録 |
| `scope_check_skipped` | LSP runtime 失敗 (`find_references` crash / unindexed file / 曖昧解消失敗) で plan-agent / code-judgment の dead code / scope check が不完全 | escape_hatch_with_pr または PR body 注記、`fallback_method` (`grep_alternation` / `none`) 明示 |
| `bug_repro_unavailable` | bug ticket だが再現手順なし、ローカル再現不能 (`gather.bug_type` が `intermittent` / `server_side` / `data_dependent` / `race_condition` / `repro_unknown`) | escape_hatch_with_pr、PR body に「再現テストなし、人間確認必要」明記 |
| `investigation_posted` | Phase 1.5 で orchestrator が計測結果を issue comment 投稿 (PR は作らず終了) | blocked_no_pr、issue comment URL を `state.report.issue_comments[]` に記録 |

`verify_skipped` の追加フィールド: `{"kind": "verify_skipped", "summary": "test skipped (tool unavailable, CI covers)", "details": "rc=5 from run_command.sh test; ci.covered_actions includes 'test'; CI workflow: .github/workflows/ci.yml", "action": "test", "reason": "tool unavailable", "ci_workflow": ".github/workflows/ci.yml"}`

### enum 値 cross-reference table

主要 enum 値の producer / consumer / schema の三点同期表 (`retrospect.md` R75 の同期漏れ pattern を防ぐ):

| enum | producer | consumer (judgment) | consumer (agent) | schema 定義 |
|---|---|---|---|---|
| `bug_type` (8 値) | gather-judgment §1b | plan-judgment §12 / code-judgment §5e | implement-agent (`phase=investigate`) | return-schemas.md L43 + bug_type table |
| `open_concerns.kind` (15 値) | code-judgment / ci-judgment / conflict-judgment / review-comment-judgment / implement-agent | pr-body-judgment §7 | retrospect-agent | return-schemas.md (本表) |
| `phase` (引数、9 値) | orchestrator (Task dispatch) | implement-agent | — | implement-agent return schema |
| `status` (per phase 別) | implement-agent | orchestrator | retrospect-agent | return-schemas.md 各 phase section |
| `implement.mode` (4 値) | orchestrator (Phase 2.5/2.6 AskUserQuestion) | implement-agent / pr-body-judgment §2 | retrospect-agent | orchestration.md |

enum 拡張時の規律: 5 enum いずれも producer / consumer / schema の 3 箇所同期が必要 (`retrospect.md` R75 参照)。

---

## retrospect-agent return

```json
{
  "status": "completed",
  "retrospect_path": "<state_dir>/retrospect.md",
  "lessons_appended": 2,
  "lessons_skipped_as_low": 1,
  "lessons_skipped_as_duplicate": 1,
  "pending_count_after_append": 7,
  "propose_skill_improvement_issue": false,
  "applied_candidates": [
    {"L": "L3", "summary": "smoke test 必須化", "reflected_in": ["SKILL.md:201"], "confidence": "high"}
  ],
  "proposed_lesson_status": [
    {"L": "L12", "issue_url": "https://github.com/ha1f/news/issues/42", "state": "closed", "reason": "completed"}
  ],
  "frequent_patterns": [
    {"existing_lesson_id": "L3", "new_lesson_summary": "...", "occurrences": 2}
  ]
}
```

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `completed` | retrospect 完了 (LESSONS.md append 済み、applied/proposed 候補は return のみ、削除/遷移は orchestrator) | `retrospect_path`, `lessons_appended`, `pending_count_after_append`, `propose_skill_improvement_issue`, `applied_candidates`, `proposed_lesson_status` |
| `catastrophic` | state_dir 破損 / LESSONS.md 書き込み不能 | `reason` |

orchestrator は以下を実行:
- `propose_skill_improvement_issue: true` → AskUserQuestion (depth=0) → 同意あれば `gh issue create` → 該当 pending entry の Status を `proposed (issue <URL>)` に書き換え
- `applied_candidates[]` → 各候補について `<skill_dir>` 内 mandate ファイルを Read して verdict → 反映済みなら entry を物理削除 + `git commit` (skill_dir 内、commit message に Summary 含める)
- `proposed_lesson_status[]` で `state: closed + reason: completed (merged)` → applied として物理削除、`reason: not_planned` → Status を `rejected (issue <URL> closed at <ts>)` に書き換え

`frequent_patterns` は append しなかった「既存 lesson (pending/proposed/rejected) と類似」のもので、頻発パターン把握用 (issue 提案の説得材料として参照可)。

---

## Recursive sub-orchestrator return (depth>0 で Task 起動された orchestrator)

depth>0 で Task 起動された orchestrator (1 つの sub-issue を担当) は、親 orchestrator に向けて return する。スキーマ:

```json
{
  "status": "completed",
  "sub_issue_id": "456",
  "sub_issue_url": "https://github.com/.../issues/456",
  "branch": "claude/...",
  "pr_url": "https://github.com/.../pull/789",
  "pr_status": "created",
  "rounds": {"gather": 1, "plan": 1, "verify": 1, "code_review": 2},
  "tend_summary": {
    "rounds_ci_fix": 1,
    "rounds_conflict": 0,
    "rounds_flaky_retry": 0,
    "outcome": "ci_green",
    "classifier_hits": ["lint"],
    "final_run_url": "https://github.com/.../runs/...",
    "review_loop_rounds": 1,
    "review_loop_replies": [{"comment_id": 12345, "classification": "preexisting_bug", "reply_url": "..."}],
    "last_seen_comment_id": 4476406789
  },
  "open_concerns": [],
  "needs_input": null
}
```

`tend_summary` は depth>0 子の Phase 6 結果を親に伝える。親は `<state_dir>/tend-summaries/` に集約 → Phase 5 retrospect-agent が読んで「CI fail 自動修正の頻発」「conflict 連鎖 rebase 渋滞」等の learning に活用。`outcome` は `ci_green` / `ci_handoff` / `conflict_handoff` / `ci_unknown` のいずれか。

| `status` | 意味 | 必須追加フィールド |
|---|---|---|
| `completed` | sub-issue で 1 つの DRAFT PR を作成 (created or stuck) | `pr_url`, `pr_status` |
| `needs_input` | 子で Q&A が必要、親に bubble up | `needs_input` 配列 (questions と同じスキーマ)、`partial_state_path` (再 dispatch 用) |
| `catastrophic` | 続行不可 | `reason` |
| `skipped_dedupe` | sub-issue の段階で重複検出、PR 作らず | `existing_pr_url`, `reason` |

### `needs_input` の構造 (bubble up 用)

```json
{
  "needs_input": [
    {
      "id": "Q1",
      "header": "<12 文字以内>",
      "question": "<質問本文>",
      "options": [
        {"label": "...", "description": "..."},
        {"label": "skip / 不明", "description": "後で決める"}
      ],
      "multi_select": false,
      "why": "<実装分岐への影響>"
    }
  ],
  "partial_state_path": "<state_dir>/state.json"
}
```

親 orchestrator は全並列子の return を待ち、`needs_input` のものを集約 (合計 max 4 質問に絞る) → AskUserQuestion → 答えを子の qa-trail.md に reflect → 子を再起動。

---

## エラー時の共通 fallback

- どの sub-agent も、JSON フェンスを出せない致命的状況になったら、最終出力に以下を出す:

  ```json
  {"status": "catastrophic", "reason": "<エラー内容>"}
  ```

- orchestrator はこれを受け取ったら AskUserQuestion (depth=0 のみ) で「stop / 続行 (該当 sub-plan / sub-issue を skip)」を尋ねる
