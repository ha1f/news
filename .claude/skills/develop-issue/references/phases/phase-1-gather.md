# Phase 1 & 1.5 — Gather + Investigate

## Phase の目的・前提・後続

- **目的**: gather-agent で issue 理解と context 収集を行い、orchestrator が `gather-judgment.md` mandate に従って verdict を判定する。verdict は `READY` / `STOP_RECOMMENDED` / `NEEDS_INPUT` / `INVESTIGATION_RECOMMENDED` の 4 種
- **前提**: `state.json` 初期化済み、`recursion_depth` / `parent_issue` 引数が渡されている。`<state_dir>` が用意済み
- **後続への影響**: `state.gather.bug_type` を populate、`gather.status = "ready"` で Phase 2 へ進む。`investigation_only==True` なら Phase 1.5 dispatch → Phase 5 (Retrospect) のみ実行して終了

## Phase 1: Gather loop with judgment (pseudocode)

```python
state = read_state_or_init(issue_id, recursion_depth=arg_depth, parent_issue=arg_parent)

# Phase 1: Gather
while True:
  result = Task(gather-agent, args={issue, state_dir, skill_dir, qa_trail_path, round, parent_issue})
  parsed = parse_json(result)
  if parsed.status == "catastrophic":
    return handle_catastrophic(parsed.reason)
  # gather-agent は常に "completed" で返す (judgment しない)
  # orchestrator が judge:
  read("references/gather-judgment.md")
  judgment = judge_gather(
    context=read(state_dir + "/context.md"),
    repo_profile=read(state_dir + "/repo-profile.md"),
    qa_trail=read(state_dir + "/qa-trail.md") if exists else None,
    observations=parsed.pre_flight_observations + parsed.open_observations
  )
  write(state_dir + f"/gather-judgment-{round}.md", judgment)
  
  if judgment.verdict == "READY":
    # gather-judgment §1b で bug_type を populate
    state.gather.bug_type = judgment.bug_type or None
    save_state(state)
    break
  elif judgment.verdict == "STOP_RECOMMENDED":
    if recursion_depth == 0:
      answer = AskUserQuestion([("中止 (推奨)", "..."), ("強行", "...")])
      if answer == "中止": exit
    else:
      return {"status": "catastrophic", "reason": "stop_recommended at depth>0"}
  elif judgment.verdict == "NEEDS_INPUT":
    # Self-fillable gaps は orchestrator が自分で埋める
    for gap in judgment.self_fillable:
      orchestrator_self_fill(gap)  # Read 等を直接実行
    # 残った questions
    if recursion_depth == 0:
      answers = AskUserQuestion(judgment.questions + meta_question)
      append_to(state_dir + "/qa-trail.md", answers)
      if user chose "進む": break
    else:
      # depth>0: bubble up to parent
      return {"status": "needs_input", "needs_input": judgment.questions, "partial_state_path": state_dir + "/state.json"}
  elif judgment.verdict == "INVESTIGATION_RECOMMENDED":
    # bug 系で再現不能 / 計測必要なケース
    if recursion_depth == 0:
      answer = AskUserQuestion([
        ("investigation 用に skill 終了", "人間 / 別 skill で計測実施"),
        ("強行 (hallucination リスク許容)", "feature と同じ flow で進める"),
        ("より具体的な acceptance を提示", "NEEDS_INPUT に切り替え、再 gather"),
        ("agent に計測代行させる", "Phase 1.5 で実行 + issue comment 投稿 + skill 終了")
      ])
      if answer == "investigation 用に skill 終了": exit
      elif answer == "強行 (hallucination リスク許容)":
        state.gather.bug_type = judgment.bug_type or None
        save_state(state)
        break  # gather READY 扱いで Phase 2 へ
      elif answer == "より具体的な acceptance を提示":
        round += 1
        continue  # NEEDS_INPUT 相当で再 gather
      elif answer == "agent に計測代行させる":
        # Phase 1.5: investigation_only flag を立てる、ループ脱出して Phase 1.5 dispatch
        state.gather.bug_type = judgment.bug_type or None
        state.gather.investigation_only = True
        save_state(state)
        break
    else:
      return {"status": "catastrophic", "reason": "investigation_recommended at depth>0"}
  round += 1
```

## Phase 1.5: Investigate (gather.investigation_only==True なら発火)

`state.gather.investigation_only==True` の場合に Phase 1 直後で dispatch、investigation_posted 後は Phase 2-7 全 skip して Phase 5 (Retrospect) のみ実行。

```python
if state.gather.investigation_only:
  result = Task(implement-agent, args={
    issue, state_dir, skill_dir,
    phase: "investigate",
    bug_type: state.gather.bug_type
  })
  parsed = parse_json(result)
  if parsed.status == "investigation_posted":
    state.report.issue_comments.append({
      "phase": "investigate",
      "url": parsed.issue_comment_url,
      "ts": now_iso()
    })
    state.report.status = "ready"
    save_state(state)
    goto Phase 5  # retrospect のみ実行して skill 終了
  elif parsed.status == "catastrophic":
    return handle_catastrophic(parsed.reason)
```

## Phase 1 末: progress comment 投稿 (depth=0 のみ)

```python
if recursion_depth == 0:
  gather_progress = build_gather_progress_comment(state)  # context.md の Issue summary + bug_type を 5 行以内
  try:
    c_url = run(f"gh issue comment {issue} --body-file <tmp>")
    state.report.issue_comments.append({"phase": "gather", "url": c_url, "ts": now_iso()})
  except: pass
  save_state(state)
```
