# Phase 7 — Review-loop (bot/human reviewer comment 反映、depth>=0 並列)

## Phase の目的・前提・後続

- **目的**: CI green + no-conflict 達成後も、bot (Gemini / Copilot / Claude review) や人間 reviewer の指摘に自律的に反応する。3 分類 (`scope_addition` / `preexisting_bug` / `off_topic`) で反映 / 別 PR 推奨 reply / off-topic reply を回す loop
- **前提**: Phase 6 完了。`pr_status in ("created", "escape_hatch_with_pr")` な PR が対象
- **後続への影響**: `state.tend.summaries[].review_loop_rounds` / `review_loop_replies[]` を更新、`MAX_REVIEW_LOOP_ROUNDS=2` 超過 / unresolved actionable で `escape_hatch_with_pr` に降格

## Phase 7 全体構造

`depth>=0` 全 instance で実行。`MAX_PARALLEL_REVIEW_LOOP=3` で同時 polling 数制限 (`MAX_PARALLEL_TEND` と独立カウント)。

各 PR の処理は 5 sub-phase:
1. **Phase 7.1**: Reviewer comment fetch (Monitor で polling)
2. **Phase 7.2**: 3 分類 ([../review-comment-judgment.md](../review-comment-judgment.md) mandate を Read)
3. **Phase 7.3**: AskUserQuestion (depth=0 のみ、`scope_addition` 採用確認) / bubble up (depth>0)
4. **Phase 7.4**: 反映実行 (`apply_and_continue` → CI 再 run、`reply_and_continue` → 次 round)
5. **Phase 7.5**: Sub-issue 双方向同期 (PR merged → checklist update、parent closed → terminate)

`MAX_TEND_ROUNDS_*` (Phase 6) と独立カウント。bot と human は同じ flow で扱うが、AskUserQuestion 必須なのは `scope_addition` 採用時のみ (bot 指摘の `preexisting_bug` / `off_topic` は確認不要、reply のみ自動実行)。

## Phase 7.1-7.4: Review polling + classify + apply (pseudocode)

