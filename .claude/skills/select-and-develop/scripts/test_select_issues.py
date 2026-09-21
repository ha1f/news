#!/usr/bin/env python3
"""select_issues.py の純関数のユニットテスト。実行: python3 test_select_issues.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from select_issues import build_candidates, parse_guardrails, parse_link_header, with_page


def issue(number, title="t", assoc="OWNER", labels=(), created="2026-07-01T00:00:00Z",
          pr=False, login=None):
    data = {
        "number": number,
        "title": title,
        "labels": [{"name": name} for name in labels],
        "created_at": created,
    }
    if assoc is not None:
        data["author_association"] = assoc
    if login is not None:
        data["user"] = {"login": login}
    if pr:
        data["pull_request"] = {}
    return data


def pr(number, body="", draft=True, branch="feature", labels=None):
    data = {"number": number, "body": body, "draft": draft,
            "head": {"ref": branch}}
    if labels is not None:  # MCP はラベルが無い PR でキー自体を返さない
        data["labels"] = labels
    return data


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
                         [{"number": 10, "draft": True, "hold": False}])
        self.assertEqual([e["number"] for e in backlog], [2])

    def test_link_keywords_variants(self):
        issues = [issue(1), issue(2), issue(3)]
        prs = [pr(10, body="Fixes #1"), pr(11, body="Refs #2"), pr(12, body="resolved #3")]
        _, in_progress, _ = build_candidates(issues, prs)
        self.assertEqual([e["number"] for e in in_progress], [1, 2, 3])

    def test_bare_issue_number_does_not_link(self):
        # キーワードの無い「#1」は言及であってリンクではない
        _, in_progress, backlog = build_candidates(
            [issue(1)], [pr(10, body="関連: #1 の議論を参照")])
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_branch_name_links(self):
        for branch in ("feat/1-something", "1-something", "fix/1_something"):
            with self.subTest(branch=branch):
                _, in_progress, _ = build_candidates([issue(1)],
                                                     [pr(10, branch=branch)])
                self.assertEqual([e["number"] for e in in_progress], [1])

    def test_branch_without_issue_number_does_not_link(self):
        _, in_progress, backlog = build_candidates(
            [issue(1)], [pr(10, branch="improve/develop-loop-env")])
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_same_issue_is_not_linked_twice(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", branch="feat/1-x")])
        self.assertEqual(len(in_progress[0]["linked_open_prs"]), 1)

    def test_collaborators_fallback_when_author_association_missing(self):
        issues = [
            issue(1, assoc=None, login="owner-user"),
            issue(2, assoc=None, login="external-user"),
            issue(3, assoc=None, login="member-user"),
        ]
        _, _, backlog = build_candidates(issues, [],
                                         collaborators=["owner-user", "member-user"])
        self.assertEqual([e["number"] for e in backlog], [1, 3])

    def test_no_collaborators_no_assoc_is_fail_closed(self):
        issues = [issue(1, assoc=None, login="someone")]
        _, _, backlog = build_candidates(issues, [])
        self.assertEqual(backlog, [])

    def test_author_association_takes_precedence_over_collaborators(self):
        issues = [
            issue(1, assoc="NONE", login="owner-user"),
            issue(2, assoc="OWNER", login="unknown"),
        ]
        _, _, backlog = build_candidates(issues, [],
                                         collaborators=["owner-user"])
        self.assertEqual([e["number"] for e in backlog], [2])


class PullRequestLabelsTest(unittest.TestCase):
    """MCP は labels を文字列リストで返し、ラベルが無い PR ではキー自体が無い。
    gh CLI は dict のリスト。どちらでも hold を拾えること"""

    def test_string_labels(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", labels=["hold"])])
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_dict_labels(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", labels=[{"name": "hold"}])])
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_missing_labels_key(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1")])
        self.assertFalse(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_other_labels_do_not_set_hold(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", labels=["bug", "enhancement"])])
        self.assertFalse(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_hold_is_per_pr_not_shared(self):
        issues = [issue(1), issue(2)]
        prs = [pr(10, body="Closes #1", labels=["hold"]),
               pr(11, body="Closes #2", labels=[])]
        _, in_progress, _ = build_candidates(issues, prs)
        self.assertEqual([e["linked_open_prs"][0]["hold"] for e in in_progress],
                         [True, False])

    def test_one_pr_closing_two_issues_carries_hold_to_both(self):
        _, in_progress, _ = build_candidates(
            [issue(1), issue(2)],
            [pr(10, body="Closes #1\nCloses #2", labels=["hold"])])
        self.assertEqual([e["linked_open_prs"][0]["hold"] for e in in_progress],
                         [True, True])


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


class ParseLinkHeaderTest(unittest.TestCase):
    def test_extracts_rel_urls(self):
        header = ('<https://api.github.com/repositories/1/issues?page=2>; rel="next", '
                   '<https://api.github.com/repositories/1/issues?page=5>; rel="last"')
        links = parse_link_header(header)
        self.assertEqual(links["next"], "https://api.github.com/repositories/1/issues?page=2")
        self.assertEqual(links["last"], "https://api.github.com/repositories/1/issues?page=5")

    def test_empty_header_returns_empty_dict(self):
        self.assertEqual(parse_link_header(""), {})
        self.assertEqual(parse_link_header(None), {})


class WithPageTest(unittest.TestCase):
    def test_adds_page_param_when_absent(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&per_page=100"
        self.assertEqual(with_page(url, 2),
                         "https://api.github.com/repos/o/r/issues?state=open&per_page=100&page=2")

    def test_replaces_existing_page_param(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&page=2&per_page=100"
        self.assertEqual(with_page(url, 3),
                         "https://api.github.com/repos/o/r/issues?state=open&page=3&per_page=100")


if __name__ == "__main__":
    unittest.main()
