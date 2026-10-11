import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import render_email_body as r

SCRIPT = Path(__file__).parent / "render_email_body.py"
SAMPLE = """## ニュース (2026-10-11 07:00 JST)

Aが<b>Bを発表</b>した。要点は2つ。

1. [A、Bを発表](https://example.com/a?x=1&y=2) (TechCrunch・英語)<br>
   発表内容の要点。

2. [C社の決算](https://example.com/c) (日経・会員限定)<br>
   売上の内訳。
"""


class RenderTest(unittest.TestCase):
    def test_parse(self):
        d = r.parse(SAMPLE)
        self.assertEqual(len(d["items"]), 2)
        self.assertEqual(d["items"][0]["source"], "TechCrunch・英語")
        self.assertEqual(d["items"][1]["note"], "売上の内訳。")
        self.assertIn("要点は2つ", d["lead"])

    def test_html_escapes_and_links(self):
        h = r.render_html(r.parse(SAMPLE))
        self.assertIn("&lt;b&gt;Bを発表&lt;/b&gt;", h)
        self.assertNotIn("<b>", h)
        self.assertIn('href="https://example.com/a?x=1&amp;y=2"', h)

    def test_text(self):
        t = r.render_text(r.parse(SAMPLE))
        self.assertIn("1. A、Bを発表 (TechCrunch・英語)", t)
        self.assertIn("   https://example.com/c", t)

    def test_deterministic(self):
        d = r.parse(SAMPLE)
        self.assertEqual(r.render_html(d), r.render_html(r.parse(SAMPLE)))
        self.assertEqual(r.render_text(d), r.render_text(r.parse(SAMPLE)))

    def test_cli_writes_next_to_input(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "output" / "2026-10-11-abc.md"
            src.parent.mkdir()
            src.write_text(SAMPLE, encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(src)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue((src.parent / "2026-10-11-abc.html").exists())
            self.assertTrue((src.parent / "2026-10-11-abc.txt").exists())

    def test_refuses_input_outside_output(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "_posts" / "2026-10-11-x.md"
            src.parent.mkdir()
            src.write_text(SAMPLE, encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(src)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(sorted(x.name for x in src.parent.iterdir()), [src.name])

    def test_refuses_real_posts_dir(self):
        posts = sorted((Path(__file__).parents[2] / "_posts").glob("*.md"))
        if not posts:
            self.skipTest("no posts")
        before = sorted(x.name for x in posts[0].parent.iterdir())
        p = subprocess.run([sys.executable, str(SCRIPT), str(posts[0])], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(before, sorted(x.name for x in posts[0].parent.iterdir()))

    def test_refuses_out_dir_outside_output(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "output" / "in.md"
            src.parent.mkdir()
            src.write_text(SAMPLE, encoding="utf-8")
            for d in ("_site", "x"):
                p = subprocess.run([sys.executable, str(SCRIPT), str(src), "--out-dir", str(Path(t) / d)], capture_output=True, text=True)
                self.assertNotEqual(p.returncode, 0, d)
                self.assertFalse((Path(t) / d).exists())

    def test_ancestor_docs_dir_is_fine(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "docs" / "output" / "a.md"
            src.parent.mkdir(parents=True)
            src.write_text(SAMPLE, encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(src)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_url_with_paren_and_same_line_note(self):
        d = r.parse("## h\n\nlead\n\n1. [Foo (bar)](https://en.wikipedia.org/wiki/Foo_(bar)) (Wiki)<br>\n   要約A。\n\n2. [S](https://e.com/d) (S)<br>要約D\n")
        self.assertEqual([i["url"] for i in d["items"]], ["https://en.wikipedia.org/wiki/Foo_(bar)", "https://e.com/d"])
        self.assertEqual(d["items"][1]["note"], "要約D")
        self.assertEqual(d["lead"], "lead")

    def test_dropped_item_fails(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "output" / "in.md"
            src.parent.mkdir()
            src.write_text(SAMPLE + "\n3. 壊れた行\n", encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(src)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)

    def test_empty_input_fails(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "output" / "in.md"
            src.parent.mkdir()
            src.write_text("## x\n\nlead\n", encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), str(src)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)

    def test_default_output_dir_is_gitignored(self):
        # 出力（html/txt）が公開 repo に入らないこと: curate-news の output/ は gitignore 対象
        root = Path(__file__).parents[2]
        for ext in (".md", ".html", ".txt"):
            p = subprocess.run(
                ["git", "check-ignore", "-q", f".claude/skills/curate-news/output/2026-10-11-abc{ext}"],
                cwd=root,
            )
            self.assertEqual(p.returncode, 0, ext)


if __name__ == "__main__":
    unittest.main()
