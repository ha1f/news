#!/usr/bin/env python3
"""wait_for_run.py の単体テスト。

回し方: cd .claude/scripts && python3 -m unittest discover -p 'test_*.py'

#426 の受け入れ条件6「スクリプトには最低限の自己検証（40桁チェックの単体テスト）を
同梱する」に対応。期待値はテスト側に直書きし、対象モジュールの定数から作らない
（定数を削る変更で検査の対象まで消えないように）。
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wait_for_run as w  # noqa: E402

FULL = "7819e16c4e12c9f83e6cbb4f40810825980837be"
SCRIPT = Path(__file__).resolve().parent / "wait_for_run.py"


def run_payload(status="completed", conclusion="success", **extra):
    run = {"id": 42, "status": status, "conclusion": conclusion,
           "html_url": "https://github.com/o/r/actions/runs/42",
           "created_at": "2026-10-02T03:00:00Z", "run_attempt": 1}
    run.update(extra)
    return {"total_count": 1, "workflow_runs": [run]}


class ExpandShaTest(unittest.TestCase):
    """40桁でない SHA を API に渡さないことを固定する（#426 の中心）。"""

    def test_full_sha_passes_through(self):
        self.assertEqual(w.expand_sha(FULL), FULL)

    def test_uppercase_full_sha_is_normalized(self):
        self.assertEqual(w.expand_sha(FULL.upper()), FULL)

    def test_surrounding_whitespace_is_stripped(self):
        self.assertEqual(w.expand_sha(f"  {FULL}\n"), FULL)

    def test_short_sha_without_git_raises(self):
        # git が解決できない短縮 SHA は例外。API を叩く前に止まる
        with self.assertRaises(ValueError) as caught:
            w.expand_sha("141c828", git_root="/nonexistent-repo-for-test")
        self.assertIn("40桁", str(caught.exception))

    def test_41_hex_is_not_accepted_as_full(self):
        with self.assertRaises(ValueError):
            w.expand_sha("0" * 41, git_root="/nonexistent-repo-for-test")

    def test_39_hex_is_not_accepted_as_full(self):
        with self.assertRaises(ValueError):
            w.expand_sha("0" * 39, git_root="/nonexistent-repo-for-test")

    def test_non_hex_40_chars_is_rejected(self):
        with self.assertRaises(ValueError):
            w.expand_sha("z" * 40, git_root="/nonexistent-repo-for-test")

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            w.expand_sha("")

    def test_ref_is_expanded_via_git(self):
        # この repo 自身で HEAD を展開できる（git rev-parse 経路の確認）
        self.assertRegex(w.expand_sha("HEAD"), r"\A[0-9a-f]{40}\Z")


class RunsPathTest(unittest.TestCase):
    def test_path_carries_full_sha_and_workflow(self):
        path = w.runs_path("o", "r", "pages.yml", FULL)
        self.assertEqual(
            path,
            "repos/o/r/actions/workflows/pages.yml/runs"
            f"?head_sha={FULL}&per_page=100")


class PickLatestTest(unittest.TestCase):
    def test_empty_list_is_none(self):
        self.assertIsNone(w.pick_latest({"total_count": 0, "workflow_runs": []}))

    def test_none_payload_is_none(self):
        self.assertIsNone(w.pick_latest(None))

    def test_total_count_without_runs_is_none(self):
        # total_count だけが非 0 のレスポンスを「run が在る」と読まない
        self.assertIsNone(w.pick_latest({"total_count": 3, "workflow_runs": []}))

    def test_picks_newest_created_at(self):
        payload = {"workflow_runs": [
            {"id": 1, "created_at": "2026-10-01T00:00:00Z", "run_attempt": 1},
            {"id": 2, "created_at": "2026-10-02T00:00:00Z", "run_attempt": 1},
        ]}
        self.assertEqual(w.pick_latest(payload)["id"], 2)

    def test_picks_latest_attempt_over_created_at(self):
        payload = {"workflow_runs": [
            {"id": 1, "created_at": "2026-10-02T00:00:00Z", "run_attempt": 1},
            {"id": 2, "created_at": "2026-10-01T00:00:00Z", "run_attempt": 2},
        ]}
        self.assertEqual(w.pick_latest(payload)["id"], 2)


class ClassifyTest(unittest.TestCase):
    def test_none_run_is_not_found(self):
        self.assertEqual(w.classify(None), ("not_found", None))

    def test_queued_is_running(self):
        self.assertEqual(w.classify({"status": "queued", "conclusion": None}),
                         ("running", None))

    def test_in_progress_is_running(self):
        self.assertEqual(w.classify({"status": "in_progress", "conclusion": None}),
                         ("running", None))

    def test_completed_success(self):
        self.assertEqual(w.classify({"status": "completed", "conclusion": "success"}),
                         ("success", "success"))

    def test_completed_failure_is_failed(self):
        self.assertEqual(w.classify({"status": "completed", "conclusion": "failure"}),
                         ("failed", "failure"))

    def test_completed_cancelled_is_failed(self):
        self.assertEqual(w.classify({"status": "completed", "conclusion": "cancelled"}),
                         ("failed", "cancelled"))

    def test_completed_without_conclusion_is_failed(self):
        self.assertEqual(w.classify({"status": "completed", "conclusion": None}),
                         ("failed", None))


