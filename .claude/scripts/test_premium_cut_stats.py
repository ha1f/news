#!/usr/bin/env python3
"""premium_cut_stats.py のテスト (#628)。"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import premium_cut_stats as pcs  # noqa: E402

POST = """---
title: t
article_tags:
  - [セキュリティ, 開発]
  - [開発]
  - [社会]
---

リード。

1. [nginx に脆弱性11件](https://example.com/a) (はてブ)<br>
   読みどころ

2. [Swift の新しい並行処理](https://example.com/b) (Zenn)<br>
   読みどころ

3. [関係ない話](https://example.com/c) (HN・英語)<br>
   読みどころ
"""


class PremiumCutStatsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.posts = os.path.join(self.tmp.name, "_posts")
        self.cache = os.path.join(self.tmp.name, "cache")
        os.makedirs(self.posts)
        os.makedirs(self.cache)
        for name in ("2026-11-01-news.md", "2026-11-01-news-engineer.md"):
            with open(os.path.join(self.posts, name), "w", encoding="utf-8") as f:
                f.write(POST)
        with open(os.path.join(self.posts, "2026-10-01-news.md"), "w", encoding="utf-8") as f:
            f.write(POST.replace("example.com/a", "example.com/old"))
        self._orig = pcs.POSTS_DIR
        pcs.POSTS_DIR = self.posts

    def tearDown(self):
        pcs.POSTS_DIR = self._orig
        self.tmp.cleanup()

    def run_main(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = pcs.main(argv)
        return code, out.getvalue()

    def row(self, text, cut):
        return next(line for line in text.splitlines() if line.startswith(f"| {cut} "))

    def test_iter_posts_maps_labels(self):
        items = list(pcs.iter_posts("2026-11-01", "2026-11-01"))
        self.assertEqual(len(items), 6)
        self.assertEqual({x[4] for x in items}, {"hatena", "zenn", "hackernews"})

    def test_posts_counts_unique_urls_and_slots(self):
        code, out = self.run_main(["posts", "--since", "2026-11-01", "--until", "2026-11-01"])
        self.assertEqual(code, 0)
        self.assertIn("1 日、掲載枠 6・異なる URL 3", out)
        # 2 フィードに同じ URL が載ると、異なる URL は 1・掲載枠は 2
        self.assertIn("| 1（1.0） | 2（2.0） |", self.row(out, "security"))
        self.assertIn("hatena(要許諾) 1", self.row(out, "security"))

    def test_pool_overlap_with_published(self):
        data = {"source_id": "zenn", "fetched_at": "2026-11-05T16:00:00+09:00", "items": [
            {"title": "nginx vulnerability", "url": "https://example.com/a",
             "published_at": "2026-11-05T10:00:00+09:00"},
            {"title": "New zero-day exploited", "url": "https://example.com/new",
             "published_at": "2026-11-05T12:00:00+09:00"},
            {"title": "Old breach report", "url": "https://example.com/new2",
             "published_at": "2026-11-01T12:00:00+09:00"},
        ]}
        with open(os.path.join(self.cache, "zenn-x.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        code, out = self.run_main(["pool", "--cache-dir", self.cache])
        self.assertEqual(code, 0)
        # 当たる 3・うち公開済み 1・未公開 2・うち直近24時間 1
        self.assertIn("| security | 3 | 1（33%） | 2 | 1 |", out)

    def test_posts_counts_article_tags(self):
        _code, out = self.run_main(["posts", "--since", "2026-11-01", "--until", "2026-11-01"])
        self.assertIn("1（1.0）[セキュリティ]", self.row(out, "security"))

    def test_pool_ignores_media_prefix_and_utm(self):
        data = {"source_id": "itmedia", "fetched_at": "2026-11-05T16:00:00+09:00", "items": [
            {"title": "[ITmedia Mobile] 充電器のセール", "url": "https://example.com/x",
             "published_at": "2026-11-05T10:00:00+09:00"},
            {"title": "nginx vulnerability", "url": "https://example.com/a?utm_source=feed",
             "published_at": "2026-11-05T10:00:00+09:00"},
        ]}
        with open(os.path.join(self.cache, "i.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        _code, out = self.run_main(["pool", "--cache-dir", self.cache])
        self.assertIn("| apple-mobile | 0 |", out)
        self.assertIn("| security | 1 | 1（100%） | 0 |", out)

    def test_pool_empty_cache_fails(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code, _out = self.run_main(["pool", "--cache-dir", self.cache])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
