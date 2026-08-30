#!/usr/bin/env python3
"""check_protected_paths.py のユニットテスト"""
import unittest
from check_protected_paths import parse_guardrails, protected_hits


class TestProtectedHits(unittest.TestCase):
    PATTERNS = [
        ".claude/skills/review-and-merge/**",
        ".github/workflows/**",
        ".claude/GUARDRAILS.md",
    ]

    def test_exact_match(self):
        self.assertEqual(
            protected_hits([".claude/GUARDRAILS.md"], self.PATTERNS),
            [".claude/GUARDRAILS.md"],
        )

    def test_prefix_match(self):
        self.assertEqual(
            protected_hits([".github/workflows/pages.yml"], self.PATTERNS),
            [".github/workflows/pages.yml"],
        )

    def test_nested_prefix_match(self):
        hits = protected_hits(
            [".claude/skills/review-and-merge/scripts/classify_prs.py"],
            self.PATTERNS,
        )
        self.assertEqual(
            hits,
            [".claude/skills/review-and-merge/scripts/classify_prs.py"],
        )

    def test_no_match(self):
        self.assertEqual(
            protected_hits(["about.md", "README.md"], self.PATTERNS),
            [],
        )

    def test_develop_issue_not_protected(self):
        self.assertEqual(
            protected_hits(
                [".claude/skills/develop-issue/SKILL.md"],
                self.PATTERNS,
            ),
            [],
        )

    def test_mixed(self):
        files = ["about.md", ".claude/GUARDRAILS.md", ".github/workflows/ci.yml"]
        hits = protected_hits(files, self.PATTERNS)
        self.assertEqual(hits, [".claude/GUARDRAILS.md", ".github/workflows/ci.yml"])

    def test_dir_itself_matches_prefix(self):
        hits = protected_hits([".github/workflows"], self.PATTERNS)
        self.assertEqual(hits, [".github/workflows"])


class TestParseGuardrails(unittest.TestCase):
    def test_parse_protected_paths(self):
        text = """```yaml
max_new_issues_per_day: 3
protected_paths:
  - .claude/skills/review-and-merge/**
  - .github/workflows/**
  - .claude/GUARDRAILS.md
```"""
        config = parse_guardrails(text)
        self.assertEqual(config["max_new_issues_per_day"], 3)
        self.assertEqual(len(config["protected_paths"]), 3)
        self.assertIn(".claude/GUARDRAILS.md", config["protected_paths"])


if __name__ == "__main__":
    unittest.main()
