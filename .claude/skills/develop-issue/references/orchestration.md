# Orchestration rules

orchestrator (SKILL.md 本体) がフェーズを進める時の判定ロジック、state.json スキーマ、並列 Task / Q&A bubble up / 再起動時の振る舞い。

各 Phase の詳細 pseudocode は `phases/*.md` を Read:

- [phases/phase-1-gather.md](phases/phase-1-gather.md) — Phase 1 + 1.5 (gather loop + investigate)
- [phases/phase-2-plan.md](phases/phase-2-plan.md) — Phase 2 + 2.5 + 2.6 (plan + ModeSelect + SubIssueCreate)
- [phases/phase-3-implement.md](phases/phase-3-implement.md) — Phase 3 (chained sequential / single)
- [phases/phase-4-report.md](phases/phase-4-report.md) — Phase 4 (issue comment 仕様含む)
- [phases/phase-6-tending.md](phases/phase-6-tending.md) — Phase 6.1-6.3 (CI watch / fix / conflict)
- [phases/phase-7-review-loop.md](phases/phase-7-review-loop.md) — Phase 7.1-7.5 (reviewer comment loop)
- [phases/phase-5-retrospect.md](phases/phase-5-retrospect.md) — Phase 5 (depth=0 only、LESSONS.md 更新)

## 定数

| 名前 | 値 | 根拠 |
|---|---|---|
| `MAX_DEPTH` | `2` | 再帰 sub-issue の最大深さ。0=ユーザ起動、1=child、2=grandchild。grandchild が分割要求しても `split_needed` に fallback (指数爆発と階層追跡コスト抑止) |
| `MAX_GATHER_ROUNDS` | `5` | gather Q&A の上限。超過後は毎 round 「続行 / 中止」を再確認 |
| `MAX_PLAN_ROUNDS` | `2` | plan revise の上限。超過で `ready_with_concerns` で進む |
| `MAX_CODE_ROUNDS` | `3` | code review 再修正の上限。超過で escape-hatch (DRAFT PR + open_concerns) |
| `MAX_DIFF_LINES` | `2000` | diff 規模上限。超過で `split_needed` |
| `MAX_TEND_ROUNDS_CI_FIX` | `3` | Phase 6.2 CI fail 自動修正 round 上限 (自分の fix 起因)。超過で `escape_hatch_with_pr` |
| `MAX_TEND_ROUNDS_CONFLICT` | `2` | Phase 6.3 conflict 解消 round 上限 (CI fix と独立カウント)。3 回目で handoff |
| `MAX_TEND_ROUNDS_FLAKY_RETRY` | `2` | Phase 6.2 flaky 判別時の空 retry 上限 (`consume_round=false`)。3 連続 flaky で handoff |
| `CI_WATCH_TIMEOUT_MIN_DEFAULT` | `30` | Phase 6.1 CI watch timeout (`repo-profile.ci.expected_duration_min * 1.5`、未設定なら 30 分) |
| `MAX_PARALLEL_TEND` | `3` | Phase 6 同時 `gh run watch` 上限 (GitHub API rate limit 1h 5000 req 対策、超過は queue) |
| `CI_RUN_POLLING_INTERVAL_SEC` | `60` | Phase 6.1 push 直後の run trigger 不安定対策で `gh run list` を polling する間隔 |
| `CI_RUN_POLLING_MAX_ATTEMPTS` | `5` | 同上の polling 試行回数上限 (5 分 = 60s × 5)。超過で `TIMEOUT_UNKNOWN` |
| `MAX_REVIEW_LOOP_ROUNDS` | `2` | Phase 7 round 上限。超過で `escape_hatch_with_pr` + `reviewer_feedback_unresolved` |
| `MAX_PARALLEL_REVIEW_LOOP` | `3` | Phase 7 同時 review-loop 上限 (`MAX_PARALLEL_TEND` と独立カウント) |
| `MAX_REVIEW_LOOP_FIX_LINES` | `100` | Phase 7 reviewer fix の変更行数上限 (人間 AskUserQuestion 確認済前提)。超過で handoff |
| `MAX_REVIEW_LOOP_FIX_FILES` | `5` | 同上 file 数上限 |
| `SCHEMA_VERSION_CURRENT` | `"1.1"` | state.json schema 版数。Resume で不在 / 古い場合は orchestrator が auto-migrate |

