# Retrospect mandate

<context>
retrospect-agent (sub-agent) が読む観点集。state_dir 全体の Read と learning 抽出は orchestrator の judgment context を圧迫するため、Phase 1-4 と同じく sub-agent に委譲する。orchestrator は retrospect-agent の return JSON だけ受け取り、threshold 超過時に AskUserQuestion で skill 改善 issue 投稿を判断する。

目的: 次回の develop-issue 実行で同じ mistake を繰り返さない / 同じ成功パターンを再現する。
</context>

## Table of Contents

- [LESSONS.md の運用モデル](#lessonsmd-の運用モデル)
- [大原則](#大原則)
- [入力ファイル](#入力ファイル-orchestrator-が-read)
- [抽出観点 7 種類](#抽出観点-category-別--7-種類-a10-で-review_loop_pattern-追加)
- [出力 1: retrospect.md](#出力-1-state_dirretrospectmd-今回実行の詳細)
- [出力 2: LESSONS.md](#出力-2-skill_dirlessonsmd-未消化-learning-queue)
- [skill 改善 issue 提案](#skill-改善-issue-提案-threshold-超過時)
- [アンチパターン](#アンチパターン)
- [skill 開発時の規律](#skill-開発時の規律-r74l29-由来)
- [L15 パターン再発防止 guard](#l15-パターン再発防止-guard-r75)

## LESSONS.md の運用モデル

LESSONS.md は **「未消化 learning queue」**。append-only な事実 log ではない。

- `pending` 状態の entry だけが「skill mandate にまだ反映されてない learning」 = 次回 Pre-flight で読む価値あり
- `applied` 状態は **存在しない (= 物理削除済み)**。mandate に反映された瞬間に entry は削除され、git log が事実 trail を担う
- `proposed (issue <URL>)` は「改善 issue 投稿待ち」signal、人間 review 結果を待つ間 entry は queue に残る
- `rejected (issue <URL> closed)` は「issue が却下された」signal、削除されず dedupe (次回 retrospect-agent が同 pattern を新 lesson 化しないため) として永続

これにより LESSONS.md は時間経過で肥大化せず、常に「未消化な learning だけが見える状態」を保つ。

## 大原則

<constraints>
- retrospect は生産的批判。「失敗探し」ではなく「次回どう改善するか」に焦点
- skill mandate ファイル (SKILL.md / agents / references / scripts) の自動編集は禁止 (regression リスク)。LESSONS.md は append + applied 物理削除 + Status 遷移のみ許容
- 削除主体は orchestrator (retrospect-agent ではない)。retrospect-agent は「applied 候補 list」を return、orchestrator が effort:max で skill mandate を Read して verdict → 物理削除実行 → commit (誤判定の最後の砦を effort:max に残す)
- lesson は 5 行以内 / 具体的かつ actionable にする (抽象論は捨てる)
- 「ユーザがフロー修正した内容」は最重要 signal — それは mandate に書いてなかった insight
- 新規 mandate 追加時の filler / tautology / `必ず` regression check も合わせて実施 (user `~/.claude/memory/feedback_no_filler_phrases.md` 由来)
</constraints>

## 入力ファイル (orchestrator が Read)

- `state_dir/` の全 judgment ファイル (`gather-judgment-*.md`, `plan-judgment-*.md`, `code-judgment-*.md`, **`pr-body-judgment-*.md`, `ci-judgment-*.md`, `conflict-judgment-*.md`, `review-judgment-*.md` (Phase 7 結果、A10)**)
- `state_dir/qa-trail.md` — Q&A 履歴 (ユーザ correction signal)
- `state_dir/plan.md` / `sub-plan-*.md`
- `state_dir/diff-summary-*.txt` (大規模な場合は scan のみ)
- `state_dir/state.json` (verify_summary, rounds 等の集計、**`tend.summaries[].review_loop_*` field 含む**)
- `state_dir/pr-urls.md`
- `state_dir/retrospect.md` (既存ファイルがあれば前回 retrospect)
- `<skill_dir>/LESSONS.md` (過去の learning と重複してないか check)
- **depth=0 から起動された場合、`child_state_dirs[]` 引数で渡された全子 state_dir も Read** (D.3、SW10): 子の `qa-trail.md` / `judgment-*.md` / `review-judgment-*.md` を集約して親 retrospect に取り込む

## 抽出観点 (category 別) — 7 種類 (A10 で `review_loop_pattern` 追加)

### 1. `script_bug` (致命度: 高)
- scripts/* が想定外の挙動をしたか? exit code 異常、stderr に error 残存、silent skip
- スモークテストが無く事故発生時のみ気付く類は **必ず lesson 化**
- 例: 「detect_secrets.sh が color escape で secret value を silently skip した。`--no-color` 必須」

### 2. `mandate_gap` (致命度: 中)
- 判定 mandate (`{role}-judgment.md`) で見落とした観点はあったか?
- code-judgment で blocker と書いたが実は本物の問題でなかったケース (false positive)
- 逆に、ユーザが「これも見るべきだった」と指摘した観点
- 例: 「plan-judgment §3 の discriminator が `depends_on` だけ見ていて、独立だが branch 衝突する場合の判定が漏れていた」

### 3. `q_a_overhead` (致命度: 低)
- Q&A で聞いた質問のうち、**orchestrator が追加ファイル Read で自分で埋められた** ものはあったか?
- ユーザに聞いた質問がすべて「実装の分岐に直接効く」ものだったか?
- 例: 「Q2 で `~/path/to/config.json` の値を聞いたが、`gh repo view --json` で取れた」

### 4. `verify_skipped_pattern` (致命度: 中)
- ローカル verify を skip した実 ケースは何か (tool 不在の具体内容)
- CI で実際に拾えたか (PR コメントで確認)
- 同じ skip パターンが頻発するなら、gather-agent で `ci.covered_actions` 抽出を改善する余地あり

### 5. `user_correction` (致命度: 高)
- 実行中にユーザが「いや、そうじゃない」「こうして」と指示した内容
- 「そんなに聞かないで」「逆にこれは聞くべき」等の interaction 改善 signal
- 例: 「skill 内 commit を勝手にしないで、テストしてから commit して」と言われた → スモークテスト必須化の lesson

### 6. success patterns (致命度: 中、ポジティブ side)
- 1 round で gather/plan/code 全部 ready に到達した issue の特徴
- recursive_split で sub-issue 並列が完璧に走った場合の条件
- 「これは今後も再現すべき」というパターン

### 7. `review_loop_pattern` (致命度: 中、A10 で新設 / Phase 7 結果)
- Phase 7 (Review-loop) の bot/human reviewer 反映で得られた learning:
  - 3 分類 (`scope_addition` / `preexisting_bug` / `off_topic`) の誤判定 pattern
  - reviewer 種別 (bot / human) ごとの反応特性 (個別 bot 名はその run 固有の事実、本 mandate では type レベルで集約)
  - `MAX_REVIEW_LOOP_FIX_LINES` 超過 → handoff の頻度 (反映できない大きな指摘の pattern)
  - 連鎖 dead code (削除パターン適用後に unused 化する symbol) を Phase 7 で初検出 → plan-judgment §11 改善案として lesson 化
- input: `state.tend.summaries[].review_loop_*` / `state_dir/review-judgment-*.md` / 子 state_dir からの集約 (depth>0 並列子の case)

## 出力 1: `<state_dir>/retrospect.md` (今回実行の詳細)

```markdown
# Retrospect (run <ISO timestamp>)

## Summary
- Issue: #<id> <title>
- Mode: <single / chained / recursive_split>
- 結果: <N> DRAFT PR (created: <m>, stuck: <n>)
- 所要 round: gather <g>, plan <p>, code <c> (sub-plan 別)

## Learning candidates
- [L1] (script_bug) <短い summary> — Evidence: <state_dir/path>:LINE
  - Proposed action: <次回の動作変更案、または mandate/script への記述追加>
- [L2] (mandate_gap) ...
- [L3] (user_correction) ...

## Promoted to LESSONS.md
- [L1, L3] を promote (L2 は重要度低のため state_dir 内のみ保持)

## 既存 LESSONS.md との重複 check
- L1 は過去の LESSON #<n> と類似 → 頻発パターン化、issue 提案候補
```

## 出力 2: `<skill_dir>/LESSONS.md` (未消化 learning queue)

各 lesson は 5 行以内 / category prefix 付き / timestamp + evidence path:

```markdown
## L<seq>: <ISO timestamp> [<category>]
**Summary**: <1 行で>
**Evidence**: <state_dir 相対 path or issue URL>
**Action**: <次回の動作変更案、mandate/script への具体的な追記内容>
**Status**: pending | proposed (issue <URL>) | rejected (issue <URL> closed at <ts>)
```

Status enum:
- **`pending`**: mandate にまだ反映されてない未消化 learning。Pre-flight で読む対象。threshold (20 件超) 判定の対象
- **`proposed (issue <URL>)`**: 改善 issue が投稿された (mandate 反映待ち、人間 review 中)。Pre-flight read 対象外、threshold 計算除外
- **`rejected (issue <URL> closed at <ts>)`**: 改善 issue が closed (won't fix / not_planned)。**削除しない** (次回同 pattern を新 lesson 化しないための dedupe signal)
- **`applied` 状態は存在しない** (mandate 反映と同時に entry 物理削除、git log が事実 trail)

`<seq>` は連番。**削除しても renumber しない** (`git log --grep "L<n>"` で過去 commit message を参照できなくなるため)。番号 gap は許容。

**遷移パスとサイクル完結**:
- `pending → proposed (issue 投稿)` → `proposed → 物理削除 (issue merged & mandate 反映)` または `proposed → rejected (issue closed not_planned)`
- `pending → 物理削除 (直接 mandate 反映、issue 経由せず手動 fix された場合)`

**`pending → applied 物理削除` の遷移責任主体** (orchestrator):
1. retrospect-agent が Step 4.5 で過去 pending lesson の `Action` 記述が skill mandate に反映済みかチェック → 反映済みなら **`applied_candidates[]` を return** (削除はしない)
2. orchestrator が effort:max で各候補について `<skill_dir>/SKILL.md` + `references/*.md` を Read して verdict → 本当に反映済みなら **entry 物理削除** + `git add` + `git commit -m "LESSONS: Delete L<seq_list> applied to <mandate_refs>"` (commit message に削除 entry の Summary 行を必ず含める = git log が事実 trail)
3. **誤判定の最後の砦を effort:max に残す**: retrospect-agent (sub-agent、semantic 理解 context 不足) に削除権を与えない設計

これが無いと pending が無限蓄積して Pre-flight read 20 件上限で古い lesson が忘却される / LESSONS.md が肥大化する。

## skill 改善 issue 提案 (threshold 超過時)

LESSONS.md の `pending` が **20 件超** になったら、Phase 5 末尾で:

```python
if count_pending_lessons(LESSONS.md) > 20 and recursion_depth == 0:
  answer = AskUserQuestion([
    ("skill 改善 issue を作る", "20 件たまった lessons を集約して skill repo に issue 投稿"),
    ("今は作らない", "次回まで保留")
  ])
  if answer == "作る":
    title = "develop-issue skill 改善提案 (lessons N 件)"
    body = render_lessons_as_issue_body(pending_lessons)
    run(f"gh issue create --repo <skill_repo> --title <title> --body-file <body>")
    mark_lessons_as_proposed(LESSONS.md)
```

理由:
- 自動 PR 作成は危険 (skill 自身を書き換えると regression リスク)
- 人間が issue を review → 必要なら develop-issue を skill repo で再帰起動して PR にする (recursive case)
- 自律的だが安全装置を残す

## アンチパターン

- skill mandate ファイル (SKILL.md / agents / references / scripts) を **自動編集する** → 禁止 (regression)
- 既存 LESSONS.md entry の **Status 以外のフィールド** (Summary / Evidence / Action) を書き換える → 禁止
- LESSONS.md entry の **renumber** → 禁止 (commit message の `L<n>` 参照が壊れる、番号 gap 許容)
- **retrospect-agent が entry を物理削除する** → 禁止 (orchestrator の責務、retrospect-agent は `applied_candidates[]` の return のみ)
- **`rejected` Status の entry を削除する** → 禁止 (dedupe signal として永続)
- lesson に「もっと良くする」のような抽象論を書く → actionable に書き直し
- ユーザ correction を lesson 化しない → 最重要 signal を取り逃す
- 過去 LESSONS.md を Read せず重複 lesson を量産 → 必ず check (`rejected` 含む全 entry が dedupe 対象)
- 「失敗探し」モードで批判だけする → success patterns も拾う

## skill 開発時の規律 (R74、L29 由来)

**大規模 mandate 変更 (`SKILL.md` / `references/*.md` / `agents/*.md` / state.json schema いずれかを 50 行以上変更) の commit 前は、agent team 3 並列 critique を first step として実行する**:
- Explore agent: ファイル横断 grep で「mandate に書いたが pseudocode に反映漏れ」「semantic conflict」検出
- general-purpose agent: 架空 issue で mental simulation、詰まる箇所列挙
- general-purpose agent: 構造的弱点 (架構 inconsistency、責務曖昧) の発掘

3 周連続で validated (周1: 7 件 / 周2: 10 件 / 周3: 5 件 critical fix 発掘)。これが無いと L15/L17 系の「mandate に書いたが pseudocode 反映漏れ」bug が高頻度で温存される。

## L15 パターン再発防止 guard (R75)

新規 mandate / 引数 / フィールドを追加する場合、commit 前に以下 3 箇所が整合してるか必ず check:
1. **consumer 側 mandate** (これを使う judge / agent doc) — 「X 観点を追加」だけでなく「実 file の write も追加」
2. **producer 側 mandate** (これを生成 / 渡す agent / orchestrator pseudocode) — Task() args / state.json schema に新 field を載せたか
3. **schema / return-schemas** — 新フィールドが schema に追加され、enum 値の網羅性が確認されたか

これが不十分だと「mandate に書いたが誰も読まない / 書き出さない」dead code 化する。周1 R57 / 周2 R69/R70/R71/R72/R65 が全てこの pattern で発覚。
