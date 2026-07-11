#!/usr/bin/env python3
"""select_issues.py の純関数のユニットテスト。実行: python3 test_select_issues.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_issues import build_candidates, parse_guardrails


def issue(number, title="t", assoc="OWNER", labels=(), created="2026-07-01T00:00:00Z", pr=False):
    data = {
        "number": number,
        "title": title,
        "author_association": assoc,
        "labels": [{"name": name} for name in labels],
        "created_at": created,
    }
    if pr:
        data["pull_request"] = {}
    return data


def pr(number, body="", draft=True):
    return {"number": number, "body": body, "draft": draft}


class BuildCandidatesTest(unittest.TestCase):
    def test_excludes_untrusted_hold_status_and_prs(self):
        issues = [
            issue(1, assoc="NONE"),
            issue(2, labels=["hold"]),
            issue(3, title="📊 daily-loop status"),
            issue(4, pr=True),
            issue(5),
        ]
        status, in_progress, backlog = build_candidates(issues, [])
        self.assertEqual(status, 3)
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [5])

    def test_sorted_oldest_first(self):
        issues = [
            issue(1, created="2026-07-03T00:00:00Z"),
            issue(2, created="2026-07-01T00:00:00Z"),
            issue(3, created="2026-07-02T00:00:00Z"),
        ]
        _, _, backlog = build_candidates(issues, [])
        self.assertEqual([e["number"] for e in backlog], [2, 3, 1])

    def test_linked_open_pr_moves_issue_to_in_progress(self):
        issues = [issue(1), issue(2)]
        prs = [pr(10, body="Closes #1", draft=True), pr(11, body="refs #99")]
        _, in_progress, backlog = build_candidates(issues, prs)
        self.assertEqual([e["number"] for e in in_progress], [1])
        self.assertEqual(in_progress[0]["linked_open_prs"],
                         [{"number": 10, "draft": True}])
        self.assertEqual([e["number"] for e in backlog], [2])

    def test_link_keywords_variants(self):
        issues = [issue(1), issue(2), issue(3)]
        prs = [pr(10, body="Fixes #1"), pr(11, body="Refs #2"), pr(12, body="resolved #3")]
        _, in_progress, _ = build_candidates(issues, prs)
        self.assertEqual([e["number"] for e in in_progress], [1, 2, 3])


class ParseGuardrailsTest(unittest.TestCase):
    def test_parses_yaml_block(self):
        text = (
            "# GUARDRAILS\n\n```yaml\n"
            "quiescence_minutes: 30\n"
            "auto_merge_mode: dry-run  # dry-run | enabled\n"
            "protected_paths:\n"
            "  - .github/workflows/**\n"
            "  - .claude/GUARDRAILS.md\n"
            "```\n本文\n"
        )
        config = parse_guardrails(text)
        self.assertEqual(config["quiescence_minutes"], 30)
        self.assertEqual(config["auto_merge_mode"], "dry-run")
        self.assertEqual(config["protected_paths"],
                         [".github/workflows/**", ".claude/GUARDRAILS.md"])


if __name__ == "__main__":
    unittest.main()
