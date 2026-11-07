#!/usr/bin/env python3
"""count_shared_urls の検証 (#612)。"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import count_shared_urls  # noqa: E402


def post(*urls):
    body = "---\nlayout: post\ntitle: \"t\"\n---\n\nリード [リンク](https://lead.example/)。\n\n"
    for n, u in enumerate(urls, 1):
        body += f"{n}. [見出し{n}]({u}) (ソース)<br>\n   読みどころ [続報](https://note.example/)。\n\n"
    return body


class TestCountSharedUrls(unittest.TestCase):
    def test_counts_only_numbered_items_within_the_same_day(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "2026-11-01-news.md").write_text(post("https://a/", "https://b/", "https://c/"), encoding="utf-8")
            (p / "2026-11-01-news-engineer.md").write_text(post("https://a/", "https://d/"), encoding="utf-8")
            (p / "2026-11-01-news-designer.md").write_text(post("https://a/", "https://b/"), encoding="utf-8")
            # 別の日の同じ URL は数えない
            (p / "2026-11-02-news.md").write_text(post("https://a/"), encoding="utf-8")
            # news 以外の投稿は対象外
            (p / "2026-11-01-other.md").write_text(post("https://a/"), encoding="utf-8")

            days = count_shared_urls.collect(p, "2026-11-01", "2026-11-01")
            self.assertEqual(list(days), ["2026-11-01"])
            day = count_shared_urls.count_day(days["2026-11-01"])
            self.assertEqual(day["feeds"], 3)
            self.assertEqual(day["slots"], 7)
            self.assertEqual(day["distinct_urls"], 4)
            self.assertEqual(day["shared_urls"], 2)  # a（3本）と b（2本）
            self.assertEqual(day["saved_slots"], 3)
            self.assertEqual(day["shared_by_feed_count"], {2: 1, 3: 1})

    def test_duplicate_url_within_one_feed_is_one_feed(self):
        day = count_shared_urls.count_day({"main": ["https://a/", "https://a/"], "eng": ["https://b/"]})
        self.assertEqual(day["shared_urls"], 0)


if __name__ == "__main__":
    unittest.main()
