#!/usr/bin/env python3
"""check_source_hints.py のユニットテスト"""
import tempfile
import unittest
from pathlib import Path

from check_source_hints import (expected_text, items_of, malformed_lines_of,
                                resolve)

FRONT_MATTER = "---\nlayout: post\ntitle: \"test\"\ndate: 2026-09-19\n---\n"

BY_NAME = {
    "はてブ": [],
    "日経": ["会員限定"],
    "Nature": ["英語", "一部会員限定"],
    "TechCrunch": ["英語"],
}
BY_DOMAIN = {
    "b.hatena.ne.jp": ([], "はてブ"),
    "nikkei.com": (["会員限定"], "日経"),
    "nature.com": (["英語", "一部会員限定"], "Nature"),
    "techcrunch.com": (["英語"], "TechCrunch"),
}


def write_post(body: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(FRONT_MATTER + body)
    tmp.close()
    return Path(tmp.name)


class TestItemsOf(unittest.TestCase):
    def test_label_present(self):
        post = write_post(
            "1. [見出し](https://techcrunch.com/a) (TechCrunch・英語)<br>\n"
            "   読みどころ\n")
        self.assertEqual(
            list(items_of(post)),
            [("見出し", "https://techcrunch.com/a", "TechCrunch・英語")])

    def test_missing_label_is_reported_not_skipped(self):
        # ラベルを必須にした正規表現だと、この行は検査から静かに消える。
        # 「ソース表記が丸ごと無い」のは一番捕まえたいケースなので None で返す
        post = write_post("1. [見出し](https://techcrunch.com/a)<br>\n")
        self.assertEqual(
            list(items_of(post)),
            [("見出し", "https://techcrunch.com/a", None)])

    def test_label_after_url_with_parenthesis(self):
        # URL に ")" を含む項目でも、末尾のラベルは取れる
        post = write_post(
            "1. [見出し](https://en.wikipedia.org/wiki/Wax_(disambiguation)) "
            "(はてブ)<br>\n")
        titles = [(t, label) for t, _, label in items_of(post)]
        self.assertEqual(titles, [("見出し", "はてブ")])

    def test_item_without_br(self):
        post = write_post("1. [見出し](https://a.example) (はてブ)\n")
        self.assertEqual(
            list(items_of(post)), [("見出し", "https://a.example", "はてブ")])


class TestMalformedLinesOf(unittest.TestCase):
    def test_bold_link_warns(self):
        post = write_post("1. **[見出し](https://a.example)** (はてブ)<br>\n")
        self.assertEqual(
            list(malformed_lines_of(post)),
            ["1. **[見出し](https://a.example)** (はてブ)<br>"])

    def test_well_formed_item_does_not_warn(self):
        post = write_post("1. [見出し](https://a.example) (はてブ)<br>\n")
        self.assertEqual(list(malformed_lines_of(post)), [])

    def test_prose_line_does_not_warn(self):
        post = write_post("今日は良い天気です。\n")
        self.assertEqual(list(malformed_lines_of(post)), [])


class TestResolve(unittest.TestCase):
    def test_own_domain_matches_own_labels(self):
        self.assertEqual(
            resolve("https://techcrunch.com/a", "TechCrunch", BY_NAME, BY_DOMAIN),
            ["英語"])

    def test_www_prefix_is_ignored(self):
        self.assertEqual(
            resolve("https://www.nikkei.com/a", "日経", BY_NAME, BY_DOMAIN),
            ["会員限定"])

    def test_aggregator_takes_link_target_labels(self):
        # はてブ経由でも、リンク先が日経なら会員限定を出す（#327 の本体）
        self.assertEqual(
            resolve("https://www.nikkei.com/article/X/", "はてブ",
                    BY_NAME, BY_DOMAIN),
            ["会員限定"])

    def test_unknown_domain_falls_back_to_source(self):
        self.assertEqual(
            resolve("https://example.com/a", "はてブ", BY_NAME, BY_DOMAIN), [])

    def test_subdomain_matches(self):
        self.assertEqual(
            resolve("https://blogs.nature.com/a", "はてブ", BY_NAME, BY_DOMAIN),
            ["英語", "一部会員限定"])


class TestExpectedText(unittest.TestCase):
    def test_no_labels(self):
        self.assertEqual(expected_text("Publickey", []), "Publickey")

    def test_single_label(self):
        self.assertEqual(expected_text("TechCrunch", ["英語"]), "TechCrunch・英語")

    def test_two_labels_joined_with_slash(self):
        self.assertEqual(
            expected_text("Nature", ["英語", "一部会員限定"]),
            "Nature・英語/一部会員限定")


if __name__ == "__main__":
    unittest.main()
