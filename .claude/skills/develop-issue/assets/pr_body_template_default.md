<!--
Default PR body template used by implement-agent when the target repository
does not provide one at .github/PULL_REQUEST_TEMPLATE.md.

Placeholder markers in {{double_braces}} are filled in by implement-agent
before calling `gh pr create --body-file`.

Section design rationale:
- 「動機 / 前提 / 根拠 / 検討した代替案 / レビューで誤解されそうな観点」は user
  `~/.claude/rules/pr-writing.md` の 5 項目に基づく。diff から読めない判断と
  文脈を PR 本文で伝えるため必須セクション。
- 「Summary」「Test plan」「Local verification」「Gather Q&A」「Review trail」
  「Open concerns」「Related」は skill 内 judgment (pr-body-judgment.md §1, §3-§8,
  §10) で観測する artifact、互換維持のため残置。

Mode-aware "Related" section ({{related_section}} placeholder):
- `single` (sub-plan 1 個): "Closes #<issue>"
- `chained_in_memory` (sub-plan 複数 / in-memory only): "Part of #<issue> (N/M)"
- `chained_with_subissues` (sub-plan 複数 / sub-issue 化済): "Closes #<sub_issue>\nPart of #<parent_issue> (N/M)"
- `parallel_recursive` (recursive_split): "Closes #<sub_issue>\nPart of #<parent_issue>"

implement-agent Step 10.3 が `state.implement.mode` を Read してこのテンプレを mode 別に生成。
**`Closes #<元 issue>` を chained_in_memory mode で使うのは禁止** (PR merge 時に元 issue が auto-close され、残り兄弟 PR が orphan 化する)。
-->

## Summary
{{summary}}

## 動機
{{motivation}}

## 前提
{{context_summary}}

## 根拠
{{rationale_with_evidence}}

## 検討した代替案
{{alternatives_considered}}

## レビューで誤解されそうな観点
{{review_pitfalls}}

## Related
{{related_section}}
{{linear_link_line_optional}}

## Test plan
{{test_plan_items}}

## Local verification
{{local_verification_section}}

## Gather Q&A
{{qa_trail_summary_or_none}}

## Review trail
- Plan review: {{plan_verdict}} in {{plan_rounds}} round(s)
- Code review: {{code_verdict}} in {{code_rounds}} round(s)

## Open concerns
{{open_concerns_or_none}}

---

🤖 Generated with [Claude Code](https://claude.com/claude-code) via the `develop-issue` skill
