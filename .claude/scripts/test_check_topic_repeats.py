#!/usr/bin/env python3
"""check_topic_repeats の検証 (#531)。"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_topic_repeats  # noqa: E402

REPO_POSTS = HERE.parents[1] / "_posts"


def post(*items):
    """items は (見出し, 読みどころ) の組。"""
    body = "---\nlayout: post\ntitle: \"見出し\"\n---\n\nリード。\n\n"
    for n, (title, note) in enumerate(items, 1):
        body += f"{n}. [{title}](https://example.com/{abs(hash(title))}) (ソース)<br>\n   {note}\n\n"
    return body


# 点数の分母を作る、よくある語だけの項目（「AI」「Claude」は珍しくない語として扱われる）
FILLER = [(f"AI の話題{n}号", f"Claude と AI についての一般的な話{n}。") for n in range(1000)]


class RealPostsTest(unittest.TestCase):
    """#531 で見逃した実例が出ること。repo の _posts をそのまま読む。

    実例の項目を後から削ったり「続報（」を付けたりすると、検出対象から外れてここが落ちる。
    そのときは実例を fixture に写してから直す。
    """

    @classmethod
    def setUpClass(cls):
        cls.archive = check_topic_repeats.Archive(REPO_POSTS)

    def pairs(self, name):
        found = check_topic_repeats.repeats_of(REPO_POSTS / name, self.archive)
        return {(it["title"], h[0][:10]) for it, hits in found for h in hits}

    def test_2026_10_20_main(self):
        pairs = self.pairs("2026-10-20-news.md")
        self.assertIn(("Deno 開発元が Cloudflare に合流、Deno の開発は終了へ", "2026-10-10"), pairs)
        self.assertIn(("Claude が暗号規格 ECDSA の25年来の謎を解明", "2026-10-17"), pairs)

    def test_2026_10_08_main(self):
        self.assertIn(
            ("Google、10カ月ぶりの最上位AI「Gemini 4 Argon」", "2026-10-01"),
            self.pairs("2026-10-08-news.md"),
        )

    def test_2026_10_11_researcher(self):
        self.assertIn(
            ("OpenAI、安全性研究者3人を解雇　双方の主張が真っ向から対立", "2026-10-02"),
            self.pairs("2026-10-11-news-researcher.md"),
        )


class RealFollowUpTargetsTest(unittest.TestCase):
    """#659 の実例: 別フィードの日付を書いた続報が出て、正しい表記が候補に入ること"""

    @classmethod
    def setUpClass(cls):
        cls.archive = check_topic_repeats.Archive(REPO_POSTS)

    def misses(self, name):
        if not (REPO_POSTS / name).exists():
            self.skipTest(f"{name} が無い")
        found = check_topic_repeats.follow_up_targets(REPO_POSTS / name, self.archive)
        return {it["title"]: [c[0] for c in cands] for it, _, _, cands in found}

    def test_2026_11_15_main_nvidia(self):
        # 表記を揃える前（#664 より前）は「フアン」と「ファン CEO」が重ならず、同じフィードの 11/13
        # （「NVIDIA、ファン CEO を事実上解任」）が候補に出ないので、起業家の 11/13 を期待していた。
        # 揃えた後は同じフィードの掲載が先に出る（curate-news 4a の「名前の無い表記の直近」）
        misses = self.misses("2026-11-15-news.md")
        self.assertEqual(misses["NVIDIA にフアン氏の復帰を求める署名、11.5万人超"][0], "続報（11/13掲載）")

    def test_2026_11_12_entrepreneur_nvidia(self):
        misses = self.misses("2026-11-12-news-entrepreneur.md")
        self.assertIn("続報（メイン 11/10掲載）", misses["NVIDIA 取締役会、ファン CEO の解任を準備と報道"])

    def test_2026_11_16_engineer_m365(self):
        misses = self.misses("2026-11-16-news-engineer.md")
        self.assertIn("続報（メイン 11/13掲載）",
                      misses["Microsoft 365 障害でアラートが届かず、ホテルのプールで塩素ガス被害"])

    def test_correct_follow_up_is_not_listed(self):
        # 11/10 メインの NVIDIA 株安は同じフィードの 11/9 を正しく指している
        self.assertNotIn("NVIDIA 株4%安、ファン CEO のスパイ疑惑を議会が超党派で追及",
                         self.misses("2026-11-10-news.md"))


class SyntheticTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.posts = Path(self._tmp.name) / "_posts"
        self.posts.mkdir()
        self.write("2026-09-20-news-designer.md", post(*FILLER))

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.posts / name
        path.write_text(text, encoding="utf-8")
        return path

    def check(self, path):
        archive = check_topic_repeats.Archive(self.posts)
        return check_topic_repeats.repeats_of(path, archive)

    def run_main(self, *paths):
        out = io.StringIO()
        with redirect_stdout(out):
            code = check_topic_repeats.main([str(p) for p in paths])
        return code, out.getvalue()

    PREV = ("Zorblax が Quuxcorp に合流", "Zorblax の開発チームが Quuxcorp の実行基盤に移る。")
    AGAIN = ("Zorblax 開発元が Quuxcorp へ", "今後は Quuxcorp 側の実装に注力するという。")

    def test_same_feed_within_window(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(self.AGAIN))
        found = self.check(today)
        self.assertEqual(len(found), 1)
        it, hits = found[0]
        self.assertEqual(it["title"], self.AGAIN[0])
        self.assertEqual(len(hits), 1)
        prev_name, prev, score, shared = hits[0]
        self.assertEqual(prev_name, "2026-10-10-news.md")
        self.assertEqual(set(shared), {"zorblax", "quuxcorp"})

    def test_name_variants_are_unified_before_matching(self):
        # 「ファン氏」と「フアン氏」は names.md の表で同じ語になる（#664）。揃えないと共有語は
        # Zorblax の1語だけで閾値に届かない
        self.write("2026-10-10-news.md", post(("Zorblax のファン氏が辞任", "取引先にも動揺が広がる。")))
        today = self.write("2026-10-20-news.md", post(("Zorblax、フアン氏の復帰を求める声", "署名が集まる。")))
        found = self.check(today)
        self.assertEqual(len(found), 1)
        self.assertEqual(set(found[0][1][0][3]), {"zorblax", "フアン"})

    def test_lists_up_to_three_candidates_by_score(self):
        # 最高点の組（10/12）に続けて、同点の組を新しい日付から出す（4組目の 10/14 は出さない）
        self.write("2026-10-12-news.md", post(("Zorblax と Quuxcorp と Vintrel", "Zorblax の話。")))
        self.write("2026-10-14-news.md", post(("Zorblax が Quuxcorp に", "前の話。")))
        self.write("2026-10-16-news.md", post(("Zorblax と Quuxcorp", "別の話。")))
        self.write("2026-10-18-news.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(("Zorblax が Quuxcorp と Vintrel を統合", "続きの話。")))
        found = self.check(today)
        self.assertEqual(len(found), 1)
        names = [h[0] for h in found[0][1]]
        self.assertEqual(names[0], "2026-10-12-news.md")
        self.assertEqual(len(names), 3)
        self.assertEqual(names[1:], ["2026-10-18-news.md", "2026-10-16-news.md"])

    def test_match_through_note(self):
        # 見出しどうしは重ならず、前回の読みどころの語でだけ重なる組（ECDSA の型）
        self.write("2026-10-17-news.md", post(("Claude が謎を解明", "NSA が示した Wexqort の値の由来。")))
        today = self.write("2026-10-20-news.md", post(("Claude が Wexqort の謎を解明", "NSA の数値の出どころ。")))
        self.assertEqual(len(self.check(today)), 1)

    def test_window_is_ten_days(self):
        self.write("2026-10-09-news.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(self.AGAIN))
        self.assertEqual(self.check(today), [])
        self.write("2026-10-10-news.md", post(self.PREV))
        self.assertEqual(len(self.check(today)), 1)

    def test_other_feed_and_same_day_are_ignored(self):
        self.write("2026-10-15-news-engineer.md", post(self.PREV))
        self.write("2026-10-20-news-researcher.md", post(self.PREV))
        today = self.write("2026-10-20-news.md", post(self.AGAIN))
        self.assertEqual(self.check(today), [])

    def test_profile_feed_matches_itself(self):
        self.write("2026-10-15-news-engineer.md", post(self.PREV))
        today = self.write("2026-10-20-news-engineer.md", post(self.AGAIN))
        self.assertEqual(len(self.check(today)), 1)

    def test_follow_up_is_skipped(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        today = self.write(
            "2026-10-20-news.md",
            post((self.AGAIN[0], "続報（10/10掲載）。開発の終了が決まった。")),
        )
        self.assertEqual(self.check(today), [])

    def test_common_terms_alone_do_not_match(self):
        self.write("2026-10-15-news.md", post(("Claude の新しい AI 機能", "AI の使い方が変わる。")))
        today = self.write("2026-10-20-news.md", post(("AI と Claude の別の話", "AI で何かができる。")))
        self.assertEqual(self.check(today), [])

    def test_main_exit_codes(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        clean = self.write("2026-10-19-news.md", post(("無関係な Plimbo の話", "Plimbo が出た。")))
        code, out = self.run_main(clean)
        self.assertEqual(code, 0, out)
        hit = self.write("2026-10-20-news.md", post(self.AGAIN))
        code, out = self.run_main(hit)
        self.assertEqual(code, 1)
        self.assertIn("要判断 2026-10-20-news.md:8 「Zorblax 開発元が Quuxcorp へ」", out)
        self.assertIn("前回 2026-10-10: 「Zorblax が Quuxcorp に合流」", out)
        code, _ = self.run_main(self.posts / "2026-10-21-news.md")
        self.assertEqual(code, 2)
        code, _ = self.run_main(self.write("notes.md", post(self.AGAIN)))
        self.assertEqual(code, 2)



class FollowUpTargetsTest(unittest.TestCase):
    """続報の指し先に前回の記事があるか (#659)"""

    setUp = SyntheticTest.setUp
    tearDown = SyntheticTest.tearDown
    write = SyntheticTest.write
    run_main = SyntheticTest.run_main
    PREV, AGAIN = SyntheticTest.PREV, SyntheticTest.AGAIN

    NAMES = {"メイン": "news", "起業家": "news-entrepreneur"}

    def targets(self, path):
        archive = check_topic_repeats.Archive(self.posts)
        return check_topic_repeats.follow_up_targets(path, archive, self.NAMES)

    def follow_up(self, md):
        return post((self.AGAIN[0], f"続報（{md}掲載）。開発の終了が決まった。"))

    def test_same_feed_target_with_event_passes(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        self.assertEqual(self.targets(self.write("2026-10-20-news.md", self.follow_up("10/10"))), [])

    def test_date_of_other_feed_is_listed_with_named_candidate(self):
        self.write("2026-10-10-news.md", post(("無関係な Plimbo の話", "Plimbo が出た。")))
        self.write("2026-10-10-news-entrepreneur.md", post(self.PREV))
        found = self.targets(self.write("2026-10-20-news.md", self.follow_up("10/10")))
        self.assertEqual(len(found), 1)
        it, where, score, cands = found[0]
        self.assertIn("メインの 2026-10-10 に同じ出来事が見当たらない", where)
        self.assertEqual(cands[0][0], "続報（起業家 10/10掲載）")

    def test_named_target_with_event_passes(self):
        self.write("2026-10-10-news-entrepreneur.md", post(self.PREV))
        self.assertEqual(self.targets(self.write("2026-10-20-news.md", self.follow_up("起業家 10/10"))), [])

    def test_named_target_without_event_is_listed(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        self.write("2026-10-10-news-entrepreneur.md", post(("無関係な Plimbo の話", "Plimbo が出た。")))
        found = self.targets(self.write("2026-10-20-news-entrepreneur.md", self.follow_up("起業家 10/10")))
        self.assertEqual(found[0][3][0][0], "続報（メイン 10/10掲載）")

    def test_missing_target_and_unknown_name_are_listed(self):
        self.write("2026-10-10-news.md", post(self.PREV))
        found = self.targets(self.write("2026-10-20-news.md", self.follow_up("10/9")))
        self.assertIn("投稿が無い", found[0][1])
        self.assertEqual(found[0][3][0][0], "続報（10/10掲載）")
        found = self.targets(self.write("2026-10-20-news.md", self.follow_up("投資家 10/10")))
        self.assertIn("フィードは無い", found[0][1])

    def test_malformed_marker_is_listed(self):
        self.write("2026-10-10-news-entrepreneur.md", post(self.PREV))
        for md in ("起業家　10/10", "起業家10/10", "10/10 起業家"):
            found = self.targets(self.write("2026-10-20-news.md", self.follow_up(md)))
            self.assertEqual(len(found), 1, md)
            self.assertIn("形でない", found[0][1])

    def test_own_feed_candidates_come_first(self):
        # 別フィードの高得点の掲載より、このフィードの直近の掲載を先に出す
        self.write("2026-10-12-news-entrepreneur.md", post(("Zorblax と Quuxcorp と Vintrel", "Zorblax の話。")))
        self.write("2026-10-14-news.md", post(self.PREV))
        found = self.targets(self.write("2026-10-20-news.md", self.follow_up("10/12")))
        self.assertEqual([c[0] for c in found[0][3]][:2], ["続報（10/14掲載）", "続報（起業家 10/12掲載）"])

    def test_main_exit_code_counts_targets(self):
        self.write("2026-10-10-news-entrepreneur.md", post(self.PREV))
        path = self.write("2026-10-20-news.md", self.follow_up("10/10"))
        code, out = self.run_main(path)
        self.assertEqual(code, 1)
        self.assertIn("続報の指し先 2026-10-20-news.md:8", out)
        self.assertIn("続報の指し先 1 項目", out)


if __name__ == "__main__":
    unittest.main()
