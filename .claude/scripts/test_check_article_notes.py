#!/usr/bin/env python3
"""check_article_notes.py のユニットテスト"""
import tempfile
import unittest
from pathlib import Path

from check_article_notes import (MIN_RESIDUE, items_of,
                                 malformed_lines_of, residue_of)

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
        self.assertEqual(list(items_of(post)), [("見出し", "ソース", "読みどころの文")])

    def test_note_missing_no_br(self):
        post = write_post("1. [見出し](https://example.com) (ソース)\n")
        self.assertEqual(list(items_of(post)), [("見出し", "ソース", "")])

    def test_double_br_is_empty_note(self):
        # <br><br> は目視上の空行だが、タグを除去しないと "<br>" という
        # 非空文字列が読みどころとして検出され、欠落を見逃す
        post = write_post(
            "1. [見出し](https://example.com) (ソース)<br><br>\n")
        self.assertEqual(list(items_of(post)), [("見出し", "ソース", "")])

    def test_trailing_br_in_note_is_stripped(self):
        post = write_post(
            "1. [見出し](https://example.com) (ソース)<br>\n"
            "  読みどころ<br>\n")
        self.assertEqual(list(items_of(post)), [("見出し", "ソース", "読みどころ")])

    def test_multiple_items(self):
        post = write_post(
            "1. [A](https://a.example) (ソース)<br>\n"
            "  読みどころA\n"
            "\n"
            "2. [B](https://b.example) (ソース)\n")
        self.assertEqual(
            list(items_of(post)),
            [("A", "ソース", "読みどころA"), ("B", "ソース", "")])


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


class TestResidueOf(unittest.TestCase):
    def test_meta_only_note_has_no_residue(self):
        # 出どころを述べるだけの読みどころは、差し引くと何も残らない
        self.assertLess(
            len(residue_of("Xcode 27.1ベータ、リリースノート公開", "HN・英語",
                           "Apple公式のリリースノートそのもの。原文で変更点を直接確認できる。")),
            MIN_RESIDUE)

    def test_aggregator_mention_only_has_no_residue(self):
        self.assertLess(
            len(residue_of("2系統の神経外胚葉前駆細胞が脳形成に寄与", "HN・英語",
                           "Hacker News経由で話題になった1本。")),
            MIN_RESIDUE)

    def test_substantive_note_keeps_residue(self):
        self.assertGreaterEqual(
            len(residue_of("「Unicode 18.0」公開、絵文字9種・17万文字収録に", "GIGAZINE",
                           "秦代の「小篆」や女真文字の追加など、新版の変更点を"
                           "文字数の内訳とともに確認できる。")),
            MIN_RESIDUE)

    def test_headline_restatement_is_not_residue(self):
        # 見出しの言い換えだけの読みどころは残らない（区切りがずれても 2 文字組で吸収する）
        self.assertLess(
            len(residue_of("富士通、純国産次世代CPU「FUJITSU-MONAKA」を発表", "日経",
                           "富士通の純国産次世代CPUの発表。")),
            MIN_RESIDUE)

    def test_source_name_in_note_is_not_residue(self):
        self.assertEqual(
            residue_of("見出し", "TechCrunch・英語", "TechCrunch"), set())


if __name__ == "__main__":
    unittest.main()
