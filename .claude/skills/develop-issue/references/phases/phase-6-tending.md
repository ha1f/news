# Phase 6 — Tending (CI green + no-conflict 自律維持、depth>=0 並列)

## Phase の目的・前提・後続

- **目的**: 作成済み PR の CI が green かつ no-conflict になるまで、orchestrator が自律的に維持する。remote container (build 環境なし) で並列実行が前提、CI が verify の唯一手段
- **前提**: Phase 4 完了。`state.plan.sub_plans[]` の `pr_status in ("created", "escape_hatch_with_pr")` な entry が tend 対象
- **後続への影響**: `state.tend.summaries[]` に per-sub-plan outcome を populate。`pr_status` が `created` / `escape_hatch_with_pr` のまま Phase 7 (Review-loop) へ

## Phase 6 全体構造

`depth>=0` 全 instance で実行 (Phase 5 と違い子も持つ、独立 state.json で round カウント)。

`MAX_PARALLEL_TEND=3` で同時 watch 数制限 (GitHub API rate limit 1h 5000 req 対策、超過は queue)。

各 PR の処理は 3 step:
1. **Phase 6.1**: CI watch (Monitor で multi-PR 並行 stream)
2. **Phase 6.2**: CI fail → 自動修正 ([../ci-judgment.md](../ci-judgment.md) mandate、`MAX_TEND_ROUNDS_CI_FIX` 上限)
3. **Phase 6.3**: Conflict 解消 ([../conflict-judgment.md](../conflict-judgment.md) mandate、`MAX_TEND_ROUNDS_CONFLICT` 上限)

`tend_summary{rounds_ci, rounds_conflict, rounds_flaky, classifier_used, outcome, run_urls}` を子の return JSON に含める。親が `<state_dir>/tend-summaries/` に集約 → Phase 5 retrospect-agent が読む。

親 issue の `### Sub-tasks` checklist は Phase 7 (Review-loop) の各 round で同期 (`gh issue edit`)。Phase 5 では rewrite しない。

## Phase 6.1: CI watch + Resume 復元 (pseudocode)

