#!/usr/bin/env python3
"""select_issues.py のユニットテスト"""
import unittest

from select_issues import build_candidates

COLLABORATORS = ["owner"]


def issue(number, title="タイトル", login="owner", labels=(), created="2026-09-01T00:00:00Z",
          assoc=None):
    data = {"number": number, "title": title, "user": {"login": login},
            "labels": list(labels), "created_at": created}
    if assoc is not None:
        data["author_association"] = assoc
    return data


def pull(number, body="", branch="feature", draft=False, labels=None):
    data = {"number": number, "body": body, "draft": draft,
            "head": {"ref": branch}}
    if labels is not None:  # MCP はラベルが無い PR でキー自体を返さない
        data["labels"] = labels
    return data


class TestTrust(unittest.TestCase):
    def test_author_association_wins_when_present(self):
        issues = [issue(1, assoc="OWNER", login="somebot")]
        _, _, backlog = build_candidates(issues, [], COLLABORATORS)
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_collaborator_list_fills_missing_association(self):
        _, _, backlog = build_candidates([issue(1)], [], COLLABORATORS)
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_non_collaborator_is_dropped(self):
        _, _, backlog = build_candidates([issue(1, login="renovate")], [],
                                         COLLABORATORS)
        self.assertEqual(backlog, [])

    def test_untrusted_association_is_dropped(self):
        issues = [issue(1, assoc="NONE", login="owner")]
        _, _, backlog = build_candidates(issues, [], COLLABORATORS)
        self.assertEqual(backlog, [])


class TestFilters(unittest.TestCase):
    def test_status_issue_is_separated(self):
        issues = [issue(1, title="📊 daily-loop status"), issue(2)]
        status, _, backlog = build_candidates(issues, [], COLLABORATORS)
        self.assertEqual(status, 1)
        self.assertEqual([e["number"] for e in backlog], [2])

    def test_hold_label_is_dropped(self):
        issues = [issue(1, labels=["hold"]), issue(2, labels=[{"name": "hold"}])]
        _, _, backlog = build_candidates(issues, [], COLLABORATORS)
        self.assertEqual(backlog, [])

    def test_pull_request_entries_are_skipped(self):
        issues = [dict(issue(1), pull_request={"url": "x"}), issue(2)]
        _, _, backlog = build_candidates(issues, [], COLLABORATORS)
        self.assertEqual([e["number"] for e in backlog], [2])


class TestLinking(unittest.TestCase):
    def test_closing_keyword_in_body_links(self):
        _, in_progress, backlog = build_candidates(
            [issue(1)], [pull(9, body="Closes #1")], COLLABORATORS)
        self.assertEqual([e["number"] for e in in_progress], [1])
        self.assertEqual(backlog, [])

    def test_branch_name_links(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pull(9, branch="feat/1-something")], COLLABORATORS)
        self.assertEqual([e["number"] for e in in_progress], [1])

    def test_same_issue_is_not_linked_twice(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pull(9, body="Closes #1", branch="feat/1-x")],
            COLLABORATORS)
        self.assertEqual(len(in_progress[0]["linked_open_prs"]), 1)

    def test_sorted_by_created_at(self):
        issues = [issue(2, created="2026-09-05T00:00:00Z"),
                  issue(1, created="2026-09-01T00:00:00Z")]
        _, _, backlog = build_candidates(issues, [], COLLABORATORS)
        self.assertEqual([e["number"] for e in backlog], [1, 2])


class TestPullRequestLabels(unittest.TestCase):
    """MCP は labels を文字列リストで返し、ラベルが無い PR ではキー自体が無い。
    gh CLI は dict のリスト。どちらでも hold を拾えること"""

    def test_string_labels(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pull(9, body="Closes #1", labels=["hold"])],
            COLLABORATORS)
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_dict_labels(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pull(9, body="Closes #1", labels=[{"name": "hold"}])],
            COLLABORATORS)
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_missing_labels_key(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pull(9, body="Closes #1")], COLLABORATORS)
        self.assertFalse(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_draft_is_carried_through(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pull(9, body="Closes #1", draft=True)], COLLABORATORS)
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["draft"])

    def test_labels_are_read_once_per_pr(self):
        # 内包表記が linked issue の数だけ回らないこと（2 issue を閉じる 1 PR）
        _, in_progress, _ = build_candidates(
            [issue(1), issue(2)],
            [pull(9, body="Closes #1\nCloses #2", labels=["hold"])],
            COLLABORATORS)
        self.assertEqual(
            [e["linked_open_prs"][0]["hold"] for e in in_progress], [True, True])


if __name__ == "__main__":
    unittest.main()
