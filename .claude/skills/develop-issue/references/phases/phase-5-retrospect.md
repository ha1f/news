# Phase 5 — Retrospect (skill の自律成長)

## Phase の目的・前提・後続

- **目的**: state_dir 全体を Read して learning を抽出、`<skill_dir>/LESSONS.md` に append + applied 物理削除 + Status 遷移を行う。skill の自律成長を実現する pipeline
- **前提**: Phase 4/6/7 完了 (depth=0 のみ)、state_dir 全ファイルが完備。depth>0 の場合は **Phase 5 を skip して親に return**
- **後続への影響**: `<skill_dir>/LESSONS.md` の更新 + `.lessons-trail/` への JSONL append。skill_dir が git 管理下なら追加で commit

## なぜ depth>0 で skip するか

並列子 (depth>0) が同時に同一 `<skill_dir>/LESSONS.md` に append/delete すると行欠落・順序破壊・seq 重複が発生する (append 操作の atomic 性が保証されない)。子の learning 抽出材料 (qa-trail / judgments) は state_dir に残るので、親 orchestrator が Phase 5 で全子の state_dir を集約して 1 回だけ append する。

```python
# enforcer (SKILL.md 冒頭で子 orchestrator が即座に skip 判定できるように)
if recursion_depth > 0:
  return final_result_for_parent_or_user()  # 子は Phase 5 skip
```

## なぜ sub-agent に委譲するか

retrospect 分析は **数千行の state_dir 全体 Read** を要するため、orchestrator が直接行うと judgment context を圧迫する。Phase 1-4 と同じ generator≠evaluator パターンで分離し、retrospect-agent は append + 候補 return のみ、削除 / Status 遷移は orchestrator が effort:max で実行 (誤判定の最後の砦)。

## Phase 5: Retrospect dispatch + verdict (pseudocode)

```python
# Phase 5: Retrospect (depth=0 only)
if recursion_depth > 0:
  return final_result_for_parent_or_user()

retrospect_result = Task(
  subagent_type="general-purpose",
  prompt=inline(read("agents/retrospect-agent.md")) + f"\nstate_dir={state_dir}\nskill_dir={skill_dir}"
)
parsed = parse_json(retrospect_result)

# Step 5.1: applied_candidates の verdict + 物理削除 (orchestrator 主体)
deleted_lessons = []
for cand in parsed.applied_candidates:
  # effort:max で各 reflected_in path を Read して semantic 確認
  for ref_path in cand.reflected_in:
    content = read(f"{skill_dir}/{ref_path}")
    # cand.summary の主旨が content に actionable に反映されているか LLM 判定
  if verdict_reflected(cand, contents):
    delete_lesson_entry(f"{skill_dir}/LESSONS.md", cand.L)  # 物理削除 (entry block 丸ごと)
    deleted_lessons.append({"L": cand.L, "summary": cand.summary, "refs": cand.reflected_in})

# Step 5.2: proposed_lesson_status の遷移 (orchestrator 主体)
for ps in parsed.proposed_lesson_status:
  if ps.state == "closed" and ps.reason == "completed":
    # issue が merge された → applied として物理削除
    delete_lesson_entry(f"{skill_dir}/LESSONS.md", ps.L)
    deleted_lessons.append({"L": ps.L, "summary": "<from L entry>", "refs": [ps.issue_url]})
  elif ps.state == "closed" and ps.reason == "not_planned":
    # issue が rejected (won't fix) → Status を rejected に書き換え (削除しない、dedupe signal)
    rewrite_status_line(f"{skill_dir}/LESSONS.md", ps.L,
                       f"rejected (issue {ps.issue_url} closed at {now_iso()})")

# Step 5.3: skill_dir 内 LESSONS.md の commit (git log が事実 trail)
if deleted_lessons:
  cd(skill_dir)
  run("git add LESSONS.md")
  body_lines = "\n".join(f"L{x.L}: {x.summary} → {','.join(x.refs)}" for x in deleted_lessons)
  msg = f"LESSONS: Delete L{','.join(x.L for x in deleted_lessons)} applied to mandate\n\n{body_lines}"
  run(f"git commit -m {shlex.quote(msg)}")  # allowed-tools で skill_dir 内のみ許可

# Step 5.4: 改善 issue 提案 (depth=0 のみ、retrospect-agent が threshold 判定済み)
# threshold は `pending` のみカウント済み (proposed/rejected 除外)
if parsed.propose_skill_improvement_issue and recursion_depth == 0:
  answer = AskUserQuestion([
    ("skill 改善 issue を作る", "pending lessons N 件を集約して skill repo に投稿"),
    ("今は作らない", "次回まで保留")
  ])
  if answer == "作る":
    skill_repo = detect_skill_repo()  # ~/.claude/skills/develop-issue の git remote
    issue_body = build_lessons_issue_body(skill_dir)  # LESSONS.md から pending を抽出
    result = run(f"gh issue create --repo {skill_repo} --title '...' --body-file <tmp>")
    issue_url = parse_issue_url(result)
    # 投稿された pending entries の Status 行を proposed に書き換え (1 行 edit)
    for L_id in proposed_lesson_ids:
      rewrite_status_line(f"{skill_dir}/LESSONS.md", L_id, f"proposed (issue {issue_url})")
    # 同 commit (skill_dir 内)
    cd(skill_dir)
    run(f"git add LESSONS.md && git commit -m 'LESSONS: Mark L<ids> proposed via {issue_url}'")

state.report.lessons_deleted = deleted_lessons
save_state(state)
return final_result_for_parent_or_user()
```

## `.lessons-trail/` 仕様

各 file は `{seq}-{action}-{ts}.json` 命名 (例: `12-applied_deleted-2026-05-18T19-00-00Z.json`)。中身は `{"L": "L12", "action": "applied_deleted", "summary": "...", "reflected_in": [...], "ts": "...", "agent_run_id": "<state_dir>"}`。次回 retrospect-agent が `.lessons-trail/` を Read して reconciliation (dedupe / 過去削除の trace 確認)。orchestrator のみが追記、`.gitignore` で skip しない (skill_dir 内 trail の本体)。

## skill mandate 自動編集の禁止

SKILL.md / agents / references / scripts の自動編集は行わない (regression 回避)。LESSONS.md への append + applied 物理削除 + Status 遷移のみ許容。mandate 改善は issue 経由。
