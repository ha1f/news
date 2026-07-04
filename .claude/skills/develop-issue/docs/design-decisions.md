# Design Decisions

load-bearing な設計判断と「変えると何が壊れるか」。各エントリは `決定 → 根拠 → 変えると壊れること` の 3 部構成。

姉妹 docs: [overview.md](./overview.md) / [phases.md](./phases.md) / [sources.md](./sources.md)

---

## D1. 判断は orchestrator 集中、heavy work は context 分離

**決定**: orchestrator (`effort: max`) が全 judgment を担当。phase agent は探索 / draft / 実行 / 要約 return のみで判定しない。判定観点は `references/{role}-judgment.md` mandate に分離して orchestrator が Read。

**根拠**:
- 判定の一貫性 (1 つの brain で全 decisions、cross-phase の整合)
- generator≠evaluator は維持される (実装 reasoning は implement-agent 内で消費、orchestrator は diff_summary だけ見る)
- context 分離は heavy task の探索・実行・diff の生 token 消費を agent に閉じ込めるため依然有効

**変えると壊れること**: phase agent が自己判定すると (1) judgment の cross-phase 一貫性が失われる、(2) generator が自分の出力を OK と言う bias、(3) judgment mandate が複数 agent に散らばり drift する。

---

## D2. `depends_on: null` 1 行で分解モードを discriminate

**決定**: plan-agent が出した sub-plan 群の `depends_on` field だけで分解モードを決める。全部 null なら `recursive_split` (並列 sub-issue)、1 つでも依存があれば `split_needed` (chained PR)、sub-plan 1 つなら `ready` (single PR)。

**根拠**:
- 明確で機械的な判定基準 (人間の subjective 判断を排除)
- 「sub-issue はそれぞれ独立であるべき。独立でないなら issue を分ける意味が薄い」原則と整合
- 独立性が確認できた時だけ sub-issue 化 (`gh issue create` × N、親 body 更新、並列 Task 起動) のオーバーヘッドを払う

**変えると壊れること**: より複雑な discriminator にすると plan-judgment が肥大化し、agent ごとに解釈が分かれる。並列で互いに干渉する sub-issue が作られ git conflict / 自己 dedupe 誤判定が頻発。

**補強**: recursive_split 候補時に複数 sub-plan が同一 file path を `changes` に list すると並列 push で merge conflict / file race。plan-judgment §3 で集合演算して blocker (sub-plan 統合 or chained に変更)。

---

## D3. Q&A は depth=0 のみ、並列子は親に bubble up

**決定**: `AskUserQuestion` は depth=0 (top-level orchestrator) のみ。並列子 (depth>0) は `status: needs_input` を return、親が集約して 1 回の AskUserQuestion で提示。

**根拠**:
- 並列子が同時に user に質問すると UX が破綻 (4 個の child から 4 個の question を user が context なく答える)
- Task で起動された agent は AskUserQuestion を呼べないという runtime 制約と整合
- 親 plan-judgment が sub-issue 化前に「実装可能な明確な単位」に分解する責務を強化 (子の `needs_input` 連発 = 親 plan の責務不全 signal)

**変えると壊れること**: 並列子が独立に user 質問すると、(1) user が複数 context を同時に追えず誤答、(2) 答えの配布順序で実行差異、(3) plan-judgment の「分解時に明確化」責務が形骸化。

---

## D4. リポジトリ非依存化: `repo-profile` で動的抽出

**決定**: skill 内に特定 repo の規約・ツール・コマンドをハードコードしない。gather-agent が対象 repo を scan して `repo-profile.{md,json}` に集約 (`commands` / `conventions` / `ci.covered_actions` / `codebase_map` / `noise_paths` / `directory_specific_conventions` / `tooling.lsp_available` / `commands.codegen[].owned_by_pattern`)。後続 phase はこれを source of truth として参照。

**根拠**:
- 任意の git リポジトリで動く汎用 skill が目的
- `CLAUDE.md` / `package.json` / `Makefile` / `.github/workflows` / `.gitignore` / 階層 CLAUDE.md / `tsconfig.json` 等から動的に読める
- repo 特性 (large mono-repo / 単一言語 / monorepo の subdir 規約) を判定に反映できる

