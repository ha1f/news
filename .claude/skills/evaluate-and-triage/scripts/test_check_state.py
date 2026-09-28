#!/usr/bin/env python3
"""check_state.py の純関数のユニットテスト。実行: python3 test_check_state.py"""
import io
import json
import sys
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_state
from check_state import (JST, api_json, assemble_output, classify_publish_prs,
                         fetch_data, fetch_pr_checks, gh_json, parse_api_time,
                         parse_link_header, parse_status_record,
                         parse_status_records, publish_state_of,
                         recent_comment_digests, since_param, summarize_health,
                         summarize_issues, with_page)


def issue(number, title="t", labels=(), pr=False, bot=False):
    data = {"number": number, "title": title,
            "labels": [{"name": name} for name in labels],
            "user": {"type": "Bot" if bot else "User"}}
    if pr:
        data["pull_request"] = {}
    return data


def status_comment(stage, phase, created_at, ok=None):
    record = {"stage": stage, "phase": phase, "summary": "s"}
    if ok is not None:
        record["ok"] = ok
    return {"created_at": created_at, "body": json.dumps(record) + "\n詳細"}


class SummarizeIssuesTest(unittest.TestCase):
    def test_finds_status_issue_and_counts_open_issues(self):
        issues = [
            issue(25, title="📊 daily-loop status"),  # status → 数えない
            issue(26),
            issue(27, labels=["hold"]),
            issue(29, pr=True),  # PR → 数えない
            issue(30, title="Dependency Dashboard", bot=True),  # bot → 数えない
        ]
        status_issue, count, comment_count = summarize_issues(issues)
        self.assertEqual(status_issue, 25)
        self.assertEqual(count, 2)
        self.assertEqual(comment_count, 0)

    def test_returns_status_issue_comment_count(self):
        issues = [issue(25, title="📊 daily-loop status")]
        issues[0]["comments"] = 612
        _, _, comment_count = summarize_issues(issues)
        self.assertEqual(comment_count, 612)

    def test_comment_count_is_zero_without_status_issue(self):
        issues = [issue(26)]
        status_issue, _, comment_count = summarize_issues(issues)
        self.assertIsNone(status_issue)
        self.assertEqual(comment_count, 0)