## State directory

各 (sub-)issue が独立した state dir を持つ:

```
<repo-root>/.claude/tmp/impl-<id>/
├── state.json
├── repo-profile.md / .json       # gather-agent が書く
├── context.md                    # gather-agent が書く
├── qa-trail.md                   # orchestrator が AskUserQuestion 回答を append
├── gather-judgment-<N>.md        # orchestrator が書く (judgment 結果)
├── plan.md                       # plan-agent が書く
├── sub-plan-<N>.md               # plan-agent が書く (sub_plans が複数の場合)
├── plan-judgment-<N>.md          # orchestrator が書く
├── diff-summary-<N>-r<round>.txt # implement-agent が書く
├── implementation-notes-<N>.md   # implement-agent が Step 4.5 で running append (free text、判断 trail、PR body 「代替案」「誤解されそうな観点」の source)。path は state.json に persist せず、consumer (code-judgment / pr-body-judgment / Phase 4 / Phase 7 / retrospect-agent) は glob `implementation-notes-*.md` で発見する (return JSON `implementation_notes_path` は 1 sub-plan 分の hint のみ、cross sub-plan は glob 必須、R-B-7)
├── code-judgment-<N>-<round>.md  # orchestrator が書く
├── pr-urls.md                    # orchestrator が append
└── (depth>0 のみ) parent-link.json   # {parent_issue, parent_state_dir, recursion_depth}
```

state dir は `<repo-root>/.claude/tmp/` 配下なので、対象リポジトリの `.gitignore` で `.claude/tmp/` が ignore されていることを起動時に確認する (推奨)。ignore されていない場合は警告し、AskUserQuestion で「ignore を追加して続行 / 別パスに退避 / 中止」を聞く (depth=0 のみ)。

## state.json schema (`schema_version: "1.1"`)

```jsonc
{
  "schema_version": "1.1",                  // string、SCHEMA_VERSION_CURRENT と一致するか migrate
  "issue": {
    "id": "<numeric>",
    "url": "<github issue URL>",
    "title": "<string>",
    "labels": ["<label>", ...]
  },
  "recursion_depth": 0,                     // 0..MAX_DEPTH
  "parent_issue": null,                     // depth>0 なら親 issue id
  "started_at": "<ISO 8601>",
  "updated_at": "<ISO 8601>",
  "gather": {
    "status": "pending|in_progress|ready|stop_recommended|catastrophic",
    "rounds": <int>,
    "questions_asked": <int>,
    "bug_type": null,                       // null | reproducible | intermittent | server_side | data_dependent | race_condition | perf_regression | repro_unknown
    "investigation_only": false             // true なら Phase 2-6 skip、Phase 5 のみ
  },
  "plan": {
    "status": "pending|in_progress|ready",
    "rounds": <int>,
    "verdict": "READY|SPLIT_NEEDED|RECURSIVE_SPLIT|ready_with_concerns",
    "sub_plans": [                          // 各 sub-plan の状態
      {
        "index": <int>, "title": "...", "branch": "...", "base": "main",
        "depends_on": null,                 // 別 sub-plan index | null
        "pr_url": "<github PR URL>", "pr_status": "created|escape_hatch_with_pr|skipped_dedupe|blocked_no_pr|skipped_due_to_upstream|child_cancelled_by_human|stuck|catastrophic",
        "sub_issue_id": null, "sub_issue_url": null,   // chained_with_subissues / parallel_recursive のみ non-null
        "verify_summary": { "passed": [...], "skipped": [{"action": "...", "reason": "...", "ci_workflow": "..."}], "failed": [...] },
        "code_review_rounds": <int>,
        "open_concerns": [{"kind": "...", "summary": "...", ...}],
        "scope_extension_proposals": [...]
      }
    ]
  },
  "implement": {
    "mode": "single|chained_in_memory|chained_with_subissues|parallel_recursive",
    "completed_sub_indices": [...], "in_flight_sub_indices": [...]
  },
  "report": {
    "status": "pending|ready|failed",
    "issue_comments": [                     // 各 phase の progress comment URL
      {"phase": "gather|plan|implement_sub_<N>|report|investigate", "url": "...", "ts": "<ISO>"}
    ]
  },
  "tend": {
    "status": "pending|in_progress|ready", "review_loop_status": "pending|in_progress|ready|parent_closed_terminate",
    "summaries": [
      {
        "sub_plan_index": <int>,
        "rounds_ci_fix": <int>, "rounds_conflict": <int>, "rounds_flaky_retry": <int>,
        "outcome": "ci_green|ci_handoff|conflict_handoff|ci_unknown|review_loop_no_actionable|review_loop_handoff|review_loop_user_deferred|no_review_received",
        "classifier_hits": [...], "final_run_url": "...",
        "last_seen_comment_id": <int>, "review_loop_rounds": <int>, "review_loop_replies": [...]
      }
    ],
    "watch_processes": [
      {"sub_plan_index": <int>, "run_id": "...", "current_step": "watching|fixing_ci|resolving_conflict|review_loop_polling", "started_at": "<ISO>", "bash_id": "..."}
    ]
  },
  "created_branches": ["...", ...]          // Phase 6.3 で --force-with-lease 適用条件 check に使う
}
```

