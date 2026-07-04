# PR body judgment mandate

<context>
orchestrator が Phase 3 の `phase=push_and_pr` 起動後・実 PR create 前に Read する観点集。implement-agent が `<state_dir>/pr-body-<sub_plan_index>.md` に書き出した PR body draft を judge する。
</context>

<constraints>
- reviewer が最初に読む artifact は PR body。コードでなく body の質が「60 秒で理解できるか」を左右する
- skill 全体は generator≠evaluator を徹底 (gather/plan/code) しているのに、最終 artifact (PR body) だけ implement-agent が単独生成して judge が無い架構 inconsistency を解消する mandate
- 評価軸は observable (Markdown セクション存在 / 文字数 / リンクの一致) で主観を最小化
- Blocker / Suggestion / Nits の判定基準は `references/judgment-conventions.md` 参照
</constraints>

## チェックリスト (sub-plan ごとに 1 回 judge)

1. **Summary** (Blocker): 3-7 行で「**なぜ** (動機) / **何を前提に** (関連 issue・先行 PR) / **どう変える** (採用案要約)」を簡潔に説明しているか (user `~/.claude/rules/pr-writing.md` 準拠、diff から読める「何を」は過度に展開しない)。strategy_summary 全文コピペ (10 行超) は冗長で blocker、空 or 「fix」のような 1 単語も blocker
2. **Related links 一致** (Blocker、mode-aware、L44/Problem 6 対応): `state.implement.mode` を取得 → mode 別に check:
   - `single`: `Closes #<issue_id>` が一致
   - `chained_in_memory`: `Part of #<issue_id> (N/M)` が一致、**`Closes #<元 issue>` の禁止 check** (一致したら blocker、PR merge で issue が auto-close され兄弟 PR が orphan 化する)
   - `chained_with_subissues`: `Closes #<sub_issue_id>` + `Part of #<parent_issue> (N/M)` の両方が一致
   - `parallel_recursive`: `Closes #<sub_issue_id>` + `Part of #<parent_issue>` の両方が一致
   - Linear リンクが context.md にあれば反映
3. **Test plan** (Blocker): sub-plan の `tests` 配列と verify 結果 (passed/skipped/stuck) が反映されているか。空 or 「手動確認」のみは blocker
4. **Local verification セクション** (Blocker): 全 action (format/lint/test/build) の状態が明示されているか。`verify_skipped` がある場合は **必ず action 名 + reason + CI workflow path** が明示されている (reviewer が CI run を辿れる)。`open_concerns.verify_skipped` と整合
5. **Gather Q&A** (Suggestion): qa-trail.md に Q&A があれば「Q→A の対」が短く要約されているか。N/A の場合は明示
6. **Review trail** (Suggestion): plan rounds / code rounds の verdict 推移が記録されているか
7. **Open concerns** (Blocker): stuck の場合のみ箇条書きで、`open_concerns` 配列の全 entry が漏れず反映されているか。`kind` enum 一覧は `references/return-schemas.md` の「`open_concerns` の構造」section 参照 (15 値、Phase 別 grouping)。各 entry の `summary` + `details` field が PR body の Open concerns セクションに反映されているか check
8. **PR body 必須 5 項目** (Blocker、user `~/.claude/rules/pr-writing.md` 準拠、refine-issue 代替):
   - **動機**: sub-plan の `acceptance` + issue body の出発点 (なぜこの変更が必要か)
   - **前提**: 関連 issue / 先行 PR / 外部仕様の cross-link
   - **根拠**: qa-trail.md の確定事項 + 実 verify 結果 (Local verification 連動、ベンチマーク結果等)
   - **検討した代替案**: sub-plan `## Approach.採用案` + 却下理由 **+ `implementation-notes-<N>.md` の `[unspecified_decision]` / `[tradeoff]` entry** を統合 (sub-plan に書かれてない実装中判断を transfer)
   - **レビューで誤解されそうな観点**: `open_concerns` / `scope_check_skipped` / `verify_skipped` **+ `implementation-notes-<N>.md` の `[unexpected_finding]` / `[spec_interpretation]` entry** を統合 (実装中に気付いた「reviewer が引っかかりそうな点」を先回り)

   PR body section の例:
   ```markdown
   ## 動機
   <sub-plan acceptance + issue 出発点>

   ## 前提
   - 関連: <issue / PR / spec link>

   ## 根拠
   - <qa-trail.md 確定事項>
   - <verify 結果 + ベンチマーク>

   ## 検討した代替案
   - <代替案 1>: 却下理由 = <...>

   ## レビューで誤解されそうな観点
   - <open_concerns / verify_skipped 等>
   ```
