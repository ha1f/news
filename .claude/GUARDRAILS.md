# daily-loop ガードレール

毎日の自動ループが従う上限と保護対象。各スキルのスクリプトがこの yaml ブロックを読む。ループ自身はこのファイルを変更しない（変更 PR は必ず人間がマージする）。

```yaml
max_new_issues_per_day: 3      # PdM の新規 issue 作成上限
open_issue_cap: 10             # open な daily-loop issue がこれを超えたらグルーミングのみ
max_develop_runs_per_day: 2    # develop-issue の実行上限
max_attempts_per_issue: 3      # 同一 issue への通算試行。超過で hold + needs-human
quiescence_minutes: 30         # マージ前に PR の最終 commit から置く時間
auto_merge_mode: dry-run       # dry-run（判定コメントのみ）| enabled（自動マージ）
protected_paths:               # 触れる PR は auto-merge 禁止 → needs-human
  - .claude/skills/review-and-merge/**
  - .github/workflows/**
  - .claude/GUARDRAILS.md
```

保護パスにこのファイル自身と review-and-merge が含まれるため、安全装置を緩める変更は必ず人間のマージを通る。

## 設計原則（ループを改善するときの憲法）

- 決定的な処理（抽出・フィルタ・分類・状態確認）はスクリプトに寄せ、LLM には判断だけさせる
- 各スキルは最小の高信号トークン集合に保ち、観測された失敗モードに対してのみ追記する
- 複雑さを増すのは、単純な解が不十分だと観測されたときだけ
- 対象が無い日は subagent を起動せず早期終了する
- スクリプトやガードレールは「モデルにできないこと」の仮定。定期的に見直し、不要になった足場は剥がす

status issue へのコメントは1行目を JSON にする（例: `{"stage": "develop", "phase": "end", "ok": true, "summary": "#26 実装 → PR #27"}`。stage は evaluate / develop / review）。スクリプトがこれを読んで前日の健全性を機械判定する。

一次ソース: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) / [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) / [Building effective agents](https://www.anthropic.com/research/building-effective-agents) / [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) / [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) / [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