```python
state.tend.review_loop_status = "in_progress"
review_loopable_subs = [sp for sp in state.plan.sub_plans
                        if sp.pr_url and sp.pr_status in ("created", "escape_hatch_with_pr")]

# Phase 7.1: 各 PR について Monitor で reviewer comment polling を起動 (background)
active_review_loops = {}  # sp.index → {bash_id, last_seen, started_at, summary}
for sp in review_loopable_subs[:MAX_PARALLEL_REVIEW_LOOP]:
  summary = next((s for s in state.tend.summaries if s.sub_plan_index == sp.index), init_summary(sp.index, None))
  if summary.review_loop_rounds >= MAX_REVIEW_LOOP_ROUNDS:
    summary.outcome = "review_loop_handoff"
    sp.pr_status = "escape_hatch_with_pr"
    sp.open_concerns.append({"kind": "reviewer_feedback_unresolved",
                              "summary": "MAX_REVIEW_LOOP_ROUNDS exceeded", "pr_url": sp.pr_url})
    continue
  poll_interval_sec = (repo_profile.ci.expected_duration_min or 14) * 30
  bash_id = Bash(f"""
    while true; do
      LAST_SEEN={summary.last_seen_comment_id or 0}
      NEW=$(gh api repos/{owner}/{repo}/pulls/{sp.pr_number}/comments --jq ".[] | select(.id > $LAST_SEEN) | .id" | head -1)
      NEW_REV=$(gh api repos/{owner}/{repo}/pulls/{sp.pr_number}/reviews --jq ".[] | select(.id > $LAST_SEEN and .body != null) | .id" | head -1)
      if [ -n "$NEW" ] || [ -n "$NEW_REV" ]; then echo "NEW_COMMENT:{sp.index}"; exit 0; fi
      sleep {poll_interval_sec}
    done
  """, run_in_background=true)
  state.tend.watch_processes.append({
    "sub_plan_index": sp.index, "current_step": "review_loop_polling",
    "started_at": now_iso(), "bash_id": bash_id
  })
  active_review_loops[sp.index] = {"bash_id": bash_id, "summary": summary, "started_at": now_iso()}
save_state(state)

# Phase 7.1 続き: Monitor で並行 stream、新 comment 検出ごとに 7.2-7.4 dispatch
review_timeout_min = (repo_profile.ci.expected_duration_min or 20) * 3
while active_review_loops:
  notification = Monitor(
    sources=[w["bash_id"] for w in active_review_loops.values()],
    until="any_process_exit_or_timeout",
    timeout_per_proc=review_timeout_min * 60
  )
  if notification.kind == "timeout":
    for sp_idx, w in active_review_loops.items():
      TaskStop(w["bash_id"])
      w["summary"].outcome = w["summary"].outcome or "no_review_received"
    break
  
  sp_index = parse_sp_from_notification(notification)  # "NEW_COMMENT:{idx}" から抽出
  sp = next(s for s in review_loopable_subs if s.index == sp_index)
  w = active_review_loops.pop(sp_index)
  summary = w["summary"]
  
  # Phase 7.2: comment 取得 + 3 分類 judgment
  comments_raw = run(f"gh api repos/{owner}/{repo}/pulls/{sp.pr_number}/comments")
  reviews_raw = run(f"gh api repos/{owner}/{repo}/pulls/{sp.pr_number}/reviews")
  unprocessed = [c for c in (comments_raw + reviews_raw)
                 if c.id > (summary.last_seen_comment_id or 0)
                 and not c.get("resolved", False) and c.get("body")]
  if not unprocessed:
    add_to_active_review_loops(sp, active_review_loops)
    continue
  
  # YOU judge: Read [../review-comment-judgment.md](../review-comment-judgment.md) mandate
  read("references/review-comment-judgment.md")
  judgment = judge_review_comments(unprocessed, repo_profile, state.implement.mode, sp)
  write(f"{state_dir}/review-judgment-{sp.index}-r{summary.review_loop_rounds + 1}.md", judgment)
  
  # Phase 7.3: AskUserQuestion (depth=0 only) or bubble up (depth>0)
  if judgment.has_actionable:
    if recursion_depth == 0:
      answers = AskUserQuestion([
        ("全て採用 (constraint 内)", f"scope_addition {len(judgment.scope_additions)} 件を採用"),
        ("scope_addition のみ採用 + 他は reply", "..."),
        ("全 reply のみ (commit なし)", "..."),
        ("skip (全部後で対応)", "review loop 終了")
      ])
      if answers == "skip":
        summary.outcome = "review_loop_user_deferred"
        summary.last_seen_comment_id = max(c.id for c in unprocessed)
        break
      judgment.user_choice = answers
    else:
      # depth>0: bubble up to parent
      return {
        "status": "needs_input",
        "needs_input": render_questions_for_parent(judgment),
        "review_judgment_path": f"{state_dir}/review-judgment-{sp.index}-r{summary.review_loop_rounds + 1}.md",
        "partial_state_path": state_dir + "/state.json"
      }
  
  # Phase 7.4: 反映実行
  if judgment.verdict == "APPLY_AND_CONTINUE":
    fix_result = Task(implement-agent, args={
      ..., phase: "apply_reviewer_feedback", sub_plan_index: sp.index,
      review_judgment_path: f"{state_dir}/review-judgment-{sp.index}-r{summary.review_loop_rounds + 1}.md",
      fix_constraints: {"max_lines": MAX_REVIEW_LOOP_FIX_LINES, "max_files": MAX_REVIEW_LOOP_FIX_FILES,
                        "allowed_kinds": ["dead_code_removal", "simple_refactor", "typo_fix", "comment_update", "test_addition"]}
    })
    parsed_fix = parse_json(fix_result)
    if parsed_fix.status == "review_fix_pushed":
      sp.head_sha = parsed_fix.new_head_sha
      summary.last_seen_comment_id = max(parsed_fix.applied_comment_ids + [c.id for c in unprocessed])
      summary.review_loop_rounds += 1
      summary.review_loop_replies.extend(parsed_fix.reply_summaries)
      restart_ci_watch_for_sp(sp)  # CI 再 trigger → Phase 6.1 polling 再開
      add_to_active_review_loops(sp, active_review_loops)  # 次 round polling
      continue
    elif parsed_fix.status == "review_fix_handoff":
      summary.outcome = "review_loop_handoff"
      sp.pr_status = "escape_hatch_with_pr"
      sp.open_concerns.append({"kind": "reviewer_feedback_unresolved", "summary": parsed_fix.reason,
                                "partial_applied_comment_ids": parsed_fix.partial_applied_comment_ids,
                                "pr_url": sp.pr_url})
      break
  elif judgment.verdict == "REPLY_AND_CONTINUE":
    reply_result = Task(implement-agent, args={
      ..., phase: "reply_to_reviewer", sub_plan_index: sp.index,
      review_judgment_path: f"{state_dir}/review-judgment-{sp.index}-r{summary.review_loop_rounds + 1}.md"
    })
    parsed_reply = parse_json(reply_result)
    summary.last_seen_comment_id = max(c.id for c in unprocessed)
    summary.review_loop_rounds += 1
    summary.review_loop_replies.extend(parsed_reply.reply_summaries)
    add_to_active_review_loops(sp, active_review_loops)
    continue
  elif judgment.verdict == "NO_ACTIONABLE":
    summary.outcome = "review_loop_no_actionable"
    summary.last_seen_comment_id = max(c.id for c in unprocessed)
    break
  else:  # ESCAPE_HATCH (MAX_REVIEW_LOOP_ROUNDS 超過等)
    summary.outcome = "review_loop_handoff"
    sp.pr_status = "escape_hatch_with_pr"
    sp.open_concerns.append({"kind": "reviewer_feedback_unresolved", "summary": "review loop escape",
                              "unresolved_comment_ids": [c.id for c in unprocessed], "pr_url": sp.pr_url})
    break
  save_state(state)
```

