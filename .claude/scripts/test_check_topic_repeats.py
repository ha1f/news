#!/usr/bin/env python3
"""check_topic_repeats の検証 (#531)。"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_topic_repeats  # noqa: E402

REPO_POSTS = HERE.parents[1] / "_posts"


def post(*items):
    """items は (見出し, 読みどころ) の組。"""
    body = "---\nlayout: post\ntitle: \"見出し\"\n---\n\nリード。\n\n"
    for n, (title, note) in enumerate(items, 1):
        body += f"{n}. [{title}](https://example.com/{abs(hash(title))}) (ソース)<br>\n   {note}\n\n"
    return body


# 点数の分母を作る、よくある語だけの項目（「AI」「Claude」は珍しくない語として扱われる）
FILLER = [(f"AI の話題{n}号", f"Claude と AI についての一般的な話{n}。") for n in range(200)]


class RealPostsTest(unittest.TestCase):
    """#531 で見逃した実例が出ること。repo の _posts をそのまま読む。"""

    @classmethod
    def setUpClass(cls):
        cls.archive = check_topic_repeats.Archive(REPO_POSTS)

    def pairs(self, name):
        found = check_topic_repeats.repeats_of(REPO_POSTS / name, self.archive)
        return {(it["title"], prev_name[:10]) for it, prev_name, *_ in found}

    def test_2026_10_20_main(self):
        pairs = self.pairs("2026-10-20-news.md")
        self.assertIn(("Deno 開発元が Cloudflare に合流、Deno の開発は終了へ", "2026-10-10"), pairs)
        self.assertIn(("Claude が暗号規格 ECDSA の25年来の謎を解明", "2026-10-17"), pairs)

    def test_2026_10_08_main(self):
        self.assertIn(
            ("Google、10カ月ぶりの最上位AI「Gemini 4 Argon」", "2026-10-01"),
            self.pairs("2026-10-08-news.md"),
        )

    def test_2026_10_11_researcher(self):
        self.assertIn(
            ("OpenAI、安全性研究者3人を解雇　双方の主張が真っ向から対立", "2026-10-02"),
            self.pairs("2026-10-11-news-researcher.md"),
        )


class SyntheticTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.posts = Path(self._tmp.name) / "_posts"
        self.posts.mkdir()
        self.write("2026-09-20-news-designer.md", post(*FILLER))

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.posts / name
        path.write_text(text, encoding="utf-8")
        return path

    def check(self, path):
        archive = check_topic_repeats.Archive(self.posts)
        return check_topic_repeats.repeats_of(path, archive)

    def run_main(self, *paths):
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_topic_repeats.main([str(p) for p in paths])
        return code, out.getvalue()

    PREV = ("Zorblax が Quuxcorp に合流", "Zorblax の開発チームが Quuxcorp の実行基盤に移る。")
    AGAIN = ("Zorblax 開発元が Quuxcorp へ", "今後は Quuxcorp 側の実装に注力するという。")

    def test_same_feed_within_window(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(self.AGAIN))
        found = self.check(today)
        self.assertEqual(len(found), 1)
        it, prev_name, prev, score, shared = found[0]
        self.assertEqual(it["title"], self.AGAIN[0])
        self.assertEqual(prev_name, "2026-10-10-news.md")
        self.assertEqual(set(shared), {"zorblax", "quuxcorp"})

    def test_match_through_note(self):
        # 見出しどうしは重ならず、前回の読みどころの語でだけ重なる組（ECDSA の型）
        self.write("2026-10-17-news.md", post(("Claude が謎を解明", "NSA が示した Wexqort の値の由来。")))
        today = self.write("2026-10-20-news.md", post(("Claude が Wexqort の謎を解明", "NSA の数値の出どころ。")))
        self.assertEqual(len(self.check(today)), 1)

    def test_window_is_ten_days(self):
        self.write("2026-10-09-news.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(self.AGAIN))
        self.assertEqual(self.check(today), [])
        self.write("2026-10-10-news.md", post(self.PREV))
        self.assertEqual(len(self.check(today)), 1)

    def test_other_feed_and_same_day_are_ignored(self):
        self.write("2026-10-15-news-engineer.md", post(self.PREV))
        self.write("2026-10-20-news-researcher.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(self.AGAIN))
        self.assertEqual(self.check(today), [])

    def test_profile_feed_matches_itself(self):
        self.write("2026-10-15-news-engineer.md", post(self.PREV))
        today = self.write("2026-10-20-news-engineer.md", post(self.AGAIN))
        self.assertEqual(len(self.check(today)), 1)

    def test_follow_up_is_skipped(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        today = self.write(
            "2026-10-20-news.md",
            post((self.AGAIN[0], "続報（10/10掲載）。開発の終了が決まった。")),
        )
        self.assertEqual(self.check(today), [])

    def test_common_terms_alone_do_not_match(self):
        self.write("2026-10-15-news.md", post(("Claude の新しい AI 機能", "AI の使い方が変わる。")))
        today = self.write("2026-10-20-news.md", post(("AI と Claude の別の話", "AI で何かができる。")))
        self.assertEqual(self.check(today), [])

    def test_main_exit_codes(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        clean = self.write("2026-10-19-news.md", post(("無関係な Plimbo の話", "Plimbo が出た。")))
        code, out = self.run_main(clean)
        self.assertEqual(code, 0, out)
        hit = self.write("2026-10-20-news.md", post(self.AGAIN))
        code, out = self.run_main(hit)
        self.assertEqual(code, 1)
        self.assertIn("要判断 2026-10-20-news.md:8 「Zorblax 開発元が Quuxcorp へ」", out)
        self.assertIn("前回 2026-10-10: 「Zorblax が Quuxcorp に合流」", out)
        code, _ = self.run_main(self.posts / "2026-10-21-news.md")
        self.assertEqual(code, 2)
        code, _ = self.run_main(self.write("notes.md", post(self.AGAIN)))
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
