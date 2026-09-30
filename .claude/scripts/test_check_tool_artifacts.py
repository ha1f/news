#!/usr/bin/env python3
"""check_tool_artifacts.py のテスト。

要点は2つ。実際に main に入った形（本文最終行の `</content>`）を確実に落とせる
ことと、投稿が実際に使う書き方（行末の `<br>`、コードとして引用したタグ名）を
落とさないこと。後者を取り違えると、記事の話題そのもので CI が red になり、
検査が無視されるようになる。
"""
import contextlib
import os
import tempfile
import unittest
from pathlib import Path

import check_tool_artifacts as c


@contextlib.contextmanager
def in_dir(path):
    """cwd を一時的に移す。例外で抜けても必ず戻す"""
    cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


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


    def test_escaped_html_entities(self):
        """`&lt;/content&gt;` は読者に `</content>` と見えるので同じ扱い"""
        p = write(FRONT + "要約の途中に &lt;/content&gt; が紛れた\n")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_truncated_tag_without_closing_bracket(self):
        """`>` を欠いた断片も混入（閉じを必須にすると見逃す）"""
        p = write(FRONT + "要約の途中に </content が紛れた\n")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_indented_unknown_lone_tag(self):
        """字下げされた未知タグも拾う（行頭固定にしない）"""
        p = write(FRONT + "   <some_future_tool_tag>\n")
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

    def test_backslash_escaped_angles(self):
        """`Option\\<NonZeroU8\\>` の書き方。この repo の投稿に実在する"""
        p = write(FRONT + "   Option\\<NonZeroU8\\>が1バイトに収まる仕組み\n")
        self.assertEqual(c.problems_of(p), [])

    def test_backslash_escaped_tool_tag_name(self):
        """語彙のタグ名でも、エスケープしてあれば記事の話題として通す"""
        p = write(FRONT + "9. [Atom の \\<content\\> 要素を再考する](https://e.com) (はてブ)<br>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_lone_autolink_url(self):
        """行全体が markdown の autolink。タグではない"""
        p = write(FRONT + "<https://example.com/spec>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_lone_autolink_mail(self):
        p = write(FRONT + "<info@example.com>\n")
        self.assertEqual(c.problems_of(p), [])

    def test_similar_word_is_not_a_tool_tag(self):
        """語彙に似た別語を拾わない（`\\b` が効いていること）"""
        p = write(FRONT + "要約の途中に <contents> や <parameters> がある\n")
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

    def test_missing_file_alongside_a_clean_one_is_failure(self):
        """欠損1件だけを渡すと「対象0件」側で exit 1 になり、欠損の扱いを固定できない"""
        clean = write(FRONT + "本文\n")
        self.assertEqual(c.main([str(clean), "_posts/does-not-exist.md"]), 1)

    def test_no_posts_is_failure(self):
        """対象0件を成功にしない（パスを間違えた実行が黙って通る）"""
        with in_dir(Path(tempfile.mkdtemp())):
            self.assertEqual(c.main([]), 1)

    def test_default_target_is_all_posts(self):
        """引数なしの既定が `_posts` 全件であること。

        このスクリプトの中心的な設計判断（他の検査は引数なし = 当日分）なので、
        既定が空や当日分に変わったら落ちるようにしておく。
        """
        d = Path(tempfile.mkdtemp())
        (d / "_posts").mkdir()
        (d / "_posts" / "2020-01-01-old.md").write_text(FRONT + "古い本文\n", encoding="utf-8")
        (d / "_posts" / "2020-01-02-old.md").write_text(FRONT + "</content>\n", encoding="utf-8")
        with in_dir(d):
            # 当日分だけを見る実装なら対象0件で 1、既定が空でも 1。全件を見るから 1
            self.assertEqual(c.main([]), 1)
            (d / "_posts" / "2020-01-02-old.md").write_text(FRONT + "本文\n", encoding="utf-8")
            # 2件とも clean になったら 0。対象0件の実装ならここで 1 のまま
            self.assertEqual(c.main([]), 0)

    def test_unknown_option_is_rejected(self):
        """`--al` のような打ち間違いが「引数なし = 全投稿」に化けない"""
        self.assertEqual(c.main(["--al"]), 2)


if __name__ == "__main__":
    unittest.main()
