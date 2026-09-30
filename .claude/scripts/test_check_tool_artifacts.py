#!/usr/bin/env python3
"""check_tool_artifacts.py のテスト。

要点は2つ。実際に main に入った形（本文最終行の `</content>`）を確実に落とせる
ことと、投稿が実際に使う書き方（行末の `<br>`、コードとして引用したタグ名）を
落とさないこと。後者を取り違えると、記事の話題そのもので CI が red になり、
検査が無視されるようになる。
"""
import tempfile
import unittest
from pathlib import Path

import check_tool_artifacts as c


def write(text):
    d = Path(tempfile.mkdtemp())
    p = d / "2026-09-24-news.md"
    p.write_text(text, encoding="utf-8")
    return p


FRONT = "---\nlayout: post\ntitle: \"テスト\"\n---\n\n"


class TestDetects(unittest.TestCase):
    def test_trailing_content_tag(self):
        """実際に混入した形。本文最終行に単独で `</content>`"""
        p = write(FRONT + "1. [記事](https://example.com) (はてブ)<br>\n   要約\n</content>\n")
        self.assertEqual([n for n, _ in c.problems_of(p)], [8])

    def test_invoke_and_parameter(self):
        p = write(FRONT + "</invoke>\n<parameter name=\"x\">\n")
        self.assertEqual([n for n, _ in c.problems_of(p)], [6, 7])

    def test_antml_namespace(self):
        p = write(FRONT + "本文 antml:invoke が残っている\n")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_tag_name_is_case_insensitive(self):
        """タグ名の大文字小文字で取りこぼさない（行の途中に置いて語彙側を試す）"""
        p = write(FRONT + "要約の途中に </CONTENT> が紛れた\n")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_tool_tag_mid_line(self):
        """行頭でなくても拾う（行全体がタグの規則だけに頼らない）"""
        p = write(FRONT + "要約の途中に </content> が紛れた\n")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_every_tool_tag_name_mid_line(self):
        """語彙の各名前が、行全体を占めていなくても効くこと。

        行の途中に置かないと「行全体がタグ」の規則が代わりに当たってしまい、
        語彙から名前を落としても検査が緑のまま通る（実測: この確認が無い状態で
        `invoke` と `parameter` を語彙から消してもテストが全て緑だった）。

        期待する名前はここに直書きする。`c.TOOL_TAG_NAMES` を回すと、名前を
        消した変更でテストの対象まで一緒に消えて緑のままになる（実測: 最初に
        そう書いて、2回目の差し戻し確認で気づいた）。
        """
        expected = ("invoke", "parameter", "function_calls", "function_results", "content")
        self.assertEqual(tuple(c.TOOL_TAG_NAMES), expected)
        for name in expected:
            for tag in (f"<{name}>", f"</{name}>", f"<{name} x=\"1\">"):
                with self.subTest(tag=tag):
                    p = write(FRONT + f"要約の途中に {tag} が紛れた\n")
                    self.assertEqual(len(c.problems_of(p)), 1, tag)

    def test_unknown_lone_tag(self):
        """語彙に無いタグでも、行全体を占めていれば拾う"""
        p = write(FRONT + "<some_future_tool_tag>\n")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_front_matter_is_checked_too(self):
        p = write("---\nlayout: post\ntitle: \"テスト\"\n</content>\n---\n\n本文\n")
        self.assertEqual([n for n, _ in c.problems_of(p)], [4])

    def test_one_report_per_line(self):
        """同じ行に複数の規則が当たっても報告は1件（直す箇所は1つ）"""
        p = write(FRONT + "</content>\n")
        self.assertEqual(len(c.problems_of(p)), 1)


class TestDoesNotDetect(unittest.TestCase):
    def test_clean_post(self):
        p = write(FRONT + "1. [記事](https://example.com) (はてブ)<br>\n   要約\n")
        self.assertEqual(c.problems_of(p), [])

    def test_br_at_end_of_line(self):
        """投稿が実際に使う唯一の HTML。4,042 個ある"""
        p = write(FRONT + "1. [記事](https://example.com) (はてブ)<br>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_lone_br_and_hr(self):
        p = write(FRONT + "<br>\n<hr>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_tag_name_quoted_as_inline_code(self):
        """`<usermedia>` のようにタグ名を話題にした記事を落とさない（実在する）"""
        p = write(FRONT + "1. [宣言的に権限を要求する `<usermedia>` 要素](https://e.com) (はてブ)<br>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_tool_tag_quoted_as_inline_code(self):
        """ツール語彙そのものを話題にした記事も、コードなら落とさない"""
        p = write(FRONT + "1. [`</content>` が混入する問題](https://e.com) (はてブ)<br>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_fenced_code_block(self):
        p = write(FRONT + "```\n</content>\n<invoke>\n```\n")
        self.assertEqual(c.problems_of(p), [])

    def test_tilde_fence(self):
        p = write(FRONT + "~~~\n</content>\n~~~\n")
        self.assertEqual(c.problems_of(p), [])

    def test_markdown_link_is_not_a_lone_tag(self):
        p = write(FRONT + "[リンク](https://example.com/a<b>c)\n")
        self.assertEqual(c.problems_of(p), [])


class TestStripCode(unittest.TestCase):
    def test_keeps_line_numbers(self):
        lines = c.strip_code("a\n```\nb\n```\nc\n")
        self.assertEqual(len(lines), 6)
        self.assertEqual(lines[0], "a")
        self.assertEqual(lines[2], "")
        self.assertEqual(lines[4], "c")

    def test_unclosed_fence_swallows_rest(self):
        """閉じられていないフェンスは末尾までコード扱い（本文として誤検知しない側に倒す）"""
        lines = c.strip_code("a\n```\n</content>\n")
        self.assertEqual(lines[2], "")

    def test_inline_code_keeps_length(self):
        """列位置がずれないよう、インラインコードは同じ長さの空白に潰す"""
        self.assertEqual(c.strip_code("x `<a>` y")[0], "x       y")


class TestMain(unittest.TestCase):
    def test_exit_code_on_clean(self):
        p = write(FRONT + "本文\n")
        self.assertEqual(c.main([str(p)]), 0)

    def test_exit_code_on_dirty(self):
        p = write(FRONT + "</content>\n")
        self.assertEqual(c.main([str(p)]), 1)

    def test_missing_file_is_failure(self):
        self.assertEqual(c.main(["_posts/does-not-exist.md"]), 1)

    def test_no_posts_is_failure(self):
        """対象0件を成功にしない（パスを間違えた実行が黙って通る）"""
        d = Path(tempfile.mkdtemp())
        cwd = Path.cwd()
        import os
        os.chdir(d)
        try:
            self.assertEqual(c.main([]), 1)
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