9. **dedupe-check 結果** (Suggestion): もし `gh search prs` で候補があった場合、PR body に「dedupe 確認済」or「重複なしを確認」が記録されているか
10. **誤情報 / 矛盾** (Blocker): PR body 内の数値 (rounds、PR count、URL) が state.json / qa-trail.md と矛盾していないか
11. **PR title prefix 適合性** (Blocker、R65): PR body draft の冒頭に提案 title が含まれる場合 (implement-agent §10.2 が body draft と一緒に title 候補を書き出す)、以下を 1 項目ずつ確認:
    - [ ] `repo-profile.conventions.pr_title.allowed` の prefix で始まっているか
    - [ ] `max_length` (デフォルト 70) 内か
    - [ ] `<scope>` 規約遵守 (詳細は `plan-judgment.md` §9 参照、user `~/.claude/rules/conventional-commits.md` 準拠の短縮形 / 3 つ以下 / モジュール名重複禁止)
    - [ ] 破壊的変更時は `<type>(<scope>)!: <description>` 形式

    title は最終 artifact の一部だが Phase 3 では存在しないため、ここが唯一の judge ポイント
12. **全体冗長性 check** (Blocker、R-C-2、user `~/.claude/rules/pr-writing.md` 「diff から読める『何を』は過度に展開しない」原則 enforcement、§1 Summary check は冒頭部のみ対象だが本項目は PR body 全体に適用): 以下のいずれかにヒットしたら blocker:
    - [ ] 変更 file 一覧を箇条書きで並べている (例: `- Foo.swift, Bar.swift を変更`) — diff で読めるので冗長
    - [ ] 各 file の変更内容を逐語的に書いている (例: `- Foo.swift L42 で if-let を guard-let に変更`) — diff で読める
    - [ ] diff そのものを PR body に貼り付けている

    PR body は「判断 / 動機 / 影響」を書く場所であり、「何を変更したか」は diff に任せる

## verdict と次の動作

| Verdict | 次の動作 |
|---|---|
| `ready` | implement-agent を `phase=create_pr` で起動 → `gh pr create --body-file <state_dir>/pr-body-<N>.md` 実行 |
| `needs_fix` | implement-agent を `phase=fix_pr_body` + blockers で再起動 (max 2 round)。3 round 目は escape-hatch で create_pr |

## 出力

`<state_dir>/pr-body-judgment-<sub_plan_index>-<round>.md`:

```markdown
# PR Body Judgment (sub-plan <N>, round <M>)

## Blockers (must fix before PR create)
- [B1] <指摘> — 場所: pr-body-<N>.md の <セクション> — 理由: ...

## Suggestions (should consider)
- [S1] ...

## Verdict
<ready | needs_fix>
```

ループ抑止: `references/judgment-conventions.md` 参照 (max 2 round、3 round 目は escape-hatch で create_pr 実行、open_concerns に「PR body 品質懸念」追記)。

## アンチパターン

- 「PR body はもっと詳しく」「もっと例を増やせ」のような抽象論 → observable 基準 (セクション存在 / 文字数範囲) で判定
- コードの実装に踏み込む → code-judgment の責務、scope 外
- 細かい言い回しで blocker 量産 → suggestion / nit に落とす
- Summary が「綺麗に書けてる」を blocker にする → 内容に虚偽 / 矛盾がなければ OK
