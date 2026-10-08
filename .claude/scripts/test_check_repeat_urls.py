#!/usr/bin/env python3
"""check_repeat_urls / published_urls / fetch_feeds のサマリー除外の検証 (#40)。"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "skills" / "curate-news" / "scripts"))

import check_repeat_urls  # noqa: E402
import fetch_feeds  # noqa: E402
import published_urls  # noqa: E402
from feed_config import FeedConfig  # noqa: E402


def post(*items, note="新しい事実がある。"):
    body = "---\nlayout: post\ntitle: \"見出し\"\n---\n\nリード。\n\n"
    for n, url in enumerate(items, 1):
        body += f"{n}. [見出し{n}]({url}) (ソース)<br>\n   {note}\n\n"
    return body


class PostsDirTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.posts = Path(self._tmp.name) / "_posts"
        self.posts.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.posts / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_check(self, *paths):
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_repeat_urls.main([str(p) for p in paths])
        return code, out.getvalue()


class TestCheckRepeatUrls(PostsDirTestCase):
    def test_url_from_an_earlier_day_fails(self):
        self.write("2026-10-07-news-designer.md", post("https://techcrunch.com/2026/10/06/pin/"))
        today = self.write("2026-10-08-news-designer.md",
                           post("https://example.com/new", "https://techcrunch.com/2026/10/06/pin/"))
        code, out = self.run_check(today)
        self.assertEqual(code, 1)
        self.assertIn("2026-10-08-news-designer.md:11", out)
        self.assertIn("初出 2026-10-07 2026-10-07-news-designer.md", out)
        self.assertIn("既出 URL 1 件", out)

    def test_window_is_not_limited_to_seven_days(self):
        self.write("2026-08-01-news.md", post("https://www.publickey1.jp/blog/26/vite.html"))
        today = self.write("2026-10-08-news.md", post("https://www.publickey1.jp/blog/26/vite.html"))
        code, _ = self.run_check(today)
        self.assertEqual(code, 1)

    def test_other_profile_on_an_earlier_day_counts(self):
        self.write("2026-10-02-news.md", post("https://www.publickey1.jp/blog/26/spanner.html"))
        today = self.write("2026-10-08-news-engineer.md", post("https://www.publickey1.jp/blog/26/spanner.html"))
        code, _ = self.run_check(today)
        self.assertEqual(code, 1)

    def test_same_day_other_profile_is_not_a_repeat(self):
        self.write("2026-10-08-news.md", post("https://example.com/a"))
        today = self.write("2026-10-08-news-engineer.md", post("https://example.com/a"))
        code, out = self.run_check(today)
        self.assertEqual(code, 0, out)

    def test_later_day_is_not_a_repeat(self):
        self.write("2026-10-09-news.md", post("https://example.com/a"))
        today = self.write("2026-10-08-news.md", post("https://example.com/a"))
        code, out = self.run_check(today)
        self.assertEqual(code, 0, out)

    def test_follow_up_with_a_different_url_passes(self):
        self.write("2026-10-06-news.md", post("https://example.com/announce"))
        today = self.write("2026-10-08-news.md",
                           post("https://example.com/analysis", note="続報（10/6掲載）。市場の反応が出た。"))
        code, out = self.run_check(today)
        self.assertEqual(code, 0, out)

    def test_follow_up_with_the_same_url_fails(self):
        self.write("2026-10-06-news.md", post("https://example.com/announce"))
        today = self.write("2026-10-08-news.md",
                           post("https://example.com/announce", note="続報（10/6掲載）。"))
        code, _ = self.run_check(today)
        self.assertEqual(code, 1)

    def test_notation_variants_match(self):
        self.write("2026-10-01-news.md", post("http://www.example.com/a/b/#top"))
        today = self.write("2026-10-08-news.md", post("https://example.com/a/b"))
        code, _ = self.run_check(today)
        self.assertEqual(code, 1)

    def test_query_distinguishes_articles(self):
        self.write("2026-10-01-news.md", post("https://example.com/?p=1"))
        today = self.write("2026-10-08-news.md", post("https://example.com/?p=2"))
        code, out = self.run_check(today)
        self.assertEqual(code, 0, out)

    def test_missing_file_fails(self):
        code, _ = self.run_check(self.posts / "2026-10-08-news.md")
        self.assertEqual(code, 1)


class TestPublishedUrls(PostsDirTestCase):
    def test_collect_keeps_the_first_appearance(self):
        self.write("2026-09-29-news-researcher.md", post("https://www.nature.com/articles/x"))
        self.write("2026-09-30-news-researcher.md", post("https://www.nature.com/articles/x"))
        got = published_urls.collect(date(2026, 10, 8), str(self.posts))
        self.assertEqual(got["nature.com/articles/x"], (date(2026, 9, 29), "2026-09-29-news-researcher.md"))

    def test_collect_ignores_links_outside_numbered_items(self):
        self.write("2026-10-01-news.md", "リードの [リンク](https://example.com/lead)。\n")
        self.assertEqual(published_urls.collect(date(2026, 10, 8), str(self.posts)), {})


class TestSummaryExcludesPublished(unittest.TestCase):
    def test_published_urls_are_hidden_from_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = os.path.join(tmp, "dummy-テスト.json")
            with open(cache, "w", encoding="utf-8") as f:
                json.dump({"items": [
                    {"title": "既出", "url": "https://www.example.com/old/"},
                    {"title": "新着", "url": "https://example.com/new"},
                ]}, f)
            feed = FeedConfig(source_id="dummy", category="テスト",
                              feed_url="https://example.com/feed", fmt="rss", ttl_minutes=60)
            published = {"example.com/old": (date(2026, 9, 1), "2026-09-01-news.md")}
            out = io.StringIO()
            with mock.patch.object(FeedConfig, "cache_path", new=cache), redirect_stdout(out):
                fetch_feeds.print_summary([feed], published)
        text = out.getvalue()
        self.assertIn("(1 items, 既出 1 件を除外)", text)
        self.assertIn("https://example.com/new", text)
        self.assertNotIn("https://www.example.com/old/", text)


if __name__ == "__main__":
    unittest.main()