**変えると壊れること**: ハードコードすると (1) 別 repo で動かない、(2) 同 repo でも規約変更追従が手動、(3) plan / code judgment が前提を持てない (`directory_specific_conventions` が無いと subdir 局所規約が無視され reviewer 信頼を失う)。

---

## D5. 完璧主義より human handoff: escape_hatch_with_pr / blocked_no_pr の分離

**決定**: 詰まった時の振る舞いを 2 つに分離。
- **`escape_hatch_with_pr`**: 実装は完了したが code review 3 round で blocker 残 → DRAFT PR は作り、`open_concerns` に懸念を記載、人間 review に渡す
- **`blocked_no_pr`**: そもそも PR を作るべきでない (secret detected / 5 round verify failure / catastrophic / human_owned 違反)

**根拠**:
- 「途中で詰まっても可能な限り DRAFT PR は作って人間 review に渡す」が `escape_hatch_with_pr` の意図 (実装が永遠に通らないケースの handoff)
- 旧 `stuck` 1 語で両意味を兼ねると集計 / Phase 4 report / retrospect で bug 生成 risk
- 完璧 PR を目指して無限 loop よりも「不完全だが明示された懸念付き DRAFT PR」のほうが reviewer に有用

**変えると壊れること**: 区別を消すと (1) safety違反 (secret) を `open_concerns` 付きで commit/push する誤動作の可能性、(2) reviewer が PR を見るべきか blocked を解消すべきかわからない、(3) retrospect で frequent stuck pattern の分類ができない。

**補強**: chained mode で upstream が `blocked_no_pr` / `catastrophic` の時、downstream は base branch が無く壊れるため `skipped_due_to_upstream` で cascade skip。Phase 4 report に handoff 必要箇所を明示。

---

## D6. PR body も judge する (架構 inconsistency 解消)

**決定**: skill 全体は generator≠evaluator を徹底するため、最終 artifact (PR body + title) も `references/pr-body-judgment.md` mandate で orchestrator が judge。implement-agent の Phase 3 を細分化 (`push_and_pr` → `create_pr` / `fix_pr_body`、max 2 round)。

**根拠**:
- PR body は reviewer が最初に読む artifact、PR 品質に直接影響
- 旧設計は implement-agent が単独生成して judge 無し → verify_skipped 漏れ / dedupe link 漏れ / Test plan 空 / PR title prefix 違反 等の頻発 bug の構造的原因
- title は最終 artifact の一部だが Phase 3 push 前には存在しないため、ここが唯一の judge ポイント (`<!-- proposed-title: ... -->` HTML コメントで PR body draft 冒頭に埋め込んで一緒に judge)

**変えると壊れること**: judge を外すと PR body の品質が implement-agent の出力品質に依存、`Test plan` 空 / `verify_skipped` 未記載 / parent-issue link 抜け等の頻発 bug が再発。reviewer 信頼を失う。

---

## D7. Phase 5 は depth=0 only (LESSONS append の race 回避)

**決定**: Phase 5 Retrospect は top-level orchestrator (depth=0) のみ実行。並列子 (depth>0) は Phase 5 を skip して親に return、子の learning 材料は state_dir に残し親が集約して 1 回だけ `LESSONS.md` に append。

**根拠**:
- 並列子が同時に `<skill_dir>/LESSONS.md` に append すると行欠落・順序破壊・seq 重複 → 自律成長サイクルの唯一の永続ストレージが破損する致命傷
- 「skill が自律的に成長する」核心機構なので絶対に race を起こさない設計
- depth=0 の親は全子 return 後に集約できる position にいる

**変えると壊れること**: depth>0 にも実行を許すと (1) LESSONS が破損して将来の Pre-flight で誤った lesson を取り込む、(2) seq 重複で `Status` 行更新の対象不明、(3) 修復には git history からの再構築が必要。

---

## D8. skill mandate ファイルの自動編集は禁止 (自律と安全の両立)

