#!/usr/bin/env python3
"""有料 run のソース絞り込み (#575) の検証。"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import commercial_filter
from feed_config import FeedConfig


def _write(d, source_id, body):
    with open(os.path.join(d, f"{source_id}.md"), "w", encoding="utf-8") as f:
        f.write(body)


def _feed(source_id, category="c"):
    return FeedConfig(source_id=source_id, category=category, feed_url="http://x", fmt="rss", ttl_minutes=60)


class CommercialFilterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_allowed_value(self):
        _write(self.d, "a", "- **商用利用（課金）**: 可\n")
        _write(self.d, "b", "- **商用利用（課金）**: 可（利用規約で明示）\n")
        self.assertTrue(commercial_filter.is_allowed("a", self.d))
        self.assertTrue(commercial_filter.is_allowed("b", self.d))

    def test_non_allowed_values(self):
        for v in ("不可（理由）", "要許諾", "要連絡（窓口）", "要判断", "規定なし（…）"):
            _write(self.d, "x", f"- **商用利用（課金）**: {v}\n")
            self.assertFalse(commercial_filter.is_allowed("x", self.d), v)

    def test_missing_or_unknown_is_excluded(self):
        _write(self.d, "noline", "- **AI利用**: 可\n")
        _write(self.d, "unknown", "- **商用利用（課金）**: 許諾済み\n")
        _write(self.d, "empty", "- **商用利用（課金）**: \n")
        self.assertFalse(commercial_filter.is_allowed("noline", self.d))
        self.assertFalse(commercial_filter.is_allowed("unknown", self.d))
        self.assertFalse(commercial_filter.is_allowed("empty", self.d))
        self.assertFalse(commercial_filter.is_allowed("nofile", self.d))

    def test_prefix_of_allowed_is_not_allowed(self):
        _write(self.d, "x", "- **商用利用（課金）**: 可否は要判断\n")
        self.assertFalse(commercial_filter.is_allowed("x", self.d))

    def test_filter_feeds(self):
        _write(self.d, "ok", "- **商用利用（課金）**: 可\n")
        _write(self.d, "ng", "- **商用利用（課金）**: 不可\n")
        kept, excluded = commercial_filter.filter_feeds(
            [_feed("ok", "1"), _feed("ok", "2"), _feed("ng", "1"), _feed("none")], self.d)
        self.assertEqual([(f.source_id, f.category) for f in kept], [("ok", "1"), ("ok", "2")])
        self.assertEqual(excluded, {"ng": "不可", "none": None})

    def test_zero_sources(self):
        _write(self.d, "ng", "- **商用利用（課金）**: 要許諾\n")
        kept, excluded = commercial_filter.filter_feeds([_feed("ng")], self.d)
        self.assertEqual(kept, [])
        self.assertEqual(excluded, {"ng": "要許諾"})


class PaidCliTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(HERE, "fetch_feeds.py"), *args],
                              capture_output=True, text=True)

    def test_paid_stops_with_zero_sources_on_current_definitions(self):
        # 2026-10-19 時点のソース定義には「可」が無い。値が更新されたらこの前提を見直す
        r = self.run_cli("--paid", "--list")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("0件", r.stderr)
        self.assertEqual(r.stdout.strip(), "")

    def test_default_list_is_unfiltered(self):
        r = self.run_cli("--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("hatena", r.stdout)


if __name__ == "__main__":
    unittest.main()
