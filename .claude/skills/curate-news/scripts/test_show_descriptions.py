#!/usr/bin/env python3
"""show_descriptions.py の純関数のユニットテスト。実行: python3 test_show_descriptions.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from show_descriptions import build_index, clean


class CleanTest(unittest.TestCase):
    def test_strips_tags_entities_and_whitespace(self):
        raw = "<p>深海の<b>昆布</b>&nbsp;について\n  解説</p>"
        self.assertEqual(clean(raw, 100), "深海の 昆布 について 解説")

    def test_truncates_with_ellipsis(self):
        self.assertEqual(clean("あいうえおかきくけこ", 5), "あいうえお…")

    def test_keeps_text_at_the_limit(self):
        self.assertEqual(clean("あいうえお", 5), "あいうえお")

    def test_empty_description(self):
        self.assertEqual(clean("", 100), "")
        self.assertEqual(clean(None, 100), "")


class BuildIndexTest(unittest.TestCase):
    CACHE = {
        "hatena-総合.json": {"items": [
            {"url": "https://example.com/a", "title": "A", "description": "a"},
            {"url": "https://example.com/b", "title": "B", "description": "b"},
        ]},
        "gigazine-全体.json": {"items": [
            {"url": "https://example.com/a", "title": "A（別ソース）", "description": "a2"},
        ]},
    }

    def test_indexes_by_url_with_cache_key(self):
        index = build_index(self.CACHE)
        self.assertEqual(sorted(index), ["https://example.com/a", "https://example.com/b"])
        self.assertEqual(index["https://example.com/b"]["cache_key"], "hatena-総合")

    def test_first_occurrence_wins_for_duplicated_url(self):
        index = build_index(self.CACHE)
        self.assertEqual(index["https://example.com/a"]["title"], "A")

    def test_ignores_items_without_url_and_empty_cache(self):
        index = build_index({"x.json": {"items": [{"title": "no url"}]}, "y.json": {}})
        self.assertEqual(index, {})


if __name__ == "__main__":
    unittest.main()
