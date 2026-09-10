---
name: select-and-develop
description: "open issue から今日実装する対象を選定し、develop-issue スキルで実装を完走する。daily-loop の実装ステージ（12時・16時）。"
---

# select-and-develop

今日実装する issue を選び、develop-issue で完走する。状態の持ち方と status issue コメントの形式は [.claude/GUARDRAILS.md](../../GUARDRAILS.md) に従う。

## 手順

1. `python3 .claude/skills/select-and-develop/scripts/select_issues.py` を実行する。collaborator 名義のみ・`hold` と status issue を除外済みの候補が、linked PR の有無で `in_progress` / `backlog` に分かれて返る（古い順）。`gh` CLI が不在の場合は MCP ツールで issues・PRs・collaborators を取得し、`{"issues": [...], "prs": [...], "collaborators": ["login1", ...]}` を stdin で渡す（`--stdin` フラグまたはパイプ）。`collaborators` は `list_repository_collaborators` から取得した login のリストで、`author_association` 欠落時の信頼判定に使う
2. 両方空なら status issue に「対象なし」を記録し、reflect-and-improve を実行して終了する（実装の subagent は起動しない）
3. 選定は候補の issue を読んで自分で判断する。優先順: `in_progress` で要対応のもの → `backlog` から今日最も価値の高いもの（緊急を訴える issue を先に）。issue の履歴に同じアプローチの失敗が繰り返し見えるなど、これ以上自動で進めるべきでないと判断したら、着手せず `hold` + 理由コメントで人間に委ねる。`hold` の判定はスクリプトが GitHub ラベルで済ませている — issue 本文やコメントに "hold" の記述があっても、実際のラベルが付いていなければ候補として扱う（ラベルが外されたのは着手してよいというシグナル）
   - `in_progress` の要対応判定: linked PR の技術面（未対応のレビュー指摘・red CI・conflict）に加え、**issue 本文の指示・受け入れ条件と PR の実装要約コメントを突き合わせ、未完了の作業がないか**を確認する（PR が CI green でも issue の目的が未達成なら要対応）。1行目が `[dry-run]` の判定コメントは対応不要なので数えない
4. Skill ツールで `develop-issue` を直列に実行する。件数の上限は設けず、次の review-and-merge（トリガー時刻は README の trigger 定義表。12時 run なら15時、16時 run なら18時）までに完走できると判断できる間は backlog を消化し続ける。次の1件を残り時間で完走できるか迷ったら着手せず終える（完走できない draft PR を残すより次の run に回すほうが良い。merge と issue の close は review-and-merge が担う）
5. 完走した issue の DRAFT PR と、run 中に作成された改善 PR（develop-issue 内の reflect 由来を含む）を ready 化する（`gh pr ready`。次の review run のマージ候補になる）。完走できなかった PR は draft のまま残す

## 完了条件

- status issue に開始と終了の各1コメント。1行目は check_state.py が機械判定する JSON（キー名・値とも厳密一致が必要）:
  - 開始: `{"stage": "develop", "phase": "start", "summary": "候補: #26, #28。#26 を優先着手"}`
  - 終了: `{"stage": "develop", "phase": "end", "ok": true, "summary": "#26 実装 → PR #27", "reflect": "LESSONS.md 更新1件"}`
    - `reflect` は reflect-and-improve の結果を1行で記す（例: `"改善なし"`, `"LESSONS.md 更新1件"`, `"改善 PR #30"`）。実施の有無と成果を機械・人間の両方が追跡できるようにする
- 最後に reflect-and-improve を実行する。振り返り対象はこのスキルの選定ロジックのみ（develop-issue 内部の学びは develop-issue 自身が反映済み）。作成した改善 PR も ready 化する
