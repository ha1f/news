# Plan judgment mandate

<context>
orchestrator が plan フェーズ後に Read する観点集。plan-agent が出力した `plan.md` / `sub-plan-N.md` を直接読んで判定する。
</context>

<constraints>
- 評価基準は `repo-profile.md` から読む (一般常識でなく対象リポジトリの規約)
- scope は plan の妥当性。実装の細部 (具体的なコード、命名の好み) は code judgment の責務
- Blocker / Suggestion / Nits の判定基準は `references/judgment-conventions.md` 参照
</constraints>

## チェックリスト

1. **受け入れ基準カバー** (Blocker): issue の受け入れ基準が sub-plan のどれかに対応しているか。漏れ → blocker
2. **Scope** (Blocker): `repo-profile` の「PR を意味ある単位で分ける」原則を満たすか。1 PR で収まらない → `split_needed` または `recursive_split`
3. **Sub-plan の独立性** (Blocker + 分解戦略決定): 独立化できるなら独立化。`depends_on` が本当に必要か検証。**同じ branch を 2 sub-plan が編集する設計 → blocker**。さらに **`recursive_split` 候補時 (= 全 `depends_on: null`) は `changes` 配列の file path を 全 sub-plan 横断で集合演算し、2 つ以上の sub-plan が同一 file path に出現するなら blocker** (R60、並列実行で git の merge conflict / file race を構造的に防ぐ)。**同様に `codegen_artifacts[]` (codegen 生成物の path、R68) も全 sub-plan 横断で集合演算、複数 sub-plan が同じ codegen trigger を持つ場合 chained 推奨** (R68、暗黙副産物の commit 越境を防ぐ)。同じ file / 生成物を触る sub-plan は 1 つに統合するか chained に変更
4. **Sub-plan の明確性** (recursive_split 時必須): 各 sub-plan が独立した sub-issue として再 gather 不要な明確さを持つか。曖昧なら revise 要求 (子で Q&A 発生する signal)
5. **Approach 代替**: sub-plan の `## Approach` セクションで採用案 + 代替案 + 却下理由が書かれているか。`repo-profile.conventions` に沿っているか、既存類似機能と一貫しているか
6. **Impact / 影響範囲**: sub-plan の `## Impact` セクションで呼び出し元 / api_contract_change / i18n / 他プラットフォーム / docs_update_required が網羅されているか
7. **Risk + Rollout**: sub-plan の `## Risks` と `## Rollout` (feature_flag / migration / 段階的 release) で後方互換性 / migration / performance / security が考慮されているか。**`repo-profile.conventions.human_owned` を Claude 側で生成しようとしている → blocker** (Rollout の migration 行で人間 handoff 明示なら OK)
7b. **Breaking change → migration 連鎖の事前検出** (R54): sub-plan の `Approach.採用案` か `Impact.api_contract_change: true` で breaking change を行う場合 (breaking change の定義は `gather-judgment.md` §2c 参照)、対応する **migration / data fix-up が Rollout に明示** されているか。明示無しで「Phase 3 で気付く」のは無駄、blocker で plan 修正要求
8. **テスト戦略**: `repo-profile.testing.required_levels` のテストが含まれているか。TDD 必須なら失敗テストから始める構造か
9. **規約準拠**: `repo-profile.commands.codegen[].trigger` にマッチする変更があれば codegen 実行が plan に明記されているか。commit/branch/PR title prefix が規約通りか。**触る dir が `repo-profile.directory_specific_conventions[].path` に該当する場合、その `rules[]` 遵守も判定対象** (R62、root と subdir 両方の規約遵守を確認)。

    PR title / commit message の `<scope>` 規約 (user `~/.claude/rules/conventional-commits.md` 準拠):
    - [ ] モジュール名の **短縮形** (`HomeFeature` → `Home`、サフィックス削除)
    - [ ] 3 つ以下のスラッシュ列挙 (4 つ以上なら scope 省略)
    - [ ] description でモジュール名に触れていない (scope で明示済みのため重複回避)
    - 破壊的変更時: `<type>(<scope>)!: <description>` 形式 (`!` 必須、`BREAKING CHANGE:` footer)
