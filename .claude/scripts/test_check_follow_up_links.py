#!/usr/bin/env python3
"""check_follow_up_links.py のテスト。

_layouts/post.html が出す形（`続報（<a class="follow-up-link" href=...>M/D掲載</a>）`）を通し、
付け損ね・別フィード・別の年を指すリンクを落とせることを確かめる。旧形式の見出しのリンク文字列
（`">続報（`）や本文外の抜粋は読みどころではないので数えない。
"""
import tempfile
import unittest
from pathlib import Path

import check_follow_up_links as c


def page(site, rel, body, head=""):
    path = Path(site) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'<head>{head}</head><article><div itemprop="articleBody">{body}</div></article>', encoding="utf-8")


def link(href, label):
    return f'続報（<a class="follow-up-link" href="{href}">{label}掲載</a>）。'


class CheckFollowUpLinksTest(unittest.TestCase):
    def setUp(self):
        self.site = tempfile.mkdtemp()
        page(self.site, "2025/12/30/news.html", "")
        page(self.site, "2025/12/30/news-engineer.html", "")
        page(self.site, "2025/12/29/news.html", "")

    def errors(self):
        return c.check(self.site)[0]

    def test_year_boundary_link_passes(self):
        page(self.site, "2026/01/02/news.html", link("/news/2025/12/30/news.html", "12/30"))
        self.assertEqual(self.errors(), [])

    def test_profile_link_to_own_feed_passes(self):
        page(self.site, "2026/01/02/news-engineer.html", link("/news/2025/12/30/news-engineer.html", "12/30"))
        self.assertEqual(self.errors(), [])

    def test_link_to_other_feed_fails(self):
        page(self.site, "2026/01/02/news-engineer.html", link("/news/2025/12/30/news.html", "12/30"))
        self.assertTrue(any("別フィード" in e for e in self.errors()))

    def test_link_to_wrong_year_fails(self):
        page(self.site, "2024/12/30/news.html", "")
        page(self.site, "2026/01/02/news.html", link("/news/2024/12/30/news.html", "12/30"))
        self.assertTrue(any("直近180日" in e for e in self.errors()))

    def test_link_to_same_day_a_year_ago_fails(self):
        # 今年の 12/30 が同じフィードに無いときに前年の 12/30 を拾った状態
        page(self.site, "2026/12/31/news.html", link("/news/2025/12/30/news.html", "12/30"))
        self.assertTrue(any("直近180日" in e for e in self.errors()))

    def test_nested_link_fails(self):
        page(self.site, "2026/01/02/news.html",
             '<a href="https://example.com/">' + link("/news/2025/12/30/news.html", "12/30") + '見出し</a>')
        self.assertTrue(any("入れ子" in e for e in self.errors()))

    def test_link_to_missing_page_fails(self):
        page(self.site, "2026/01/02/news.html", link("/news/2025/12/28/news.html", "12/28"))
        self.assertTrue(any("存在しない" in e for e in self.errors()))

    def test_bare_marker_with_existing_page_fails(self):
        page(self.site, "2026/01/02/news.html", "続報（12/30掲載）。")
        self.assertTrue(any("リンクが無い" in e for e in self.errors()))

    def test_bare_marker_without_same_feed_page_passes(self):
        # 12/29 はメインにしか無い。プロファイルでは文字のまま残るのが正しい
        page(self.site, "2026/01/02/news-engineer.html", "続報（12/29掲載）。")
        errors, linked, unlinked = c.check(self.site)
        self.assertEqual((errors, linked, unlinked), ([], 0, 1))

    def test_marker_in_headline_link_text_and_meta_is_ignored(self):
        page(self.site, "2026/01/02/news.html",
             '<a href="https://example.com/">続報（12/30掲載）。旧形式の見出し</a>',
             head='<meta name="description" content="続報（12/30掲載）。抜粋">')
        self.assertEqual(self.errors(), [])


class NamedFeedFollowUpTest(unittest.TestCase):
    """前回が別フィードにしか無いときの「続報（起業家 M/D掲載）」(#659)"""

    NAMES = {"メイン": "news", "起業家": "news-entrepreneur", "ソフトウェアエンジニア": "news-engineer"}

    def setUp(self):
        self.site = tempfile.mkdtemp()
        page(self.site, "2026/11/14/news.html", "")
        page(self.site, "2026/11/14/news-entrepreneur.html", "")

    def errors(self):
        return c.check(self.site, self.NAMES)[0]

    def test_named_link_to_that_feed_passes(self):
        page(self.site, "2026/11/15/news.html", link("/news/2026/11/14/news-entrepreneur.html", "起業家 11/14"))
        self.assertEqual(self.errors(), [])

    def test_main_named_from_profile_passes(self):
        page(self.site, "2026/11/15/news-engineer.html", link("/news/2026/11/14/news.html", "メイン 11/14"))
        self.assertEqual(self.errors(), [])

    def test_named_link_to_other_feed_fails(self):
        page(self.site, "2026/11/15/news.html", link("/news/2026/11/14/news.html", "起業家 11/14"))
        self.assertTrue(any("別フィード" in e for e in self.errors()))

    def test_bare_named_marker_with_existing_page_fails(self):
        page(self.site, "2026/11/15/news.html", "続報（起業家 11/14掲載）。")
        self.assertTrue(any("リンクが無い" in e for e in self.errors()))

    def test_bare_named_marker_without_page_passes(self):
        page(self.site, "2026/11/15/news.html", "続報（ソフトウェアエンジニア 11/14掲載）。")
        self.assertEqual(c.check(self.site, self.NAMES), ([], 0, 1))

    def test_unknown_feed_name_fails(self):
        page(self.site, "2026/11/15/news.html", "続報（投資家 11/14掲載）。")
        self.assertTrue(any("表示名に無い" in e for e in self.errors()))

    def test_unlinked_count_excludes_only_bare_errors(self):
        # リンク付きの表記の NG は「文字のまま」の件数から引かない
        page(self.site, "2026/11/15/news.html",
             link("/news/2026/11/14/news.html", "投資家 11/14") + "続報（研究者 11/14掲載）。")
        names = dict(self.NAMES, 研究者="news-researcher")
        errors, linked, unlinked = c.check(self.site, names)
        self.assertEqual((len(errors), linked, unlinked), (1, 1, 1))

    def test_feed_names_from_real_profile_pages(self):
        names = c.feed_names()
        if len(names) == 1:
            self.skipTest("profiles/ が無い")
        self.assertEqual(names["メイン"], "news")
        self.assertEqual(names["起業家"], "news-entrepreneur")
        for name in names:
            self.assertRegex(name, r'^[^\s<>（）"]+$')


if __name__ == "__main__":
    unittest.main()
