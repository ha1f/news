# LSP fallback と Dead code 判定 (共通)

<context>
本 file は LSP (Language Server Protocol) 使用前提の判定 (`find_references` / `goto_definition` 等) で、LSP が unavailable / runtime fail の場合の fallback 戦略を集約する。
`plan-judgment.md` §11 / `code-judgment.md` §5d / 関連 agent prompt が参照する。
</context>

## Table of Contents

- [LSP availability 判定](#lsp-availability-判定)
- [Fallback 戦略](#fallback-戦略)
- [Dead code 判定 (機械的削除)](#dead-code-判定-機械的削除)
- [open_concerns 連携](#open_concerns-連携)

## LSP availability 判定

以下を 1 項目ずつ確認:

- [ ] `repo-profile.tooling.lsp_available: true` であるか
- [ ] LSP runtime call が成功するか (crash / unindexed file / 曖昧解消失敗していないか)

両方 `true` なら LSP 使用、片方でも false なら fallback。

## Fallback 戦略

LSP が unavailable または runtime fail の場合:

1. **grep alternation の best-effort**: `grep -rn "<symbol>" --include='*.<ext>'` で逆方向参照を検出
2. 本 PR で touch する file 内の参照は除外して count
3. `open_concerns.scope_check_skipped` に `{kind: "scope_check_skipped", fallback_method: "grep_alternation" or "none"}` を追加
4. PR body / sub-plan に「LSP 無のため網羅性に欠ける」明記必須

## Dead code 判定 (機械的削除)

削除対象 symbol の参照が 0 件の場合 (= dead code) の判定基準:

- **plan-judgment §11** (機械的削除 N>20 箇所で Blocker): plan 段階の早期判定、`## Dead code candidates` セクション必須
- **code-judgment §5d** (機械的削除 N>10 箇所で Blocker): code 段階の実 diff 判定、より厳しめ
- それ以外 (`<= 10` 程度) は Suggestion (Phase 7 で reviewer 指摘される前に sub-plan に追加検討)

機械的削除の典型 pattern:
- `if #available` / `if-else` 等で N>10 変更
- `@available` attribute 削除
- 複合条件 / guard / リネーム / シンプル削除パターン

差分の理由: plan は推定値ベースで甘め、code は実 diff があるので厳しめ。両方の閾値超過なら確実に Blocker。

## open_concerns 連携

LSP fallback / Dead code 判定で発生した open_concerns:

| kind | trigger | 動作 |
|---|---|---|
| `scope_check_skipped` | LSP fail → grep fallback | escape_hatch_with_pr または PR body 注記、`fallback_method` 明示 |
| `code_review_blocker` (機械的削除 Blocker) | 機械的削除 N>10 (code) / N>20 (plan) | needs_fix で再 dispatch |

詳細は `return-schemas.md` の `open_concerns` 構造を参照。
