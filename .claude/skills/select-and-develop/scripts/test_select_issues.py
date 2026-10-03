#!/usr/bin/env python3
"""select_issues.py の純関数のユニットテスト。実行: python3 test_select_issues.py"""
import io
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import select_issues
from select_issues import (bot_exclusion_reliable, build_candidates, collect_recent_records,
                           count_open_issues, load_summarize_issues, parse_guardrails,
                           parse_link_header, resolve_status_comments, since_param, with_page)


def run_main(payload):
    """--stdin モードで main() を通し、標準出力の JSON を返す"""
    stdin, stdout, argv = sys.stdin, sys.stdout, sys.argv
    sys.stdin = io.StringIO(json.dumps(payload))
    sys.stdout = io.StringIO()
    sys.argv = ["select_issues.py", "--stdin"]
    try:
        code = select_issues.main()
        out = sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout, sys.argv = stdin, stdout, argv
    assert code == 0, f"main() が {code} を返しました"
    return json.loads(out)


def issue(number, title="t", assoc="OWNER", labels=(), created="2026-07-01T00:00:00Z",
          pr=False, login=None, user_type=None):
    data = {
        "number": number,
        "title": title,
        "labels": [{"name": name} for name in labels],
        "created_at": created,
    }
    if assoc is not None:
        data["author_association"] = assoc
    if login is not None or user_type is not None:
        data["user"] = {}
        if login is not None:
            data["user"]["login"] = login
        if user_type is not None:
            data["user"]["type"] = user_type
    if pr:
        data["pull_request"] = {}
    return data


def pr(number, body="", draft=True, branch="feature", labels=None):
    data = {"number": number, "body": body, "draft": draft,
            "head": {"ref": branch}}
    if labels is not None:  # MCP はラベルが無い PR でキー自体を返さない
        data["labels"] = labels
    return data