**決定**: Phase 5 retrospect は `LESSONS.md` への append / 物理削除 / Status 遷移のみ許容。`SKILL.md` / `references/` / `agents/` / `scripts/` の自動編集は禁止。`Status: pending` が 20 件超で `AskUserQuestion` → 同意あれば `gh issue create` で skill repo に improvement issue 投稿、人間 review を挟む。

**根拠**:
- mandate ファイル自動編集は regression リスク (LLM 1 turn の誤判定で次回以降の全 run に悪影響)
- LESSONS.md は **未消化 learning queue** (永続記録ではなく `git log` が事実 trail)。append / 削除 / Status 遷移は機械的で safe
- skill 改善は issue 経由で人間 review → 必要なら develop-issue を skill repo で再帰起動して PR 化 (recursive case)
- 自律性 (learning が積み上がる) と安全性 (人間 review を残す) の両立

**変えると壊れること**: mandate 自動編集を許すと (1) 1 回の誤判定が全 run に永続的に悪影響、(2) PR review 経由の人間チェックが消える、(3) LLM が「自分を改善した」hallucination から無意味な mandate を追加し続ける。

---

## D11. LESSONS.md は未消化 queue、git log が事実 trail (持続可能性)

**決定**: LESSONS.md は append-only な永続 log ではなく **「未消化 learning queue」**。`pending` (mandate 未反映) / `proposed (issue <URL>)` (issue 投稿待ち) / `rejected (issue closed)` (dedupe signal) の 3 状態のみ保持。mandate 反映と同時に entry は **物理削除** され、commit message + git log が事実 trail を担う。

**根拠**:
- append-only にすると `applied` 状態の entry が無限に蓄積、改修者の読みやすさと git diff コストが指数増加
- mandate に反映された lesson は redundant: 真は SKILL.md / references/ にあり、lesson は経緯 memo に過ぎない
- 削除前に commit message に `L<seq>: <Summary> → <reflected_in>` を必ず含めることで `git log --grep "L<n>"` で後から trace 可能
- `rejected` だけは残す: issue 却下されても問題は未解決、削除すると次回 retrospect-agent が同 pattern を新 lesson 化 → 無限 propose ループ。dedupe signal として永続必要

**変えると壊れること**:
- append-only に戻す → ファイル肥大化、改修者の読みやすさ劣化、ユーザ前提「prompt update 完了したら過去 lesson の必要性は下がる」に反する
- `rejected` も削除する → 無限 propose ループ (同じ issue を何度も投稿)
- 削除主体を retrospect-agent (sub-agent) に渡す → semantic 理解 context 不足で誤削除リスク (D8 の最後の砦が崩れる)
- commit message に Summary を含めない → git log trail が機能せず削除した瞬間に情報が消失

**削除主体は orchestrator** (effort:max): retrospect-agent は `applied_candidates[]` を return するだけ。orchestrator が `<skill_dir>/SKILL.md` + `references/*.md` を Read して「本当に反映済みか」verdict → 物理削除 + commit。allowed-tools に `Bash(git commit *)` を skill_dir scope で追加。

---

## D9. ローカル verify skip の許容 (CI fallback)

**決定**: `format` / `lint` / `test` / `build` のいずれかが「tool 不在」(`scripts/run_command.sh` が `rc=5` を返す = exit 127 を wrapper が変換) で実行不能、かつ `repo-profile.ci.covered_actions` に該当 action があれば skip して PR まで進める。`open_concerns.verify_skipped` に記録 + PR body の `Local verification` セクションに明示。

**根拠**:
- 「最大限ローカル、できないものは CI に委ねる」原則。GitHub Actions 環境で必要 tool が揃ってるのにローカル不能で止めるのは時間の無駄
- skip と failure の厳密区別: command 起動不能 (`rc=5`) のみ skip、command が走って exit 非0 は failure (5 round retry → stuck)
- CI で対応 action が走らない repo では skip 不可 (人間に届かないため stuck)、safety net 維持

**変えると壊れること**: 失敗を skip にすると CI 緑なのに本質的 bug が紛れる。skip を許容しないとローカル環境制約で止まって PR が一切作れない。区別を曖昧にするとどちらも頻発。

