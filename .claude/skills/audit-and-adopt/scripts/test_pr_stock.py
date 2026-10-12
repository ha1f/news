#!/usr/bin/env python3
"""pr_stock.py の純関数のユニットテスト。実行: python3 test_pr_stock.py"""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pr_stock import classify_stock

NOW = datetime(2026, 10, 18, 2, 0, tzinfo=timezone.utc)


def open_pr(number, draft=False, labels=(), body="", created="2026-10-01T00:00:00Z",
            updated="2026-10-17T00:00:00Z"):
    return {"number": number, "title": f"PR {number}", "draft": draft,
            "labels": list(labels), "body": body,
            "created_at": created, "updated_at": updated}


def merged_pr(number, title="", body="", merged="2026-10-12T06:00:00Z"):
    return {"number": number, "title": title or f"PR {number}", "body": body,
            "merged_at": merged}


def numbers(entries):
    return [e["number"] for e in entries]


class SupersededTest(unittest.TestCase):
    def test_body_names_predecessor(self):
        result = classify_stock(
            [open_pr(525, draft=True)],
            [merged_pr(527, body="Refs #522\n\nPR #525（review で要修正 → draft）の後継です。")],
            [], NOW)
        self.assertEqual(result["superseded"],
                         [{"number": 525, "title": "PR 525", "successor": 527, "idle_days": 1}])

    def test_title_names_predecessor(self):
        result = classify_stock(
            [open_pr(537, draft=True)],
            [merged_pr(541, title="feat(scripts): メール本文を生成する（PR #537 の後継、#528）")],
            [], NOW)
        self.assertEqual(numbers(result["superseded"]), [537])

    def test_plain_mention_is_not_succession(self):
        result = classify_stock(
            [open_pr(12, draft=True)],
            [merged_pr(30, body="PR #12 の指摘を参考にした。後継の作業は別 issue に回す")],
            [], NOW)
        self.assertEqual(result["superseded"], [])

    def test_hold_pr_stays_in_hold_with_successor(self):
        # hold は人間の預かりなので、後継がマージ済みでもループは閉じず判断リストに載せる
        result = classify_stock(
            [open_pr(443, labels=["hold"])],
            [merged_pr(501, body="PR #443（hold）の後継です")],
            [], NOW)
        self.assertEqual(result["superseded"], [])
        self.assertEqual(result["hold"][0]["superseded_by"], 501)


class StaleDraftTest(unittest.TestCase):
    def test_idle_draft_without_linked_issue(self):
        result = classify_stock(
            [open_pr(433, draft=True, updated="2026-09-27T00:00:00Z")], [], [], NOW)
        self.assertEqual(numbers(result["stale_drafts"]), [433])
        self.assertEqual(result["stale_drafts"][0]["idle_days"], 21)

    def test_recent_draft_is_left_alone(self):
        result = classify_stock(
            [open_pr(542, draft=True, updated="2026-10-14T00:00:00Z")], [], [], NOW)
        self.assertEqual(result["stale_drafts"], [])
        self.assertEqual(result["stalled"], [])

    def test_draft_whose_linked_issue_is_closed(self):
        result = classify_stock(
            [open_pr(400, draft=True, body="Closes #390", updated="2026-10-01T00:00:00Z")],
            [], [391], NOW)
        self.assertEqual(numbers(result["stale_drafts"]), [400])

    def test_draft_with_open_linked_issue_is_stalled(self):
        # linked issue が open なら develop が拾うはずの PR。止まっているのは手順の異常
        result = classify_stock(
            [open_pr(400, draft=True, body="Refs #390", updated="2026-10-01T00:00:00Z")],
            [], [390], NOW)
        self.assertEqual(result["stale_drafts"], [])
        self.assertEqual(result["stalled"][0]["number"], 400)
        self.assertEqual(result["stalled"][0]["linked_open_issues"], [390])


class HoldAndStalledTest(unittest.TestCase):
    def test_all_hold_prs_listed_oldest_first(self):
        result = classify_stock(
            [open_pr(501, labels=["hold"], created="2026-10-04T00:00:00Z"),
             open_pr(292, draft=True, labels=["hold"], created="2026-09-09T00:00:00Z",
                     updated="2026-09-09T00:00:00Z")],
            [], [], NOW)
        self.assertEqual(numbers(result["hold"]), [292, 501])
        self.assertEqual(result["hold"][0]["age_days"], 39)
        self.assertEqual(result["stale_drafts"], [])

    def test_idle_ready_pr_is_stalled(self):
        # ready で hold も無いのに動かない PR は review が拾えていない
        result = classify_stock(
            [open_pr(396, updated="2026-09-23T00:00:00Z")], [], [], NOW)
        self.assertEqual(numbers(result["stalled"]), [396])

    def test_summary_counts(self):
        result = classify_stock(
            [open_pr(1, draft=True), open_pr(2, labels=["hold"]), open_pr(3),
             open_pr(4, draft=True, labels=["hold"], created="2026-09-08T00:00:00Z")],
            [], [], NOW)
        self.assertEqual(result["summary"],
                         {"open": 4, "draft": 1, "hold": 2, "ready": 1, "oldest_age_days": 40})


if __name__ == "__main__":
    unittest.main()
