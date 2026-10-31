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
        tags, article_tags, count, _ = c.parse(GOOD)
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

    def test_other_list_items_shift_numbering(self):
        """リード文の箇条書きは `<li>` になり、表示側の記事番号をずらす。要素数が合っていても落とす"""
        text = post("tags: [AI]\narticle_tags:\n  - [AI]\n  - []\n  - []\n").replace(
            "リード文。\n", "リード文。\n\n- 補足A\n- 補足B\n")
        self.assertTrue(any("リスト項目が 2 個" in e for e in c.check(text, require=True)))

    def test_nested_list_item(self):
        text = post("tags: [AI]\narticle_tags:\n  - [AI]\n  - []\n  - []\n").replace(
            "   読みどころ1\n", "   読みどころ1\n   - 入れ子\n")
        self.assertTrue(any("リスト項目が 1 個" in e for e in c.check(text, require=True)))

    def test_flow_style_raises(self):
        """flow 形式は Jekyll が読むので、--all で黙って飛ばさない"""
        text = post("tags: [AI]\narticle_tags: [[AI], [], []]\n")
        with self.assertRaises(ValueError):
            c.check(text, require=False)

    def test_comments_are_skipped(self):
        text = post("tags: [AI]\narticle_tags:\n  - [AI]  # 1本目\n  # …記事の本数だけ並べる\n  - []\n  - []\n")
        self.assertEqual(c.check(text, require=True), [])

    def test_title_with_triple_dash(self):
        """title に `---` を含んでも front matter を途中で切らない"""
        text = post("tags: [AI]\narticle_tags:\n  - [AI]\n  - []\n").replace(
            'title: "見出し"', 'title: "A---B"')
        self.assertTrue(any("2 件" in e for e in c.check(text, require=False)))


class TestSerendipity(unittest.TestCase):
    """serendipity（セレンディピティ枠の記事番号, #619）。表示側は N 本目に印を出すので、範囲外は黙って消える"""

    FRONT = "tags: [AI, セキュリティ]\narticle_tags:\n  - [AI]\n  - [セキュリティ, AI]\n  - []\n"

    def check(self, line, before=True):
        front = line + self.FRONT if before else self.FRONT + line
        return c.check(post(front), require=True)

    def test_absent_is_ok(self):
        self.assertEqual(c.check(GOOD, require=True), [])

    def test_last_article(self):
        self.assertEqual(self.check("serendipity: [3]\n"), [])

    def test_after_article_tags(self):
        self.assertEqual(self.check("serendipity: [2, 3]\n", before=False), [])

    def test_empty_is_ok(self):
        self.assertEqual(self.check("serendipity: []\n"), [])

    def test_out_of_range(self):
        """番号は本文の記事の位置（1始まり）。記事の表記上の番号 10 ではなく 3 本目"""
        self.assertTrue(any("範囲外" in e for e in self.check("serendipity: [10]\n")))
        self.assertTrue(any("範囲外" in e for e in self.check("serendipity: [0]\n")))

    def test_too_many(self):
        self.assertTrue(any("2 本まで" in e for e in self.check("serendipity: [1, 2, 3]\n")))

    def test_duplicate(self):
        self.assertTrue(any("重複" in e for e in self.check("serendipity: [3, 3]\n")))

    def test_not_number(self):
        self.assertTrue(any("整数" in e for e in self.check("serendipity: [末尾]\n")))

    def test_fullwidth_digits(self):
        self.assertTrue(any("整数" in e for e in self.check("serendipity: [１]\n")))

    def test_checked_without_article_tags(self):
        text = post("serendipity: [10]\n")
        self.assertTrue(any("範囲外" in e for e in c.check(text, require=False)))

    def test_block_style(self):
        self.assertTrue(any("フロー形式" in e for e in self.check("serendipity:\n  - 3\n")))


if __name__ == "__main__":
    unittest.main()
