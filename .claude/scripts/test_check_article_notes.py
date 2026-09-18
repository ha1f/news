#!/usr/bin/env python3
"""check_article_notes.py のユニットテスト"""
import tempfile
import unittest
from pathlib import Path

from check_article_notes import items_of, malformed_lines_of

FRONT_MATTER = "---\nlayout: post\ntitle: \"test\"\ndate: 2026-09-18\n---\n"


def write_post(body: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(FRONT_MATTER + body)
    tmp.close()
    return Path(tmp.name)


class TestItemsOf(unittest.TestCase):
    def test_note_present(self):
        post = write_post(
            "1. [見出し](https://example.com) (ソース)<br>\n"
            "  読みどころの文\n")
        self.assertEqual(list(items_of(post)), [("見出し", "読みどころの文")])

    def test_note_missing_no_br(self):
        post = write_post("1. [見出し](https://example.com) (ソース)\n")
        self.assertEqual(list(items_of(post)), [("見出し", "")])

    def test_double_br_is_empty_note(self):
        # <br><br> は目視上の空行だが、タグを除去しないと "<br>" という
        # 非空文字列が読みどころとして検出され、欠落を見逃す
        post = write_post(
            "1. [見出し](https://example.com) (ソース)<br><br>\n")
        self.assertEqual(list(items_of(post)), [("見出し", "")])

    def test_trailing_br_in_note_is_stripped(self):
        post = write_post(
            "1. [見出し](https://example.com) (ソース)<br>\n"
            "  読みどころ<br>\n")
        self.assertEqual(list(items_of(post)), [("見出し", "読みどころ")])

    def test_multiple_items(self):
        post = write_post(
            "1. [A](https://a.example) (ソース)<br>\n"
            "  読みどころA\n"
            "\n"
            "2. [B](https://b.example) (ソース)\n")
        self.assertEqual(
            list(items_of(post)),
            [("A", "読みどころA"), ("B", "")])


class TestMalformedLinesOf(unittest.TestCase):
    def test_bold_link_warns(self):
        post = write_post("1. **[見出し](https://example.com)** (ソース)<br>\n")
        self.assertEqual(
            list(malformed_lines_of(post)),
            ["1. **[見出し](https://example.com)** (ソース)<br>"])

    def test_extra_space_after_number_warns(self):
        post = write_post("1.  [見出し](https://example.com) (ソース)<br>\n")
        self.assertEqual(
            list(malformed_lines_of(post)),
            ["1.  [見出し](https://example.com) (ソース)<br>"])

    def test_bullet_list_warns(self):
        post = write_post("- [見出し](https://example.com) (ソース)<br>\n")
        self.assertEqual(
            list(malformed_lines_of(post)),
            ["- [見出し](https://example.com) (ソース)<br>"])

    def test_well_formed_item_does_not_warn(self):
        post = write_post("1. [見出し](https://example.com) (ソース)<br>\n")
        self.assertEqual(list(malformed_lines_of(post)), [])

    def test_prose_line_does_not_warn(self):
        post = write_post("今日は良い天気です。\n")
        self.assertEqual(list(malformed_lines_of(post)), [])


if __name__ == "__main__":
    unittest.main()