class HealthTest(unittest.TestCase):
    # today=2026-07-11 (JST) の前日 = 07-10。JST 10時 = UTC 01時
    def test_healthy_day(self):
        comments = [
            status_comment("evaluate", "start", "2026-07-10T01:00:00Z"),
            status_comment("evaluate", "end", "2026-07-10T01:20:00Z", ok=True),
            status_comment("develop", "start", "2026-07-10T03:00:00Z"),
            status_comment("develop", "end", "2026-07-10T04:30:00Z", ok=True),
            status_comment("review", "start", "2026-07-10T06:00:00Z"),
            status_comment("review", "end", "2026-07-10T06:40:00Z", ok=True),
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11", True)
        self.assertEqual(health["incomplete"], [])
        self.assertEqual(health["failed"], [])
        self.assertEqual(health["missing"], [])
        self.assertFalse(health["no_records"])

    def test_dead_session_detected_as_incomplete(self):
        comments = [
            status_comment("evaluate", "start", "2026-07-10T01:00:00Z"),
            # end が無い = セッション死亡
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11", True)
        self.assertEqual(health["incomplete"], ["evaluate"])
        # start があるので missing ではない。develop/review は無記録なので missing
        self.assertEqual(health["missing"], ["develop", "review"])

    def test_silently_dead_stage_detected_as_missing(self):
        # evaluate だけ無記録（trigger 停止など）で他は正常 → missing に出る
        comments = [
            status_comment("develop", "start", "2026-07-10T03:00:00Z"),
            status_comment("develop", "end", "2026-07-10T04:00:00Z", ok=True),
            status_comment("review", "start", "2026-07-10T06:00:00Z"),
            status_comment("review", "end", "2026-07-10T06:30:00Z", ok=True),
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11", True)
        self.assertEqual(health["missing"], ["evaluate"])
        self.assertEqual(health["incomplete"], [])
        self.assertFalse(health["no_records"])

    def test_failed_stage_and_no_records(self):
        comments = [
            status_comment("review", "start", "2026-07-10T06:00:00Z"),
            status_comment("review", "end", "2026-07-10T06:40:00Z", ok=False),
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11", True)
        self.assertEqual(health["failed"], ["review"])
        # 前日ぶんが0件かつ、それ以前にも記録が無い（真の導入直後）→ no_records
        empty = summarize_health([], "2026-07-11", False)
        self.assertTrue(empty["no_records"])
        # 導入直後（全ステージ無記録）は missing を立てない
        self.assertEqual(empty["missing"], [])

    def test_ignores_other_days_and_non_json_comments(self):
        comments = [
            status_comment("evaluate", "start", "2026-07-09T01:00:00Z"),  # 前々日
            {"created_at": "2026-07-10T01:00:00Z", "body": "ただのメモ"},
        ]
        health = summarize_health(parse_status_records(comments), "2026-07-11", False)
        self.assertTrue(health["no_records"])

    def test_jst_date_boundary(self):
        # UTC 07-09T23:00 = JST 07-10 08:00 → 前日扱いになる
        comments = [status_comment("evaluate", "start", "2026-07-09T23:00:00Z")]
        health = summarize_health(parse_status_records(comments), "2026-07-11", False)
        self.assertFalse(health["no_records"])

    def test_full_day_outage_detected_when_earlier_records_exist(self):
        # #422: 前日ぶんが0件でも、それ以前に stage レコードがあれば異常として報告する
        # （丸一日ループが止まった実例。#421 の週次利用上限の枯渇で観測）
        health = summarize_health([], "2026-07-11", True)
        self.assertFalse(health["no_records"])
        self.assertEqual(health["missing"], ["evaluate", "develop", "review"])

    def test_true_bootstrap_still_not_flagged(self):
        # 本当の導入直後（status issue に stage レコードが一度も無い）は異常にしない
        health = summarize_health([], "2026-07-11", False)
        self.assertTrue(health["no_records"])
        self.assertEqual(health["missing"], [])


NOW = datetime(2026, 9, 28, 1, 1, 0, tzinfo=timezone.utc)  # 10:01 JST


def pages_pr(number=446, ref="pages/2026-09-28-multi", sha="a" * 40,
             updated_at="2026-09-28T00:14:42Z"):
    return {"number": number, "updated_at": updated_at,
            "head": {"ref": ref, "sha": sha}}


def _minutes_ago(minutes):
    """--stdin モードは main() 内で実時刻を使うので、入力側を今から起こす。"""
    return (datetime.now(timezone.utc)
            - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_run(status="completed", conclusion="success", updated_at="2026-09-28T00:16:09Z"):
    return {"status": status, "conclusion": conclusion, "updated_at": updated_at}


class ClassifyPublishPrsTest(unittest.TestCase):
    """2026-09-28 の実測（#447）を再現する。9時の publish が PR #446 を作った19秒後に
    セッションを終え、CI は 09:16 に success になったが、10時の evaluate まで
    マージされなかった。`pages/` の open PR が1件ある点だけでは「走行中」と
    区別がつかない。"""

    def classify(self, prs, checks, now=NOW, quiescence=30):
        return classify_publish_prs(prs, checks, now, quiescence)

    def test_stopped_after_creating_the_pr_is_stalled(self):
        out = self.classify([pages_pr()], {"a" * 40: check_run()})
        self.assertEqual(len(out), 1)
        self.assertTrue(out[0]["stalled"])
        self.assertEqual(out[0]["number"], 446)
        self.assertEqual(out[0]["idle_minutes"], 44)  # 00:16:09Z → 01:01Z
        self.assertEqual(out[0]["checks_status"], "completed")
        self.assertEqual(out[0]["checks_conclusion"], "success")

    def test_ci_still_running_is_not_stalled(self):
        # publish-pages は「pending なら完了を待つ」と決めているので、CI が走って
        # いる間は止まっていない
        out = self.classify([pages_pr()], {"a" * 40: check_run(status="in_progress",
                                                               conclusion=None)})
        self.assertFalse(out[0]["stalled"])

    def test_recent_activity_is_not_stalled(self):
        out = self.classify([pages_pr(updated_at="2026-09-28T00:50:00Z")],
                            {"a" * 40: check_run(updated_at="2026-09-28T00:52:00Z")})
        self.assertFalse(out[0]["stalled"])
        self.assertEqual(out[0]["idle_minutes"], 9)

    def test_idle_measured_from_the_later_of_pr_and_ci(self):
        # PR の updated_at は古いが CI が直前に完了したケース。CI 側を採らないと
        # 「マージ直前の PR」を止まったと誤判定する
        out = self.classify([pages_pr(updated_at="2026-09-28T00:14:42Z")],
                            {"a" * 40: check_run(updated_at="2026-09-28T00:59:00Z")})
        self.assertFalse(out[0]["stalled"])
        self.assertEqual(out[0]["idle_minutes"], 2)

    def test_red_ci_left_untouched_is_stalled_and_carries_the_conclusion(self):
        # 赤いまま放置された PR も「誰も進めていない」。マージでなく修正が要ると
        # 分かるよう conclusion を出す
        out = self.classify([pages_pr()], {"a" * 40: check_run(conclusion="failure")})
        self.assertTrue(out[0]["stalled"])
        self.assertEqual(out[0]["checks_conclusion"], "failure")

    def test_missing_ci_run_falls_back_to_elapsed_time(self):
        # CI の run を引き当てられなくても、経過時間だけで止まりを検知する
        # （走行中扱いのままにすると永久に気づけない）
        out = self.classify([pages_pr()], {})
        self.assertTrue(out[0]["stalled"])
        self.assertIsNone(out[0]["checks_status"])

    def test_unparsable_timestamps_are_not_called_stalled(self):
        # 時刻が読めないときに止まった扱いにすると、走行中の publish の PR を
        # 別ステージがマージしにいく
        out = self.classify([pages_pr(updated_at="")], {})
        self.assertFalse(out[0]["stalled"])
        self.assertIsNone(out[0]["idle_minutes"])

    def test_hold_label_is_never_stalled(self):
        # GUARDRAILS の唯一の停止信号。ここを迂回すると、オーナーが止めた配信を
        # ループが勝手にマージする経路ができる
        pr = pages_pr()
        pr["labels"] = [{"name": "hold"}]
        out = self.classify([pr], {"a" * 40: check_run()})
        self.assertFalse(out[0]["stalled"])
        self.assertTrue(out[0]["hold"])

    def test_other_labels_do_not_block_the_judgement(self):
        pr = pages_pr()
        pr["labels"] = [{"name": "documentation"}]
        out = self.classify([pr], {"a" * 40: check_run()})
        self.assertTrue(out[0]["stalled"])
        self.assertFalse(out[0]["hold"])

    def test_draft_is_never_stalled(self):
        pr = pages_pr()
        pr["draft"] = True
        out = self.classify([pr], {"a" * 40: check_run()})
        self.assertFalse(out[0]["stalled"])
        self.assertTrue(out[0]["draft"])

    def test_non_pages_prs_are_ignored(self):
        out = self.classify([{"number": 441, "updated_at": "2026-09-01T00:00:00Z",
                              "head": {"ref": "feat/414-x", "sha": "b" * 40}}], {})
        self.assertEqual(out, [])

    def test_quiescence_boundary_is_inclusive(self):
        at_30 = self.classify([pages_pr(updated_at="2026-09-28T00:31:00Z")], {})
        self.assertTrue(at_30[0]["stalled"])
        self.assertEqual(at_30[0]["idle_minutes"], 30)
        at_29 = self.classify([pages_pr(updated_at="2026-09-28T00:32:00Z")], {})
        self.assertFalse(at_29[0]["stalled"])


class PublishStateTest(unittest.TestCase):
    def test_stalled_wins_over_running(self):
        prs = [{"stalled": False}, {"stalled": True}]
        self.assertEqual(publish_state_of(prs, None), "stalled")

    def test_open_pages_pr_that_is_not_stalled_is_running(self):
        self.assertEqual(publish_state_of([{"stalled": False}], None), "running")

    def test_main_build_in_flight_is_running(self):
        self.assertEqual(publish_state_of([], {"status": "in_progress"}), "running")

    def test_nothing_in_flight_is_idle(self):
        self.assertEqual(publish_state_of([], {"status": "completed"}), "idle")
        self.assertEqual(publish_state_of([], None), "idle")


class ParseApiTimeTest(unittest.TestCase):
    def test_parses_github_z_format_as_utc(self):
        self.assertEqual(parse_api_time("2026-09-28T00:14:42Z"),
                         datetime(2026, 9, 28, 0, 14, 42, tzinfo=timezone.utc))

    def test_missing_or_broken_values_are_none(self):
        for value in (None, "", "2026-09-28", "not a time", 12345):
            self.assertIsNone(parse_api_time(value), value)


class AssembleOutputPublishTest(unittest.TestCase):
    """出力そのもの（公開する JSON のキー）を固定する。"""

    def run_assemble(self, prs, pr_checks, pages_build=None):
        return assemble_output({"quiescence_minutes": 30}, "2026-09-28", False, None,
                               pages_build, prs, [], [], pr_checks=pr_checks, now=NOW)

    def test_stalled_publish_is_visible_in_the_output(self):
        out = self.run_assemble([pages_pr()], {"a" * 40: check_run()})
        self.assertEqual(out["publish_state"], "stalled")
        self.assertEqual([pr["number"] for pr in out["publish_prs"] if pr["stalled"]], [446])

    def test_running_publish_is_visible_in_the_output(self):
        out = self.run_assemble([pages_pr()], {"a" * 40: check_run(status="queued",
                                                                  conclusion=None)})
        self.assertEqual(out["publish_state"], "running")
        self.assertEqual(out["publish_prs"][0]["stalled"], False)

    def test_quiescence_minutes_comes_from_guardrails(self):
        # 44分アイドルの PR は cap 60 なら「まだ走行中」
        out = assemble_output({"quiescence_minutes": 60}, "2026-09-28", False, None, None,
                              [pages_pr()], [], [], pr_checks={"a" * 40: check_run()},
                              now=NOW)
        self.assertEqual(out["publish_state"], "running")

    def test_default_quiescence_when_guardrails_lacks_the_key(self):
        out = assemble_output({}, "2026-09-28", False, None, None, [pages_pr()], [], [],
                              pr_checks={"a" * 40: check_run()}, now=NOW)
        self.assertEqual(out["publish_state"], "stalled")


class FetchPrChecksTest(unittest.TestCase):
    """CI run の取得。判定の純関数が正しくても、ここが黙って空を返すと
    判定材料が PR の updated_at だけに縮退する（誤判定に直結する）。"""

    def fake_fetch(self, runs, log):
        def fetch_json(path, **kwargs):
            log.append(path)
            return {"workflow_runs": runs}
        return fetch_json

    def test_no_request_without_pages_prs(self):
        log = []
        out = fetch_pr_checks(self.fake_fetch([], log), [
            {"head": {"ref": "feat/x", "sha": "b" * 40}}])
        self.assertEqual(out, {})
        self.assertEqual(log, [])

    def test_asks_the_pr_workflow_not_the_pages_workflow(self):
        # pages.yml は main への push でしか走らないので、これを引くと
        # PR の head_sha は1件も当たらない
        log = []
        fetch_pr_checks(self.fake_fetch([], log), [pages_pr()])
        self.assertEqual(len(log), 1)
        self.assertIn("jekyll-build-check.yml", log[0])
        self.assertNotIn("pages.yml", log[0])

    def test_keeps_the_newest_run_per_sha(self):
        # 一覧は新しい順なので、同じ sha の最初の1件がその head の最新 run
        runs = [{"head_sha": "a" * 40, "status": "completed",
                 "conclusion": "success", "updated_at": "2026-09-28T00:16:09Z"},
                {"head_sha": "a" * 40, "status": "completed",
                 "conclusion": "failure", "updated_at": "2026-09-28T00:05:00Z"}]
        out = fetch_pr_checks(self.fake_fetch(runs, []), [pages_pr()])
        self.assertEqual(out["a" * 40]["conclusion"], "success")
        self.assertEqual(out["a" * 40]["updated_at"], "2026-09-28T00:16:09Z")

    def test_missing_workflow_returns_empty(self):
        out = fetch_pr_checks(lambda path, **kwargs: None, [pages_pr()])
        self.assertEqual(out, {})


class FetchDataWiringTest(unittest.TestCase):
    """取得した CI run が判定まで届いているか。ここが切れると出力は
    エラーにならずに静かに劣化する（#447 の再発）。"""

    def fetch_json(self, path, **kwargs):
        if path.startswith("contents/"):
            return None                      # 当日の投稿は main に無い
        if path == "pages":
            return None
        if path.startswith("actions/workflows/pages.yml"):
            return {"workflow_runs": []}
        if path.startswith("actions/workflows/jekyll-build-check.yml"):
            return {"workflow_runs": [{"head_sha": "a" * 40, "status": "completed",
                                       "conclusion": "success",
                                       "updated_at": "2026-09-28T00:16:09Z"}]}
        if path.startswith("pulls"):
            return [pages_pr()]
        if path.startswith("issues"):
            return []
        raise AssertionError("想定外のパス: %s" % path)

    def test_ci_timestamps_reach_the_judgement(self):
        out = fetch_data(self.fetch_json, {"quiescence_minutes": 30}, "2026-09-28",
                         datetime(2026, 9, 28, 10, 1, tzinfo=JST))
        self.assertEqual(out["publish_state"], "stalled")
        pr = out["publish_prs"][0]
        self.assertEqual(pr["checks_conclusion"], "success")
        # CI 完了 00:16:09Z から 01:01Z までの44分。PR の updated_at(00:14:42Z)
        # だけで測ると46分になるので、CI 側が届いていることがこの値で分かる
        self.assertEqual(pr["idle_minutes"], 44)

    def test_jst_now_is_converted_before_comparing_with_github_utc(self):
        # now を JST のまま渡しても、UTC の Z 形式と比べてずれない
        out = fetch_data(self.fetch_json, {"quiescence_minutes": 30}, "2026-09-28",
                         datetime(2026, 9, 28, 9, 20, tzinfo=JST))  # = 00:20Z
        self.assertEqual(out["publish_prs"][0]["idle_minutes"], 3)
        self.assertEqual(out["publish_state"], "running")


class StdinModeTest(unittest.TestCase):
    """`--stdin` は gh も REST も使えない環境の保険。ここで pr_checks を落とすと、
    判定材料が PR の updated_at だけに静かに縮退する。"""

    def run_main(self, payload):
        stdin, stdout, argv = sys.stdin, sys.stdout, sys.argv
        sys.stdin = io.StringIO(json.dumps(payload))
        sys.stdout = io.StringIO()
        sys.argv = ["check_state.py", "--stdin"]
        try:
            check_state.main()
            return json.loads(sys.stdout.getvalue())
        finally:
            sys.stdin, sys.stdout, sys.argv = stdin, stdout, argv

    def test_pr_checks_reaches_the_judgement(self):
        out = self.run_main({
            "post_exists": False,
            "prs": [pages_pr(updated_at=_minutes_ago(90))],
            "issues": [],
            "comments": [],
            "pr_checks": {"a" * 40: {"status": "in_progress", "conclusion": None,
                                     "updated_at": _minutes_ago(1)}},
        })
        # CI が走行中なので止まりではない。pr_checks を捨てると PR の updated_at
        # （90分前）だけで見て stalled になる
        self.assertEqual(out["publish_state"], "running")
        self.assertEqual(out["publish_prs"][0]["checks_status"], "in_progress")

    def test_works_without_pr_checks(self):
        out = self.run_main({"post_exists": False, "prs": [], "issues": [], "comments": []})
        self.assertEqual(out["publish_state"], "idle")


class AssembleOutputHealthTest(unittest.TestCase):
    """`has_earlier_records` の由来（status issue の総コメント数と `since` 絞り込み後の
    件数の差分）を assemble_output 経由（summarize_issues → summarize_health）で確かめる。
    summarize_health の単体テストは has_earlier_records を直接渡すので、その値の
    出どころ自体はここでしか踏まない。"""

    def run_assemble(self, status_issue_comments_total, fetched_comments, today="2026-07-11"):
        issues = [issue(25, title="📊 daily-loop status")]
        issues[0]["comments"] = status_issue_comments_total
        return assemble_output({}, today, True, None, None, [], issues, fetched_comments)

    def test_outage_detected_when_lifetime_total_exceeds_fetched_window(self):
        # 前日ぶんの取得が0件でも、status issue の総コメント数がそれより多ければ
        # （= since より前にも記録がある）異常として missing に出る
        out = self.run_assemble(status_issue_comments_total=620, fetched_comments=[])
        self.assertFalse(out["health"]["no_records"])
        self.assertEqual(out["health"]["missing"], ["evaluate", "develop", "review"])

    def test_true_bootstrap_when_totals_match(self):
        # 本当の導入直後は総コメント数と取得件数が一致する（前日以前の記録が無い）
        out = self.run_assemble(status_issue_comments_total=0, fetched_comments=[])
        self.assertTrue(out["health"]["no_records"])
        self.assertEqual(out["health"]["missing"], [])

    def test_healthy_day_with_only_yesterdays_records(self):
        # 総コメント数と取得件数が一致していても、前日ぶんの記録があれば正常判定になる
        comments = [
            status_comment("evaluate", "start", "2026-07-10T01:00:00Z"),
            status_comment("evaluate", "end", "2026-07-10T01:20:00Z", ok=True),
        ]
        out = self.run_assemble(status_issue_comments_total=2, fetched_comments=comments)
        self.assertFalse(out["health"]["no_records"])
        self.assertEqual(out["health"]["incomplete"], [])


class RecentCommentDigestsTest(unittest.TestCase):
    """#430: 1行目の stage レコードは切らない（後段の run が前段の結論を再利用できるように）。

    入力は 2026-09-26T01:12:24Z の evaluate end コメント（1行目 479字・全長 2,108字）の実物。
    本文と一緒に BODY_LIMIT=200 で切ると `...配信が丸ごと欠落 / #42` で終わり、
    グルーミング結論（`#407 #409` が作り直し不要）に届かなかった。
    """

    FIRST_LINE = (
        '{"stage": "evaluate", "phase": "end", "ok": true, "summary": "open issue 15/10（cap 超過でグルーミングのみ、ペルソナ subagent は起動せず）。Step 0 の異常対応として ops issue 2件起票: #421 週次利用上限の枯渇で約42時間ループ停止・2026-09-25 の配信が丸ごと欠落 / #422 health が全ステージ無記録を導入直後と同一視して正常報告する欠陥。グルーミング4件: #407 #409（作業完了済みで draft のまま滞留・作り直し不要）/ #408（PR #416 と同一ファイルの順序）/ #291（hold 17日・理由コメント無し・M4 が停止）。オーナーへ Slack DM 1通", "reflect": "PR #423（ノートに proxy が塞ぐ /search/* と、ループ停止の原因を辿る list_triggers → get_session の経路を追記。CI green・ready 化済み）"}'
    )
    COMMENT = {"created_at": "2026-09-26T01:12:24Z",
               "body": FIRST_LINE + "\n\n## やったこと\n\n" + "詳細" * 500}

    def test_record_is_not_truncated(self):
        digest = recent_comment_digests([self.COMMENT])[0]
        self.assertEqual(digest["record"]["stage"], "evaluate")
        self.assertIn("#407 #409", digest["record"]["summary"])
        self.assertIn("作り直し不要", digest["record"]["summary"])
        self.assertIn("PR #423", digest["record"]["reflect"])

    def test_body_holds_the_rest_and_is_still_truncated(self):
        digest = recent_comment_digests([self.COMMENT])[0]
        self.assertNotIn('"stage"', digest["body"])
        self.assertTrue(digest["body"].startswith("## やったこと"))
        self.assertEqual(len(digest["body"]), check_state.BODY_LIMIT)

    def test_non_record_comment_keeps_the_old_shape(self):
        digest = recent_comment_digests([{"created_at": "2026-09-26T02:00:00Z",
                                          "body": "人間のコメント" * 100}])[0]
        self.assertNotIn("record", digest)
        self.assertEqual(len(digest["body"]), check_state.BODY_LIMIT)

    def test_keeps_only_the_latest_comments(self):
        comments = [status_comment("develop", "start", f"2026-09-26T{i:02d}:00:00Z")
                    for i in range(13)]
        digests = recent_comment_digests(comments)
        self.assertEqual(len(digests), check_state.COMMENT_LIMIT)
        self.assertEqual(digests[-1]["created_at"], "2026-09-26T12:00:00Z")

    def test_audit_record_is_carried_too(self):
        """audit は週次で health 集計の対象外だが、結論の受け渡しには載せる
        （GUARDRAILS.md が認める stage であり、後段が読み返せないと受け渡しの穴になる）"""
        comment = {"created_at": "2026-09-20T02:30:00Z",
                   "body": json.dumps({"stage": "audit", "phase": "end",
                                       "summary": "監査3件"}, ensure_ascii=False) + "\n本文"}
        digest = recent_comment_digests([comment])[0]
        self.assertEqual(digest["record"]["stage"], "audit")

    def test_audit_record_does_not_break_health(self):
        comments = [{"created_at": "2026-07-10T02:30:00Z",
                     "body": json.dumps({"stage": "audit", "phase": "end", "ok": True})},
                    status_comment("evaluate", "start", "2026-07-10T01:00:00Z")]
        health = summarize_health(parse_status_records(comments), "2026-07-11", False)
        self.assertEqual(sorted(health["stages"]), ["develop", "evaluate", "review"])
        self.assertTrue(health["stages"]["evaluate"]["start"])

    def test_output_carries_the_grooming_conclusion(self):
        issues = [issue(25, title="📊 daily-loop status")]
        issues[0]["comments"] = 1
        out = assemble_output({}, "2026-09-27", True, None, None, [], issues, [self.COMMENT])
        self.assertIn("#407 #409", json.dumps(out, ensure_ascii=False))


class ParseStatusRecordTest(unittest.TestCase):
    def test_reads_stage_record(self):
        self.assertEqual(parse_status_record('{"stage": "develop", "phase": "start"}\n本文'),
                         {"stage": "develop", "phase": "start"})

    def test_rejects_non_json_and_unknown_stage(self):
        self.assertIsNone(parse_status_record("ただのコメント"))
        self.assertIsNone(parse_status_record('{"stage": "publish"}'))
        self.assertIsNone(parse_status_record('["develop"]'))
        self.assertIsNone(parse_status_record(""))


class ParseLinkHeaderTest(unittest.TestCase):
    def test_extracts_rel_urls(self):
        header = ('<https://api.github.com/repositories/1/issues?page=2>; rel="next", '
                   '<https://api.github.com/repositories/1/issues?page=5>; rel="last"')
        links = parse_link_header(header)
        self.assertEqual(links["next"], "https://api.github.com/repositories/1/issues?page=2")
        self.assertEqual(links["last"], "https://api.github.com/repositories/1/issues?page=5")

    def test_empty_header_returns_empty_dict(self):
        self.assertEqual(parse_link_header(""), {})
        self.assertEqual(parse_link_header(None), {})

    def test_single_link(self):
        header = '<https://api.github.com/repositories/1/issues?page=2>; rel="next"'
        self.assertEqual(parse_link_header(header),
                         {"next": "https://api.github.com/repositories/1/issues?page=2"})


class WithPageTest(unittest.TestCase):
    def test_adds_page_param_when_absent(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&per_page=100"
        self.assertEqual(with_page(url, 2),
                         "https://api.github.com/repos/o/r/issues?state=open&per_page=100&page=2")

    def test_replaces_existing_page_param(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&page=2&per_page=100"
        self.assertEqual(with_page(url, 3),
                         "https://api.github.com/repos/o/r/issues?state=open&page=3&per_page=100")

    def test_no_query_string_yet(self):
        self.assertEqual(with_page("https://api.github.com/repos/o/r/pages", 2),
                         "https://api.github.com/repos/o/r/pages?page=2")


class SinceParamTest(unittest.TestCase):
    """`since` は URL エスケープの要らない UTC の Z 形式にする。

    `+09:00` を生で入れると `+` がスペース扱いになり、GitHub は 422 で弾かずに
    別の時刻として受け取る（実測でカットオフが16時間ずれ、evaluate が毎朝
    health の missing に落ちた）。"""

    JST = timezone(timedelta(hours=9))

    def test_is_utc_z_format_without_escapable_chars(self):
        now = datetime(2026, 9, 21, 12, 7, 31, 625372, tzinfo=self.JST)
        self.assertEqual(since_param(now), "2026-09-19T15:00:00Z")

    def test_never_emits_plus_or_microseconds(self):
        for hour in range(24):
            value = since_param(datetime(2026, 9, 21, hour, 30, 5, 1234, tzinfo=self.JST))
            self.assertNotIn("+", value)
            self.assertNotIn(".", value)
            self.assertTrue(value.endswith("Z"), value)

    def test_cutoff_is_previous_midnight_jst(self):
        # 前日 00:00 JST = 前々日 15:00 UTC
        now = datetime(2026, 9, 21, 23, 59, tzinfo=self.JST)
        self.assertEqual(since_param(now), "2026-09-19T15:00:00Z")


class FakeResponse:
    def __init__(self, payload, link=None):
        self._body = json.dumps(payload).encode()
        self.headers = {"Link": link} if link else {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code):
    return urllib.error.HTTPError("https://api.github.com/x", code, "boom", {},
                                  None)


class ApiJsonTest(unittest.TestCase):
    """バグ本体があった api_json のループと分岐を踏む。"""

    def call(self, path, responses, **kwargs):
        """responses を順に返す fake urlopen で api_json を回し、要求 URL を記録する。"""
        seen = []

        def fake_urlopen(request, timeout=None):
            seen.append(request.full_url)
            result = responses.pop(0)
            if isinstance(result, urllib.error.HTTPError):
                result.read = lambda: b"{}"
                raise result
            return result

        with mock.patch.object(check_state.urllib.request, "urlopen", fake_urlopen):
            return api_json(path, **kwargs), seen

    def test_follows_pages_by_number_not_link_url(self):
        # GitHub が返す next は /repositories/{id}/ 形式。proxy がこの形を 403 で弾くので
        # 辿ってはいけない（これを辿っていたのが修正前のバグ）
        link = ('<https://api.github.com/repositories/999/issues?page=2>; rel="next"')
        result, seen = self.call(
            "repos/o/r/issues?state=open&per_page=100",
            [FakeResponse([{"number": 1}], link), FakeResponse([{"number": 2}])])
        self.assertEqual(result, [{"number": 1}, {"number": 2}])
        self.assertEqual(seen, [
            "https://api.github.com/repos/o/r/issues?state=open&per_page=100",
            "https://api.github.com/repos/o/r/issues?state=open&per_page=100&page=2",
        ])
        for url in seen:
            self.assertNotIn("/repositories/", url)

    def test_stops_when_no_next_link(self):
        result, seen = self.call("repos/o/r/pulls", [FakeResponse([{"number": 1}])])
        self.assertEqual(result, [{"number": 1}])
        self.assertEqual(len(seen), 1)

    def test_paginate_false_ignores_next_link(self):
        link = '<https://api.github.com/repositories/999/x?page=2>; rel="next"'
        result, seen = self.call("repos/o/r/x", [FakeResponse([{"a": 1}], link)],
                                 paginate=False)
        self.assertEqual(result, [{"a": 1}])
        self.assertEqual(len(seen), 1)

    def test_dict_response_returned_as_is(self):
        result, _ = self.call("repos/o/r/pages", [FakeResponse({"html_url": "u"})])
        self.assertEqual(result, {"html_url": "u"})

    def test_ok_missing_swallows_listed_status(self):
        result, _ = self.call("repos/o/r/pages", [http_error(403)], ok_missing=(403,))
        self.assertIsNone(result)

    def test_ok_404_swallows_404(self):
        result, _ = self.call("repos/o/r/contents/x", [http_error(404)], ok_404=True)
        self.assertIsNone(result)

    def test_unlisted_status_raises(self):
        with self.assertRaises(RuntimeError):
            self.call("repos/o/r/pages", [http_error(403)])
        with self.assertRaises(RuntimeError):
            self.call("repos/o/r/x", [http_error(500)], ok_404=True, ok_missing=(403,))


class GhJsonTest(unittest.TestCase):
    """gh 経路でも ok_missing を受けて捨てない（REST 経路と挙動を揃える）。"""

    def run_with(self, stderr, returncode=1, **kwargs):
        completed = mock.Mock(returncode=returncode, stdout="{}", stderr=stderr)
        with mock.patch.object(check_state.subprocess, "run", return_value=completed):
            return gh_json("repos/o/r/pages", **kwargs)

    def test_ok_missing_swallows_403(self):
        self.assertIsNone(self.run_with("HTTP 403: Forbidden", ok_missing=(403,)))

    def test_ok_missing_does_not_swallow_other_errors(self):
        with self.assertRaises(RuntimeError):
            self.run_with("HTTP 500: Server Error", ok_missing=(403,))

    def test_still_raises_without_ok_missing(self):
        with self.assertRaises(RuntimeError):
            self.run_with("HTTP 403: Forbidden")

    def test_status_digits_elsewhere_in_message_do_not_count(self):
        # URL やメッセージ中の 403 を HTTP ステータスと取り違えない
        with self.assertRaises(RuntimeError):
            self.run_with("HTTP 500: could not resolve issues/403/comments",
                          ok_missing=(403,))

    def test_ok_404_matches_only_http_404(self):
        self.assertIsNone(self.run_with("HTTP 404: Not Found", ok_404=True))
        with self.assertRaises(RuntimeError):
            self.run_with("HTTP 500: run 404 failed", ok_404=True)


class ResolveRepoTest(unittest.TestCase):
    """origin の URL 表記ゆれから owner/repo を取り出す。"""

    def resolve(self, url):
        completed = mock.Mock(stdout=url + "\n")
        with mock.patch.object(check_state.subprocess, "run",
                               return_value=completed) as run:
            result = check_state.resolve_repo()
        self.last_call = run.call_args
        return result

    def test_asks_git_at_the_repo_root_not_cwd(self):
        """cwd がどこでも同じ答えになるよう `git -C <repo root>` で引く。"""
        self.resolve("https://github.com/ha1f/news.git")
        argv = self.last_call.args[0]
        root = str(Path(check_state.__file__).resolve().parents[4])
        self.assertEqual(argv[:3], ["git", "-C", root])
        self.assertIn("remote.origin.url", argv)

    def test_https_with_and_without_git_suffix(self):
        self.assertEqual(self.resolve("https://github.com/ha1f/news.git"), ("ha1f", "news"))
        self.assertEqual(self.resolve("https://github.com/ha1f/news"), ("ha1f", "news"))

    def test_ssh_form(self):
        self.assertEqual(self.resolve("git@github.com:ha1f/news.git"), ("ha1f", "news"))

    def test_trailing_slash(self):
        self.assertEqual(self.resolve("https://github.com/ha1f/news/"), ("ha1f", "news"))

    def test_non_github_url_raises(self):
        with self.assertRaises(RuntimeError):
            self.resolve("https://example.com/foo")


if __name__ == "__main__":
    unittest.main()
