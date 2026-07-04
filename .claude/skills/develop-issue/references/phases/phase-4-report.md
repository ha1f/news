# Phase 4 — Report

## Phase の目的・前提・後続

- **目的**: state_dir 上のファイルを Read し、自分の (sub-)issue に **authoritative 判断 trail** を投稿する。再現性 (同じ orchestrator が再処理して同じ結論に到達できる) + 可読性 (人間が短時間で全体像把握) が目的
- **前提**: Phase 3 完了 (`state.plan.sub_plans[].pr_url` populated)、または Phase 1.5 で投稿予定
- **後続への影響**: `state.report.issue_comments[]` に entry append、`state.report.status = "ready"`。Phase 7 後に rewriting しない (authoritative)

## Phase 4: Report dispatch (pseudocode)

```python
# Phase 4: Report (depth=0/depth>0 両方、自分の (sub-)issue にコメント、authoritative source)
# schema 1.1: issue_comments[] array に追加 (旧 schema の issue_comment_url singular は migrate_state で変換済)
report = build_issue_report(state_dir)   # 後述「出力フォーマット」参照
write(f"{state_dir}/issue-report.md", report)
try:
  comment_url = run(f"gh issue comment {issue} --body-file {state_dir}/issue-report.md")
  state.report.status = "ready"
  state.report.issue_comments.append({"phase": "report", "url": comment_url, "ts": now_iso()})
except Exception as e:
  state.report.status = "failed"
  state.report.reason = str(e)
  # PR は既に作成済みなので Phase 全体は失敗扱いにしない
save_state(state)
```

## 入力ファイル

- `gather-judgment-*.md` (最終 round) — Pre-flight verdict、Q&A 確定事項、scope/受け入れ基準
- `qa-trail.md` — Q&A 履歴 (人間が答えたもの)
- `plan.md` / `plan-judgment-*.md` — 分解戦略 (single / split_needed / recursive_split) と根拠
- `code-judgment-*.md` — 各 sub-plan の verdict、round 数、open concerns
- `pr-urls.md` — 作成 PR URL の append log
- `repo-profile.md` — 規約・TDD・human_owned の key 設定 (再現性ノート用)
- `state.json` の `plan.sub_plans[]` — 各 sub-plan の `pr_url` / `pr_status` / `verify_summary` / `code_review_rounds` / `open_concerns` (集計済み、§3/§4 セクション生成の primary source)
- `implementation-notes-*.md` (R-B-1、存在時のみ) — sub-plan ごとの判断 trail (4 category、free text)。**stuck / escape_hatch_with_pr の場合は §4 「作成 PR」セクションに `[unspecified_decision]` / `[unexpected_finding]` の冒頭 1-2 件を summary として追記** (PR body には流れないため、Phase 4 が唯一の永続記録)

## 出力フォーマット (6 セクション固定、各セクション 5 行以内目標)

```markdown
## 🤖 develop-issue 実装結果 (run <ISO timestamp>)

### 1. Acceptance / Scope / Decisions (refine-issue 代替)
- **Acceptance** (確定した受け入れ基準): <issue body + Q&A 確定事項 + sub-plan acceptance の集約、3-5 行>
- **Scope (in)**: <この skill 実行で扱った範囲、sub-plan の Changes / Tests に対応>
- **Scope (out)**: <意図的に対象外とした範囲、Q&A で「やらない」と決まったもの、handoff した human_owned>
- **Decisions** (技術判断の前提合意): <UI / UX / データ形式 / 命名 / feature flag 要否などの judgment、qa-trail.md の Q&A 結論を集約、3-5 行>

### 2. Q&A trail (詳細)
- Q1: <質問> → <回答> (出典: qa-trail.md)
- Q2: ... (Q&A が無ければ「Q&A 無し」)

### 3. 分解戦略
- verdict: `<single | split_needed | recursive_split>` (sub-plan <N> 個)
- 根拠: <plan-judgment-*.md の verdict 理由を 1-2 行で。recursive_split なら独立性の根拠も>

### 4. 作成 PR
- #<n>: <title> — DRAFT — <URL>   (正常)
- #<n>: <title> — DRAFT (stuck: <reason>) — <URL>   (escape-hatch、3 round needs_fix 残 / diff 大規模 / verify_failure 等)
  - **stuck/escape-hatch の場合** (R-B-1): `implementation-notes-<index>.md` の `[unspecified_decision]` / `[unexpected_finding]` 冒頭 1-2 件を要約として追記 (PR body には流れないため Phase 4 が唯一の永続記録)
- (skipped_dedupe の場合) — #<n>: <既存 PR title> — 重複検知のため skip — <既存 URL>
- (catastrophic の場合) — 作成失敗: <reason>
- recursive_split の場合は sub-issue 経由の PR URL も同じ書式で列挙

### 5. Local verification
- format/lint/test/build: <passed / skipped (CI で確認待ち, reason) / stuck>
- (skip があれば CI workflow path も明示: `.github/workflows/ci.yml`)

### 6. 再現性ノート
- 規約: <repo-profile.conventions の key 項目を 2-3 個、出典付き>
- TDD: <tdd_required の値 + 出典>
- human_owned: <影響有無、有なら handoff した旨>
- (open concerns があれば「次回 attempt 時の注意」として 1 行)
```

## 注意

- 冗長な full dump は避ける。各セクション 5 行以内、合計 30 行を目安
- 「再現性」のため Q&A 確定事項と分解戦略の根拠は必ず含める (これらは state dir 外には残らず、issue comment が唯一の永続記録)
- depth>0 (sub-issue) も同じフォーマットで自分の sub-issue にコメント (親 issue へのリンクは sub-issue body の `Part of #<parent>` で既に張られている)
- 失敗時 (`gh issue comment` 失敗) は state.json に記録して return 時に親に伝える。Phase 全体は失敗扱いにしない (PR は既に作成済み)
