#!/usr/bin/env python3
"""check_article_tags.py のテスト。

要点は要素数のずれを落とせること。表示側（archive.md）は N 本目の `<li>` に
N 番目の要素を当てるので、1件ずれると以降の記事のトピックが全部ずれたまま
「記事単位で絞れた」顔で配信される。
"""
import unittest

import check_article_tags as c

BODY = """
リード文。

1. [見出し1](https://example.com/1) (ソース)<br>
   読みどころ1

2. [見出し2](https://example.com/2) (ソース)<br>
   読みどころ2

10. [見出し10](https://example.com/10) (ソース)<br>
    読みどころ10
"""


def post(front):
    return "---\nlayout: post\ntitle: \"見出し\"\n" + front + "---\n" + BODY


GOOD = post("tags: [AI, セキュリティ]\narticle_tags:\n  - [AI]\n  - [セキュリティ, AI]\n  - []\n")


class TestCheck(unittest.TestCase):
    def test_good(self):
        self.assertEqual(c.check(GOOD, require=True), [])

    def test_parse_keeps_order_and_empty(self):
        tags, article_tags, count = c.parse(GOOD)
        self.assertEqual(tags, ["AI", "セキュリティ"])
        self.assertEqual(article_tags, [["AI"], ["セキュリティ", "AI"], []])
        self.assertEqual(count, 3)

    def test_count_mismatch(self):
        text = post("tags: [AI, セキュリティ]\narticle_tags:\n  - [AI]\n  - [セキュリティ]\n")
        errors = c.check(text, require=True)
        self.assertEqual(len(errors), 1)
        self.assertIn("2 件", errors[0])
        self.assertIn("3 本", errors[0])

    def test_unknown_topic(self):
        text = post("tags: [AI, ゲーム]\narticle_tags:\n  - [AI]\n  - [ゲーム]\n  - []\n")
        self.assertTrue(any("ゲーム" in e and "語彙" in e for e in c.check(text, require=True)))

    def test_too_many_topics(self):
        text = post("tags: [AI, 開発, 社会, 経済]\narticle_tags:\n  - [AI, 開発, 社会, 経済]\n  - []\n  - []\n")
        self.assertTrue(any("4 個" in e for e in c.check(text, require=True)))

    def test_three_topics_allowed(self):
        text = post("tags: [AI, 開発, 社会]\narticle_tags:\n  - [AI, 開発, 社会]\n  - []\n  - []\n")
        self.assertEqual(c.check(text, require=True), [])

    def test_duplicate_topic(self):
        text = post("tags: [AI]\narticle_tags:\n  - [AI, AI]\n  - []\n  - []\n")
        self.assertTrue(any("重複" in e for e in c.check(text, require=True)))

    def test_tags_superset_of_union(self):
        """日単位の tags に、どの記事にも付いていないトピックが残っている"""
        text = post("tags: [AI, 経済]\narticle_tags:\n  - [AI]\n  - []\n  - []\n")
        self.assertTrue(any("和集合" in e for e in c.check(text, require=True)))

    def test_tags_subset_of_union(self):
        text = post("tags: [AI]\narticle_tags:\n  - [AI]\n  - [経済]\n  - []\n")
        self.assertTrue(any("和集合" in e for e in c.check(text, require=True)))

    def test_missing_required(self):
        self.assertEqual(c.check(post("tags: [AI]\n"), require=True), ["article_tags が無い"])

    def test_missing_not_required(self):
        self.assertEqual(c.check(post("tags: [AI]\n"), require=False), [])

    def test_article_tags_followed_by_other_key(self):
        """article_tags の後ろに別のキーが来ても、そこで読み終える"""
        text = post("article_tags:\n  - [AI]\n  - []\n  - []\ntags: [AI]\n")
        self.assertEqual(c.check(text, require=True), [])

    def test_malformed_item_raises(self):
        text = post("tags: [AI]\narticle_tags:\n  - AI\n  - []\n  - []\n")
        with self.assertRaises(ValueError):
            c.check(text, require=True)

    def test_quoted_topics(self):
        text = post("tags: [\"AI\"]\narticle_tags:\n  - [\"AI\"]\n  - []\n  - []\n")
        self.assertEqual(c.check(text, require=True), [])


if __name__ == "__main__":
    unittest.main()