class WaitTest(unittest.TestCase):
    """fetch をモックして待ちのループを固定する。呼び出し引数もアサートする。"""

    def _fetcher(self, payloads):
        calls = []

        def fetch(path):
            calls.append(path)
            return payloads[min(len(calls) - 1, len(payloads) - 1)]

        return fetch, calls

    def test_success_returns_immediately(self):
        fetch, calls = self._fetcher([run_payload()])
        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=10,
                        appear_timeout=5, once=False)
        self.assertEqual(result["state"], "success")
        self.assertEqual(result["polls"], 1)
        self.assertEqual(result["run_id"], 42)
        # 渡した 40桁の SHA がそのまま API のパスに乗っている
        self.assertEqual(calls, [w.runs_path("o", "r", "pages.yml", FULL)])

    def test_failure_is_distinguished_from_success(self):
        fetch, _ = self._fetcher([run_payload(conclusion="failure")])
        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=10,
                        appear_timeout=5, once=False)
        self.assertEqual(result["state"], "failed")
        self.assertEqual(result["conclusion"], "failure")

    def test_waits_until_completed(self):
        fetch, calls = self._fetcher([
            run_payload(status="queued", conclusion=None),
            run_payload(status="in_progress", conclusion=None),
            run_payload(),
        ])
        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=10,
                        appear_timeout=5, once=False)
        self.assertEqual(result["state"], "success")
        self.assertEqual(result["polls"], 3)
        self.assertEqual(len(calls), 3)

    def test_missing_run_is_not_found_not_running(self):
        # 「run が無い」と「run が未完了」を分ける（#426 の受け入れ条件3）
        fetch, _ = self._fetcher([{"total_count": 0, "workflow_runs": []}])
        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=10,
                        appear_timeout=0, once=False)
        self.assertEqual(result["state"], "not_found")
        self.assertIsNone(result["run_id"])
        self.assertIn("見つかりません", result["message"])

    def test_missing_run_returns_at_appear_timeout_not_at_timeout(self):
        # appear_timeout を無視して全体の timeout まで待つ実装だと、SHA 違いに気づくのが
        # 遅れる（#426 の症状そのもの）。1回で返ることで固定する
        fetch, calls = self._fetcher([{"total_count": 0, "workflow_runs": []}])
        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=1.0,
                        appear_timeout=0, once=False)
        self.assertEqual(result["state"], "not_found")
        self.assertEqual(result["polls"], 1)
        self.assertEqual(len(calls), 1)

    def test_running_timeout_is_running_not_not_found(self):
        fetch, _ = self._fetcher([run_payload(status="in_progress", conclusion=None)])
        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=0,
                        appear_timeout=0, once=False)
        self.assertEqual(result["state"], "running")
        self.assertEqual(result["run_id"], 42)
        self.assertIn("待てば完了", result["message"])

    def test_once_does_not_poll_twice(self):
        # 2回目の取得が来たら即座に失敗させる（once を無視する実装がハングでなく
        # red で出るように。LESSONS: 検証器が止まると結果を読めない）
        calls = []

        def fetch(path):
            calls.append(path)
            if len(calls) > 1:
                raise AssertionError("--once なのに2回目の取得が走った")
            return run_payload(status="in_progress", conclusion=None)

        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=999,
                        appear_timeout=999, once=True)
        self.assertEqual(result["state"], "running")
        self.assertEqual(len(calls), 1)

    def test_once_on_missing_run_says_not_yet(self):
        calls = []

        def fetch(path):
            calls.append(path)
            if len(calls) > 1:
                raise AssertionError("--once なのに2回目の取得が走った")
            return {"total_count": 0, "workflow_runs": []}

        result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=0, timeout=999,
                        appear_timeout=999, once=True)
        self.assertEqual(result["state"], "not_found")
        self.assertIn("まだ", result["message"])