class BuildCandidatesTest(unittest.TestCase):
    def test_excludes_untrusted_hold_status_and_prs(self):
        issues = [
            issue(1, assoc="NONE"),
            issue(2, labels=["hold"]),
            issue(3, title="📊 daily-loop status"),
            issue(4, pr=True),
            issue(5),
        ]
        status, in_progress, backlog = build_candidates(issues, [])
        self.assertEqual(status, 3)
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [5])

    def test_sorted_oldest_first(self):
        issues = [
            issue(1, created="2026-07-03T00:00:00Z"),
            issue(2, created="2026-07-01T00:00:00Z"),
            issue(3, created="2026-07-02T00:00:00Z"),
        ]
        _, _, backlog = build_candidates(issues, [])
        self.assertEqual([e["number"] for e in backlog], [2, 3, 1])

    def test_linked_open_pr_moves_issue_to_in_progress(self):
        issues = [issue(1), issue(2)]
        prs = [pr(10, body="Closes #1", draft=True), pr(11, body="refs #99")]
        _, in_progress, backlog = build_candidates(issues, prs)
        self.assertEqual([e["number"] for e in in_progress], [1])
        self.assertEqual(in_progress[0]["linked_open_prs"],
                         [{"number": 10, "draft": True, "hold": False}])
        self.assertEqual([e["number"] for e in backlog], [2])

    def test_link_keywords_variants(self):
        issues = [issue(1), issue(2), issue(3)]
        prs = [pr(10, body="Fixes #1"), pr(11, body="Refs #2"), pr(12, body="resolved #3")]
        _, in_progress, _ = build_candidates(issues, prs)
        self.assertEqual([e["number"] for e in in_progress], [1, 2, 3])

    def test_bare_issue_number_does_not_link(self):
        # キーワードの無い「#1」は言及であってリンクではない
        _, in_progress, backlog = build_candidates(
            [issue(1)], [pr(10, body="関連: #1 の議論を参照")])
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_quoted_link_keywords_do_not_link(self):
        """コードとして引用したリンクキーワードは linked PR を作らない (#473)。

        偽リンクが付くと、その issue は in_progress に振られて backlog から外れ、
        実装 run に拾われなくなる。実測 (PR #471): 正規表現の挙動表と他 PR の
        引用だけで #408 / #421 にリンクが付いていた
        """
        body = ("~~~\n'Refs #1' -> ['1']\n~~~\n"
                "散文での引用も同じ: `Closes #2`\n")
        _, in_progress, backlog = build_candidates(
            [issue(1), issue(2)], [pr(10, body=body, branch="improve/no-number")])
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [1, 2])

    def test_prose_link_survives_code_stripping(self):
        """コードを落とす処理が、実際に進める `Closes #N` を巻き添えにしない"""
        body = "```\nCloses #1\n```\n\n実際に進めるのはこちら。Closes #2\n"
        _, in_progress, backlog = build_candidates(
            [issue(1), issue(2)], [pr(10, body=body, branch="improve/no-number")])
        self.assertEqual([e["number"] for e in in_progress], [2])
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_branch_name_links(self):
        for branch in ("feat/1-something", "1-something", "fix/1_something"):
            with self.subTest(branch=branch):
                _, in_progress, _ = build_candidates([issue(1)],
                                                     [pr(10, branch=branch)])
                self.assertEqual([e["number"] for e in in_progress], [1])

    def test_branch_without_issue_number_does_not_link(self):
        _, in_progress, backlog = build_candidates(
            [issue(1)], [pr(10, branch="improve/develop-loop-env")])
        self.assertEqual(in_progress, [])
        self.assertEqual([e["number"] for e in backlog], [1])

    def test_same_issue_is_not_linked_twice(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", branch="feat/1-x")])
        self.assertEqual(len(in_progress[0]["linked_open_prs"]), 1)

    def test_collaborators_fallback_when_author_association_missing(self):
        issues = [
            issue(1, assoc=None, login="owner-user"),
            issue(2, assoc=None, login="external-user"),
            issue(3, assoc=None, login="member-user"),
        ]
        _, _, backlog = build_candidates(issues, [],
                                         collaborators=["owner-user", "member-user"])
        self.assertEqual([e["number"] for e in backlog], [1, 3])

    def test_no_collaborators_no_assoc_is_fail_closed(self):
        issues = [issue(1, assoc=None, login="someone")]
        _, _, backlog = build_candidates(issues, [])
        self.assertEqual(backlog, [])

    def test_author_association_takes_precedence_over_collaborators(self):
        issues = [
            issue(1, assoc="NONE", login="owner-user"),
            issue(2, assoc="OWNER", login="unknown"),
        ]
        _, _, backlog = build_candidates(issues, [],
                                         collaborators=["owner-user"])
        self.assertEqual([e["number"] for e in backlog], [2])


class PullRequestLabelsTest(unittest.TestCase):
    """MCP は labels を文字列リストで返し、ラベルが無い PR ではキー自体が無い。
    gh CLI は dict のリスト。どちらでも hold を拾えること"""

    def test_string_labels(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", labels=["hold"])])
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_dict_labels(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", labels=[{"name": "hold"}])])
        self.assertTrue(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_missing_labels_key(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1")])
        self.assertFalse(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_other_labels_do_not_set_hold(self):
        _, in_progress, _ = build_candidates(
            [issue(1)], [pr(10, body="Closes #1", labels=["bug", "enhancement"])])
        self.assertFalse(in_progress[0]["linked_open_prs"][0]["hold"])

    def test_hold_is_per_pr_not_shared(self):
        issues = [issue(1), issue(2)]
        prs = [pr(10, body="Closes #1", labels=["hold"]),
               pr(11, body="Closes #2", labels=[])]
        _, in_progress, _ = build_candidates(issues, prs)
        self.assertEqual([e["linked_open_prs"][0]["hold"] for e in in_progress],
                         [True, False])

    def test_one_pr_closing_two_issues_carries_hold_to_both(self):
        _, in_progress, _ = build_candidates(
            [issue(1), issue(2)],
            [pr(10, body="Closes #1\nCloses #2", labels=["hold"])])
        self.assertEqual([e["linked_open_prs"][0]["hold"] for e in in_progress],
                         [True, True])


class ParseGuardrailsTest(unittest.TestCase):
    def test_parses_yaml_block(self):
        text = (
            "# GUARDRAILS\n\n```yaml\n"
            "quiescence_minutes: 30\n"
            "auto_merge_mode: dry-run  # dry-run | enabled\n"
            "protected_paths:\n"
            "  - .github/workflows/**\n"
            "  - .claude/GUARDRAILS.md\n"
            "```\n本文\n"
        )
        config = parse_guardrails(text)
        self.assertEqual(config["quiescence_minutes"], 30)
        self.assertEqual(config["auto_merge_mode"], "dry-run")
        self.assertEqual(config["protected_paths"],
                         [".github/workflows/**", ".claude/GUARDRAILS.md"])


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


class OpenIssuesTest(unittest.TestCase):
    """open issue 数の出どころと、出力に載ることを確かめる。

    数え方そのもの（何を除くか）のテストは evaluate-and-triage 側にある。
    ここで期待値を書き写すと、正本を変えたときにこのテストごと古くなるので、
    「正本の関数を使っているか」と「値が出力に載るか」だけを見る。
    """

    def test_uses_the_function_from_check_state(self):
        summarize = load_summarize_issues()
        source = (Path(__file__).resolve().parents[2]
                  / "evaluate-and-triage" / "scripts" / "check_state.py")
        self.assertEqual(summarize.__name__, "summarize_issues")
        self.assertEqual(Path(summarize.__code__.co_filename).resolve(), source)

    def test_output_carries_open_issues(self):
        """SKILL.md が「そのまま貼れ」と指示している唯一のフィールドが出力に在るか"""
        out = run_main({"issues": [issue(1, login="ha1f", user_type="User"),
                                   issue(2, login="ha1f", user_type="User")], "prs": []})
        self.assertEqual(out["open_issues"], 2)
        self.assertNotIn("open_issues_note", out)

    def test_count_failure_does_not_drop_candidates(self):
        """正本が読めなくても候補の出力は止めない（develop ステージを止めない）"""
        original = select_issues.load_summarize_issues
        select_issues.load_summarize_issues = lambda: (_ for _ in ()).throw(
            FileNotFoundError("check_state.py"))
        try:
            out = run_main({"issues": [issue(7, login="ha1f", user_type="User")], "prs": []})
        finally:
            select_issues.load_summarize_issues = original
        self.assertIsNone(out["open_issues"])
        self.assertIn("check_state.py", out["open_issues_note"])
        self.assertEqual([e["number"] for e in out["backlog"]], [7])

    def test_note_when_bot_exclusion_cannot_work(self):
        """user.type の無いデータ (MCP の list_issues) では参考値だと分かるようにする"""
        self.assertTrue(bot_exclusion_reliable([{"user": {"type": "User"}}]))
        self.assertFalse(bot_exclusion_reliable([{"user": {"type": "User"}}, {"number": 2}]))
        count, note = count_open_issues([{"number": 1, "title": "t"}])
        self.assertEqual(count, 1)
        self.assertIn("参考値", note)


def status_comment(created_at, summary, stage="evaluate", phase="end"):
    record = {"stage": stage, "phase": phase, "ok": True, "summary": summary}
    return {"created_at": created_at, "body": json.dumps(record, ensure_ascii=False) + "\n\n## 本文"}


class RecentStatusRecordsTest(unittest.TestCase):
    """#430: 前段 run の結論を、後段ステージが追加のスクリプト実行なしで読めるようにする。

    レコードの読み方そのもの（1行目 JSON をどう解釈するか）のテストは
    evaluate-and-triage 側にある。ここでは「正本の関数を使っているか」と
    「結論が出力に載るか」「古い結論が『直近』として混ざらないか」を見る。
    """

    NOW = datetime(2026, 9, 27, 3, 0, 0, tzinfo=timezone.utc)  # cutoff = 2026-09-25T03:00:00Z
    GROOMING_SUMMARY = (
        "open issue 15/10（cap 超過でグルーミングのみ）。グルーミング4件: "
        "#407 #409（作業完了済みで draft のまま滞留・作り直し不要）/ #408（PR #416 と同一ファイルの順序）")
    GROOMING = status_comment("2026-09-26T01:12:24Z", GROOMING_SUMMARY)

    def test_output_carries_the_previous_stage_conclusion(self):
        # main() 経由なので now を注入できず実時刻の窓で切られる。窓の外に落ちると
        # 何も壊れていないのに時間の経過だけで red になるため、この1件だけは
        # created_at を「今」から起こす（窓そのもののテストは NOW を渡す別の3件が担う）
        recent = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        out = run_main({"issues": [issue(1, login="ha1f", user_type="User")], "prs": [],
                        "comments": [status_comment(recent, self.GROOMING_SUMMARY)]})
        records = out["recent_status_records"]
        self.assertEqual(records[0]["created_at"], recent)
        self.assertIn("#407 #409", records[0]["summary"])
        self.assertIn("作り直し不要", records[0]["summary"])
        self.assertNotIn("recent_status_records_note", out)

    def test_uses_the_parser_from_check_state(self):
        parse = select_issues.load_check_state().parse_status_records
        source = (Path(__file__).resolve().parents[2]
                  / "evaluate-and-triage" / "scripts" / "check_state.py")
        self.assertEqual(parse.__name__, "parse_status_records")
        self.assertEqual(Path(parse.__code__.co_filename).resolve(), source)

    def test_sorts_ascending_and_keeps_the_latest(self):
        """入力の順序に依存しないこと（GitHub は古い順だが、--stdin 経由は保証が無い）"""
        stamps = ["2026-09-26T09:00:00Z", "2026-09-25T04:00:00Z", "2026-09-27T01:00:00Z",
                  "2026-09-26T01:00:00Z"]
        records, note = collect_recent_records(
            [status_comment(at, at) for at in stamps], now=self.NOW)
        self.assertIsNone(note)
        self.assertEqual([r["created_at"] for r in records], sorted(stamps))

    def test_keeps_only_RECORDS_LIMIT_records(self):
        comments = [status_comment(f"2026-09-26T{h:02d}:00:00Z", f"s{h}") for h in range(24)]
        records, note = collect_recent_records(comments, now=self.NOW)
        self.assertIsNone(note)
        self.assertEqual(len(records), select_issues.RECORDS_LIMIT)
        self.assertEqual(records[-1]["summary"], "s23")

    def test_stale_records_are_dropped_with_a_note(self):
        """`since` を付けずに1ページ目を取ると最古の100件が来る（status issue は570件超）。
        2ヶ月前の結論を「直近」として後段に渡すのは、空で渡すより悪い"""
        records, note = collect_recent_records(
            [status_comment("2026-08-01T01:19:48Z", "2ヶ月前の結論"),
             status_comment("2026-08-02T01:11:15Z", "同じく")], now=self.NOW)
        self.assertEqual(records, [])
        self.assertIn("since", note)

    def test_records_failure_does_not_drop_candidates(self):
        original = select_issues.load_check_state
        select_issues.load_check_state = lambda: (_ for _ in ()).throw(
            FileNotFoundError("check_state.py"))
        try:
            out = run_main({"issues": [issue(7, login="ha1f", user_type="User")], "prs": [],
                            "comments": [self.GROOMING]})
        finally:
            select_issues.load_check_state = original
        self.assertEqual(out["recent_status_records"], [])
        self.assertIn("check_state.py", out["recent_status_records_note"])
        self.assertEqual([e["number"] for e in out["backlog"]], [7])

    def test_malformed_comments_are_not_blamed_on_check_state(self):
        """コメント側のデータ不備を「正本が読めない」と報告すると原因を取り違える"""
        records, note = collect_recent_records([{"body": '{"stage": "develop"}'}])
        self.assertEqual(records, [])
        self.assertIn("取り出せませんでした", note)
        self.assertNotIn("正本", note)

    def test_stdin_comments_are_used_as_given(self):
        comments, note = resolve_status_comments([self.GROOMING], None, 25)
        self.assertEqual(comments, [self.GROOMING])
        self.assertIsNone(note)

    def test_stdin_without_comments_says_so(self):
        """空リストを渡された（0件）と、渡されていないを区別する"""
        self.assertEqual(resolve_status_comments([], None, 25), ([], None))
        comments, note = resolve_status_comments(None, None, 25)
        self.assertEqual(comments, [])
        self.assertIn("--stdin", note)

    def test_note_when_status_issue_is_unknown(self):
        comments, note = resolve_status_comments(None, lambda *a: 1 / 0, None)
        self.assertEqual(comments, [])
        self.assertIn("取得していません", note)  # fetch 失敗の note と区別できる語で照合する

    def test_note_when_the_fetch_fails(self):
        def boom(status_issue, since):
            raise RuntimeError("GitHub API 502")
        comments, note = resolve_status_comments(None, boom, 25)
        self.assertEqual(comments, [])
        self.assertIn("502", note)

    def test_fetch_is_called_with_since(self):
        """`since` を渡さないと最古の100件が返る。呼び出し引数まで固定する"""
        calls = []
        resolve_status_comments(None, lambda issue_number, since: calls.append((issue_number, since)) or [],
                                25)
        self.assertEqual(calls[0][0], 25)
        self.assertRegex(calls[0][1], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_api_path_carries_since_and_per_page(self):
        paths = []
        original_api, original_resolve = select_issues.api_json, select_issues.resolve_repo
        select_issues.api_json = lambda path: paths.append(path) or []
        select_issues.resolve_repo = lambda: ("o", "r")
        try:
            select_issues.fetch_status_comments_via_api(25, "2026-09-25T03:00:00Z")
        finally:
            select_issues.api_json, select_issues.resolve_repo = original_api, original_resolve
        self.assertEqual(paths, ["repos/o/r/issues/25/comments"
                                 "?per_page=100&since=2026-09-25T03:00:00Z"])

    def test_gh_path_carries_since_and_per_page(self):
        paths = []
        original = select_issues.gh_json
        select_issues.gh_json = lambda path: paths.append(path) or []
        try:
            select_issues.fetch_status_comments_via_gh(25, "2026-09-25T03:00:00Z")
        finally:
            select_issues.gh_json = original
        self.assertEqual(paths, ["repos/{owner}/{repo}/issues/25/comments"
                                 "?per_page=100&since=2026-09-25T03:00:00Z"])

    def test_since_is_utc_z_format_without_escapable_chars(self):
        since = since_param(datetime(2026, 9, 27, 3, 11, 9, 123456, tzinfo=timezone.utc))
        self.assertEqual(since, "2026-09-25T03:11:09Z")
        self.assertNotIn("+", since)
        self.assertNotIn(".", since)


class WithPageTest(unittest.TestCase):
    def test_adds_page_param_when_absent(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&per_page=100"
        self.assertEqual(with_page(url, 2),
                         "https://api.github.com/repos/o/r/issues?state=open&per_page=100&page=2")

    def test_replaces_existing_page_param(self):
        url = "https://api.github.com/repos/o/r/issues?state=open&page=2&per_page=100"
        self.assertEqual(with_page(url, 3),
                         "https://api.github.com/repos/o/r/issues?state=open&page=3&per_page=100")


if __name__ == "__main__":
    unittest.main()
