# Code judgment mandate

<context>
orchestrator が code フェーズ (implement-agent が `ready_for_review` で return した後) に Read する観点集。implement-agent が生成した `diff_summary` (`<state_dir>/diff-summary-<N>-r<round>.txt`) を直接読んで判定する。
</context>

<constraints>
- 評価基準は `repo-profile.md` から読む (一般常識でなく対象リポジトリの規約)
- 実装者は楽観バイアスを持つ。「動くだろう」「テストしたから大丈夫」を疑う
- scope は実装が plan と issue を満たしているか。plan 自体の妥当性は plan judgment の責務
- orchestrator は implement-agent の reasoning context を持たない → diff_summary だけで判定 (generator≠evaluator)
- Blocker / Suggestion / Nits の判定基準は `references/judgment-conventions.md` 参照
</constraints>

## チェックリスト

1. **受け入れ基準充足** (Blocker): issue の各条件を満たしているか
2. **Plan との一致**: sub-plan `changes` の各ファイルが実際に変更され、`risks` への対処が見えるか。plan にない不要変更がないか。`<state_dir>/implementation-notes-<N>.md` が存在する場合は Read して **「sub-plan に書かれてない判断 (`[unspecified_decision]`) が plan-judgment §11 dead code coverage / §12 bug-specific completeness 等で本来 plan に上がってるべきものか」** を確認 (頻発するなら gather/plan の充足度不足、retrospect 化候補)
3. **セキュリティ** (Blocker、diff 全体に適用):
    - 入力検証: ユーザー入力 / 外部 API / ファイルパス / SQL の sanitize 確認
    - 認可漏れ: protected resource アクセス時の認可 check
    - 機密情報: token / key のハードコード、ログへの secret 出力
    - Web 脆弱性 (該当 repo の場合のみ): XSS / CSRF / SQLi / path traversal
4. **エラーハンドリング**: silent failure (`catch(e){}`) なし、actionable なメッセージ、リトライ可否の区別
5. **テスト網羅** (Blocker、`repo-profile.testing` 基準):
    - `required_levels` のテストが含まれているか
    - TDD 必須なら失敗テスト → 緑のサイクルか
    - 異常系がカバーされているか
    - テスト名が検証内容を示しているか
    - 不要な console.log / print が残っていないか
5a. **Existing test ownership** (Blocker、R52): sub-plan の `## Existing tests` セクションに列挙された既存 test の expectation が、該当 PR で変更されている場合、それが **意図的な breaking change** (sub-plan の `Approach` / `Rollout` で言及済み) でない限り blocker。「新規 test 緑だが既存 test 破壊」の classic regression を catch
5b. **Local verify skip 許容判定** (`open_concerns.verify_skipped` がある場合): 各 skip entry について以下を 1 項目ずつ確認:

    - [ ] `repo-profile.ci.covered_actions` に該当 action が含まれているか
    - [ ] skip 理由が `rc=5` (tool 不在、wrapper 変換後) であって実行 failure ではないか

    両方 [ ] checked なら許容 (verdict には影響しない)、片方でも未 check なら blocker。

    注: orchestrator が見るのは wrapper 後の `rc=5`、元 `exit 127` ではない (run_command.sh:74-79 で変換)。本セクションが `verify_skipped` 許容判定の定義本体、`return-schemas.md` / `repo-profile-extraction.md` は本定義を参照する
5c. **Performance regression 観点** (R55、Suggestion + 条件付き Blocker): diff に **loop / アルゴリズム複雑度を変える変更** (e.g., 新規 `forEach` 入れ子、`Array.find` を `for` に変更、SQL `JOIN` 追加、O(n²) 化) が含まれる場合、Suggestion として「benchmark / profile 観点」を必ず記録。CI に benchmark gate が無いことを `repo-profile.ci.covered_actions` で確認、無ければ「ローカル測定不能、reviewer 判定必須」を `open_concerns` に追加
5d. **Cascade dead code 検出** (L44/L46/Problem 2、Blocker for 機械的削除、それ以外 Suggestion): diff に削除 (`-`) が含まれる場合、削除された identifier (symbol / 変数 / クラス) が **他の場所で使われていないか** check。LSP fallback / 機械的削除判定基準は `references/lsp-fallback.md` 参照 (Dead code 判定の本体)。

    本 file での判定 step:
    - [ ] LSP available なら `find_references` で逆方向 call site が 0 件か確認 (本 PR で touch する file 内の参照は除外)
    - [ ] LSP 失敗時は `grep -rn "<symbol>" --include='*.<ext>'` で best-effort、`open_concerns.scope_check_skipped` 必須
    - [ ] 残数 0 だが diff に削除が無い → blocker (この PR で削除すべき) または nits
    - [ ] 機械的削除 N>10 変更の場合 blocker、それ以外 suggestion (plan-judgment §11 は N>20 で Blocker、より厳しめなのは実 diff があるため)