### Schema version 履歴

| version | 主な変更 |
|---------|----------|
| `"1.0"` | 初版 (`schema_version` field なし、`report.issue_comment_url` singular、`implement.mode: "chained_sequential"` 等の旧 enum) |
| `"1.1"` | Phase 7 (Review-loop) 対応: `report.issue_comments[]` array、`tend.summaries[].last_seen_comment_id` / `review_loop_rounds` / `review_loop_replies[]` 追加、`implement.mode` enum split (`chained_sequential` → `chained_in_memory` / `chained_with_subissues`)、`sub_plans[].sub_issue_id` / `sub_issue_url` を全 mode で持つ、`sub_plans[].scope_extension_proposals[]` 追加、`gather.bug_type` 追加 |

### Resume 時の migration shim (auto-migrate、1.0 → 1.1)

```python
def migrate_state(state):
  if state.get("schema_version") == SCHEMA_VERSION_CURRENT:
    return state  # 最新
  v = state.get("schema_version", "1.0")
  if v == "1.0":
    # report.issue_comment_url (singular) → issue_comments[] (array)
    state.setdefault("report", {})
    if state["report"].get("issue_comment_url"):
      state["report"]["issue_comments"] = [{
        "phase": "report",
        "url": state["report"].pop("issue_comment_url"),
        "ts": state.get("updated_at", "1970-01-01T00:00:00Z")
      }]
    elif "issue_comments" not in state["report"]:
      state["report"]["issue_comments"] = []
    # implement.mode rename
    state.setdefault("implement", {})
    if state["implement"].get("mode") == "chained_sequential":
      state["implement"]["mode"] = "chained_in_memory"  # 暫定マッピング
      # 注: chained_with_subissues 相当の case でも chained_in_memory に丸まる情報損失あり
      # Resume 時に sub_plans[].sub_issue_id が non-null なら orchestrator が再検出して chained_with_subissues に補正
      sub_plans = state.get("plan", {}).get("sub_plans", [])
      if any(sp.get("sub_issue_id") for sp in sub_plans):
        state["implement"]["mode"] = "chained_with_subissues"
    # tend.summaries[] 各 entry に new field の default
    state.setdefault("tend", {})
    state["tend"].setdefault("status", "pending")
    state["tend"].setdefault("review_loop_status", "pending")
    for s in state["tend"].get("summaries", []):
      s.setdefault("last_seen_comment_id", 0)
      s.setdefault("review_loop_rounds", 0)
      s.setdefault("review_loop_replies", [])
      s.setdefault("outcome", None)
      s.setdefault("rounds_ci_fix", 0)
      s.setdefault("rounds_conflict", 0)
      s.setdefault("rounds_flaky_retry", 0)
    state["tend"].setdefault("watch_processes", [])
    state["tend"].setdefault("summaries", [])
    # sub_plans[] 各 entry の new field の default
    for sp in state.get("plan", {}).get("sub_plans", []):
      sp.setdefault("sub_issue_id", None)
      sp.setdefault("sub_issue_url", None)
      sp.setdefault("scope_extension_proposals", [])
      sp.setdefault("followup_issue_url", None)
    # gather.bug_type / investigation_only の default
    state.setdefault("gather", {})
    state["gather"].setdefault("bug_type", None)
    state["gather"].setdefault("investigation_only", False)
    # created_branches default
    state.setdefault("created_branches", [])
    state["schema_version"] = "1.1"
  return state
```

