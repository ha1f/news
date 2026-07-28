---
name: audit-and-adopt
description: "ループ自身の資産（スキル・ルール・ワークフロー・ドキュメント）を監査し、エコシステムの新機能やベストプラクティスを取り込む。daily-loop の週次ステージ（日曜11時）。「環境を監査して」でも使う。"
---

# audit-and-adopt

プロダクトでなく「ループ自身の環境」を改善対象にする週次ステージ。オーナーの指摘を待たずに、外部視点の批評とエコシステム追従を自動で回す。状態の持ち方と status issue コメントの形式は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う（stage は `audit`）。

日次の reflect-and-improve が拾うのは「その会話で観測された摩擦」。会話の外にある劣化 — マージ済み資産の陳腐化・エコシステムとの乖離・手順の形骸化 — はどのステージも見ていないため、ここが受け持つ。オーナーが指摘するはずだった水準の発見を人間なしで毎週出せていれば成功。

## 手順

3つのレンズを fresh context の subagent で回し、自分は PdM として取捨する:

1. **資産批評** — `.claude/` 配下と VISION.md / DESIGN.md / README.md から今週の対象を1〜2個選ぶ（前回監査の status 記録を見てローテーション、最終更新が古いものを優先）。外部の専門家として批評させる: 正確性・肥大化・日付つき事実の失効・pin したバージョンの乖離・公式ベストプラクティスとの差分
2. **エコシステム** — Claude Code の changelog（https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md）・公式 docs（https://code.claude.com/docs/）・公式スキル集（https://github.com/anthropics/skills）を確認させ、この repo が使っていない有用な新機能・取り込む価値のある外部スキルを採用判断つきで報告させる。判断の物差しは GUARDRAILS の設計原則と DESIGN.md（目新しさより整合を優先）
3. **プロセス監査** — 直近1週間のマージ済み PR が無ければ subagent を起動せず「該当なし」とする（早期終了の原則）。あれば、それらと status issue の記録を、各スキルが定める手順の痕跡（UI PR のスクショ確認コメント、複数案の検討記録、reflect の実施、issue の受け入れ条件との突合コメント）と照合させ、手順が守られなかった事例を挙げさせる。違反には「なぜ守られなかったか」の仮説（手順が重い・曖昧・知られていない）まで付けさせる。あわせて終了コメントの `tokens` を1週間分並べさせ、消費が伸び続けているステージがあれば原因（手順の肥大化・読み込むファイルの増加など）の仮説を付けさせる

取捨の基準: 観測された問題・確実な失効だけ拾い、推測的な改善は捨てる。軽微で確実な修正（バージョン更新・失効した記述の訂正）は直接 DRAFT PR にして ready 化する。判断が要るものは issue にする（書式・上限は evaluate-and-triage の新規 issue と同じ。上限は日単位で evaluate と共有なので、当日の作成済み件数を差し引く。cap 超過時は見送り、status 記録に残す）。ビジョン・フェーズに関わる提案は VISION.md の更新 PR。該当なしのレンズは無理に絞り出さず「該当なし」でよい。

## 完了条件

- 3レンズの結果がそれぞれ issue / PR / status 記録の「該当なし」のいずれかに落ちている
- status issue に開始と終了の各1コメント（1行目 JSON、stage は `audit`。選んだ監査対象と結果の要約を summary に）
- 最後に reflect-and-improve を実行し、作成した改善 PR を ready 化する（次の review run のレビュー対象になる）
