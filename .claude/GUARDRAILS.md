# daily-loop ガードレール

毎日の自動ループが従う上限と保護対象。各スキルのスクリプトがこの yaml ブロックを読む。ループ自身はこのファイルを変更しない（変更 PR は必ず人間がマージする）。

```yaml
max_new_issues_per_day: 3      # PdM の新規 issue 作成上限
open_issue_cap: 10             # open issue（status issue 除く）がこれを超えたらグルーミングのみ
quiescence_minutes: 30         # マージ前に PR の最終 commit から置く時間
auto_merge_mode: enabled       # dry-run（判定コメントのみ）| enabled（自動マージ）
protected_paths:               # 触れる PR は auto-merge 禁止 → hold を付けて人間に委ねる
  - .claude/skills/review-and-merge/**
  - .github/workflows/**
  - .claude/GUARDRAILS.md
```

保護パスにこのファイル自身と review-and-merge が含まれるため、安全装置を緩める変更は必ず人間のマージを通る。

## 状態の持ち方

GitHub ネイティブの状態だけで回す: PR の draft（作業中・触らない）/ ready（レビュー・マージ候補）、issue の open / closed、作者の author_association、linked PR、タイムスタンプ。専用ラベルは `hold`（自動処理を止めて人間が見る。人間・ループのどちらが付けてもよく、理由をコメントに書く）の1つだけ。優先度・進捗・完了をラベルやカウンタで管理しない。

status issue（📊 daily-loop status）へのコメントは1行目を JSON にする（例: `{"stage": "develop", "phase": "end", "ok": true, "summary": "#26 実装 → PR #27"}`。stage は evaluate / develop / review）。スクリプトがこれを読んで前日の健全性を機械判定する。

全アクションがオーナー名義のため GitHub 通知は発生しない。人間の対応が必要になったとき（緊急 issue の起票・保護パスへの hold・revert 実行）は、Slack ツールが使えればオーナーに DM で1通知する。

## コンテンツの権利ガードレール

配信する文章は「事実は自由、表現は保護」の原則で書く。見出し・リンクによる所在表示は検索サービスと同様に原則適法だが、要約は厚くするほど原文の翻案（著作権侵害）に近づく。価値は要約の詳しさではなく選定と導線で出す。

- リード・読みどころ・要約は事実と論点の抽出に限る。原文の構成・修辞をなぞる詳細要約や逐語訳はしない
- 記事本文・記事画像は転載せず、リンクで原文に誘導する
- ソースの利用規約（RSS の商用利用条件等）の整理は有料化前に人間が行う

## 設計原則（ループを改善するときの憲法）

- 決定的な処理（抽出・フィルタ・分類・状態確認）はスクリプトに寄せ、LLM には判断だけさせる
- スキルは誰の好みでも動く汎用の仕組みに保つ。特定ユーザの興味・好みはデータ（preferences.md 等）に置き、スキルやスクリプトに焼き込まない
- 状態は GitHub ネイティブなもので表し、専用のラベル・プロトコル・カウンタを増やさない
- 各スキルは最小の高信号トークン集合に保ち、観測された失敗モードに対してのみ追記する
- 複雑さを増すのは、単純な解が不十分だと観測されたときだけ
- 対象が無い日は subagent を起動せず早期終了する
- スクリプトやガードレールは「モデルにできないこと」の仮定。定期的に見直し、不要になった足場は剥がす

一次ソース: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) / [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) / [Building effective agents](https://www.anthropic.com/research/building-effective-agents) / [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) / [Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) / [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