Resume 戦略 で必ず実行。orchestrator が state.json を Read した直後、`migrate_state(state)` を呼んで save 直前に `schema_version` を最新値に更新する。

### 主要 schema フィールドの位置づけ

**per-sub-plan 結果は `plan.sub_plans[]` に集約** (`pr_url`, `pr_status`, `verify_summary`, `code_review_rounds`, `open_concerns`)。`implement.{mode, completed_sub_indices, in_flight_sub_indices}` は実行 orchestration の進捗状態だけ持ち、結果は持たない (DRY: 結果の所在は 1 箇所)。

`sub_plans[].verify_summary` はローカル verify skip の追跡に使う。Phase 4 (`build_issue_report`) がここを Read して "Local verification" セクションを生成する。

**recursive_split 時の追加フィールド** (parallel_recursive mode): `sub_plans[]` entry に `sub_issue_id` / `sub_issue_url` / `child_state_dir` / `child_status` ("pending"/"in_flight"/"completed"/"catastrophic") が追加され、`pr_url` / `pr_status` は child orchestrator return から populate。`verify_summary` は子の state.json にあり親側には複製しない (各 sub-issue の issue-report.md で独立に summarize)。

`report.status` は `pending` / `ready` / `failed` (gh issue comment 失敗時)。失敗しても PR は既に作成済みなので Phase 全体は失敗扱いにしない。

| `status` フィールドの値 | 意味 |
|---|---|
| `pending` | まだ着手していない |
| `in_progress` | 着手中 |
| `ready` | 完了 |
| `stop_recommended` | 続行非推奨 (gather のみ) |
| `catastrophic` | 続行不可 |

| `implement.mode` | sub-issue 作成 | 並列実行 | 用途 |
|---|---|---|---|
| `single` | × | × | sub-plan 1 個、直接 implement |
| `chained_in_memory` | × | × | sub-plan 複数、in-memory のみで順次。sub-issue 化なし、PR は `Part of #<元 issue> (N/M)` で trace |
| `chained_with_subissues` | ○ | × | sub-plan 複数、sub-issue 化して順次。親 issue 上で進捗 trace 可、PR は `Closes #<sub_issue> + Part of #<parent>` 形式 |
| `parallel_recursive` | ○ | ○ | sub-plan 全 `depends_on: null` (= 完全独立)、sub-issue 化して並列子 orchestrator 起動 |

**判定**: plan-judgment.md "分解戦略 discriminator" で verdict (`recursive_split` / `split_needed` / `ready`) を出す → orchestrator が Phase 2.5 で AskUserQuestion (depth=0、重い副作用確認) で mode を選択。**size 閾値は verdict 分岐に組み込まない** (D2 1-line discriminator 維持)。size signal は plan-agent の reasonable call 根拠材料としてのみ使用。

| `gather.bug_type` (新、`null` 可) | 意味 |
|---|---|
| `null` | feature / refactor / 非 bug (default、`bug` label 不在時) |
| `reproducible` | 再現手順あり、feature と同 flow |
| `intermittent` | 間欠 bug、再現テスト書く / 強行 を AskUserQuestion |
| `server_side` | サーバ side bug、client では再現不能 → INVESTIGATION_RECOMMENDED |
| `data_dependent` | 本番データ依存、ローカル再現不能 → INVESTIGATION_RECOMMENDED |
| `race_condition` | レース条件、再現テスト書く / 強行 を AskUserQuestion |
| `perf_regression` | パフォーマンス劣化、benchmark gate なしなら HANDOFF |
| `repro_unknown` | 再現手順無く judgment 不能 → INVESTIGATION_RECOMMENDED |