10. **不要変更**: issue 無関係な refactor / リネーム / 整形が含まれていないか (suggestion レベル)
11. **Dead code coverage** (L44/L46/Problem 2、機械的削除 N>20 箇所で Blocker、それ以外 Suggestion): plan-agent Step 1.8 で生成される `## Dead code candidates` セクションが sub-plan-N.md に存在するか確認:
    - 機械的削除 (`if #available` / `if-else` / 複合条件 / guard / `@available` attribute / リネーム / シンプル削除パターン適用で N>20 箇所) → セクション存在必須、blocker
    - sub-plan の Changes に「連鎖 dead code」が含まれていない場合は **Reviewer に指摘される前に plan で発見可能性大**
    - LSP fallback 戦略 (`tooling.lsp_available: false` または LSP runtime fail = `open_concerns.scope_check_skipped` あり) は `references/lsp-fallback.md` 参照。grep alternation の best-effort で許容、ただし `## Dead code candidates` セクションに「LSP 無のため網羅性に欠ける」明記必須
12. **Bug-specific completeness** (Problem 4/Group C、bug ticket のみ、Blocker): `state.gather.bug_type` (= bug 種別判定結果、`gather-judgment.md` §1b で populate、`return-schemas.md` の bug_type cross-phase matrix 参照) が `reproducible` / `intermittent` / `race_condition` の場合、sub-plan-N.md に以下のセクションが存在するか:
    - `## Reproduction` (既知の再現手順 / 再現テスト先行で書く mandate)
    - `## Root cause hypothesis` (実装前の仮説)
    - `## Verification approach` (修正後の確認方法、`reproducible` なら regression test 必須)

    無ければ blocker。`bug_type` が `null` の場合 = feature/refactor、本セクションは skip。`server_side` / `data_dependent` / `repro_unknown` の場合は `investigation_recommended` で plan に来るべきでない (Phase 1.5 で skill 終了)、来ていたら blocker

## 分解戦略 discriminator (D2 = `depends_on` 1 行原則維持、I14)

| 状況 | Verdict | 後続動作 (mode 決定は orchestrator が AskUserQuestion で確認、size 二次基準なし) |
|---|---|---|
| sub-plan 1 個 | `ready` | `mode=single` で implement-agent 起動 |
| 複数 sub-plan、全 `depends_on: null` | `recursive_split` | Phase 2.5 で **3 択 AskUserQuestion** (depth=0): `parallel_recursive` (並列 + sub-issue) / `chained_with_subissues` (順次 + sub-issue) / `chained_in_memory` (順次 + sub-issue なし) → mode 決定 |
| 複数 sub-plan、1 つでも `depends_on` あり | `split_needed` | Phase 2.6 で **2 択 AskUserQuestion** (depth=0): `chained_with_subissues` (順次 + sub-issue) / `chained_in_memory` (順次 + sub-issue なし) → mode 決定 |

理由: D2 を守るため verdict は `depends_on` 1 行のみで決まる。**`mode` の決定は verdict と独立**、AskUserQuestion でユーザに 1 回確認 (I15 と同パターン、重い副作用 = sub-issue × N 作成を保護)。

**size 二次基準 (sub_plan 数 / estimated_diff_lines) は verdict 分岐に組み込まない** (improvement-plan-v2 F-A4)。`L41` 等の size signal は plan-agent 内の reasonable call 根拠材料としてのみ使用 (description 用、判定軸外)。

## 全 verdict 一覧

| Verdict | orchestrator の次の動作 |
|---|---|
| `ready` | implement-agent 起動 |
| `needs_revise` | plan-agent 再起動 (blockers を渡す、max 2 round) |
| `split_needed` | sub-plan を順次処理 (chained) |
| `recursive_split` | `gh issue create` + 並列 Task |
| `blocked_by_dependency` | AskUserQuestion (depth=0 のみ) |
| `no_op` | AskUserQuestion (depth=0 のみ) |
| `catastrophic` | AskUserQuestion で停止確認 |

## 出力

`<state_dir>/plan-judgment-<round>.md`:

```markdown
# Plan Judgment (round <N>)

## Blockers
- [B1] <指摘> — 該当: sub-plan-N の <セクション> — 理由: ...

## Suggestions
- [S1] ...

## Nits
- [N1] ...

## Verdict
<ready | needs_revise | split_needed | recursive_split | blocked_by_dependency | no_op | catastrophic>

## Sub-plans (ready / split_needed / recursive_split 時)
- index, title, branch, base, depends_on, summary
```

ループ抑止: `references/judgment-conventions.md` 参照 (max 2 round)。
