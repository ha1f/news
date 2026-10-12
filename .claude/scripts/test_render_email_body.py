import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import render_email_body as r

SCRIPT = Path(__file__).parent / "render_email_body.py"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".claude" / "skills" / "curate-news" / "output"


def out_tmp():
    """gitignore 対象の curate-news/output/ の下に一時ディレクトリを作る（スクリプトはここしか受け付けない）。"""
    OUT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=OUT)


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
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
        with out_tmp() as t:
            src = Path(t) / "2026-10-11-abc.md"
            src.write_text(SAMPLE, encoding="utf-8")
            p = run(src)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue((Path(t) / "2026-10-11-abc.html").exists())
            self.assertTrue((Path(t) / "2026-10-11-abc.txt").exists())

    def test_cli_accepts_subdir_of_output(self):
        with out_tmp() as t:
            src = Path(t) / "in.md"
            src.write_text(SAMPLE, encoding="utf-8")
            p = run(src, "--out-dir", Path(t) / "mail")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue((Path(t) / "mail" / "in.html").exists())

    def test_refuses_input_in_dir_merely_named_output(self):
        # パスのどこかに `output` があるだけ（gitignore されない）では通さない
        with tempfile.TemporaryDirectory() as t:
            for d in ("output", "_posts/output", "docs/output"):
                src = Path(t) / d / "in.md"
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(SAMPLE, encoding="utf-8")
                p = run(src)
                self.assertNotEqual(p.returncode, 0, d)
                self.assertEqual(sorted(x.name for x in src.parent.iterdir() if x.is_file()), ["in.md"], d)

    def test_refuses_real_posts_dir(self):
        posts = sorted((ROOT / "_posts").glob("*.md"))
        if not posts:
            self.skipTest("no posts")
        before = sorted(x.name for x in posts[0].parent.iterdir())
        p = run(posts[0])
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(before, sorted(x.name for x in posts[0].parent.iterdir()))

    def test_refuses_out_dir_outside_curate_output(self):
        # review 指摘 (PR #537) の実例: repo 内の `output` という名前の公開されうる場所
        with out_tmp() as t:
            src = Path(t) / "in.md"
            src.write_text(SAMPLE, encoding="utf-8")
            with tempfile.TemporaryDirectory() as other:
                targets = [Path(other) / d for d in ("_site", "x", "output")]
                targets += [ROOT / "_posts" / "output", ROOT / "output", ROOT / "docs" / "output", ROOT / "assets" / "output"]
                for d in targets:
                    existed = d.exists()
                    p = run(src, "--out-dir", d)
                    self.assertNotEqual(p.returncode, 0, d)
                    self.assertEqual(d.exists(), existed, d)
                    self.assertFalse((d / "in.html").exists(), d)

    def test_refuses_dotdot_escape(self):
        with out_tmp() as t:
            src = Path(t) / "in.md"
            src.write_text(SAMPLE, encoding="utf-8")
            p = run(src, "--out-dir", OUT / ".." / "output-x")
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse((OUT.parent / "output-x").exists())

    def test_url_with_paren_and_same_line_note(self):
        d = r.parse("## h\n\nlead\n\n1. [Foo (bar)](https://en.wikipedia.org/wiki/Foo_(bar)) (Wiki)<br>\n   要約A。\n\n2. [S](https://e.com/d) (S)<br>要約D\n")
        self.assertEqual([i["url"] for i in d["items"]], ["https://en.wikipedia.org/wiki/Foo_(bar)", "https://e.com/d"])
        self.assertEqual(d["items"][1]["note"], "要約D")
        self.assertEqual(d["lead"], "lead")

    def test_dropped_item_fails(self):
        with out_tmp() as t:
            src = Path(t) / "in.md"
            src.write_text(SAMPLE + "\n3. 壊れた行\n", encoding="utf-8")
            p = run(src)
            self.assertNotEqual(p.returncode, 0)

    def test_empty_input_fails(self):
        with out_tmp() as t:
            src = Path(t) / "in.md"
            src.write_text("## x\n\nlead\n", encoding="utf-8")
            p = run(src)
            self.assertNotEqual(p.returncode, 0)

    def test_default_output_dir_is_gitignored(self):
        # 出力（html/txt）が公開 repo に入らないこと: curate-news の output/ は gitignore 対象
        for rel in ("2026-10-11-abc.md", "2026-10-11-abc.html", "2026-10-11-abc.txt", "mail/x.html"):
            p = subprocess.run(
                ["git", "check-ignore", "-q", f".claude/skills/curate-news/output/{rel}"],
                cwd=ROOT,
            )
            self.assertEqual(p.returncode, 0, rel)


if __name__ == "__main__":
    unittest.main()
