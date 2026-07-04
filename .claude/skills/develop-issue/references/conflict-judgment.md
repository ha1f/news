# Conflict judgment mandate (Phase 6.3)

<context>
orchestrator が Phase 6.3 (PR が `CONFLICTING` 検出時) に Read して判定する mandate。`gh pr update-branch` vs `git rebase` vs handoff の選択を行う。
</context>

## Table of Contents

- [入力ファイル](#入力ファイル)
- [出力ファイル](#出力ファイル)
- [安全な方法から試す](#大原則-安全な方法から試す)
- [Strategy 1: gh pr update-branch](#strategy-1-gh-pr-update-branch)
- [Strategy 2: git rebase](#strategy-2-git-rebase--force-with-lease)
- [Strategy 3: HANDOFF](#strategy-3-handoff)
- [round counter](#round-counter)
- [並列実行時の連鎖 rebase](#並列実行時の連鎖-rebase)
- [アンチパターン](#アンチパターン)

## 入力ファイル

- `gh pr view <pr_url> --json mergeable,mergeStateStatus,baseRefName,headRefName` 結果 (orchestrator が直接実行)
- `state.json.created_branches[]` (force-with-lease 適用条件 check 用)
- `gh api repos/<owner>/<repo>/branches/<branch>/protection` (branch protection 事前 check)
- 該当 `sub-plan-<N>.md` (Approach / Changes、conflict 範囲推定用)

## 出力ファイル

`<state_dir>/conflict-judgment-<sub_plan_index>-r<round>.md`:

```markdown
# Conflict judgment (sub_plan_index=N, round=R)

## State
- pr_url: <url>
- mergeable: CONFLICTING / UNKNOWN
- baseRef: main, headRef: claude/...
- base_diverged_commits: <count>

## Strategy
- approach: gh_pr_update_branch | git_rebase | handoff
- safety_check:
  - branch_in_created_branches[]: true | false
  - target_is_default_branch: true | false
  - branch_protection_allows_force: true | false | unknown
- reasoning: <1-2 行>

## Verdict
- verdict: AUTO_RESOLVE_VIA_UPDATE | AUTO_RESOLVE_VIA_REBASE | HANDOFF
- escape_reason (verdict=HANDOFF 時): <1 行>
```

## 大原則: 安全な方法から試す

<constraints>
- 順序遵守: gh pr update-branch → git rebase → handoff の優先順位を守る (force push の影響範囲を最小化)
- 2 条件 AND (自己作成 branch + non-default branch) を満たさない場合は即 HANDOFF
- Strategy file のため Blocker/Suggestion/Nits 3 階層は使わない。verdict は AUTO_RESOLVE_VIA_UPDATE / AUTO_RESOLVE_VIA_REBASE / HANDOFF の 3 値
- 詳細は `references/judgment-conventions.md` 参照
</constraints>

順序:
1. **`gh pr update-branch`** (GitHub の "Update branch" 機能、merge commit を作るが force push 不要、最も safe)
2. 失敗時 (textual conflict 発生 = update-branch でも解消不能) → **`git rebase origin/main` + `git push --force-with-lease`** (2 条件 AND 満たす場合のみ)
3. 上記いずれも不能 → `HANDOFF`

## Strategy 1: `gh pr update-branch`

GitHub remote で upstream の最新を branch に merge する。force push 不要、safe。

実行: `gh pr update-branch <pr_url>`

成功条件: exit 0、`gh pr view --json mergeable` が `MERGEABLE` に遷移
失敗条件: exit 非0、または `mergeable` が `CONFLICTING` のまま (textual conflict があり GitHub が自動解消不能)

→ 失敗時は Strategy 2 へ

## Strategy 2: `git rebase` + `--force-with-lease`

ローカルで rebase して force-with-lease で push。**hard rule の `--force` 禁止例外** として、以下 **2 条件 AND + protection check** を全て満たす場合のみ許容:

| 条件 | 判定方法 | 失敗時 |
|---|---|---|
| 1. 自己作成 branch | `state.json.created_branches[]` 含む | HANDOFF |
| 2. target ≠ default branch | `repo-profile.repo.default_branch` 比較 | HANDOFF |
| 3. branch protection allow_force_pushes | `gh api repos/.../protection` で true | HANDOFF |

**branch 名 pattern は判定に使わない**: 旧設計で `claude/*` を 3 条件目にしていたが、(a) D4 (repo-agnostic) と矛盾 — `repo-profile.conventions.branch_naming.pattern` が branch 命名規約の真の所在、(b) `created_branches[]` で「自己作成」は十分証明される。

実行 (2 条件 + protection OK 時):
```bash
git fetch origin
git rebase origin/main
# conflict が発生したら git rebase --abort して HANDOFF
git push --force-with-lease origin <branch>
```

成功条件: rebase 完了 (`git status` clean)、force-with-lease push exit 0
失敗条件:
- rebase 中の textual conflict (`<<<<<<< HEAD` markers 出現) → `git rebase --abort` で復旧 + `HANDOFF` (orchestrator が automerge を試みない、human review 必須)
- force-with-lease reject (remote が想定 commit と異なる = reviewer が直接 commit した可能性) → `HANDOFF` (retry 禁止、reviewer commit を上書きしない)
- branch protection reject → `HANDOFF`

## Strategy 3: `HANDOFF`

以下のいずれかで `verdict: HANDOFF`:
- Strategy 1 / 2 が両方失敗
- 2 条件 AND を満たさない (created_branches 外 / default branch 等)
- branch protection が force push 禁止
- reviewer commit を検知 (`--force-with-lease` reject)
- rebase で textual conflict 発生

`open_concerns` に以下を記録:
```json
{
  "kind": "<one of: conflict_unresolvable, pr_branch_modified_by_human, force_push_blocked>",
  "pr_url": "...",
  "base_diverged_commits": N,
  "attempted_strategies": ["gh_pr_update_branch", "git_rebase"],
  "last_error": "..."
}
```

## round counter

`MAX_TEND_ROUNDS_CONFLICT=2`。conflict round は CI fix round と独立カウント (upstream churn 起因の外因なので分離する)。2 round 超過で `HANDOFF`。

3 つの round counter (各々独立):

| counter | state field | 上限 |
|---|---|---|
| CI fix | `state.tend.summaries[].rounds_ci_fix` | `MAX_TEND_ROUNDS_CI_FIX` |
| Flaky retry | `state.tend.summaries[].rounds_flaky_retry` | `MAX_TEND_ROUNDS_FLAKY_RETRY=2` |
| Conflict | `state.tend.summaries[].rounds_conflict` | `MAX_TEND_ROUNDS_CONFLICT=2` |

## 並列実行時の連鎖 rebase

複数 sub-issue PR が並列に同 main を追う環境では、1 つの PR が merge されると他 PR は conflict 発生。各 instance が自分の Phase 6.3 で rebase する。round 上限 2 を超えたら handoff (catastrophic cascade を切る)。

## アンチパターン

- `git push --force` (lease なし) を使う → 禁止。reviewer の push を盲目的上書き
- 2 条件 AND を skip して force push → 禁止。allowlist 外 branch / default branch を絶対 force しない
- `--force-with-lease` reject を retry する → 禁止。reviewer commit を即 handoff
- rebase 中の textual conflict を自動解消する (orchestrator が `git checkout --ours` / `--theirs` を使う) → 禁止。semantic 判断は human review
- `git pull` (rebase でなく merge) → branch history が汚れる、PR diff が読みにくくなる。常に `git rebase` か `gh pr update-branch`