---

## D10. heavy command 禁止の例外: 低リスク state 操作

**決定**: orchestrator は build / test / git mutation 等の重い操作を自分で実行しない原則だが、以下は低リスク state 操作として明示例外:
- `gh issue create` (sub-issue 化)
- `gh issue edit` (親 issue body update)
- `gh issue comment` (Phase 4 report)
- `git diff` (code judgment 用 read-only)
- state dir 内ファイルの write (state.json / context.md / pr-urls.md / judgment ファイル)

**根拠**:
- これらは orchestrator の責務 (Phase 遷移 / 集約 / 判断 trail 永続化) に直接紐づく
- `Task` で agent に委譲すると context 切断・return 待ちで非効率
- いずれも reversible (Issue / comment は edit 可、state dir は local file、`git diff` は read-only)
- build / test / push / `gh pr create` は依然 implement-agent に委譲

**変えると壊れること**: 例外を消すと (1) sub-issue 作成のたびに Task 起動で latency 増、(2) Phase 4 comment 投稿で state dir 全文を Task に渡す必要が出て context 浪費、(3) code judgment が要約 (diff_summary) だけ見て本物 diff を見たい時に Read できない。

---

## 設計トレードオフ一覧

主要トレードオフを 1 表に集約。詳細根拠は対応する D# を参照。

| 軸 | 選択 | 対 (採らなかった案) | 詳細 |
|---|---|---|---|
| judgment の所在 | orchestrator 集中 | 各 phase agent 自己判定 | D1 |
| 分解判定 | `depends_on` 1 行 discriminator | 多軸の subjective 判定 | D2 |
| 並列子の Q&A | 親に bubble up | 各子が独立 user 質問 | D3 |
| repo 特化 | 動的抽出 (repo-profile) | ハードコード | D4 |
| 詰まり時の挙動 | escape_hatch / blocked の 2 分離 | 単一 stuck | D5 |
| PR body 品質 | mandate で judge | implement-agent 単独生成 | D6 |
| Phase 5 実行範囲 | depth=0 only | 全 depth で実行 | D7 |
| skill mandate の改善 | mandate 自動編集禁止 + 人間 review 経由 | 完全自動編集 | D8 |
| verify skip | tool 不在のみ + CI cover で skip 許容 | 一切 skip 禁止 / 任意 skip 許容 | D9 |
| heavy command 禁止 | `gh issue * / git diff / skill_dir 内 git commit` を明示例外 | 全 command を agent に委譲 | D10 |
| LESSONS.md の永続性 | 未消化 queue (applied 物理削除、git log が trail) | append-only 永続 log | D11 |
| PR 作成後の責務 | Phase 6 (Tending) で CI green + no-conflict 維持まで自律 | DRAFT PR 作成で終了 | D12 |

---

## D12. Phase 6 (Tending): CI green + no-conflict 自律維持

**決定**: DRAFT PR 作成で skill を終了させず、Phase 6 (Tending) で CI green + no-conflict まで責任を持つ。`gh run watch` で同期待機、CI fail は `ci-judgment.md` mandate で自動修正可カテゴリのみ修正 (lint/format/import、≤5 行/1 file 制約)、conflict は `gh pr update-branch` → 失敗時 `git rebase` + `--force-with-lease` (2 条件 AND)。`depth>=0` 全 instance で並列実行、各 instance が独立 round counter。

**根拠 (skill core vision との整合)**:
- skill は **remote container (build 環境なし) で並列実行**が前提 → ローカル verify 不能 → **CI が verify の唯一手段**
- DRAFT PR 作成で終わると CI fail / conflict の事後処理が人間任せ → 「自律的に完了」要件未充足
- 並列で main がガンガン動く環境 → conflict 頻発 → 自動 rebase が必須
- prompt 自己成長 (Phase 5 retrospect) のため、Phase 6 結果 (`tend_summary`) を learning material として活用