`tend.summaries[]` は Phase 6 (Tending) の per-sub-plan 結果 (CI green / conflict 解消の round 数、最終 outcome、最終 run URL)。Phase 5 retrospect-agent が読んで「CI fail 自動修正が頻発した pattern」「conflict 連鎖 rebase 渋滞」等の learning に活用。

`tend.watch_processes[]` は Phase 6.1 で `gh run watch` を background 起動した process を追跡 (`run_id` / `current_step: watching|fixing_ci|resolving_conflict` / `started_at`)。Monitor で multi-PR 並行 watch + Resume 対策の両方を担う: session が死んで background process が消えても、Resume 時に各 `run_id` について `gh run view <run_id> --json status,conclusion` で「すでに終了している run」を復元 → completed なら Monitor 起動せず conclusion で直接 Phase 6.2/6.3 へ分岐。

`created_branches[]` は Phase 6.3 で `--force-with-lease` 適用の 2 条件 AND check (「自己作成 branch のみ force 許容」) に使う。implement-agent が branch 作成時に append、orchestrator は読むのみ。

## Phase 進行ロジック (概要)

全 Phase 通しての制御フロー:

```
Phase 1 (Gather)
  → judgment verdict 分岐:
    - READY → Phase 2
    - INVESTIGATION_RECOMMENDED + user 選択 "agent に計測代行" → Phase 1.5
    - STOP_RECOMMENDED / NEEDS_INPUT → AskUserQuestion or bubble up
Phase 1.5 (Investigate、investigation_only==True 時のみ)
  → Phase 5 (Retrospect) のみ実行、Phase 2-7 skip
Phase 2 (Plan)
  → verdict 分岐:
    - READY → Phase 3 (single mode)
    - SPLIT_NEEDED → Phase 2.6 (chained_with_subissues) or 直接 Phase 3 (chained_in_memory)
    - RECURSIVE_SPLIT → Phase 2.5 (AskUserQuestion で mode 選択)
Phase 2.5 (ModeSelect、recursive_split 時)
  → parallel_recursive → Phase 2.6 で sub-issue 化 + 並列子起動 → Phase 4
  → chained_with_subissues → Phase 2.6 → Phase 3
  → chained_in_memory → Phase 3
Phase 2.6 (SubIssueCreate helper、sub-issue 化要時のみ)
Phase 3 (Implement、chained sequential / single)
  → 各 sub-plan ごとに implement → code judge → push_and_pr → PR body judge → create_pr
Phase 4 (Report、authoritative)
  → issue comment で 6 セクション固定 trail 投稿 (詳細フォーマットは [phases/phase-4-report.md](phases/phase-4-report.md))
Phase 6 (Tending、depth>=0 並列)
  → 6.1 CI watch → 6.2 CI fail 修正 / 6.3 Conflict 解消
Phase 7 (Review-loop、depth>=0 並列、Phase 6 後)
  → 7.1 polling → 7.2 3 分類 → 7.3 AskUserQuestion → 7.4 反映 → 7.5 sub-issue 同期
Phase 5 (Retrospect、depth=0 only)
  → LESSONS.md 更新
```

各 Phase の詳細 pseudocode は本 file 冒頭の `phases/*.md` リンクを参照。

## 並列 Task 起動 (Phase 2.5b)

