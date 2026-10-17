#!/usr/bin/env python3
"""check_link_domains.py / gen_source_domains.py のユニットテスト"""
import json
import os
import unittest
from pathlib import Path

import gen_source_domains
from check_link_domains import check_item, host_of, label_matches

TABLE = {
    "HN": ["news.ycombinator.com"],
    "はてブ": ["b.hatena.ne.jp"],
    "TechCrunch": ["techcrunch.com"],
    "日経": ["nikkei.com"],
}


def head(href, label, shown=None):
    span = f'<span class="link-domain">{shown}</span>' if shown else ""
    return f'<a href="{href}">見出し</a>{span} ({label})'


class TestHostOf(unittest.TestCase):
    def test_strips_www_and_port(self):
        self.assertEqual(host_of("https://www.nikkei.com:443/a"), "nikkei.com")


class TestLabelMatches(unittest.TestCase):
    def test_subdomain_of_label_domain(self):
        self.assertTrue(label_matches("xtech.nikkei.com", "日経", TABLE))

    def test_aggregator_destination(self):
        self.assertFalse(label_matches("arxiv.org", "HN", TABLE))

    def test_suffix_without_dot_is_not_a_match(self):
        self.assertFalse(label_matches("notnikkei.com", "日経", TABLE))

    def test_unknown_label_found_in_host(self):
        # ソース定義より前の過去の投稿のラベル
        self.assertTrue(label_matches("theverge.com", "The Verge", TABLE))
        self.assertTrue(label_matches("lobste.rs", "Lobsters", TABLE))

    def test_label_with_suffix_uses_first_word(self):
        self.assertTrue(label_matches("reddit.com", "Reddit r/ML", TABLE))
        self.assertFalse(label_matches("arxiv.org", "Reddit r/ML", {"Reddit": ["reddit.com"]}))

    def test_unknown_label_word_found_in_host(self):
        self.assertTrue(label_matches("blog.cloudflare.com", "Cloudflare Blog", TABLE))
        self.assertTrue(label_matches("takoratta.hatenablog.com", "Notes by Takoratta", TABLE))
        self.assertTrue(label_matches("p2ptk.org", "p2ptk[.]org", TABLE))

    def test_generic_word_alone_is_not_a_match(self):
        self.assertFalse(label_matches("blog.example.com", "Some Blog", TABLE))

    def test_unknown_label_not_in_host(self):
        self.assertFalse(label_matches("swift.org", "Lobsters", TABLE))
        self.assertFalse(label_matches("nikkei.com", "日本食糧新聞", TABLE))


class TestCheckItem(unittest.TestCase):
    def test_aggregator_with_domain_ok(self):
        self.assertIsNone(check_item(
            head("https://arxiv.org/abs/1", "HN・英語", "arxiv.org"), TABLE))

    def test_aggregator_without_domain_ng(self):
        self.assertIn("ありません", check_item(
            head("https://arxiv.org/abs/1", "HN・英語"), TABLE))

    def test_media_label_without_domain_ok(self):
        self.assertIsNone(check_item(
            head("https://techcrunch.com/a", "TechCrunch・英語"), TABLE))

    def test_media_label_with_domain_ng(self):
        # #294 の二重表示
        self.assertIn("一致するのに", check_item(
            head("https://techcrunch.com/a", "TechCrunch・英語", "techcrunch.com"), TABLE))

    def test_wrong_domain_text_ng(self):
        self.assertIn("違います", check_item(
            head("https://www.itmedia.co.jp/a", "はてブ", "itmedia.com"), TABLE))

    def test_ask_hn_points_to_hn_itself(self):
        self.assertIsNone(check_item(
            head("https://news.ycombinator.com/item?id=1", "HN・英語"), TABLE))

    def test_label_after_follow_up_note(self):
        self.assertIsNone(check_item(
            '<a href="https://techcrunch.com/a">見出し</a>（続報）(TechCrunch)', TABLE))


class TestItemRe(unittest.TestCase):
    def test_tight_list_item_is_checked(self):
        from check_link_domains import ITEM_RE
        html = '<li id="article-1"><a href="https://arxiv.org/a">H</a> (HN・英語)</li>'
        m = ITEM_RE.search(html)
        self.assertIsNotNone(m)
        self.assertIn("ありません", check_item(m.group("head"), TABLE))


class TestGenerated(unittest.TestCase):
    def test_data_file_is_current(self):
        # repo ルートから相対パスで読むので、スクリプトの置き場から2つ上に移って比べる
        root = Path(__file__).resolve().parents[2]
        cwd = os.getcwd()
        os.chdir(root)
        try:
            table = gen_source_domains.build()
            self.assertIsNotNone(table)
            self.assertEqual(
                gen_source_domains.OUT.read_text(encoding="utf-8"),
                gen_source_domains.render(table),
                "_data/source_domains.json が古い。gen_source_domains.py で書き直す")
            data = json.loads(gen_source_domains.OUT.read_text(encoding="utf-8"))
            self.assertEqual(data["Hacker News"], data["HN"])
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
