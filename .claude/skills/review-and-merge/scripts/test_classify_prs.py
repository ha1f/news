#!/usr/bin/env python3
"""classify_prs.py の純関数のユニットテスト。実行: python3 test_classify_prs.py"""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_prs import classify, protected_hits, version_bump_only

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)
CONFIG = {
    "quiescence_minutes": 30,
    "protected_paths": [".claude/skills/review-and-merge/**",
                        ".github/workflows/**", ".claude/GUARDRAILS.md"],
}
DIGEST_BUMP = """@@ -40,4 +40,4 @@
       - name: Deploy to GitHub Pages
         id: deployment
-        uses: actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128 # v5
+        uses: actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346 # v5
"""
LOGIC_CHANGE = """@@ -6,3 +6,3 @@
 permissions:
-  contents: read
+  contents: write
"""


def pr(number, draft=False, labels=(), files=("index.md",),
       last_commit="2026-07-11T10:00:00Z", body="", assoc="OWNER", author="ha1f",
       head_in_repo=None, patches=None):
    return {"number": number, "title": f"PR {number}", "draft": draft,
            "labels": list(labels), "files": list(files),
            "last_commit_at": last_commit, "body": body,
            "author_association": assoc, "author": author,
            "head_in_repo": head_in_repo, "patches": patches or {}}


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

    def test_head_in_repo_decides_trust_regardless_of_author_kind(self):
        # bot でも人間でも、この repo に branch を持てる名義は書き込み権限の証明
        prs = [
            pr(1, assoc="CONTRIBUTOR", author="renovate[bot]", head_in_repo=True),
            pr(2, assoc="OWNER", author="ha1f", head_in_repo=False),  # fork からの PR
        ]
        result = classify(prs, CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["merge_candidates"]], [1])
        self.assertEqual([p["number"] for p in result["external"]], [2])

    def test_author_association_is_fallback_when_head_unknown(self):
        prs = [pr(1, assoc="COLLABORATOR"), pr(2, assoc="CONTRIBUTOR")]
        result = classify(prs, CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["merge_candidates"]], [1])
        self.assertEqual([p["number"] for p in result["external"]], [2])

    def test_non_boolean_head_in_repo_falls_back_to_association(self):
        # MCP 経路で LLM が "false" や repo 名を入れても信頼に倒れない
        prs = [pr(1, assoc="CONTRIBUTOR", head_in_repo="false"),
               pr(2, assoc="CONTRIBUTOR", head_in_repo="ha1f/news"),
               pr(3, assoc="OWNER", head_in_repo="")]
        result = classify(prs, CONFIG, NOW)
        self.assertEqual([p["number"] for p in result["external"]], [1, 2])
        self.assertEqual([p["number"] for p in result["merge_candidates"]], [3])

    def test_guardrail_value_change_stays_protected(self):
        # 裸の整数の書き換え（quiescence を 0 にする等）はバージョン置換ではない
        patch = "@@ -8 +8 @@\n-quiescence_minutes: 30\n+quiescence_minutes: 0\n"
        result = classify([pr(1, files=[".claude/GUARDRAILS.md"],
                              patches={".claude/GUARDRAILS.md": patch})], CONFIG, NOW)
        self.assertEqual(result["protected"][0]["protected_files"], [".claude/GUARDRAILS.md"])

    def test_version_bump_in_protected_path_is_not_protected(self):
        renovate = pr(1, author="renovate[bot]", head_in_repo=True,
                      files=[".github/workflows/pages.yml"],
                      patches={".github/workflows/pages.yml": DIGEST_BUMP})
        result = classify([renovate], CONFIG, NOW)
        self.assertEqual(result["protected"], [])
        self.assertEqual(result["merge_candidates"][0]["protected_version_bumps"],
                         [".github/workflows/pages.yml"])

    def test_logic_change_in_protected_path_stays_protected_even_for_bot(self):
        renovate = pr(1, author="renovate[bot]", head_in_repo=True,
                      files=[".github/workflows/pages.yml"],
                      patches={".github/workflows/pages.yml": LOGIC_CHANGE})
        result = classify([renovate], CONFIG, NOW)
        self.assertEqual(result["protected"][0]["protected_files"],
                         [".github/workflows/pages.yml"])

    def test_protected_path_without_patch_stays_protected(self):
        result = classify([pr(1, files=[".github/workflows/pages.yml"])], CONFIG, NOW)
        self.assertEqual(len(result["protected"]), 1)


class VersionBumpOnlyTest(unittest.TestCase):
    def test_digest_and_semver_replacements(self):
        self.assertTrue(version_bump_only(DIGEST_BUMP))
        self.assertTrue(version_bump_only(
            "@@ -1 +1 @@\n-      PLAYWRIGHT_VERSION: 1.62.1\n+      PLAYWRIGHT_VERSION: 1.63.0\n"))
        self.assertTrue(version_bump_only("@@ -1 +1 @@\n-3.14.7\n+3.14.8\n"))

    def test_tag_to_digest_pin_and_major_tag_bump(self):
        self.assertTrue(version_bump_only(
            "@@ -1 +1 @@\n-        uses: actions/checkout@v4\n+        uses: actions/checkout@v5\n"))
        # pin（タグ→SHA + コメント）は置換を超えるので bump ではない → protected のまま
        self.assertFalse(version_bump_only(
            "@@ -1 +1 @@\n-        uses: actions/checkout@v4\n"
            "+        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v4\n"))

    def test_anything_else_is_not_a_bump(self):
        self.assertFalse(version_bump_only(LOGIC_CHANGE))
        self.assertFalse(version_bump_only("@@ -1 +1,2 @@\n-x: 1.0\n+x: 1.1\n+run: rm -rf /\n"))
        self.assertFalse(version_bump_only(""))
        self.assertFalse(version_bump_only(None))

    def test_bare_integer_changes_are_not_bumps(self):
        for patch in [
            "@@ -8 +8 @@\n-quiescence_minutes: 30\n+quiescence_minutes: 0\n",
            "@@ -1 +1 @@\n-  open_issue_cap: 10\n+  open_issue_cap: 999\n",
            "@@ -1 +1 @@\n-    - cron: '0 1 * * *'\n+    - cron: '0 23 * * *'\n",
            "@@ -1 +1 @@\n-    timeout-minutes: 5\n+    timeout-minutes: 500\n",
            "@@ -1 +1 @@\n-    parents[3]\n+    parents[0]\n",
            "@@ -1 +1 @@\n-[0-9a-f]{7,64}\n+[0-9a-f]{1,64}\n",
        ]:
            self.assertFalse(version_bump_only(patch), patch)

    def test_reorder_and_move_are_not_bumps(self):
        self.assertFalse(version_bump_only(
            "@@ -1,2 +1,2 @@\n-      - run: npm ci\n-      - run: npm test\n"
            "+      - run: npm test\n+      - run: npm ci\n"))
        self.assertFalse(version_bump_only(
            "@@ -10,3 +10,2 @@\n gate:\n-      - uses: ./.github/actions/deploy\n"
            "@@ -30,2 +29,3 @@\n open:\n+      - uses: ./.github/actions/deploy\n"))
        # 内容が `--` で始まる削除行（frontmatter 等）も数に入る
        self.assertFalse(version_bump_only(
            "@@ -1,2 +1 @@\n-PLAYWRIGHT_VERSION: 1.62.1\n---\n+PLAYWRIGHT_VERSION: 1.63.0\n"))
        self.assertFalse(version_bump_only(
            "@@ -1 +1 @@\n-        uses: actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128\n"
            "+        uses: evil/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128\n"))


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
