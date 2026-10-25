#!/usr/bin/env python3
"""check_missing_publish_days.py のテスト。

2026-09-25 の週次利用上限の枯渇で配信が丸ごと1日欠落した（#421）。この検査が
その型の欠落を確実に拾えることが要点。純関数（`posted_dates` / `missing_days`）
は合成データで検証し、`git ls-tree` を呼ぶ部分（`list_post_filenames`）はここでは
検証しない（環境依存の I/O のため、実データでの確認は develop-issue の run 内で
`origin/main` に対して直接実行して行った）。
"""
import unittest
from datetime import date

import check_missing_publish_days as c

PROFILES = ("", "-designer", "-engineer", "-entrepreneur", "-researcher")


def filenames_for(dates):
    """指定した日付ぶんの5投稿（共通+プロファイル4種）のファイル名一覧を作る。"""
    return [f"_posts/{d}-news{suffix}.md" for d in dates for suffix in PROFILES]


class TestPostedDates(unittest.TestCase):
    def test_extracts_dates_from_filenames(self):
        names = filenames_for(["2026-09-24", "2026-09-26"])
        self.assertEqual(c.posted_dates(names), {"2026-09-24", "2026-09-26"})

    def test_ignores_non_post_paths(self):
        names = ["_posts/2026-09-24-news.md", "README.md", "_posts/not-a-date.md"]
        self.assertEqual(c.posted_dates(names), {"2026-09-24"})

    def test_one_file_is_enough_to_count_the_day(self):
        """1件でも投稿があれば「配信あり」。欠落の判定は0件の日だけを問題にする。"""
        self.assertEqual(c.posted_dates(["_posts/2026-09-24-news-designer.md"]),
                          {"2026-09-24"})


class TestMissingDays(unittest.TestCase):
    def test_detects_a_single_gap_day(self):
        """#421 の実際の型: 09-24 と 09-26 に投稿があり、09-25 だけ0件。"""
        names = filenames_for(["2026-09-21", "2026-09-22", "2026-09-23",
                                "2026-09-24", "2026-09-26"])
        start, end = date(2026, 9, 21), date(2026, 9, 26)
        self.assertEqual(c.missing_days(names, start, end), ["2026-09-25"])

    def test_no_gap_returns_empty(self):
        names = filenames_for(["2026-09-24", "2026-09-25", "2026-09-26"])
        start, end = date(2026, 9, 24), date(2026, 9, 26)
        self.assertEqual(c.missing_days(names, start, end), [])

    def test_multiple_gap_days_reported_oldest_first(self):
        names = filenames_for(["2026-09-21", "2026-09-25"])
        start, end = date(2026, 9, 21), date(2026, 9, 25)
        self.assertEqual(c.missing_days(names, start, end),
                          ["2026-09-22", "2026-09-23", "2026-09-24"])

    def test_partial_day_still_counts_as_posted(self):
        """1プロファイル分しか無くても、その日自体は0件でないので missing に出さない
        （欠けたプロファイルの検知はこのスクリプトの対象外。issue の受け入れ条件は
        「記事0件の日」）。"""
        names = ["_posts/2026-09-25-news.md"]
        start, end = date(2026, 9, 25), date(2026, 9, 25)
        self.assertEqual(c.missing_days(names, start, end), [])


class TestEarliestDate(unittest.TestCase):
    def test_returns_the_earliest_date(self):
        names = filenames_for(["2026-09-24", "2026-08-01", "2026-09-26"])
        self.assertEqual(c.earliest_date(names), date(2026, 8, 1))

    def test_none_when_no_posts(self):
        self.assertIsNone(c.earliest_date([]))


class TestFindMissingDays(unittest.TestCase):
    def test_excludes_today_and_stops_at_earliest_post(self):
        """当日は検査対象外（配信がまだ実行されていない可能性がある）。
        配信開始日より前は「配信開始前」として対象にしない。"""
        names = filenames_for(["2026-09-24", "2026-09-26"])

        # list_post_filenames を差し替えて today を固定し、境界を検証する
        orig = c.list_post_filenames
        c.list_post_filenames = lambda ref: names
        try:
            days = c.find_missing_days("origin/main", lookback=30,
                                        today=date(2026, 9, 27))
        finally:
            c.list_post_filenames = orig
        # 検査範囲は [2026-09-24 (=最古の投稿), 2026-09-26]（当日 09-27 は除外）
        self.assertEqual(days, ["2026-09-25"])

    def test_no_posts_at_all_reports_the_whole_lookback_window(self):
        """投稿が1件も無ければ「配信開始前」との区別がつかないので、
        lookback 全体（当日を除く直近 lookback 日ぶん、ちょうど lookback 件）を
        欠落として報告する（安全側。誤って握りつぶさない）。"""
        orig = c.list_post_filenames
        c.list_post_filenames = lambda ref: []
        try:
            days = c.find_missing_days("origin/main", lookback=3,
                                        today=date(2026, 9, 27))
        finally:
            c.list_post_filenames = orig
        # [today - lookback, today - 1] = 09-24, 09-25, 09-26 のちょうど3日
        self.assertEqual(days, ["2026-09-24", "2026-09-25", "2026-09-26"])


if __name__ == "__main__":
    unittest.main()
