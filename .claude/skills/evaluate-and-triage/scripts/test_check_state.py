#!/usr/bin/env python3
"""check_state.py の純関数のユニットテスト。実行: python3 test_check_state.py"""
import json
import sys
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_state
from check_state import (api_json, gh_json, parse_link_header, parse_status_records,
                         since_param, summarize_health, summarize_issues, with_page)


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

    def test_single_link(self):
        header = '<https://api.github.com/repositories/1/issues?page=2>; rel="next"'
        self.assertEqual(parse_link_header(header),
                         {"next": "https://api.github.com/repositories/1/issues?page=2"})


class WithPageTest(unittest.TestCase):
    def test_adds_page_param_when_absent(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&per_page=100"
        self.assertEqual(with_page(url, 2),
                         "https://api.github.com/repos/o/r/issues?state=open&per_page=100&page=2")

    def test_replaces_existing_page_param(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&page=2&per_page=100"
        self.assertEqual(with_page(url, 3),
                         "https://api.github.com/repos/o/r/issues?state=open&page=3&per_page=100")

    def test_no_query_string_yet(self):
        self.assertEqual(with_page("https://api.github.com/repos/o/r/pages", 2),
                         "https://api.github.com/repos/o/r/pages?page=2")


class SinceParamTest(unittest.TestCase):
    """`since` は URL エスケープの要らない UTC の Z 形式にする。

    `+09:00` を生で入れると `+` がスペース扱いになり、GitHub は 422 で弾かずに
    別の時刻として受け取る（実測でカットオフが16時間ずれ、evaluate が毎朝
    health の missing に落ちた）。"""

    JST = timezone(timedelta(hours=9))

    def test_is_utc_z_format_without_escapable_chars(self):
        now = datetime(2026, 9, 21, 12, 7, 31, 625372, tzinfo=self.JST)
        self.assertEqual(since_param(now), "2026-09-19T15:00:00Z")

    def test_never_emits_plus_or_microseconds(self):
        for hour in range(24):
            value = since_param(datetime(2026, 9, 21, hour, 30, 5, 1234, tzinfo=self.JST))
            self.assertNotIn("+", value)
            self.assertNotIn(".", value)
            self.assertTrue(value.endswith("Z"), value)

    def test_cutoff_is_previous_midnight_jst(self):
        # 前日 00:00 JST = 前々日 15:00 UTC
        now = datetime(2026, 9, 21, 23, 59, tzinfo=self.JST)
        self.assertEqual(since_param(now), "2026-09-19T15:00:00Z")


class FakeResponse:
    def __init__(self, payload, link=None):
        self._body = json.dumps(payload).encode()
        self.headers = {"Link": link} if link else {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code):
    return urllib.error.HTTPError("https://api.github.com/x", code, "boom", {},
                                  None)


class ApiJsonTest(unittest.TestCase):
    """バグ本体があった api_json のループと分岐を踏む。"""

    def call(self, path, responses, **kwargs):
        """responses を順に返す fake urlopen で api_json を回し、要求 URL を記録する。"""
        seen = []

        def fake_urlopen(request, timeout=None):
            seen.append(request.full_url)
            result = responses.pop(0)
            if isinstance(result, urllib.error.HTTPError):
                result.read = lambda: b"{}"
                raise result
            return result

        with mock.patch.object(check_state.urllib.request, "urlopen", fake_urlopen):
            return api_json(path, **kwargs), seen

    def test_follows_pages_by_number_not_link_url(self):
        # GitHub が返す next は /repositories/{id}/ 形式。proxy がこの形を 403 で弾くので
        # 辿ってはいけない（これを辿っていたのが修正前のバグ）
        link = ('<https://api.github.com/repositories/999/issues?page=2>; rel="next"')
        result, seen = self.call(
            "repos/o/r/issues?state=open&per_page=100",
            [FakeResponse([{"number": 1}], link), FakeResponse([{"number": 2}])])
        self.assertEqual(result, [{"number": 1}, {"number": 2}])
        self.assertEqual(seen, [
            "https://api.github.com/repos/o/r/issues?state=open&per_page=100",
            "https://api.github.com/repos/o/r/issues?state=open&per_page=100&page=2",
        ])
        for url in seen:
            self.assertNotIn("/repositories/", url)

    def test_stops_when_no_next_link(self):
        result, seen = self.call("repos/o/r/pulls", [FakeResponse([{"number": 1}])])
        self.assertEqual(result, [{"number": 1}])
        self.assertEqual(len(seen), 1)

    def test_paginate_false_ignores_next_link(self):
        link = '<https://api.github.com/repositories/999/x?page=2>; rel="next"'
        result, seen = self.call("repos/o/r/x", [FakeResponse([{"a": 1}], link)],
                                 paginate=False)
        self.assertEqual(result, [{"a": 1}])
        self.assertEqual(len(seen), 1)

    def test_dict_response_returned_as_is(self):
        result, _ = self.call("repos/o/r/pages", [FakeResponse({"html_url": "u"})])
        self.assertEqual(result, {"html_url": "u"})

    def test_ok_missing_swallows_listed_status(self):
        result, _ = self.call("repos/o/r/pages", [http_error(403)], ok_missing=(403,))
        self.assertIsNone(result)

    def test_ok_404_swallows_404(self):
        result, _ = self.call("repos/o/r/contents/x", [http_error(404)], ok_404=True)
        self.assertIsNone(result)

    def test_unlisted_status_raises(self):
        with self.assertRaises(RuntimeError):
            self.call("repos/o/r/pages", [http_error(403)])
        with self.assertRaises(RuntimeError):
            self.call("repos/o/r/x", [http_error(500)], ok_404=True, ok_missing=(403,))


class GhJsonTest(unittest.TestCase):
    """gh 経路でも ok_missing を受けて捨てない（REST 経路と挙動を揃える）。"""

    def run_with(self, stderr, returncode=1, **kwargs):
        completed = mock.Mock(returncode=returncode, stdout="{}", stderr=stderr)
        with mock.patch.object(check_state.subprocess, "run", return_value=completed):
            return gh_json("repos/o/r/pages", **kwargs)

    def test_ok_missing_swallows_403(self):
        self.assertIsNone(self.run_with("HTTP 403: Forbidden", ok_missing=(403,)))

    def test_ok_missing_does_not_swallow_other_errors(self):
        with self.assertRaises(RuntimeError):
            self.run_with("HTTP 500: Server Error", ok_missing=(403,))

    def test_still_raises_without_ok_missing(self):
        with self.assertRaises(RuntimeError):
            self.run_with("HTTP 403: Forbidden")


class ResolveRepoTest(unittest.TestCase):
    """origin の URL 表記ゆれから owner/repo を取り出す。"""

    def resolve(self, url):
        completed = mock.Mock(stdout=url + "\n")
        with mock.patch.object(check_state.subprocess, "run", return_value=completed):
            return check_state.resolve_repo()

    def test_https_with_and_without_git_suffix(self):
        self.assertEqual(self.resolve("https://github.com/ha1f/news.git"), ("ha1f", "news"))
        self.assertEqual(self.resolve("https://github.com/ha1f/news"), ("ha1f", "news"))

    def test_ssh_form(self):
        self.assertEqual(self.resolve("git@github.com:ha1f/news.git"), ("ha1f", "news"))

    def test_trailing_slash(self):
        self.assertEqual(self.resolve("https://github.com/ha1f/news/"), ("ha1f", "news"))

    def test_non_github_url_raises(self):
        with self.assertRaises(RuntimeError):
            self.resolve("https://example.com/foo")


if __name__ == "__main__":
    unittest.main()
