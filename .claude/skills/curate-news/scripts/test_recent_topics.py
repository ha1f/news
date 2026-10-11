import contextlib
import io
import os
import sys
import tempfile
import unittest
from datetime import date
from unittest import mock

import recent_topics as mod

_REAL_POSTS_DIR = mod._POSTS_DIR


def _post(directory, name, *headlines):
    body = "\n".join(
        f"{i}. [{h}](https://example.com/{abs(hash((name, h)))}) (Src)<br>\n   読みどころ"
        for i, h in enumerate(headlines, 1)
    )
    with open(os.path.join(directory, name), "w", encoding="utf-8") as f:
        f.write("---\ntitle: t\n---\n\n" + body + "\n")


def _run(*argv):
    out = io.StringIO()
    with mock.patch.object(sys, "argv", ["recent_topics.py", *argv]), contextlib.redirect_stdout(out):
        mod.main()
    return out.getvalue()


class RecentTopicsWindowTest(unittest.TestCase):
    """直近3日は全フィード、10日前までは自分のフィードだけを照合に出す (#531)"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.posts = os.path.join(tmp.name, "_posts")
        self.output = os.path.join(tmp.name, "output")
        self.profiles = os.path.join(tmp.name, "profiles")
        for d in (self.posts, self.output, self.profiles):
            os.mkdir(d)
        with open(os.path.join(self.profiles, "researcher.md"), "w", encoding="utf-8") as f:
            f.write("researcher\n")
        for attr, value in (("_POSTS_DIR", self.posts), ("_OUTPUT_DIR", self.output),
                            ("_PROFILES_DIR", self.profiles)):
            patcher = mock.patch.object(mod, attr, value)
            patcher.start()
            self.addCleanup(patcher.stop)

        # 今日 = 10/11。直近3日 = 10/08〜10/10、自分のフィード = 10/01〜10/07
        _post(self.posts, "2026-10-11-news.md", "今日のメイン")
        _post(self.posts, "2026-10-10-news.md", "昨日のメイン")
        _post(self.posts, "2026-10-09-news-researcher.md", "2日前の研究者")
        _post(self.posts, "2026-10-08-news-designer.md", "3日前のデザイナー")
        _post(self.posts, "2026-10-07-news.md", "4日前のメイン")
        _post(self.posts, "2026-10-07-news-designer.md", "4日前のデザイナー")
        _post(self.posts, "2026-10-02-news-researcher.md", "9日前の研究者")
        _post(self.posts, "2026-10-01-news.md", "10日前のメイン")
        _post(self.posts, "2026-09-30-news.md", "11日前のメイン")
        _post(self.output, "2026-10-05-news-abcd1234.md", "6日前の自分の出力")
        _post(self.output, "2026-10-05-news-ffff0000.md", "6日前の他人の出力")

    def test_default_profile(self):
        out = _run("--hash", "abcd1234", "--today", "2026-10-11")
        for h in ("昨日のメイン", "2日前の研究者", "3日前のデザイナー",
                  "4日前のメイン", "6日前の自分の出力", "10日前のメイン"):
            self.assertIn(h, out)
        for h in ("今日のメイン", "4日前のデザイナー", "9日前の研究者",
                  "11日前のメイン", "6日前の他人の出力"):
            self.assertNotIn(h, out)

    def test_named_profile(self):
        out = _run("--profile", "researcher", "--hash", "abcd1234", "--today", "2026-10-11")
        for h in ("昨日のメイン", "3日前のデザイナー", "9日前の研究者", "6日前の自分の出力"):
            self.assertIn(h, out)
        for h in ("4日前のメイン", "10日前のメイン", "4日前のデザイナー"):
            self.assertNotIn(h, out)

    def test_profile_path_inside_profiles_dir(self):
        path = os.path.join(self.profiles, "researcher.md")
        out = _run("--profile", path, "--hash", "abcd1234", "--today", "2026-10-11")
        self.assertIn("9日前の研究者", out)
        self.assertNotIn("4日前のメイン", out)

    def test_profile_outside_repo_uses_only_output_for_older_days(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("private\n")
        self.addCleanup(os.unlink, f.name)
        out = _run("--profile", f.name, "--hash", "abcd1234", "--today", "2026-10-11")
        self.assertIn("昨日のメイン", out)
        self.assertIn("6日前の自分の出力", out)
        for h in ("4日前のメイン", "9日前の研究者", "10日前のメイン"):
            self.assertNotIn(h, out)

    def test_own_days_not_above_days_adds_nothing(self):
        out = _run("--hash", "abcd1234", "--today", "2026-10-11", "--own-days", "3")
        self.assertIn("3日前のデザイナー", out)
        self.assertNotIn("4日前のメイン", out)

    def test_older_dates_are_labelled(self):
        out = _run("--hash", "abcd1234", "--today", "2026-10-11")
        self.assertIn("## 2026-10-08\n", out)
        self.assertIn("## 2026-10-07（このフィードのみ）\n", out)
        self.assertIn("## 2026-10-01（このフィードのみ）\n", out)
        self.assertLess(out.index("## 2026-10-10"), out.index("## 2026-10-07"))


class RecentTopicsRealPostsTest(unittest.TestCase):
    """#531 の実例2件で、前回の掲載が照合の入力に入ること"""

    def _skip_unless(self, *names):
        for name in names:
            if not os.path.exists(os.path.join(_REAL_POSTS_DIR, name)):
                self.skipTest(f"{name} が無い")

    def test_main_gemini_4_argon(self):
        self._skip_unless("2026-10-01-news.md")
        out = _run("--hash", "none0000", "--today", "2026-10-08")
        self.assertIn("## 2026-10-01（このフィードのみ）", out)
        self.assertIn("Google、新モデル「Gemini 4 Argon」を公開", out)

    def test_researcher_openai_safety_researchers(self):
        self._skip_unless("2026-10-02-news-researcher.md")
        out = _run("--profile", "researcher", "--hash", "none0000", "--today", "2026-10-11")
        self.assertIn("OpenAI、安全性研究者3人と契約を打ち切り", out)


if __name__ == "__main__":
    unittest.main()
