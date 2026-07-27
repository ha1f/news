#!/usr/bin/env python3
"""check_state.py の純関数のユニットテスト。実行: python3 test_check_state.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_state import (assemble_output, load_profiles, parse_status_records,
                         summarize_health, summarize_issues)


def issue(number, title="t", labels=(), pr=False, bot=False):
    data = {"number": number, "title": title,
            "labels": [{"name": name} for name in labels],
            "user": {"type": "Bot" if bot else "User"}}
    if pr:
        data["pull_request"] = {}
    return data


def status_comment(stage, phase, created_at, ok=None):
    record = {"stage": stage, "phase": phase, "summary": "s"}
    if ok is not None:
        record["ok"] = ok
    return {"created_at": created_at, "body": json.dumps(record) + "\n詳細"}


class SummarizeIssuesTest(unittest.TestCase):
    def test_finds_status_issue_and_counts_open_issues(self):
        issues = [
            issue(25, title="📊 daily-loop status"),  # status → 数えない
            issue(26),
            issue(27, labels=["hold"]),
            issue(29, pr=True),  # PR → 数えない
            issue(30, title="Dependency Dashboard", bot=True),  # bot → 数えない
        ]
        status_issue, count = summarize_issues(issues)
        self.assertEqual(status_issue, 25)
        self.assertEqual(count, 2)


class HealthTest(unittest.TestCase):
    # today=2026-07-11 (JST) の前日 = 07-10。JST 10時 = UTC 01時
    def test_healthy_day(self):
        comments = [
            status_comment("evaluate", "start", "2026-07-10T01:00:00Z"),
            status_comment("evaluate", "end", "2026-07-10T01:20:00Z", ok=True),
            status_comment("develop", "start", "2026-07-10T03:00:00Z"),
            status_comment("develop", "end", "2026-07-10T04:30:00Z", ok=True),
            status_comment("review", "start", "2026-07-10T06:00:00Z"),
            status_comment("review", "end", "2026-07-10T06:40:00Z", ok=True),
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11")
        self.assertEqual(health["incomplete"], [])
        self.assertEqual(health["failed"], [])
        self.assertEqual(health["missing"], [])
        self.assertFalse(health["no_records"])

    def test_dead_session_detected_as_incomplete(self):
        comments = [
            status_comment("evaluate", "start", "2026-07-10T01:00:00Z"),
            # end が無い = セッション死亡
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11")
        self.assertEqual(health["incomplete"], ["evaluate"])
        # start があるので missing ではない。develop/review は無記録なので missing
        self.assertEqual(health["missing"], ["develop", "review"])

    def test_silently_dead_stage_detected_as_missing(self):
        # evaluate だけ無記録（trigger 停止など）で他は正常 → missing に出る
        comments = [
            status_comment("develop", "start", "2026-07-10T03:00:00Z"),
            status_comment("develop", "end", "2026-07-10T04:00:00Z", ok=True),
            status_comment("review", "start", "2026-07-10T06:00:00Z"),
            status_comment("review", "end", "2026-07-10T06:30:00Z", ok=True),
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11")
        self.assertEqual(health["missing"], ["evaluate"])
        self.assertEqual(health["incomplete"], [])
        self.assertFalse(health["no_records"])

    def test_failed_stage_and_no_records(self):
        comments = [
            status_comment("review", "start", "2026-07-10T06:00:00Z"),
            status_comment("review", "end", "2026-07-10T06:40:00Z", ok=False),
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11")
        self.assertEqual(health["failed"], ["review"])
        empty = summarize_health([], "2026-07-11")
        self.assertTrue(empty["no_records"])
        # 導入直後（全ステージ無記録）は missing を立てない
        self.assertEqual(empty["missing"], [])

    def test_ignores_other_days_and_non_json_comments(self):
        comments = [
            status_comment("evaluate", "start", "2026-07-09T01:00:00Z"),  # 前々日
            {"created_at": "2026-07-10T01:00:00Z", "body": "ただのメモ"},
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11")
        self.assertTrue(health["no_records"])

    def test_jst_date_boundary(self):
        # UTC 07-09T23:00 = JST 07-10 08:00 → 前日扱いになる
        comments = [status_comment("evaluate", "start", "2026-07-09T23:00:00Z")]
        health = summarize_health(parse_status_records(comments), "2026-07-11")
        self.assertFalse(health["no_records"])


class AssembleOutputTest(unittest.TestCase):
    PROFILES = [
        {"id": "owner", "post_slug": "news", "name": "既定", "base": "/", "default": True},
        {"id": "commuter", "post_slug": "commuter", "name": "通勤", "base": "/feeds/commuter/"},
    ]

    def assemble(self, posts_exist):
        return assemble_output(
            config={}, today="2026-07-11", profiles=self.PROFILES,
            posts_exist=posts_exist, pages=None, pages_build=None,
            prs=[], issues=[], comments=[])

    def test_all_feeds_published(self):
        result = self.assemble({"owner": True, "commuter": True})
        self.assertTrue(result["post_in_main"])
        self.assertEqual(result["missing_posts"], [])

    def test_partially_published_feed_is_reported(self):
        result = self.assemble({"owner": True, "commuter": False})
        self.assertFalse(result["post_in_main"])
        self.assertEqual(result["missing_posts"], ["commuter"])
        self.assertEqual(result["posts_in_main"], {"owner": True, "commuter": False})

    def test_unknown_profile_in_input_is_ignored(self):
        result = self.assemble({"owner": True, "commuter": True, "ghost": True})
        self.assertEqual(sorted(result["posts_in_main"]), ["commuter", "owner"])

    def test_profiles_are_passed_through_for_url_assembly(self):
        result = self.assemble({"owner": True, "commuter": True})
        self.assertEqual([p["base"] for p in result["profiles"]], ["/", "/feeds/commuter/"])


class RepositoryProfilesTest(unittest.TestCase):
    def test_bundled_profiles_json_is_loadable(self):
        profiles = load_profiles()
        self.assertTrue(all({"id", "post_slug", "name", "base"} <= set(p) for p in profiles))


if __name__ == "__main__":
    unittest.main()