```python
def parallel_run_recursive_children(sub_plans, depth):
  # 全 sub-plan に対して 1 つの Task を起動。同 message 内多重 Task call で並列実行。
  # 各 Task の prompt は SKILL.md の Phase orchestration を inline + 引数:
  #   issue=<sub_issue_id>, state_dir=<child_state_dir>, skill_dir=<...>,
  #   recursion_depth=<depth>, parent_issue=<parent_issue_id>
  
  task_calls = []
  for sp in sub_plans:
    task_calls.append({
      "subagent_type": "general-purpose",
      "description": f"sub-issue #{sp.sub_issue_id}",
      "prompt": render_sub_orchestrator_prompt(sp, depth)
    })
  
  # 同 message 内多重 Task call → 並列実行
  results = invoke_all_tasks_in_single_message(task_calls)
  
  # 集約 (Phase 1 gather Q&A、Phase 7 review-comment 両方の source を aggregate)
  needs_input_aggregate = []
  for sp, result in zip(sub_plans, results):
    parsed = parse_json(result)
    if parsed.status == "needs_input":
      # needs_input.source: "gather" / "review_loop" / "investigate" 等で分類
      source = parsed.needs_input_source or "gather"
      needs_input_aggregate.append((sp, parsed.needs_input, source, parsed.partial_state_path,
                                    parsed.get("review_judgment_path")))
    elif parsed.status in ("completed", "skipped_dedupe"):
      sp.pr_status = parsed.pr_status
      sp.pr_url = parsed.pr_url
      # Phase 7 結果も親に集約
      if parsed.get("tend_summary"):
        sp.tend_summary = parsed.tend_summary  # review_loop_rounds / review_loop_replies / last_seen_comment_id 含む
      append_to(state_dir + "/pr-urls.md", parsed.pr_url)
    elif parsed.status == "catastrophic":
      sp.pr_status = "catastrophic"
      sp.reason = parsed.reason
  
  # Q&A bubble up handling (Phase 1 gather + Phase 7 review-comment 共通)
  if needs_input_aggregate:
    questions = pick_top_4_questions_across_children(needs_input_aggregate)
    # questions の前に header で source を明示 ("[Gather]" / "[Review]")
    answers = AskUserQuestion(questions + meta_question)
    distribute_answers_to_children(answers, needs_input_aggregate)  # source 別に振り分け
    # 子を再起動 (Phase 1 gather 起点 vs Phase 7 review-loop 起点で entry point 別)
    parallel_run_recursive_children(
      [sp for sp, _, _, _, _ in needs_input_aggregate],
      depth,
      resume_from_phase=lambda sp, src: "review_loop" if src == "review_loop" else "gather"
    )
```

`distribute_answers_to_children` の振り分けルール:

| source | 書き込み先 | 子の resume 起点 |
|---|---|---|
| `gather` | 子の `qa-trail.md` に append | Phase 1 |
| `review_loop` | 子の `review-judgment-<idx>-r<round>.md` に user_choice 追記 | Phase 7.4 |
| `investigate` | 子の `investigation-artifacts.md` に append | Phase 1.5 |

## AskUserQuestion 構築ルール (depth=0 のみ)

- gather-judgment から得た `questions` (max 4) を **そのまま** AskUserQuestion に渡す
  - `header` フィールドはそのまま (12 文字以内チェック)
  - `options` はそのまま (skip 相当を含む)
- 末尾に必ずメタ質問を追加 (合計が 4 を超えるなら、questions を 3 個に絞る):

```python
meta_question = {
  "question": "情報収集はもう十分ですか?",
  "header": "Continue?",
  "options": [
    {"label": "もう一度レビューする", "description": "..."},
    {"label": "このまま Plan に進む", "description": "..."}
  ],
  "multiSelect": False
}
```

## Resume 戦略

`<state-dir>` が存在する場合の起動時動作:

1. `state.json` を読む
2. **schema migration**: `state.schema_version` を確認、`SCHEMA_VERSION_CURRENT` ("1.1") と異なる / 不在 (= 1.0 互換) なら `migrate_state(state)` を実行して新スキーマに変換 → save (詳細は上記 §"Resume 時の migration shim")
3. `gather.status != "ready"` → Phase 1 から
4. `plan.status != "ready"` → Phase 2 から
5. `plan.verdict == "RECURSIVE_SPLIT"`:
   - 各 `sub_plans[].sub_issue_id` を確認
   - `child_state_dir` を確認、未完の child orchestrator を再起動 (並列で `in_flight_sub_indices` 全員、同 message で)
