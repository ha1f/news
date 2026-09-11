#!/usr/bin/env python3
"""classify_prs.py の純関数のユニットテスト。実行: python3 test_classify_prs.py"""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_prs import classify, protected_hits

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)
CONFIG = {
    "quiescence_minutes": 30,
    "protected_paths": [".claude/skills/review-and-merge/**",
                        ".github/workflows/**", ".claude/GUARDRAILS.md"],
    "trusted_bots": ["renovate[bot]"],
}


def pr(number, draft=False, labels=(), files=("index.md",),
       last_commit="2026-07-11T10:00:00Z", body="", assoc="OWNER", author="ha1f"):
    return {"number": number, "title": f"PR {number}", "draft": draft,
            "labels": list(labels), "files": list(files),
            "last_commit_at": last_commit, "body": body,
            "author_association": assoc, "author": author}


class ClassifyTest(unittest.TestCase):
    def test_draft_hold_external_are_separated(self):
        prs = [
            pr(1, draft=True),
            pr(2, labels=["hold"]),
            pr(3, assoc="NONE"),
        ]
        result = classify(prs, CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["drafts"]], [1])
        self.assertEqual([p["number"] for p in result["hold"]], [2])
        self.assertEqual([p["number"] for p in result["external"]], [3])
        self.assertEqual(result["merge_candidates"], [])

    def test_quiescence_gate(self):
        result = classify([pr(1, last_commit="2026-07-11T11:45:00Z")], CONFIG, NOW)
        self.assertIn("quiescence", result["not_ready"][0]["reason"])
        self.assertEqual(result["merge_candidates"], [])

    def test_protected_path_detected(self):
        result = classify([pr(1, files=[".github/workflows/pages.yml"])], CONFIG, NOW)
        self.assertEqual(result["protected"][0]["protected_files"],
                         [".github/workflows/pages.yml"])
        self.assertEqual(result["merge_candidates"], [])

    def test_ready_pr_becomes_candidate_with_linked_issues(self):
        result = classify([pr(1, body="Closes #26\nRefs #30")], CONFIG, NOW)
        self.assertEqual(result["merge_candidates"][0]["linked_issues"], [26, 30])
        self.assertFalse(result["merge_candidates"][0]["bot"])

    def test_trusted_bot_is_candidate_without_protected_path_gate(self):
        # Renovate の PR は CONTRIBUTOR 名義で workflow を触るが、trusted_bots なら候補になる
        renovate = pr(1, assoc="CONTRIBUTOR", author="renovate[bot]",
                      files=[".github/workflows/pages.yml"])
        result = classify([renovate], CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["merge_candidates"]], [1])
        self.assertTrue(result["merge_candidates"][0]["bot"])
        self.assertEqual(result["protected"], [])
        self.assertEqual(result["external"], [])

    def test_trusted_bot_still_waits_for_quiescence_and_respects_hold(self):
        prs = [
            pr(1, assoc="CONTRIBUTOR", author="renovate[bot]",
               last_commit="2026-07-11T11:45:00Z"),
            pr(2, assoc="CONTRIBUTOR", author="renovate[bot]", labels=["hold"]),
        ]
        result = classify(prs, CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["not_ready"]], [1])
        self.assertEqual([p["number"] for p in result["hold"]], [2])

    def test_unlisted_bot_stays_external(self):
        other = pr(1, assoc="CONTRIBUTOR", author="dependabot[bot]")
        result = classify([other], CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["external"]], [1])
        self.assertFalse(result["external"][0]["bot"])

    def test_missing_trusted_bots_config_treats_bots_as_external(self):
        config = {k: v for k, v in CONFIG.items() if k != "trusted_bots"}
        renovate = pr(1, assoc="CONTRIBUTOR", author="renovate[bot]")
        result = classify([renovate], config, NOW)
        self.assertEqual([p["number"] for p in result["external"]], [1])


class ProtectedHitsTest(unittest.TestCase):
    def test_glob_and_exact(self):
        files = [".claude/GUARDRAILS.md", ".claude/skills/review-and-merge/SKILL.md",
                 ".claude/skills/review-and-merge/scripts/classify_prs.py", "index.md"]
        hits = protected_hits(files, CONFIG["protected_paths"])
        self.assertEqual(hits, [".claude/GUARDRAILS.md",
                                ".claude/skills/review-and-merge/SKILL.md",
                                ".claude/skills/review-and-merge/scripts/classify_prs.py"])

    def test_prefix_is_not_substring_match(self):
        hits = protected_hits([".github/workflows-old/x.yml"], [".github/workflows/**"])
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