```python
# Phase 6: Tending (depth>=0 全 instance で実行、CI green + no-conflict 自律維持)
state.tend = {"status": "in_progress", "summaries": [], "watch_processes": []}
tendable_subs = [sp for sp in state.plan.sub_plans
                 if sp.pr_url and sp.pr_status in ("created", "escape_hatch_with_pr")]
timeout_min = (repo_profile.ci.expected_duration_min or 20) * 1.5

# Phase 6.1: 全 PR の CI watch を background で並行起動 (Monitor で stream)
# foreground 同期 block すると N × 30min = 大量の wall clock 消費するが、
# background + Monitor なら N PR を同時 watch → 全体 ~30min に圧縮できる
active_watches = {}  # sp.index → {bash_id, run_id, started_at, summary}
for sp in tendable_subs[:MAX_PARALLEL_TEND]:
  # push commit sha 紐付け run を取得 (CI trigger 不安定対策、60s polling × max 5)
  run_id = None
  for attempt in range(CI_RUN_POLLING_MAX_ATTEMPTS):
    # Resume gap mitigation: state.json.tend.watch_processes[] に run_id があれば再利用
    existing = next((w for w in state.tend.watch_processes if w.sub_plan_index == sp.index), None)
    if existing and existing.run_id:
      run_id = existing.run_id
      break
    runs = run(f"gh run list --branch {sp.branch} --limit 1 --json databaseId,createdAt,headSha")
    if runs and runs[0].headSha == sp.head_sha:
      run_id = runs[0].databaseId
      break
    sleep(CI_RUN_POLLING_INTERVAL_SEC)
  if not run_id:
    sp.pr_status = "escape_hatch_with_pr"
    sp.open_concerns.append({"kind": "ci_unknown", "summary": "CI run not detected"})
    state.tend.summaries.append({"sub_plan_index": sp.index, "outcome": "ci_unknown",
                                  "rounds_ci_fix": 0, "rounds_conflict": 0, "rounds_flaky_retry": 0})
    continue
  
  # Resume 復元: すでに完了している run なら Monitor 起動せず直接結果取得
  pre_state = run(f"gh run view {run_id} --json status,conclusion")
  if pre_state.status == "completed":
    summary = init_summary(sp.index, run_id)
    if pre_state.conclusion == "success":
      handle_ci_green_then_check_conflict(sp, summary)  # Phase 6.3 へ
    else:
      handle_ci_fail(sp, summary, run_id)  # Phase 6.2 へ (内部で再 watch 必要なら再起動)
    state.tend.summaries.append(summary)
    continue
  
  # まだ in_progress: background watch を起動 + state.json に記録 (Resume 対策)
  bash_id = Bash(f"gh run watch {run_id} --exit-status", run_in_background=true)
  state.tend.watch_processes.append({
    "sub_plan_index": sp.index, "run_id": run_id,
    "current_step": "watching", "started_at": now_iso(), "bash_id": bash_id
  })
  active_watches[sp.index] = {
    "bash_id": bash_id, "run_id": run_id, "started_at": now_iso(),
    "summary": init_summary(sp.index, run_id)
  }
save_state(state)

# Phase 6.1 続き: Monitor で全 background watch を並行 stream
# 各 watch の exit (CI 完了) 通知を受けて該当 sp の Phase 6.2/6.3 へ dispatch
while active_watches:
  notification = Monitor(
    sources=[w["bash_id"] for w in active_watches.values()],
    until="any_process_exit_or_timeout",
    timeout_per_proc=timeout_min * 60
  )
  sp_index = find_sp_by_bash_id(active_watches, notification.bash_id)
  sp = next(s for s in tendable_subs if s.index == sp_index)
  watch = active_watches.pop(sp_index)
  summary = watch["summary"]
  
  if notification.kind == "timeout":
    TaskStop(watch["bash_id"])  # background process を kill
    summary.outcome = "ci_unknown"
    sp.pr_status = "escape_hatch_with_pr"
    sp.open_concerns.append({"kind": "ci_unknown", "summary": f"CI watch timeout ({timeout_min}min)",
                              "run_url": f"https://github.com/.../runs/{watch['run_id']}"})
    state.tend.summaries.append(summary)
    save_state(state)
    continue
  
  ci_conclusion = "success" if notification.exit_code == 0 else "failure"
  # CI fail → Phase 6.2 ループ、CI green → Phase 6.3 conflict check (下記、flat な 2 ブロックで実行)
  tend_done = False
  while not tend_done:
    if ci_conclusion == "failure":
      # === Phase 6.2: CI fail 自動修正ループ ===
      if summary.rounds_ci_fix >= MAX_TEND_ROUNDS_CI_FIX:
        summary.outcome = "ci_handoff"
        sp.pr_status = "escape_hatch_with_pr"
        sp.open_concerns.append({"kind": "ci_persistent_failure", "run_url": summary.final_run_url,
                                  "classifier_hits": summary.classifier_hits,
                                  "attempted_fixes": [...]})
        break
      run(f"gh run download {watch['run_id']} -D {state_dir}/ci-runs/r{summary.rounds_ci_fix}/")
      # YOU judge: Read [../ci-judgment.md](../ci-judgment.md) mandate + repo-profile.ci.fail_classifiers + log
      ci_judgment = judge_ci_fail(state_dir, sp.index, summary.rounds_ci_fix,
                                   repo_profile.ci.fail_classifiers,
                                   prev_log=state_dir + f"/ci-runs/r{summary.rounds_ci_fix-1}/" if summary.rounds_ci_fix > 0 else None)
      write(f"{state_dir}/ci-judgment-{sp.index}-r{summary.rounds_ci_fix}.md", ci_judgment.md)
      summary.classifier_hits.extend(ci_judgment.classifier_hits)
      if ci_judgment.verdict == "FLAKY_RETRY":
        if summary.rounds_flaky_retry >= MAX_TEND_ROUNDS_FLAKY_RETRY:
          summary.outcome = "ci_handoff"
          sp.pr_status = "escape_hatch_with_pr"
          sp.open_concerns.append({"kind": "ci_flaky_suspected", "run_url": summary.final_run_url})
          break
        summary.rounds_flaky_retry += 1
        ci_conclusion = await_next_ci_run(sp)  # push 無し、CI rerun (consume_round=false)
        continue
      elif ci_judgment.verdict == "AUTO_FIX":
        fix_result = Task(implement-agent, args={
          ..., phase: "fix_ci_failure", sub_plan_index: sp.index,
          ci_judgment_path: f"{state_dir}/ci-judgment-{sp.index}-r{summary.rounds_ci_fix}.md",
          fix_constraints: ci_judgment.fix_constraints
        })
        parsed_fix = parse_json(fix_result)
        if parsed_fix.status == "ci_handoff":  # implement-agent が constraint 超過 detect
          summary.outcome = "ci_handoff"
          sp.pr_status = "escape_hatch_with_pr"
          sp.open_concerns.append({"kind": "ci_persistent_failure", "run_url": summary.final_run_url,
                                    "summary": "fix exceeded constraints (>5 lines or >1 file)"})
          break
        sp.head_sha = parsed_fix.new_head_sha
        summary.rounds_ci_fix += 1
        ci_conclusion = await_next_ci_run(sp)  # CI 再 run 待ち
        continue
      else:  # HANDOFF / TIMEOUT_UNKNOWN
        summary.outcome = "ci_handoff"
        sp.pr_status = "escape_hatch_with_pr"
        sp.open_concerns.append({"kind": ci_judgment.handoff_kind, "run_url": summary.final_run_url,
                                  "classifier_hits": summary.classifier_hits,
                                  "last_log_excerpt": ci_judgment.evidence})
        break
    else:  # ci_conclusion == "success"
      # === Phase 6.3: Conflict check + 解消ループ ===
      pr_state = run(f"gh pr view {sp.pr_url} --json mergeable,mergeStateStatus,baseRefName,headRefName")
      if pr_state.mergeable != "CONFLICTING":
        summary.outcome = "ci_green"
        tend_done = True
        break
      if summary.rounds_conflict >= MAX_TEND_ROUNDS_CONFLICT:
        summary.outcome = "conflict_handoff"
        sp.pr_status = "escape_hatch_with_pr"
        sp.open_concerns.append({"kind": "conflict_unresolvable", "pr_url": sp.pr_url,
                                  "attempted_strategies": ["gh_pr_update_branch", "git_rebase"]})
        break
      # YOU judge: Read [../conflict-judgment.md](../conflict-judgment.md) + created_branches + branch protection
      # 2 条件 AND (branch 名 pattern は判定に使わない、created_branches で自己作成は十分証明)
      protection = run(f"gh api repos/{owner}/{repo}/branches/{sp.branch}/protection") or {}
      can_force = (sp.branch in state.created_branches and
                   sp.branch != repo_profile.repo.default_branch and
                   protection.get("allow_force_pushes", {}).get("enabled", True))
      conflict_judgment = judge_conflict(sp, can_force)
      write(f"{state_dir}/conflict-judgment-{sp.index}-r{summary.rounds_conflict}.md", conflict_judgment.md)
      if conflict_judgment.verdict == "AUTO_RESOLVE_VIA_UPDATE":
        try:
          run(f"gh pr update-branch {sp.pr_url}")  # orchestrator 直接実行 (safe な GitHub API)
          summary.rounds_conflict += 1
          ci_conclusion = await_next_ci_run(sp)  # rebase が新 commit 生成、CI 再 run
          continue
        except subprocess.CalledProcessError:
          conflict_judgment.verdict = "AUTO_RESOLVE_VIA_REBASE"  # fallback
      if conflict_judgment.verdict == "AUTO_RESOLVE_VIA_REBASE":
        rebase_result = Task(implement-agent, args={
          ..., phase: "resolve_conflict", sub_plan_index: sp.index,
          conflict_judgment_path: f"{state_dir}/conflict-judgment-{sp.index}-r{summary.rounds_conflict}.md"
        })
        parsed_rebase = parse_json(rebase_result)
        if parsed_rebase.status == "conflict_resolved":
          sp.head_sha = parsed_rebase.new_head_sha
          summary.rounds_conflict += 1
          ci_conclusion = await_next_ci_run(sp)  # CI 再 run
          continue
        else:  # conflict_handoff (textual conflict、force-with-lease reject 等)
          summary.outcome = "conflict_handoff"
          sp.pr_status = "escape_hatch_with_pr"
          sp.open_concerns.append({"kind": parsed_rebase.handoff_kind, "pr_url": sp.pr_url})
          break
      else:  # HANDOFF (2 条件 AND 不成立、branch protection block 等)
        summary.outcome = "conflict_handoff"
        sp.pr_status = "escape_hatch_with_pr"
        sp.open_concerns.append({"kind": "force_push_blocked", "pr_url": sp.pr_url,
                                  "reason": conflict_judgment.escape_reason})
        break
  state.tend.summaries.append(summary)
  # 残りの tendable_subs から queue に入れる
  if len(tendable_subs) > MAX_PARALLEL_TEND and (next_sp := pop_next_queued(tendable_subs, active_watches)):
    add_to_active_watches(next_sp, active_watches, state.tend.watch_processes)
  save_state(state)

state.tend.status = "ready"
save_state(state)
```

## 補足: `await_next_ci_run(sp)` の意味

CI fix push 後 / rebase push 後の新 CI run を取得 → in_progress なら新 background watch を起動 → exit code から `ci_conclusion` を返す。Resume 復元と同じ pattern で `pre_state = gh run view --json status,conclusion` を先に試す。