6. `implement.current_sub_plan < len(sub_plans)` → Phase 3 を current_sub_plan から (chained_in_memory / chained_with_subissues の場合)
7. implement-agent 自身は branch 存在と diff-summary / code-judgment ファイルから resume
8. **既存 PR detection**: 各 sub_plan について `gh pr list --head <branch> --state all --json number,url,state` で既存 PR を照会。見つかれば state.json sub_plan に `pr_url` / `pr_status` を populate し、Phase 3 を skip して Phase 4 (Report) へ。複数 PR ヒットなら AskUserQuestion で「既存再利用 / 新規作成」を確認。skill 中断後の手動 PR 作成 / 別 session 完走済みでの重複 PR 量産を防ぐ
9. **CI run trigger 未検出 escape 後の resume**: `state.tend.summaries[]` の `outcome: "ci_unknown"` entry について、対応 `sp.head_sha` と現在の `gh pr view <pr_url> --json headRefOid` を比較。変わっていれば (user が手動 push した) → Phase 6.1 の polling を再開、`run_id` 再取得を試行

git 上に branch が存在することが source of truth。state.json はあくまで効率化のヒント。

### Resume 分岐の pseudocode

```python
# orchestrator 起動時
if file_exists(state_dir + "/state.json"):
  state = read_json(state_dir + "/state.json")
  state = migrate_state(state)  # schema_version 不一致なら 1.0→1.1 auto-migrate
  save_state(state)  # migrated state を save (subsequent code が新スキーマ前提で動く)
  if (now() - state.updated_at).total_seconds() < 900:
    ans = AskUserQuestion([("続行", "..."), ("中止", "...")])
    if ans == "中止": exit(0)
  # 既存 PR detection (各 sub_plan)
  for sp in state.plan.sub_plans or []:
    if sp.branch and not sp.pr_url:
      existing = run(f"gh pr list --head {sp.branch} --state all --json number,url,state")
      if existing:
        if len(existing) > 1:
          ans = AskUserQuestion([("既存再利用", "..."), ("新規作成", "...")])
          if ans == "既存再利用":
            sp.pr_url = existing[0].url
            sp.pr_status = "created"
        else:
          sp.pr_url = existing[0].url
          sp.pr_status = "created"
  save_state(state)
  # 通常 resume 戦略 (gather → plan → implement.current_sub_plan) で続行
else:
  state = {}
  # 初回起動
```

## 並行起動検知

orchestrator 起動時:
- `<state-dir>/state.json` が存在し、`updated_at` が **15 分以内** ならば、別セッションが進行中の可能性
- AskUserQuestion (depth=0 のみ) で「他で実行中の可能性あり。続行 / 中止」を確認

## ガードレール (orchestrator が自分で守る)

- 重い command (build / test / git mutation) は implement-agent に委譲
- 例外 (orchestrator の責務): `gh issue create / edit / comment` / `git diff` (read-only) / state dir 内ファイルの write
- フェーズを skip しない (state.json で完了済みでも、依存関係が破綻していたら検知)
- 同じ sub-agent を同一引数で 3 回以上呼ばない (loop 検知)

## catastrophic ハンドリング

`status: "catastrophic"` を受け取ったら:
1. `reason` を state.json に記録
2. これまでに作った PR (`pr-urls.md`) はそのまま残す
3. depth=0 → AskUserQuestion で `["中止 (推奨)", "次の sub-plan を試す"]`
4. depth>0 → 親に bubble up (`status: "catastrophic"` で return)

Phase 1 / B の catastrophic は実装フェーズに行けないので「中止」一択 (確認のみ)。
Phase 3 の catastrophic は次 sub-plan を試す選択肢あり (parallel mode では他の siblings は続行)。

## Sub-issue dedupe (false positive 回避)

implement-agent が dedupe-check する時、`parent_issue` 引数が渡されている場合は:
- `gh search prs` で見つかった候補のうち、PR body に `Part of #<parent_issue>` を含むものは **sibling として除外** (false positive 回避)
- これ以外は通常通り重複扱い

orchestrator が implement-agent に `parent_issue` 引数を渡すことで、子 implement-agent がこの除外ルールを適用できる。
