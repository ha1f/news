import tempfile
import unittest
from pathlib import Path

from note_format_stats import body_of, sentences_of, stats_of


class NoteFormatStatsTest(unittest.TestCase):
    def test_follow_up_prefix_is_not_a_sentence(self):
        note = "続報（11/18掲載）。新たに修正版の公開日が決まった"
        self.assertEqual(body_of(note), "新たに修正版の公開日が決まった")
        self.assertEqual(sentences_of(note), 1)

    def test_two_sentences(self):
        self.assertEqual(sentences_of("A社が新モデルを出した。価格は据え置き。"), 2)
        self.assertEqual(sentences_of("A社が新モデルを出した。"), 1)

    def test_stats_of_post(self):
        text = (
            "---\nlayout: post\n---\n\nリード。\n\n"
            "1. [見出し1](https://example.com/1) (HN)<br>\n"
            "   " + "あ" * 51 + "\n\n"
            "2. [見出し2](https://example.com/2) (HN)<br>\n"
            "   一文目の事実がある。二文目の事実もある\n"
        )
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "post.md"
            p.write_text(text, encoding="utf-8")
            r = stats_of(p)
        self.assertEqual(r["items"], 2)
        self.assertEqual(r["multi_sentence"], 1)
        self.assertEqual(r["over_50"], 1)
        self.assertEqual(r["max_len"], 51)


if __name__ == "__main__":
    unittest.main()
