# モデル世代ノート

モデル世代固有の挙動と API 仕様の変化。対象プロンプトが前提とする世代とのズレを見つけるために使う。時限情報はこのファイルに集約し、世代交代時はここだけ更新する（SKILL.md 本文は世代非依存）。

最終更新: 2026-07。現行世代: Claude 5 family (Fable 5 / Mythos 5)、Opus 4.8、Sonnet 5、Haiku 4.5。

## 世代を貫く傾向（4.5 → 5）

指示追従性が世代ごとに上がり、「強く言う」テクニック（強調・否定形の禁止指示など、SKILL.md Step 1 参照）が世代を追うごとに不要化・有害化している。世代交代は棚卸しの合図でもある: 旧世代向けに書かれたスキル・プロンプトは新世代には prescriptive すぎて品質を下げうるため、能力向上のたびに「この指示・ツール・ガードレールはまだ必要か」を再評価する（公式推奨）。

## API 仕様の変化（古いプロンプト・コードの診断に）

| 項目 | 旧 | 現行 |
|---|---|---|
| prefill（assistant 応答の事前入力） | 使用可 | Opus 4.6 以降で廃止（400 エラー）。structured outputs / system prompt / tool strict mode で代替 |
| extended thinking | `budget_tokens` 手動指定 | `effort` パラメータ（low / medium / high / xhigh / max、デフォルト high）。Opus 4.8+ で手動 budget は 400 エラー |
| sampling params（temperature / top_p / top_k） | 調整可 | Opus 4.8+ で非デフォルト値は 400 エラー。挙動制御はプロンプトで行う |

出典: https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8 / https://platform.claude.com/docs/en/build-with-claude/effort

## Claude 5 (Fable / Mythos) 向けの新パターン

出典: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

- **goal-oriented**: overplanning には「When you have enough information to act, act.」
- **checkpoint は 1 文の原則で**: 止まる条件は「破壊的・不可逆な操作、スコープ変更、本人しか知らない情報のときだけ確認する」で足り、パターン列挙は不要
- **progress claims の監査**: 「進捗報告の前に各主張をこのセッションの tool result と突き合わせる」で fabrication がほぼ消える（公式テスト）
- **memory system**: lessons のファイル記録・参照を指示すると長期実行が大幅に改善（1 ファイル 1 教訓 + 冒頭 1 行サマリ、重複は更新、誤りは削除）
- **subagent 積極派**: dispatch が増える方向。委譲が適切な条件（独立性）と非同期運用を明示する
- **reasoning の転記指示は禁物**: 「思考過程を回答に書き出せ」系の指示は reasoning_extraction refusal を誘発する。thinking blocks を読む設計に変える
- **境界の明示**: 頼まれていない修正には「問題の説明や質問のときは評価を報告して止まる。修正は求められてから」

## 4.5〜4.7 世代の注意（当該モデル向けプロンプトを見るとき）

- 4.6: subagent の過剰使用傾向 → 「単純なタスクは直接実行」の指示が有効
- 4.6/4.7: 「迷ったらツールを使え」が過剰呼び出しを招く
- effort 推奨: coding は Opus 4.7/4.8 で xhigh 開始、Sonnet 4.6 は medium 開始。Fable 5 は low でも旧世代の xhigh 相当以上
