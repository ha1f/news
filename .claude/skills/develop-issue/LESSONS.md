# develop-issue skill: LESSONS log

Phase 5 (Retrospect) で append される **未消化 learning queue**。`applied` 状態は存在しない (mandate 反映と同時に entry 物理削除、`<skill_dir>/.lessons-trail/` の JSONL が事実 trail)。`pending` (未反映) / `proposed (issue <URL>)` (issue 投稿待ち) / `rejected (issue closed)` (dedupe signal) の 3 状態のみ保持。

次回 orchestrator は Pre-flight で **`Status: pending` の最新 20 件** を Read して context に取り込み、同じ mistake を回避する。

詳細は [references/retrospect.md](references/retrospect.md) / [docs/design-decisions.md D11](docs/design-decisions.md) 参照。

---

## L39: 2026-05-18 [known_gap]
**Summary**: Phase 6 設計で advisor が指摘した 2 件の known gap (Resume mid-Phase 6 未設計 / `MAX_PARALLEL_TEND` が recursive_split で no-op)。part 1 は L40 で部分解消、part 2 は実走 validation 待ち
**Evidence**: advisor 指摘 (commit fe1ed4b 後)
**Action**: (1) Resume gap: **part 1 は L40 (Monitor 活用) で部分解消** — `state.json.tend.watch_processes[].run_id` を Read → `gh run view <run_id>` で「すでに終了している run」を復元できるようになった。完全解消には `current_step: fixing_ci / resolving_conflict` の各 step も復元する logic 必要 (mid-fix で session 死亡時)、これは実走で頻発するか観測してから対応。(2) MAX_PARALLEL_TEND gap: `chunks(tendable_subs, MAX_PARALLEL_TEND)` は per-orchestrator なので、recursive_split で各 child が 1 sub_plan を持つ case では no-op。N children が同時 CI watch で global rate limit (5000 req/h) 到達リスク。parent-link.json で semaphore 持つか、親 orchestrator が child tend を直列化する設計検討。実走で発火するか観測してから対応
**Status**: pending

## L42: 2026-05-18 [script_bug]
**Summary**: scripts/diff_summary.sh の base 引数で local `main` を渡すと、local main が origin/main より古い場合 upstream merge commit が diff に混入。worktree 環境では local main が fetch されてない場合に常時発生
**Evidence**: 本 run では gather/plan-agent は `diff_summary.sh` を呼ばなかったが、worktree 環境 (state_dir 親 path に `.claude/worktrees/` を含む) で base ref 解決を local main にすると常時混入リスク。project memory `project_worktree_gitignored_files` で worktree 特性は既知
**Action**: scripts/diff_summary.sh に「`git rev-parse --git-common-dir != --git-dir` で worktree 環境を検知時、または base 引数がリモート追跡なしの local branch の場合、警告 + origin/<base> に自動置換 fallback」を追加。`--auto-origin` フラグで明示制御も可
**Status**: pending

## L47: 2026-05-18 [mandate_gap + meta]
**Summary**: 大規模 mandate 変更時の 3 並列 critique (R74) で 33 issues 検出。Phase 7/1.5/2.6 pseudocode が SKILL.md に section だけ追加されたまま orchestration.md pseudocode に存在しない pattern (= L15 系の頻発 bug "mandate に書いたが pseudocode 反映漏れ") を再発。Iteration 8 で全 critical fix 投入したが、3 並列 critique は agent team の "first step" として強制化すべき
**Evidence**: `/tmp/develop-issue-improvement/iteration7-{explore,mental-sim,architect}-critique.md` で全 critique NEEDS_FIX (Critical 12 + High 12 + Medium 8 + 27 fragile point + 9 invariant violation)
**Action**: SKILL.md に「scope = SKILL.md / references / agents 50+ 行変更の commit 前に 3 並列 critique を first step として強制実行」を **明文化** (現在 references/retrospect.md "skill 開発時の規律 R74" にあるが、SKILL.md 本体には書かれていない)。skill_dir 内 commit 時の pre-commit hook (新規) で commit 前に critique を要求する仕組みも検討
**Status**: pending