class ExitCodeTest(unittest.TestCase):
    def test_exit_codes_are_distinct(self):
        self.assertEqual(sorted(w.EXIT.values()), [0, 1, 2, 3, 4])
        self.assertEqual(w.EXIT["success"], 0)
        self.assertEqual(w.EXIT["failed"], 1)
        self.assertEqual(w.EXIT["usage"], 2)
        self.assertEqual(w.EXIT["not_found"], 3)
        self.assertEqual(w.EXIT["running"], 4)

    def test_short_sha_exits_2_without_touching_the_api(self):
        # 実プロセスで確認する（短縮 SHA は API に到達する前に落ちる）。
        # --git-root を解決できない場所に向けることで、ローカルに object が来ても
        # 展開が成功して偽 red にならないようにする
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "pages.yml", "141c828",
             "--git-root", "/nonexistent-repo-for-test", "--once", "--quiet"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["state"], "usage")
        self.assertIn("40桁", payload["message"])
        # usage 経路でも出力のキーが揃っている（`jq -r .transport` が落ちない）
        self.assertEqual(
            sorted(payload),
            sorted(["state", "sha", "workflow", "repo", "run_id", "status", "conclusion",
                    "html_url", "polls", "waited_seconds", "transport", "message"]))

    def test_other_repo_with_short_sha_exits_2(self):
        # ローカルの commit に展開した40桁を別 repo に投げると静かに not_found になる
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "pages.yml", "HEAD",
             "--repo", "someone-else/other-repo", "--once", "--quiet"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["state"], "usage")
        self.assertIn("--repo", payload["message"])


class DefaultsTest(unittest.TestCase):
    """実測に由来する既定値を固定する（#426 の受け入れ条件4）。

    期待値はテスト側に直書きする（対象モジュールの定数から作ると、定数を変える
    変更で検査の対象まで一緒に動いて緑のまま通る）。由来の実測:
    build は push から2分弱、マージ後の pages.yml は1分未満、run の出現は最大19秒。
    """

    def test_default_interval_is_30_seconds(self):
        self.assertEqual(w.DEFAULT_INTERVAL, 30)

    def test_default_timeout_is_600_seconds(self):
        self.assertEqual(w.DEFAULT_TIMEOUT, 600)

    def test_default_appear_timeout_is_120_seconds(self):
        self.assertEqual(w.DEFAULT_APPEAR_TIMEOUT, 120)

    def test_appear_timeout_is_shorter_than_timeout(self):
        # run の出現待ちが全体の上限と同じだと、SHA 違いに気づくのが遅れる
        self.assertLess(w.DEFAULT_APPEAR_TIMEOUT, w.DEFAULT_TIMEOUT)

    def test_interval_covers_the_measured_completion_times(self):
        # 間隔が長すぎると build（約2分）の完了に気づくのが遅れ、
        # 上限が短すぎると完了前に打ち切る
        self.assertLessEqual(w.DEFAULT_INTERVAL, 60)
        self.assertGreaterEqual(w.DEFAULT_TIMEOUT, 300)

    def test_parser_defaults_match_the_constants(self):
        args = w.build_parser().parse_args(["pages.yml", FULL])
        self.assertEqual(args.interval, 30)
        self.assertEqual(args.timeout, 600)
        self.assertEqual(args.appear_timeout, 120)
        self.assertFalse(args.once)
        self.assertFalse(args.no_gh)

    def test_wait_sleeps_between_polls(self):
        # time.sleep を外す変更で、間隔の既定値が意味を失う。
        # 終了条件は取得回数で決める（slept の件数で決めると、sleep を外した実装が
        # ハングして結果を読めなくなる。LESSONS: 検証器が止まると判定できない）
        slept, calls = [], []

        def fetch(path):
            calls.append(path)
            return (run_payload() if len(calls) >= 3
                    else run_payload(status="in_progress", conclusion=None))

        original = w.time.sleep
        w.time.sleep = slept.append
        try:
            result = w.wait(fetch, "o", "r", "pages.yml", FULL, interval=7,
                            timeout=600, appear_timeout=120, once=False)
        finally:
            w.time.sleep = original
        self.assertEqual(result["state"], "success")
        self.assertEqual(len(calls), 3)
        self.assertEqual(slept, [7, 7])


class FetcherTest(unittest.TestCase):
    def test_prefer_gh_false_uses_rest(self):
        _, state = w.make_fetcher(prefer_gh=False)
        self.assertEqual(state["transport"], "rest")

    def test_no_gh_flag_is_parsed(self):
        self.assertTrue(w.build_parser().parse_args(["pages.yml", FULL, "--no-gh"]).no_gh)


class ExpandShaRepoScopeTest(unittest.TestCase):
    def test_allow_git_false_rejects_short_sha(self):
        with self.assertRaises(ValueError) as caught:
            w.expand_sha("141c828", allow_git=False)
        self.assertIn("--repo", str(caught.exception))

    def test_allow_git_false_still_accepts_full_sha(self):
        self.assertEqual(w.expand_sha(FULL, allow_git=False), FULL)


class ResolveRepoTest(unittest.TestCase):
    def test_explicit_repo_is_split(self):
        self.assertEqual(w.resolve_repo("ha1f/news"), ("ha1f", "news"))

    def test_explicit_repo_without_slash_raises(self):
        with self.assertRaises(ValueError):
            w.resolve_repo("news")

    def test_default_resolves_from_origin(self):
        owner, repo = w.resolve_repo()
        self.assertTrue(owner and repo)


if __name__ == "__main__":
    unittest.main()
