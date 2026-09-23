#!/usr/bin/env python3
"""check_post_titles.py のテスト。

日付だけの title（#401 で 368 件直したもの）と、表示名が付いた形の両方を
落とせることが要点。取り違えると、次のキュレーション run が日付 title を
書き戻しても検査が通ってしまう。
"""
import tempfile
import unittest
from datetime import date
from pathlib import Path

import check_post_titles as c


class TestTitleOf(unittest.TestCase):
    def _write(self, text):
        d = Path(tempfile.mkdtemp())
        p = d / "2026-09-21-news.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_double_quoted(self):
        p = self._write('---\nlayout: post\ntitle: "AI大手の攻防"\ndate: 2026-09-21\n---\n\n本文\n')
        self.assertEqual(c.title_of(p), "AI大手の攻防")

    def test_single_quoted(self):
        p = self._write("---\ntitle: 'AI大手の攻防'\n---\n\n本文\n")
        self.assertEqual(c.title_of(p), "AI大手の攻防")

    def test_unquoted(self):
        p = self._write("---\ntitle: AI大手の攻防\n---\n\n本文\n")
        self.assertEqual(c.title_of(p), "AI大手の攻防")

    def test_no_title(self):
        p = self._write("---\nlayout: post\ndate: 2026-09-21\n---\n\n本文\n")
        self.assertIsNone(c.title_of(p))

    def test_body_title_line_is_not_read(self):
        """本文に title: で始まる行があっても front matter の外は見ない"""
        p = self._write('---\ntitle: "見出し"\n---\n\ntitle: "本文のほう"\n')
        self.assertEqual(c.title_of(p), "見出し")


class TestHeadlineOf(unittest.TestCase):
    def test_strips_profile_suffix(self):
        self.assertEqual(c.headline_of("Opus 5.5公開（ソフトウェアエンジニア）"), "Opus 5.5公開")

    def test_keeps_inner_parens(self):
        self.assertEqual(c.headline_of("GPT-6（Sol）を追加投入"), "GPT-6（Sol）を追加投入")

    def test_no_suffix(self):
        self.assertEqual(c.headline_of("AI大手の攻防"), "AI大手の攻防")


class TestDateOf(unittest.TestCase):
    def test_main_post(self):
        self.assertEqual(c.date_of(Path("_posts/2026-09-21-news.md")), date(2026, 9, 21))

    def test_profile_post(self):
        self.assertEqual(c.date_of(Path("_posts/2026-08-02-news-designer.md")), date(2026, 8, 2))

    def test_not_a_post_filename(self):
        self.assertIsNone(c.date_of(Path("_posts/news.md")))


class TestProblemsOf(unittest.TestCase):
    def _post(self, name, title):
        d = Path(tempfile.mkdtemp())
        p = d / name
        p.write_text(f'---\nlayout: post\ntitle: "{title}"\ndate: 2026-09-21\n---\n\n本文\n',
                     encoding="utf-8")
        return p

    def test_content_title_passes(self):
        p = self._post("2026-09-21-news.md", "AI大手の攻防、規制と信頼にも波及")
        self.assertEqual(c.problems_of(p), [])

    def test_content_title_with_profile_suffix_passes(self):
        p = self._post("2026-09-21-news-engineer.md",
                       "Opus 5.5公開、運用コスト4割減（ソフトウェアエンジニア）")
        self.assertEqual(c.problems_of(p), [])

    def test_date_only_title_fails(self):
        """#401 で直した 170 件の main 投稿の形"""
        p = self._post("2026-09-21-news.md", "2026年9月21日")
        self.assertEqual(len(c.problems_of(p)), 1)
        self.assertIn("日付", c.problems_of(p)[0])

    def test_date_with_profile_suffix_fails(self):
        """#401 で直した 198 件の profile 投稿の形。接尾辞があっても落とす"""
        p = self._post("2026-09-21-news-designer.md", "2026年9月21日（デザイナー）")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_date_embedded_in_headline_fails(self):
        """日付が見出しの一部でも、一覧のバッジと二重になるので落とす"""
        p = self._post("2026-09-21-news.md", "2026年9月21日のAI大手の攻防")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_month_day_only_fails(self):
        p = self._post("2026-09-21-news.md", "9月21日のニュースまとめ")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_iso_date_fails(self):
        p = self._post("2026-09-21-news.md", "2026-09-21 のニュース")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_other_day_date_passes(self):
        """その投稿自身の日付でなければ、記事内容としての日付表記は通す"""
        p = self._post("2026-09-21-news.md", "改正法が10月1日に施行へ")
        self.assertEqual(c.problems_of(p), [])

    def test_missing_title_fails(self):
        d = Path(tempfile.mkdtemp())
        p = d / "2026-09-21-news.md"
        p.write_text("---\nlayout: post\ndate: 2026-09-21\n---\n\n本文\n", encoding="utf-8")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_empty_title_fails(self):
        p = self._post("2026-09-21-news.md", "")
        self.assertEqual(len(c.problems_of(p)), 1)

    def test_suffix_only_title_fails(self):
        p = self._post("2026-09-21-news-designer.md", "（デザイナー）")
        self.assertEqual(len(c.problems_of(p)), 1)


class TestMain(unittest.TestCase):
    def test_explicit_paths(self):
        d = Path(tempfile.mkdtemp())
        good = d / "2026-09-21-news.md"
        good.write_text('---\ntitle: "AI大手の攻防"\n---\n\n本文\n', encoding="utf-8")
        bad = d / "2026-09-20-news.md"
        bad.write_text('---\ntitle: "2026年9月20日"\n---\n\n本文\n', encoding="utf-8")
        self.assertEqual(c.main([str(good)]), 0)
        self.assertEqual(c.main([str(bad)]), 1)

    def test_missing_file_fails(self):
        self.assertEqual(c.main(["_posts/no-such-file.md"]), 1)


if __name__ == "__main__":
    unittest.main()
