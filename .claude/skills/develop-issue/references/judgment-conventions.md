# Judgment conventions (skill 全体共通)

<context>
本 file は全 judgment mandate (`gather-judgment.md` / `plan-judgment.md` / `code-judgment.md` / `pr-body-judgment.md` / `ci-judgment.md` / `conflict-judgment.md` / `review-comment-judgment.md`) が参照する共通規約。
各 judgment file は本 file の定義に準拠する (Blocker/Suggestion/Nits の独自定義を持たない)。
</context>

## Table of Contents

- [verdict 強度の 3 階層](#verdict-強度の-3-階層)
- [文脈別マッピング](#文脈別マッピング)
- [Judgment file vs Strategy file](#judgment-file-vs-strategy-file)
- [ループ抑止 (共通)](#ループ抑止-共通)
- [Reference file 冒頭表記の規約](#reference-file-冒頭表記の規約)

## verdict 強度の 3 階層

各 judgment mandate は指摘を以下 3 階層で分類する。

| 階層 | 定義 | verdict / 動作 |
|---|---|---|
| Blocker | merge / 次フェーズ前に必ず修正必要。user 規約 / acceptance / security 違反 | `needs_fix` / `needs_revise` で fix dispatch を発火 |
| Suggestion | 改善推奨だが merge 阻止しない (将来 maintainability / 軽微 regression リスク) | verdict には影響しない、PR body の Suggestions section に記録 |
| Nits | 微細な好み・stylistic、reviewer 判断で skip 可 (typo / commit message の細部 等) | verdict には影響しない、reviewer が ack するだけで OK |

## 文脈別マッピング

判定時のマッピング指針:

- 「受け入れ基準を満たさない」「PR が安全に merge できない」「user 規約 (`.claude/rules/*`) 違反」 → **Blocker**
- 「ベストプラクティスから外れる」「将来 maintainability に影響」「regression リスク中程度」 → **Suggestion**
- 「typo」「commit message の細部」「import 順序」 → **Nits**

## Judgment file vs Strategy file

- **Judgment file** (`plan-judgment.md` / `code-judgment.md` / `pr-body-judgment.md` / `review-comment-judgment.md`): 出力は review-like (Blockers/Suggestions/Nits/Verdict)。本 file 3 階層を採用
- **Strategy file** (`ci-judgment.md` / `conflict-judgment.md`): 出力は strategy-decision (verdict 1 つ + 詳細)。Blocker/Suggestion/Nits は使わない
- **Pre-flight file** (`gather-judgment.md`): 出力は context build (Self-fillable gaps / Questions / Verdict)。Blocker は出力 schema 内に明示、Suggestion/Nits は使わない

## ループ抑止 (共通)

全 judgment file に共通する規律:

- 前回 judgment を Read し、解決済み blocker は再掲しない
- N round 経過しても解決しないなら `stuck` / `escape_hatch` で DRAFT PR を作成 (`open_concerns` に残課題を記録)
- 同じ blocker を毎 round 繰り返す挙動は禁止

各 file の round 上限:
- `plan-judgment`: 2 round
- `code-judgment`: 3 round
- `pr-body-judgment`: 2 round (3 round 目は escape-hatch で create_pr)
- `review-comment-judgment`: `MAX_REVIEW_LOOP_ROUNDS=2`

## Reference file 冒頭表記の規約

全 reference file の冒頭は third person で `(誰) が (どの phase) で読む観点集` 形式で記述する。
新規 reference file 追加時の regression 監視ポイント。
