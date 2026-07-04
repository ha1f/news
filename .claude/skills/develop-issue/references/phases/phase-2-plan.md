# Phase 2, 2.5, 2.6 — Plan + ModeSelect + SubIssueCreate

## Phase の目的・前提・後続

- **目的**: plan-agent で `plan.md` / `sub-plan-N.md` を draft し、orchestrator が `plan-judgment.md` mandate に従って分解戦略 verdict を出す。verdict は `READY` / `SPLIT_NEEDED` / `RECURSIVE_SPLIT` / `NEEDS_REVISE` / `BLOCKED_BY_DEPENDENCY` / `NO_OP` の 6 種
- **前提**: Phase 1 完了 (`state.gather.status == "ready"` かつ `investigation_only==False`)、`state.gather.bug_type` populate 済み
- **後続への影響**: `state.plan.verdict` と `state.implement.mode` を確定。`parallel_recursive` / `chained_with_subissues` の場合は sub-issue 作成 + 親 issue body update を伴う

## Phase 2: Plan loop (pseudocode)

```python
plan_round = 1
while plan_round <= 2:
  result = Task(plan-agent, args={issue, state_dir, skill_dir, round: plan_round, blockers: prev_blockers})
  parsed = parse_json(result)
  if parsed.status == "catastrophic":
    return handle_catastrophic(parsed.reason)
  
  read("references/plan-judgment.md")
  judgment = judge_plan(
    plan=read(state_dir + "/plan.md"),
    context=read(state_dir + "/context.md"),
    repo_profile=read(state_dir + "/repo-profile.md"),
    sub_plans_summary=parsed.sub_plans_summary
  )
  write(state_dir + f"/plan-judgment-{plan_round}.md", judgment)
  
  if judgment.verdict in ("READY", "SPLIT_NEEDED", "RECURSIVE_SPLIT"):
    state.plan.verdict = judgment.verdict
    state.plan.sub_plans = judgment.sub_plans
    break
  elif judgment.verdict == "NEEDS_REVISE":
    prev_blockers = judgment.blockers
    plan_round += 1
    continue
  elif judgment.verdict in ("BLOCKED_BY_DEPENDENCY", "NO_OP"):
    if recursion_depth == 0:
      ask_and_handle_or_exit(judgment)
    else:
      return {"status": "catastrophic", "reason": f"{judgment.verdict} at depth>0"}
  elif judgment.verdict == "CATASTROPHIC":
    return handle_catastrophic(judgment.reason)

# 2 round で READY 未達なら Open concerns に記録して進む
if plan_round > 2:
  state.plan.verdict = "ready_with_concerns"
  append_open_concerns_to_plan(judgment.blockers)

# Phase 2 末: progress comment 投稿 (depth=0 のみ、marker 投稿失敗は phase 全体を止めない)
if state.plan.status == "ready" and not state.report.issue_comments_has("plan"):
  plan_progress = build_plan_progress_comment(state)  # plan.md の Sub-plan 目次 / verdict / sub-plan 数 を 5 行以内に
  try:
    comment_url = run(f"gh issue comment {issue} --body-file <tmp>")
    state.report.issue_comments.append({"phase": "plan", "url": comment_url, "ts": now_iso()})
  except:
    pass
  save_state(state)
```

## Phase 2.5: Recursive split (verdict == RECURSIVE_SPLIT)

```python
if state.plan.verdict == "RECURSIVE_SPLIT":
  if recursion_depth >= MAX_DEPTH:
    # depth 上限到達 → chained PR で fallback
    state.plan.verdict = "SPLIT_NEEDED"
    goto Phase 2.6 dispatch
  else:
    if recursion_depth == 0:
      answer = AskUserQuestion([
        ("並列実行する", "sub-issue 化 + 並列子 orchestrator (parallel_recursive)"),
        ("chained で sub-issue 化する", "順次 + sub-issue 進捗 trace (chained_with_subissues)"),
        ("chained でメモリのみ", "順次 + sub-issue 化なし (chained_in_memory)"),
        ("中止", "skill 停止")
      ])
      if answer == "中止": exit
      elif answer == "chained で sub-issue 化する":
        state.plan.verdict = "SPLIT_NEEDED"
        state.implement.mode = "chained_with_subissues"
        goto Phase 2.6
      elif answer == "chained でメモリのみ":
        state.plan.verdict = "SPLIT_NEEDED"
        state.implement.mode = "chained_in_memory"
        goto Phase 3
    state.implement.mode = "parallel_recursive"
    create_sub_issues_and_update_parent(state, recursion_depth)
    # Phase 2.5b: 並列 Task 起動 (1 message 内多重 Task call)
    parallel_run_recursive_children(state.plan.sub_plans, recursion_depth + 1)
    goto Phase 4
```

## Phase 2.5/2.6 共通 helper: sub-issue 化 + 親 issue body update

```python
def create_sub_issues_and_update_parent(state, depth):
  for sp in state.plan.sub_plans:
    body = render_sub_issue_body(sp, parent=issue, plan_text=sp.summary_full)
    result = run(f"gh issue create --title '{sp.title}' --body-file <tmp> --label sub-task")
    sub_issue_id = parse_issue_id(result)
    sub_issue_url = parse_issue_url(result)
    sp.sub_issue_id = sub_issue_id
    sp.sub_issue_url = sub_issue_url
    sp.child_state_dir = f".claude/tmp/impl-{sub_issue_id}/"  # parallel_recursive のみ実 dir 作成、chained_with_subissues は in-memory 同 state_dir
  save_state(state)
  # 親 issue body update
  parent_body = run(f"gh issue view {issue} --json body -q '.body'")
  new_body = append_subtasks_section(parent_body, state.plan.sub_plans)
  write("/tmp/new_body.md", new_body)
  run(f"gh issue edit {issue} --body-file /tmp/new_body.md")
```

## Phase 2.6: ChainedSubIssues (verdict == SPLIT_NEEDED かつ chained_with_subissues 採用時)

`chained_in_memory` との分岐は plan-judgment の reasonable call で決まる (size 閾値は plan-agent 内の判断材料、verdict 分岐には組み込まない)。直接 Phase 3 へ進む場合 (`chained_in_memory`) は Phase 2.6 を skip。

```python
if state.plan.verdict == "SPLIT_NEEDED" and state.implement.mode == "chained_with_subissues":
  # depth=0 で 1 回 AskUserQuestion で重い副作用確認
  if recursion_depth == 0 and not state.report.issue_comments_has("sub_issues_confirmation"):
    answer = AskUserQuestion([
      ("はい、sub-issue を作る", f"{len(state.plan.sub_plans)} 個 sub-issue 化 + 親 body checklist update"),
      ("メモリのみで進める", "sub-issue 化 skip (chained_in_memory に切替、Part of #<元 issue> で trace)"),
      ("中止", "skill 停止")
    ])
    if answer == "中止": exit
    elif answer == "メモリのみで進める":
      state.implement.mode = "chained_in_memory"
      save_state(state)
      goto Phase 3
  create_sub_issues_and_update_parent(state, recursion_depth)
  # chained_with_subissues は順次なので並列 Task 起動しない、Phase 3 へ進む
  # implement-agent には family_id = parent_issue (= 親 issue.id) を渡す
```