5e. **Regression test 検証** (Problem 4、bug ticket のみ、Blocker for `reproducible` bug): `state.gather.bug_type == "reproducible"` の場合、diff に以下が含まれているか 1 項目ずつ確認:
    - [ ] 修正前は failing、修正後に green になる test (新規 test ファイル / 既存 test の新規 case 追加)
    - [ ] test 名 / 内容に bug の症状 (issue body の symptom 引用、または `Reproduction` セクションの再現手順) が反映されているか

    両方 [ ] checked なら OK、片方でも未 check なら blocker (`bug fix without regression test`)。

    bug_type 別の挙動:
    - `null` (feature/refactor) → 本セクション skip
    - `reproducible` → 上記 2 項目必須 (Blocker)
    - `intermittent` / `race_condition` → suggestion (再現困難 → AskUserQuestion で confirm 済前提)
    - `server_side` / `data_dependent` / `repro_unknown` → `open_concerns.bug_repro_unavailable` (= ローカル再現不能のため reviewer 検証必須を示すマーカー、`return-schemas.md` の「open_concerns の構造」section 参照) 必須
6. **規約準拠** (`repo-profile.conventions` + `directory_specific_conventions`): commit メッセージ style、branch 名 pattern、PR title prefix、spec ドキュメント (`spec_docs.required: true` なら作成 + `prohibited_content` 違反なし)。**触る dir が `repo-profile.directory_specific_conventions[].path` に該当する場合、その `rules[]` 遵守も判定** (R62、subdir CLAUDE.md で root と異なる規約があれば優先 — 例: `ios/CLAUDE.md` の「iOS test runs は --include-ios」)
7. **命名 / DRY / 可読性**: 意図を表す命名、ロジック重複なし、既存ヘルパー再利用、自明な what コメントなし、マジック定数に説明
8. **`human_owned` 抵触** (Blocker): `repo-profile.conventions.human_owned[].detection` にマッチする変更を含んでいたら必ず blocker (human_owned 検知 schema は `references/repo-profile-schema.md` 参照、gather/plan/code の 3 段階で判定 timing が異なる)
9. **Codegen 実行** (Blocker): `repo-profile.commands.codegen[].trigger` にマッチする変更があれば、対応する codegen 生成物が commit に含まれているか
10. **不要変更/散らかり**: issue 無関係な refactor、デバッグコード (`debugger`/`console.log`/`dump()`)、TODO/FIXME 残り
11. **Diff サイズ** (条件付き): 2000 行超 → `split_needed` (orchestrator 理解と人間レビューの限界)

## verdict と次の動作

| Verdict | 次の動作 |
|---|---|
| `ready` | implement-agent に `phase=push_and_pr` で再 dispatch |
| `needs_fix` | implement-agent に `phase=fix_blockers` + blockers を渡して再 dispatch (max 3 round) |
| `split_needed` | break (status: `stuck` with open_concerns "diff too large")、DRAFT PR は作成 |

## 出力

`<state_dir>/code-judgment-<sub_plan_index>-<round>.md`:

```markdown
# Code Judgment (sub-plan <N>, round <M>)

## Blockers (must fix before merge)
- [B1] <指摘> — 場所: `path/to/file:LINE` — 理由: ...

## Suggestions (should consider)
- [S1] ...

## Nits (optional)
- [N1] ...

## Verdict
<ready | needs_fix | split_needed>
```

ループ抑止: `references/judgment-conventions.md` 参照 (max 3 round、超過なら `stuck` で DRAFT PR を作る、`open_concerns` に残課題を書く)。
