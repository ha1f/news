---
name: select-and-develop
description: "open issue から今日実装する対象を選定し、develop-issue スキルで実装を完走する。daily-loop の12時ステージ。"
---

# select-and-develop

今日実装する issue を選び、develop-issue で完走する。status issue コメントの形式は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う。

## 手順

1. `python3 .claude/skills/select-and-develop/scripts/select_issues.py` を実行する。フィルタ（collaborator 名義のみ・hold / needs-human と status issue を除外）と優先度ソート済みの候補が `in_progress` / `backlog` で返る
2. 両方空なら status issue に「対象なし」を記録して終了する（subagent を起動しない）
3. 選定順: `in_progress` のうち要対応のもの（linked PR に未対応のレビュー指摘・red CI・conflict がある）→ `backlog` の先頭から。`attempts` が `max_attempts_per_issue` に達した issue は着手せず `hold` + `needs-human` を付与する
4. 着手する issue に「🤖 develop-issue attempt N」コメントを投稿してから、Skill ツールで `develop-issue` を直列に実行する（上限 `max_develop_runs_per_day`）。2件目は、1件目の完了時点で残り時間内に完走できる規模のときだけ着手する。迷ったら1件で終える
5. 完走した issue の PR に `daily-loop` + `loop:awaiting-review` を付与する（15時のマージ候補になる条件。完走できなかった中途の PR には付けない）

## 完了条件

- status issue に開始と終了（着手した issue / 作成した PR / 試行超過で外した issue）の各1コメント
- 最後に reflect-and-improve を実行する。振り返り対象はこのスキルの選定ロジックのみ（develop-issue 内部の学びは develop-issue 自身が反映済み）。作成した PR に `daily-loop` + `loop:awaiting-review` を付与する
