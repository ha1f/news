# Phase 3 — Implement (chained sequential, or single)

## Phase の目的・前提・後続

- **目的**: 各 sub-plan について implement-agent が branch / TDD impl / verify / pre-stage / commit / codegen / diff_summary 生成を実行、orchestrator が `code-judgment.md` mandate で judge し、ready なら push + PR body draft + PR body judge + 実 PR create まで進める
- **前提**: Phase 2 完了 (`state.plan.verdict in {READY, SPLIT_NEEDED}` で `state.implement.mode in {single, chained_in_memory, chained_with_subissues}`)。`parallel_recursive` は Phase 2.5b で並列子起動、本 Phase は走らない
- **後続への影響**: 各 sub-plan に `pr_url` / `pr_status` / `verify_summary` / `open_concerns` / `scope_extension_proposals` を populate。`state.implement.current_sub_plan` を更新。implement-agent は Step 4.5 で `<state_dir>/implementation-notes-<index>.md` (free text、判断 trail) を running append し、return JSON で `implementation_notes_path` を渡す (PR body の「代替案」「誤解されそうな観点」placeholder source として Step 10.3 で消費される)

## Phase 3: Implement loop (pseudocode)

```python
for sp in state.plan.sub_plans[state.implement.current_sub_plan:]:
  state.implement.current_phase = "implement"
  impl_round = 1

  # family_id は mode 別 (兄弟 PR 識別用)
  if state.implement.mode == "chained_with_subissues":
    family_id = sp.sub_issue_id  # 各 sub-plan の sub-issue が family_id
  elif state.implement.mode == "parallel_recursive":
    family_id = parent_issue  # 親 (= 元 issue) が family_id
  else:  # single / chained_in_memory
    family_id = issue.id  # 元 issue

  # 初回 implement
  result = Task(implement-agent, args={
    issue, state_dir, sub_plan_index: sp.index, skill_dir,
    phase: "implement", parent_issue, family_id
  })
  parsed = parse_json(result)
  
  # chained_* mode の cascade skip 共通判定
  is_chained_mode = state.implement.mode in ("chained_in_memory", "chained_with_subissues")
  
  while True:
    if parsed.status == "catastrophic":
      handle_per_phase_catastrophic(sp, parsed)
      # chained_* mode で upstream catastrophic 時は downstream の base branch が
      # 存在しないため壊れる。dependents を識別して skip 連鎖。
      if is_chained_mode:
        dependents = [d for d in state.plan.sub_plans
                      if d.index > sp.index and chain_traverse_to(sp, d)]
        for d in dependents:
          d.pr_status = "skipped_due_to_upstream"
          d.open_concerns = [{"kind": "upstream_catastrophic",
                              "summary": f"upstream sub-plan-{sp.index} failed"}]
          append_to(state_dir + "/pr-urls.md", f"(skipped_due_to_upstream) sub-plan-{d.index}")
        state.implement.current_sub_plan = len(state.plan.sub_plans)
      break
    if parsed.status == "blocked_no_pr":
      sp.pr_status = "blocked_no_pr"
      sp.open_concerns = parsed.open_concerns
      sp.verify_summary = aggregate_verify(parsed.open_concerns)
      sp.code_review_rounds = impl_round
      append_to(state_dir + "/pr-urls.md", f"(blocked_no_pr) {parsed.open_concerns}")
      if is_chained_mode:
        dependents = [d for d in state.plan.sub_plans
                      if d.index > sp.index and chain_traverse_to(sp, d)]
        for d in dependents:
          d.pr_status = "skipped_due_to_upstream"
          d.open_concerns = [{"kind": "upstream_blocked_no_pr",
                              "summary": f"upstream sub-plan-{sp.index} blocked"}]
          append_to(state_dir + "/pr-urls.md", f"(skipped_due_to_upstream) sub-plan-{d.index}")
        state.implement.current_sub_plan = len(state.plan.sub_plans)
      break
    if parsed.status != "ready_for_review":
      break  # 不明 status
    
    # code judgment
    read("references/code-judgment.md")
    diff_summary = read(parsed.diff_summary_path)
    judgment = judge_code(
      diff_summary=diff_summary,
      plan=read(state_dir + f"/sub-plan-{sp.index}.md"),
      context=read(state_dir + "/context.md"),
      repo_profile=read(state_dir + "/repo-profile.md")
    )
    write(state_dir + f"/code-judgment-{sp.index}-{impl_round}.md", judgment)
    
    if judgment.verdict == "READY":
      # Step 1: push + PR body draft 書き出し (実 PR create はまだしない)
      result = Task(implement-agent, args={..., phase: "push_and_pr"})
      parsed_pr_draft = parse_json(result)
      if parsed_pr_draft.status == "skipped_dedupe":
        sp.pr_status = "skipped_dedupe"
        sp.existing_pr_url = parsed_pr_draft.existing_pr_url
        append_to(state_dir + "/pr-urls.md", f"(skipped_dedupe) {sp.existing_pr_url}")
        break
      assert parsed_pr_draft.status == "ready_for_body_review"
      # Step 2: PR body judge (pr-body-judgment.md mandate)
      pr_body_round = 1
      while True:
        read("references/pr-body-judgment.md")
        pr_body_judgment = judge_pr_body(
          pr_body=read(parsed_pr_draft.pr_body_path),
          plan=read(state_dir + f"/sub-plan-{sp.index}.md"),
          state=read(state_dir + "/state.json"),
          qa_trail=read(state_dir + "/qa-trail.md")
        )
        write(state_dir + f"/pr-body-judgment-{sp.index}-{pr_body_round}.md", pr_body_judgment)
        if pr_body_judgment.verdict == "READY":
          break  # 次の Step 3 へ
        if pr_body_round >= 2:
          # escape-hatch: PR body 品質懸念付きで create
          sp.open_concerns += [{"kind": "pr_body_quality_concern",
                                "summary": pr_body_judgment.blockers}]
          break
        # NEEDS_FIX: implement-agent に pr_body だけ修正させる
        result = Task(implement-agent, args={
          ..., phase: "fix_pr_body", pr_body_blockers: pr_body_judgment.blockers
        })
        parsed_pr_draft = parse_json(result)
        pr_body_round += 1
      # Step 3: 実 PR create
      result = Task(implement-agent, args={..., phase: "create_pr"})
      parsed_pr = parse_json(result)
      sp.pr_status = parsed_pr.status  # "created" or "stuck"
      sp.pr_url = parsed_pr.pr_url
      sp.pr_body_rounds = pr_body_round
      sp.verify_summary = aggregate_verify(parsed.open_concerns)
      sp.code_review_rounds = impl_round
      # Step 3b: scope_extension_proposals[] を受け取って persist
      if parsed.scope_extension_proposals:
        sp.scope_extension_proposals = parsed.scope_extension_proposals
        # depth=0 で AskUserQuestion で取り込み確認
        if recursion_depth == 0 and len(parsed.scope_extension_proposals) > 0:
          answers = AskUserQuestion([
            ("採用 (別 PR で対応)", f"{len(parsed.scope_extension_proposals)} 件の scope 拡張提案を別 PR / 別 issue に積む"),
            ("却下", "本 issue scope 外として扱う"),
            ("後で判断", "次回 develop-issue 実行時に retake")
          ])
          # 採用なら gh issue create で新 issue 化 (本 PR の "follow-up" として trace)
          if answers == "採用 (別 PR で対応)":
            new_issue = run(f"gh issue create --title 'follow-up: {sp.title}' --body-file <scope_extension_proposals.md>")
            sp.followup_issue_url = parse_issue_url(new_issue)
      append_to(state_dir + "/pr-urls.md", parsed_pr.pr_url)
      # Step 3c: progress comment 投稿 (marker のみ)
      progress_comment = build_implement_progress_comment(sp)  # PR URL + verify status + 5 行以内
      try:
        c_url = run(f"gh issue comment {issue} --body-file <tmp>")
        state.report.issue_comments.append({"phase": f"implement_sub_{sp.index}", "url": c_url, "ts": now_iso()})
      except: pass
      break
    elif judgment.verdict == "NEEDS_FIX":
      if impl_round >= 3:
        # escape-hatch: PR は作る
        result = Task(implement-agent, args={..., phase: "push_and_pr"})
        parsed_pr = parse_json(result)
        sp.pr_status = "escape_hatch_with_pr"
        sp.pr_url = parsed_pr.pr_url
        sp.open_concerns = judgment.blockers
        sp.verify_summary = aggregate_verify(parsed.open_concerns)
        sp.code_review_rounds = impl_round
        append_to(state_dir + "/pr-urls.md", f"(stuck: code_review_blocker) {parsed_pr.pr_url}")
        break
      # fix
      result = Task(implement-agent, args={
        ..., phase: "fix_blockers", blockers: judgment.blockers, round: impl_round + 1
      })
      parsed = parse_json(result)
      impl_round += 1
      continue
    elif judgment.verdict == "SPLIT_NEEDED":
      # diff 大規模、stuck で PR は作る
      result = Task(implement-agent, args={..., phase: "push_and_pr"})
      parsed_pr = parse_json(result)
      sp.pr_status = "escape_hatch_with_pr"
      sp.pr_url = parsed_pr.pr_url
      sp.open_concerns = [{"kind": "diff_too_large", "summary": "split recommended"}]
      sp.verify_summary = aggregate_verify(parsed.open_concerns)
      sp.code_review_rounds = impl_round
      append_to(state_dir + "/pr-urls.md", f"(stuck: diff_too_large) {parsed_pr.pr_url}")
      break
  
  save_state(state)
  state.implement.current_sub_plan = sp.index + 1
```
