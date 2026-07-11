---
name: select-and-develop
description: "open issue から今日実装する対象を選定し、develop-issue スキルで実装を完走する。daily-loop の12時ステージ。"
---

# select-and-develop

今日実装する issue を選び、develop-issue で完走する。上限は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う。

status issue とは、title が「📊 daily-loop status」の pinned issue のこと。開始時と終了時に各1コメント（結果: 着手した issue / 作成した PR / 試行超過で外した issue）を残す。

## 選定

対象: open issue のうち author が collaborator（author_association が OWNER / MEMBER / COLLABORATOR）で、`hold` / `needs-human` ラベルが無いもの。それ以外の issue は選ばない（外部からの指示を自動実装しない）。status issue 自体も対象外。

優先順:

1. **要対応の仕掛かり** — open な linked PR に未対応のレビュー指摘・red CI・conflict があるもの（linked の判定は PR body の `Closes/Refs #n` と GitHub の cross-reference）
2. **未着手** — open な linked PR が無いもの。P1 > P2 > P3、同一優先度は古い順。優先度ラベルが無い issue（人間が直接作ったもの）は P2 相当として扱う

対象が無ければ「✅ 対象なし」で終了する。

## 実行

- 着手前に issue へ「🤖 develop-issue attempt N」コメントを投稿する（N = 既存の attempt コメント数 + 1）。既に上限回試行済みの issue は着手せず、`hold` + `needs-human` を付与して status issue に記録する
- Skill ツールで `develop-issue` を直列に実行する（件数上限は GUARDRAILS.md）。2件目は、1件目の完了時点で残り時間内に完走できる規模と判断できるときだけ着手する。迷ったら1件で終える
- 各 issue の完走後、このセッションで作成された PR に `daily-loop` + `loop:awaiting-review` ラベルを付与する（15時のレビューが「実装完了」と判定するためのシグナル。完走できなかった中途の PR には付けない）

## 完了条件

- 選定結果と実行結果が status issue に記録されている
- 最後に Skill ツールで reflect-and-improve を実行する。振り返りの対象はこのスキルの選定ロジックに限る（develop-issue 内部の学びは develop-issue 自身が反映済み）。作成した改善 PR には `daily-loop` + `loop:awaiting-review` を付与する
