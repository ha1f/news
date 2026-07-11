---
name: select-and-develop
description: "open issue から今日実装する対象を選定し、develop-issue スキルで実装を完走する。daily-loop の12時ステージ。"
---

# select-and-develop

今日実装する issue を選び、develop-issue で完走する。状態の持ち方と status issue コメントの形式は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う。

## 手順

1. `python3 .claude/skills/select-and-develop/scripts/select_issues.py` を実行する。collaborator 名義のみ・`hold` と status issue を除外済みの候補が、linked PR の有無で `in_progress` / `backlog` に分かれて返る（古い順）
2. 両方空なら status issue に「対象なし」を記録して終了する（subagent を起動しない）
3. 選定は候補の issue を読んで自分で判断する。優先順: `in_progress` で要対応のもの（linked PR に未対応のレビュー指摘・red CI・conflict がある）→ `backlog` から今日最も価値の高いもの（緊急を訴える issue を先に）。issue の履歴に同じアプローチの失敗が繰り返し見えるなど、これ以上自動で進めるべきでないと判断したら、着手せず `hold` + 理由コメントで人間に委ねる
4. Skill ツールで `develop-issue` を直列に実行する（上限 `max_develop_runs_per_day`）。2件目は、1件目の完了時点で残り時間内に完走できる規模のときだけ着手する。迷ったら1件で終える
5. 完走した issue の DRAFT PR を ready 化する（`gh pr ready`。15時のマージ候補になる）。完走できなかった PR は draft のまま残す

## 完了条件

- status issue に開始と終了の各1コメント（1行目 JSON、stage は `develop`。着手した issue / 作成した PR / hold にした issue を summary に）
- 最後に reflect-and-improve を実行する。振り返り対象はこのスキルの選定ロジックのみ（develop-issue 内部の学びは develop-issue 自身が反映済み）。作成した改善 PR も ready 化する