**3 つの round counter を独立にカウント**:
- `MAX_TEND_ROUNDS_CI_FIX=3` (自分の fix 起因の round、決定的)
- `MAX_TEND_ROUNDS_CONFLICT=2` (upstream churn 起因の round、外因)
- `MAX_TEND_ROUNDS_FLAKY_RETRY=2` (flaky 空 retry、`consume_round=false`)

共通カウンタにすると flaky CI で誤 escape、または並列 PR 連鎖 rebase 渋滞で全 PR が tend timeout する確率高い (3 agent critique で converge した key insight)。

**自動修正可カテゴリは大幅縮小** (lint / format / import / single-file 型注釈のみ、`max_changed_lines=5` / `max_changed_files=1` 制約):
- remote container で build 不能 = fix の正しさは次の CI run でしか分からない → 表面 fix で別 test 壊す regression リスク高
- 確実に直せる「決定的な単一 file fix」のみ自動、それ以外は handoff
- 制約超過したら implement-agent が `status: ci_handoff` を即 return (orchestrator が transition)

**`--force-with-lease` 例外** (2 条件 AND): hard rule の `--force` 全禁止を緩めるが、安全境界を 2 条件で厳格化:
1. `state.json.created_branches[]` に登録済み (実装者自身が作った branch のみ、手動作成 / reviewer 作成 branch を触らない)
2. `target != repo-profile.repo.default_branch` (main / master / develop を絶対 force しない)

**branch 名 pattern (`claude/*` 等) は条件に含めない** — D4 (repo-agnostic) 違反、`created_branches[]` で「自己作成」は十分証明される。pattern check は safety net として重複かつ hardcode source。

加えて `gh api repos/.../branches/.../protection` で branch protection allow_force_pushes を事前 check。reject 時は retry せず即 handoff (reviewer の直接 commit を盲目的上書きしない、信頼破壊回避)。

**Phase 順序 4 → 6 → 5**:
- Phase 5 retrospect が Phase 6 結果 (CI fail pattern、conflict 連鎖、flaky 検出) を learning に取り込めるよう、Phase 6 を Phase 5 の前
- Phase 5 = depth=0 only (LESSONS race 防止) / Phase 6 = depth>=0 全 instance、と responsibility 分離

**変えると壊れること**:
- Phase 6 を捨てる → DRAFT PR 作成で終了、CI fail / conflict が人間任せ、skill の「自律的に完了」core vision 崩壊
- 自動修正可カテゴリを広げる (test fix を含める等) → 表面 fix で regression、tend loop が無限化、`escape_hatch_with_pr` 連発で人間 review 信頼を失う
- `--force-with-lease` を 2 条件 AND 無しに許容 → 他者の branch を force push、reviewer commit を上書き、信頼破壊
- 共通 round counter → 並列 PR 連鎖 rebase で全 PR が tend timeout (Agent 2 mental simulation で 60-80% 確率の致命傷)
- Phase 順序を 5 → 6 にすると → retrospect が tend learning を拾えない、CI fail pattern の learning 漏れ
- Phase 6 を depth=0 only にする (Phase 5 と同じ) → 並列子の PR を親が tend する集中処理になり、API rate limit の hot spot、並列性の意味が消える

**`MAX_PARALLEL_TEND=3`**: GitHub API rate limit (1h 5000 req) 対策。`gh run watch` は polling 内部実装で req 消費、3 並列で同時 watch 上限。超過は queue。

**Monitor で multi-PR 並行 watch (ローカル実行で特に有効)**: `gh run watch` を `Bash(run_in_background=true)` で起動、各 process を Monitor で並行 stream。foreground 同期 block すると ローカル multi-PR tend で `N × 30min = 大量の wall clock` を消費するが、background + Monitor なら `~30min` (CI duration) に圧縮。remote container でも benefit あるが、特にローカルで人間が wait する場面で大きく効く。

`state.json.tend.watch_processes[]` に `run_id` + `current_step` を記録することで **L39 part 1 (Resume mid-Phase 6 gap) を部分解消**: session が死んで background process が消えても、Resume 時に各 `run_id` について `gh run view <run_id> --json status,conclusion` で「すでに終了している run」を復元 → completed なら Monitor 起動せず conclusion で直接分岐。
