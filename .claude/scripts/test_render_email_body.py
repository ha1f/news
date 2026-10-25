import json
import shutil
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


FOOTER = {"sender": "運営<者>", "unsubscribe_url": "{{ unsubscribe_url }}", "lines": ["問い合わせ: info@example.com"]}


class FooterTest(unittest.TestCase):
    def write(self, d, data):
        f = Path(d) / "footer.json"
        f.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return f

    def test_cli_puts_sender_and_unsubscribe_in_both_html_and_text(self):
        with out_tmp() as t, tempfile.TemporaryDirectory() as priv:  # フッタは output/ の外（private repo 側）に置ける
            src = Path(t) / "2026-10-11-abc.md"
            src.write_text(SAMPLE, encoding="utf-8")
            p = run(src, "--footer", self.write(priv, FOOTER))
            self.assertEqual(p.returncode, 0, p.stderr)
            h = (Path(t) / "2026-10-11-abc.html").read_text(encoding="utf-8")
            txt = (Path(t) / "2026-10-11-abc.txt").read_text(encoding="utf-8")
        self.assertIn("このメールは 運営&lt;者&gt; がお送りしています。", h)
        self.assertIn('配信を停止する（今後受け取らない）場合: <a href="{{ unsubscribe_url }}">', h)
        self.assertIn("問い合わせ: info@example.com", h)
        self.assertLess(h.index("C社の決算"), h.index("がお送りしています"))
        self.assertIn("このメールは 運営<者> がお送りしています。", txt)
        self.assertIn("配信を停止する（今後受け取らない）場合: {{ unsubscribe_url }}", txt)
        self.assertIn("問い合わせ: info@example.com", txt)
        self.assertTrue(txt.rstrip().endswith("問い合わせ: info@example.com"))

    def test_https_url_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            f = r.load_footer(self.write(d, {"sender": "運営者", "unsubscribe_url": "https://example.com/u?id=1&x=2"}))
        self.assertEqual(f["lines"], [])
        self.assertIn('href="https://example.com/u?id=1&amp;x=2"', r.render_html(r.parse(SAMPLE), f))

    def test_without_footer_nothing_is_added(self):
        self.assertNotIn("お送りしています", r.render_html(r.parse(SAMPLE)))
        self.assertNotIn("お送りしています", r.render_text(r.parse(SAMPLE)))

    def test_missing_or_invalid_footer_fails(self):
        bad = [
            "{",
            [],
            {"unsubscribe_url": "{{ unsubscribe_url }}"},
            {"sender": "", "unsubscribe_url": "{{ unsubscribe_url }}"},
            {"sender": "a\nb", "unsubscribe_url": "{{ unsubscribe_url }}"},
            {"sender": "運営者"},
            {"sender": "運営者", "unsubscribe_url": "  "},
            {"sender": "運営者", "unsubscribe_url": "http://example.com/u"},
            {"sender": "運営者", "unsubscribe_url": "javascript:alert(1)"},
            {"sender": "運営者", "unsubscribe_url": "{{ unsubscribe_url }}\" onclick=\"x"},
            {"sender": "運営者", "unsubscribe_url": "{{ unsubscribe_url }}", "lines": [""]},
            {"sender": "運営者", "unsubscribe_url": "{{ unsubscribe_url }}", "lines": "住所"},
        ]
        with tempfile.TemporaryDirectory() as d:
            for data in bad:
                with self.assertRaises(ValueError, msg=data):
                    r.load_footer(self.write(d, data))
            with self.assertRaises(ValueError):
                r.load_footer(Path(d) / "none.json")
        with out_tmp() as t:
            src = Path(t) / "2026-10-11-abc.md"
            src.write_text(SAMPLE, encoding="utf-8")
            p = run(src, "--footer", Path(t) / "none.json")
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("フッタを読めない", p.stderr)
            self.assertFalse((Path(t) / "2026-10-11-abc.html").exists())


class RenderTest(unittest.TestCase):
    def cleanup_if_new(self, path):
        """実装が壊れて repo 内の実パスに書いてしまったとき、テスト前に無かったものだけ消す。"""
        if not path.exists():
            self.addCleanup(lambda: shutil.rmtree(path) if path.is_dir() else path.unlink(missing_ok=True))

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
                    self.cleanup_if_new(d)
                    existed = d.exists()
                    p = run(src, "--out-dir", d)
                    self.assertNotEqual(p.returncode, 0, d)
                    self.assertEqual(d.exists(), existed, d)
                    self.assertFalse((d / "in.html").exists(), d)

    def test_refuses_dotdot_escape(self):
        with out_tmp() as t:
            src = Path(t) / "in.md"
            src.write_text(SAMPLE, encoding="utf-8")
            self.cleanup_if_new(OUT.parent / "output-x")
            p = run(src, "--out-dir", OUT / ".." / "output-x")
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse((OUT.parent / "output-x").exists())

    def test_refuses_symlinks_out_of_output(self):
        # resolve でなく字面で判定すると、output/ 内の symlink 経由で外に書ける・外を読める
        with out_tmp() as t, tempfile.TemporaryDirectory() as outside:
            t, outside = Path(t), Path(outside)
            src = t / "in.md"
            src.write_text(SAMPLE, encoding="utf-8")
            (t / "linkdir").symlink_to(outside, target_is_directory=True)
            p = run(src, "--out-dir", t / "linkdir")
            self.assertNotEqual(p.returncode, 0)
            (t / "in.html").symlink_to(outside / "evil.html")
            p = run(src)
            self.assertNotEqual(p.returncode, 0)
            (t / "in.html").unlink()
            ext = outside / "post.md"
            ext.write_text(SAMPLE, encoding="utf-8")
            (t / "post.md").symlink_to(ext)
            p = run(t / "post.md")
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(sorted(x.name for x in outside.iterdir()), ["post.md"])

    def test_refuses_overwriting_input(self):
        with out_tmp() as t:
            src = Path(t) / "x.html"
            src.write_text(SAMPLE, encoding="utf-8")
            p = run(src)
            self.assertNotEqual(p.returncode, 0)
            self.assertEqual(src.read_text(encoding="utf-8"), SAMPLE)

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
