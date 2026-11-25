#!/usr/bin/env python3
"""email_preview.py のユニットテスト。実行: python3 test_email_preview.py"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import email_preview as ep

SCRIPT = Path(__file__).resolve().parent / "email_preview.py"

POST = """---
layout: post
title: "見出し（ソフトウェアエンジニア）"
date: 2026-11-24
profile: engineer
article_tags:
  - [開発]
  - [AI]
---

リード文。

1. [A がアルファ版に](https://example.com/a) (HN・英語)<br>
   配布が始まった

2. [B の決算](https://example.com/b) (日経・会員限定)<br>
   売上の内訳
"""


class ToCuratedTest(unittest.TestCase):
    def test_front_matter_is_stripped_and_heading_restored(self):
        out = ep.to_curated(POST, "2026-11-24")
        self.assertTrue(out.startswith("## ニュース (2026-11-24 JST)\n\nリード文。"))
        self.assertNotIn("layout:", out)
        self.assertNotIn("article_tags", out)

    def test_render_reads_lead_and_items_without_front_matter(self):
        doc = ep.render_email_body.parse(ep.to_curated(POST, "2026-11-24"))
        self.assertEqual(doc["heading"], "ニュース (2026-11-24 JST)")
        self.assertEqual(doc["lead"], "リード文。")
        self.assertEqual([it["note"] for it in doc["items"]], ["配布が始まった", "売上の内訳"])

    def test_unclosed_front_matter_is_rejected(self):
        with self.assertRaises(ValueError):
            ep.to_curated("---\nlayout: post\n\n1. [A](https://example.com/a)\n", "2026-11-24")

    def test_placeholder_footer_passes_the_real_validator(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "footer.json"
            p.write_text(ep.json.dumps(ep.PLACEHOLDER_FOOTER, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(ep.render_email_body.load_footer(p)["sender"], ep.PLACEHOLDER_FOOTER["sender"])


class CliTest(unittest.TestCase):
    def test_writes_txt_and_html_with_footer_under_output(self):
        with tempfile.TemporaryDirectory() as d:
            post = Path(d) / "2099-01-02-news-engineer.md"
            post.write_text(POST, encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), str(post)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            txt = ep.EVAL_DIR / "2099-01-02-news-engineer.txt"
            html = ep.EVAL_DIR / "2099-01-02-news-engineer.html"
            try:
                body = txt.read_text(encoding="utf-8")
                # 件名・先頭の見出しは有料 run と同じく、プロファイルの title をフィード名にした文 (#703)
                first = body.splitlines()[0]
                self.assertTrue(first.startswith("ソフトウェアエンジニア｜"), first)
                self.assertTrue(first.endswith("（1/2）"), first)
                self.assertNotIn("ニュース (", first)
                self.assertIn("\n\nリード文。", body)
                self.assertIn("配信を停止する", body)
                self.assertIn(f"<title>{ep.render_email_body.html.escape(first)}</title>", html.read_text(encoding="utf-8"))
                self.assertIn(render_mark(), html.read_text(encoding="utf-8"))
            finally:
                for p in (txt, html, ep.EVAL_DIR / post.name):
                    p.unlink(missing_ok=True)

    def test_rejects_non_post_name(self):
        with tempfile.TemporaryDirectory() as d:
            post = Path(d) / "notes.md"
            post.write_text(POST, encoding="utf-8")
            r = subprocess.run([sys.executable, str(SCRIPT), str(post)], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)


def render_mark():
    return ep.render_email_body.FOOTER_MARK


if __name__ == "__main__":
    unittest.main()
