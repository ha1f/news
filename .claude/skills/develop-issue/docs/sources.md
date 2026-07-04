# 出典 / 公式一次ソース

skill 設計の根拠となる一次ソース。改修時に「なぜこの mandate / Phase 構成か」を遡る場合の出発点。skill 自体の作り方ガイド (命名規約 / フロントマター詳細 / progressive disclosure 解説) は公式 doc を直接参照。

姉妹 docs: [overview.md](./overview.md) / [phases.md](./phases.md) / [design-decisions.md](./design-decisions.md)

---

## Anthropic 公式 (skill 仕様の真)

| 用途 | リンク |
|---|---|
| Skill の思想 (Equipping Agents with Skills) | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| **Skill Authoring Best Practices** (実用ガイド、最厚) | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Agent Skills Overview (フロントマター仕様) | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| Claude Code: Extend Claude with skills (CC 固有機能 = `!`...`` ` / `disable-model-invocation` / `context: fork` 等) | https://code.claude.com/docs/en/skills |
| 公式 Skills レポジトリ (リファレンス実装集) | https://github.com/anthropics/skills |
| **`skill-creator` SKILL.md** (skill 作成プロセス自体のベストプラクティス) | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md |
| The Complete Guide to Building Skills (総合 PDF) | https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf |
| Agent Skills 標準 (オープン規格) | https://agentskills.io |

---

## 設計判断の根拠となった blog (D# と紐付け)

| D# | リンク | 何を根拠化したか |
|---|---|---|
| D4 | https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start | `repo-profile.codebase_map` / `noise_paths` / 階層 CLAUDE.md / LSP integration (large mono-repo での精度・効率) |

---

## Issue → 実装系の参考実装 (inspiration 源)

| リンク | メモ |
|---|---|
| https://github.com/troykelly/claude-skills | 51 skill 構成。「Issue 駆動 13 ステップ workflow」のカテゴリ分けが参考 (Issue & Project mgmt / Planning / Implementation / Code review) |
| https://shaharia.com/blog/github-issue-to-production-automated-claude-code/ | Issue → PR の 7 ステージ feedback loop。各 loop が別観点 (style / integration / best-practice) で検証 = generator≠evaluator 原則 (D1) の出典 |
| https://addyosmani.com/blog/agent-harness-engineering/ | Agent = Model + Harness。**Ratchet Pattern** (skill の全行は過去の特定失敗に紐づくべき) / **Working Backwards from Behavior** (存在理由が言えないなら削れ) / 「success is silent, failures are verbose」 |

---

## ローカル参考実装

```
~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator/
├── SKILL.md
├── agents/{grader,comparator,analyzer}.md   # eval サブエージェント
├── references/schemas.md                     # evals.json / grading.json JSON schema
└── scripts/aggregate_benchmark.py            # eval パイプライン
```

公式 `skill-creator` のフルテキスト。skill 改修時に「公式はどう書いてるか」を確認する基準点。

---

## 他 LLM の Skill 概念 (比較)

| リンク | メモ |
|---|---|
| https://github.com/google-gemini/gemini-skills | Google 側「Skill」概念。SDK 知識注入用で類似構造 |
| https://ai.google.dev/gemini-api/docs/coding-agents | Gemini の MCP + Skills 設計思想 |
