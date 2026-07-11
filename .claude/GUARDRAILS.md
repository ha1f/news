# daily-loop ガードレール

毎日の自動ループ（evaluate-and-triage / select-and-develop / review-and-merge）が従う上限と保護対象。ループ自身はこのファイルを変更しない（このファイルへの変更 PR は必ず人間がマージする）。

## 数値

| 項目 | 値 |
|---|---|
| PdM の新規 issue 作成 | 最大 3件/日 |
| open な daily-loop issue の上限（超えたら新規作成せずグルーミング） | 10件 |
| develop-issue の実行 | 最大 2件/日 |
| 同一 issue への develop-issue 通算試行（超過で hold + needs-human） | 3回 |
| マージ前の quiescence（PR の最終 commit からの経過時間） | 30分 |

## 保護パス（auto-merge 禁止 → needs-human を付与して人間に委ねる）

- `.claude/skills/review-and-merge/**`
- `.github/workflows/**`
- `.claude/GUARDRAILS.md`

## auto-merge モード

mode: dry-run

- `dry-run` — review-and-merge は判定コメントだけ残し、マージ・close・ready 化を実行しない
- `enabled` — 合格した PR を自動マージする