## L48: 2026-05-18 [success_patterns + meta]
**Summary**: 13 problem (user 5 + critic 8) を 5 group + 11 Action item に統合 → 10 iteration で段階実装 (Iteration 4.5 schema migration → 5 Group A → 6 Group B/C → 7 critique → 8 critical fix → 9 trail/Lesson → 10 final) は agent team 駆動 skill 改善の success pattern
**Evidence**: 本 session の skill self-improvement プロセス (Iteration 1-10)。9 reference / 4 agent / SKILL.md / state.json schema を 6 iteration で破壊なく拡張
**Action**: 新 reference `references/skill-improvement-process.md` を作成し、5 group 分類 / 11 Action item テンプレ / Iteration 順序の rationale を mandate 化。次回 skill 改善時 (LESSONS pending 20 件超 → improvement issue 発生時等) に再利用
**Status**: pending

## L49: 2026-05-18 [mandate_gap]
**Summary**: `Closes` / `Refs` / `Part of` の表記不整合 (SW5、Problem 6) は SKILL.md / template / pr-body-judgment / implement-agent / R69 sibling exclusion の 5 箇所同期が必要。1 箇所だけ修正すると他で破綻、I25 三点同期 (R75) の代表事例
**Evidence**: 今回の #10525 実走で PR #10554 が `Closes #10525`、残り 4 PR が `Refs #10525`、template が `Part of` で R69 grep が `Part of` のみ。merge 時 issue auto-close で残り 4 PR が orphan 化するリスクが実体化
**Action**: Iteration 8 で mode-aware PR body mandate (F-A2) を実装し、`assets/pr_body_template_default.md` を mode-aware に、`agents/implement-agent.md` Step 10.3 で mode 別 `{{related_section}}` 生成、`references/pr-body-judgment.md §2` で mode-aware blocker check に拡張。本 lesson は「I25 三点同期は keyword 数 ≥ 5 のとき特に注意」rule として `retrospect.md` "skill 開発時の規律" に追記検討
**Status**: pending

## L50: 2026-05-18 [user_correction + critical]
**Summary**: ユーザ "no clarifying questions" instruction で AskUserQuestion を skip する場合、safety net (`STOP_RECOMMENDED` / `NEEDS_INPUT` / `RECURSIVE_SPLIT` AskUserQuestion / Gemini 指摘 3 分類 AskUserQuestion 等) が一括無効化される pattern (SW3、Problem 11)。今回の #10525 実走で qa-trail.md が空生成、ユーザ確認なしで判断が走る
**Evidence**: gather-judgment-1.md / plan-judgment-1.md / Gemini 対応で AskUserQuestion を skip した event 3 件、いずれも qa-trail.md に痕跡なし
**Action**: Iteration 9 で SKILL.md に "reasonable_call bypass の trace" mandate 追加。judgment file 末尾に `## Bypass trace` section で (a) Original verdict、(b) Skip reason、(c) Hypothetical answer、(d) Risk を必須記録。pre-flight read 対象に過去 Bypass trace を追加して、同 pattern の再 bypass を warn
**Status**: pending

## L51: 2026-05-19 [user_correction]
**Summary**: LESSONS applied 化で mandate に昇格する際、**project-specific 参照 (固有 bot 名 / issue 番号 / 固有 symbol 名) を抽象化する check が漏れた**。`#10554` / `LiveEpisodeDescriptionWithToggleTableViewCell` は抽象化したが、`review_bots[]` の default に `gemini-code-assist` / `github-copilot` 等 6 固有名を hardcode、`retrospect.md` review_loop_pattern で reviewer 種別を bot 個別名で列挙、と類似 pattern が複数発生
**Evidence**: ユーザ指摘「geminiとかってどうして列挙したの？あんまり具体的な事かかないほうがいいと思ってる」 + skill audit で `repo-profile-schema.md` L171-176/L227 + `retrospect.md` L92/L94 に hardcode 残存。GitHub API `comment.user.type == "Bot"` だけで bot/human 判定可能、固有 list 不要
**Action**: applied 化 PR の前に **「mandate に固有名を残してないか」audit step** を retrospect-agent の `applied_candidates[]` 検証フローに追加。具体: (1) repo / project 名、(2) external service 名 (Gemini / Copilot / Renovate 等)、(3) issue/PR 番号、(4) 固有 symbol/class 名を grep + AskUserQuestion 確認。今回 5/19 audit + fix で `review_bots[]` default `[]` 化、`comment.user.type == "Bot"` 主判定に書き換え、retrospect.md の reviewer 種別を type レベルに抽象化
**Status**: pending