## Phase 7.5: Sub-issue 双方向同期 (chained_with_subissues / parallel_recursive のみ)

Phase 7 の各 round 末で実行:
- 親 issue body の `- [ ] #<sub_id>` checklist を子 PR の merge 状態に同期 (merged → `- [x]`)
- 子 sub-issue が `closed` (非 merge) になっていたら orchestrator は対応 child orchestrator を terminate (Phase 7 を子で skip)
- 親 issue が `closed` になっていたら全 child を terminate

```python
if state.implement.mode in ("chained_with_subissues", "parallel_recursive"):
  for sp in state.plan.sub_plans:
    if not sp.sub_issue_id: continue
    pr_state = run(f"gh pr view {sp.pr_url} --json state,mergedAt")
    if pr_state.state == "MERGED":
      parent_body = run(f"gh issue view {issue} --json body -q '.body'")
      new_body = update_checklist_item(parent_body, sp.sub_issue_id, checked=True)
      write("/tmp/new_body.md", new_body)
      run(f"gh issue edit {issue} --body-file /tmp/new_body.md")
    sub_issue_state = run(f"gh issue view {sp.sub_issue_id} --json state,stateReason")
    if sub_issue_state.state == "CLOSED" and pr_state.state != "MERGED":
      sp.pr_status = "child_cancelled_by_human"
      sp.open_concerns.append({"kind": "child_cancelled", "sub_issue_url": sp.sub_issue_url})
  # 親 issue closed なら全 child 終了 (depth>0 で発火)
  parent_state = run(f"gh issue view {issue} --json state")
  if parent_state.state == "CLOSED":
    state.tend.review_loop_status = "parent_closed_terminate"
    save_state(state)
    goto Phase 5

state.tend.review_loop_status = "ready"
save_state(state)
```
