#!/usr/bin/env python3
"""check_name_variants の検証 (#664)。"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_name_variants  # noqa: E402

# 期待値は表（names.md）から作らず直書きする。表から行が消えたら落ちてほしい
RULES = check_name_variants.compiled(check_name_variants.load_table())


def found(text):
    return [(v, c) for _, v, c in check_name_variants.find_variants(text, RULES)]


def post(title, body):
    return f"---\nlayout: post\ntitle: \"{title}\"\ntags: [AI]\n---\n\n{body}\n"


class TableTest(unittest.TestCase):
    def test_issue_examples_are_in_the_table(self):
        pairs = set(check_name_variants.load_table())
        self.assertIn(("アンソロピック", "Anthropic"), pairs)
        self.assertIn(("ファン氏", "フアン氏"), pairs)
        self.assertIn(("ファン CEO", "フアン CEO"), pairs)
        self.assertIn(("Nvidia", "NVIDIA"), pairs)

    def test_header_and_separator_rows_are_not_rules(self):
        variants = {v for v, _ in check_name_variants.load_table()}
        self.assertNotIn("揺れ", variants)
        self.assertNotIn("---", variants)

    def test_missing_table_exits_2(self):
        orig = check_name_variants.NAMES_MD
        check_name_variants.NAMES_MD = Path(tempfile.gettempdir()) / "no-such-names.md"
        try:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(check_name_variants.main(["--all"]), 2)
        finally:
            check_name_variants.NAMES_MD = orig


class FindTest(unittest.TestCase):
    def test_variants_in_title_lead_and_note(self):
        text = post(
            "アンソロピックが19日上場へ",
            "NVIDIA は3日続落。ファン氏の辞任から5日。\n\n"
            "1. [Nvidia、ファン CEO の後任を指名](https://example.com/a) (日経・会員限定)<br>\n"
            "   ジェンスン・ファン氏が率いた30年",
        )
        self.assertEqual(
            found(text),
            [
                ("アンソロピック", "Anthropic"),
                ("ファン氏", "フアン氏"),
                ("Nvidia", "NVIDIA"),
                ("ファン CEO", "フアン CEO"),
                ("ジェンスン・ファン", "ジェンスン・フアン"),
            ],
        )

    def test_canonical_forms_pass(self):
        text = post(
            "Anthropic が19日上場へ",
            "NVIDIA のフアン氏、フアン CEO、ジェンスン・フアン。Intel と Tesla。",
        )
        self.assertEqual(found(text), [])

    def test_katakana_inside_longer_word_is_not_counted(self):
        # 前後にカタカナが続く形（別の語の一部）は数えない
        self.assertEqual(found(post("見出し", "ニューテスラ型とインテルサット、ウーバーイーツ")), [])
        # 直後が漢字・英字・記号なら数える
        self.assertEqual(
            found(post("見出し", "インテル株、テスラ57%減益、サムスン電子")),
            [("インテル", "Intel"), ("テスラ", "Tesla"), ("サムスン", "Samsung")],
        )

    def test_latin_is_case_sensitive_and_word_bounded(self):
        self.assertEqual(found(post("見出し", "NVIDIA と nvidia と NvidiaX と xNvidia と Nvidia")), [("Nvidia", "NVIDIA")])

    def test_link_targets_and_code_are_ignored(self):
        text = post(
            "見出し",
            "1. [NVIDIA の話](https://example.com/Nvidia/アンソロピック) (TechCrunch・英語)<br>\n"
            "   `Nvidia` という表記の話",
        )
        self.assertEqual(found(text), [])

    def test_front_matter_other_than_title_is_ignored(self):
        text = "---\nlayout: post\ntitle: \"Anthropic\"\ndescription: \"アンソロピック\"\n---\n\n本文\n"
        self.assertEqual(found(text), [])

    def test_line_numbers(self):
        text = post("アンソロピック", "本文\n\nファン氏")
        lines = [n for n, _, _ in check_name_variants.find_variants(text, RULES)]
        self.assertEqual(lines, [3, 9])


class NormalizeTest(unittest.TestCase):
    def test_keeps_honorific(self):
        self.assertEqual(
            check_name_variants.normalize("ファン氏とファン CEO、アンソロピックと Nvidia", RULES),
            "フアン氏とフアン CEO、Anthropicと NVIDIA",
        )


class MainTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_main(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_name_variants.main(list(args))
        return code, out.getvalue()

    def test_exit_codes_and_output(self):
        bad = self.dir / "2026-11-17-news.md"
        bad.write_text(post("見出し", "アンソロピックの話"), encoding="utf-8")
        good = self.dir / "2026-11-17-news-engineer.md"
        good.write_text(post("見出し", "Anthropic の話"), encoding="utf-8")
        code, out = self.run_main(str(bad), str(good))
        self.assertEqual(code, 1)
        self.assertIn("NG 2026-11-17-news.md:7: 「アンソロピック」→「Anthropic」", out)
        self.assertIn("検査 2 件 / 表記の揺れ 1 件", out)
        code, out = self.run_main(str(good))
        self.assertEqual(code, 0)

    def test_missing_file_is_ng(self):
        code, out = self.run_main(str(self.dir / "nope.md"))
        self.assertEqual(code, 1)
        self.assertIn("ファイルがありません", out)


if __name__ == "__main__":
    unittest.main()
