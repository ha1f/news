import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import paid_daily as p
import send_email

SCRIPT = Path(__file__).parent / "paid_daily.py"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".claude" / "skills" / "curate-news" / "output"
DAY = "2026-10-21"
PROFILE = "# 興味・関心\n\n- 宇宙開発と半導体の供給網\n"
CURATED = """## ニュース (2026-10-21 07:00 JST)

宇宙と半導体の一日。

1. [打ち上げ会社が初の黒字](https://example.com/a) (日経・会員限定)<br>
   売上の半分を設備貸しが占め、前年は赤字だった。
"""
KEY = send_email.PROVIDER["api_key_env"]


class FakeResponse:
    def __init__(self, payload):
        self.raw = json.dumps(payload).encode() if payload is not None else b""

    def read(self):
        return self.raw

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeOpener:
    def __init__(self):
        self.requests = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        return FakeResponse({"id": "em_1", "status": "transactional"} if req.full_url.endswith("/emails") else None)


def quiet(fn, *a, **k):
    with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
        rc = fn(*a, **k)
    return rc, out.getvalue(), err.getvalue()


class PaidDailyTest(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()  # 作業ツリーの外
        self.addCleanup(t.cleanup)
        self.root = Path(t.name).resolve()
        (self.root / "profiles").mkdir()
        # 出力の置き場を、本物の output/ の下の一時ディレクトリに差し替える（他の run の出力を消さない）
        OUT.mkdir(parents=True, exist_ok=True)
        o = tempfile.TemporaryDirectory(dir=OUT)
        self.addCleanup(o.cleanup)
        self.out = Path(o.name)
        for mod in (p, p.render_email_body, send_email):
            patcher = mock.patch.object(mod, "OUTPUT_DIR", self.out)
            patcher.start()
            self.addCleanup(patcher.stop)

    def readers(self, *rows):
        (self.root / "readers.json").write_text(json.dumps(list(rows)), encoding="utf-8")

    def reader(self, rid, profile_text=PROFILE, sid=None):
        if profile_text is not None:
            (self.root / "profiles" / f"{rid}.md").write_text(profile_text, encoding="utf-8")
        return {"reader_id": rid, "subscriber_id": sid or f"sub_{rid}", "profile": f"profiles/{rid}.md"}

    def curate(self, rid, text=CURATED):
        """curate-news の代わりに、プロファイルのハッシュの名前で当日の出力を書く。"""
        _, h = p.profile_of(self.root, p.reader_of(self.root, rid))
        (self.out / f"{DAY}-{h}.md").write_text(text, encoding="utf-8")
        return h

    def run_reader(self, rid, send=False, **kw):
        rc, _, _ = quiet(p.prepare, self.root, DAY, rid)
        if rc:
            return rc
        self.curate(rid, **kw)
        return quiet(p.finalize, self.root, DAY, rid, send)[0]

    def test_root_inside_worktree_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".claude") as d:
            (Path(d) / "readers.json").write_text("[]", encoding="utf-8")
            with self.assertRaises(SystemExit) as cm:
                p.check_root(Path(d))
            self.assertIn("作業ツリーの中", str(cm.exception))
        self.readers()
        self.assertEqual(p.check_root(self.root), self.root)

    def test_missing_profile_fails_only_that_reader(self):
        self.readers(self.reader("alice"), self.reader("bob", profile_text=None))
        self.assertEqual(self.run_reader("alice"), 0)
        rc, _, err = quiet(p.prepare, self.root, DAY, "bob")
        self.assertEqual(rc, 1)
        self.assertIn("プロファイルのファイルが無いか読めない", err)
        # default の汎用フィードを作る経路に入らない: bob の分は何も作られず、送る予定も出ない
        self.assertFalse((self.out / f"{DAY}-default.md").exists())
        self.assertNotEqual(quiet(p.finalize, self.root, DAY, "bob", False)[0], 0)
        self.assertFalse((p.run_dir(DAY) / "bob.html").exists())
        runs = p.run_state(DAY)
        self.assertIs(runs["alice"]["ok"], True)
        self.assertIs(runs["bob"]["ok"], False)
        self.assertTrue((p.run_dir(DAY) / "alice.html").exists())

    def test_profile_outside_root_or_empty_fails(self):
        r = self.reader("alice")
        outside = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)  # 実在する --root の外のファイル
        outside.write(PROFILE)
        outside.close()
        self.addCleanup(os.unlink, outside.name)
        r["profile"] = os.path.relpath(outside.name, self.root)
        self.readers(r, self.reader("bob", profile_text="  \n"))
        self.assertEqual(quiet(p.prepare, self.root, DAY, "alice")[0], 1)
        self.assertEqual(quiet(p.prepare, self.root, DAY, "bob")[0], 1)

    def test_same_profile_readers_do_not_overwrite_each_other(self):
        self.readers(self.reader("alice"), self.reader("bob"))
        self.assertEqual(self.run_reader("alice"), 0)
        self.assertEqual(self.run_reader("bob", text=CURATED.replace("打ち上げ会社", "別の会社")), 0)
        d = p.run_dir(DAY)
        self.assertIn("打ち上げ会社", (d / "alice.md").read_text(encoding="utf-8"))
        self.assertIn("別の会社", (d / "bob.md").read_text(encoding="utf-8"))
        self.assertIn("打ち上げ会社", (d / "alice.html").read_text(encoding="utf-8"))

    def test_finalize_refuses_leftover_output_from_previous_reader(self):
        # alice と同じ内容の bob: alice の当日の出力が残っていても、bob の prepare が消すので bob に送らない
        self.readers(self.reader("alice"), self.reader("bob"))
        self.assertEqual(self.run_reader("alice"), 0)
        self.assertEqual(quiet(p.prepare, self.root, DAY, "bob")[0], 0)
        rc, _, err = quiet(p.finalize, self.root, DAY, "bob", False)
        self.assertEqual(rc, 1)
        self.assertIn("当日の出力が無い", err)

    def test_finalize_requires_prepare_with_same_profile(self):
        self.readers(self.reader("alice"))
        self.curate("alice")
        self.assertEqual(quiet(p.finalize, self.root, DAY, "alice", False)[0], 1)
        quiet(p.prepare, self.root, DAY, "alice")
        (self.root / "profiles" / "alice.md").write_text(PROFILE + "- 追記\n", encoding="utf-8")
        self.curate("alice")
        rc, _, err = quiet(p.finalize, self.root, DAY, "alice", False)
        self.assertEqual(rc, 1)
        self.assertIn("プロファイルが変わった", err)

    def test_dry_run_is_default_and_saves_nothing(self):
        self.readers(self.reader("alice"))
        quiet(p.prepare, self.root, DAY, "alice")
        self.curate("alice")
        with mock.patch.object(send_email.urllib.request, "urlopen", side_effect=AssertionError("ネットワークに出た")), \
                mock.patch.dict(os.environ, {KEY: "k"}):
            rc, out, _ = quiet(p.finalize, self.root, DAY, "alice", False)
        self.assertEqual(rc, 0)
        self.assertIn("[dry-run] 宛先 sub_alice", out)
        self.assertFalse((self.root / "sent").exists())
        self.assertIs(p.run_state(DAY)["alice"]["sent"], False)

    def test_send_saves_output_and_next_prepare_restores_it(self):
        self.readers(self.reader("alice"))
        quiet(p.prepare, self.root, DAY, "alice")
        h = self.curate("alice")
        opener = FakeOpener()
        with mock.patch.object(send_email.urllib.request, "urlopen", opener), mock.patch.dict(os.environ, {KEY: "k"}):
            # send_email.main の既定引数 opener は定義時に束縛されるので、関数ごと差し替える
            real = send_email.main
            with mock.patch.object(send_email, "main", lambda argv: real(argv, opener=opener)):
                rc = quiet(p.finalize, self.root, DAY, "alice", True)[0]
                self.assertEqual(rc, 0)
                self.assertEqual(opener.requests[1].full_url.split("/subscribers/")[1], "sub_alice/emails/em_1")
                stored = self.root / "sent" / "alice" / f"{DAY}.md"
                self.assertEqual(stored.read_text(encoding="utf-8"), CURATED)
                # 同じ日の再送はしない
                quiet(p.prepare, self.root, DAY, "alice")
                self.curate("alice")
                rc, _, err = quiet(p.finalize, self.root, DAY, "alice", True)
                self.assertEqual(rc, 1)
                self.assertIn("送信済み", err)
        # 次の run（output/ は空から）: 送信済みの出力が同じハッシュの名前で戻り、recent_urls.py の重複除外に入る
        for f in self.out.glob("*.md"):
            f.unlink()
        rc, out, _ = quiet(p.prepare, self.root, "2026-10-22", "alice")
        self.assertEqual(rc, 0)
        self.assertIn("送信済み 1 日分", out)
        self.assertEqual((self.out / f"{DAY}-{h}.md").read_text(encoding="utf-8"), CURATED)

    def test_prepare_replaces_other_readers_history_with_same_hash(self):
        self.readers(self.reader("alice"), self.reader("bob"))
        _, h = p.profile_of(self.root, p.reader_of(self.root, "alice"))
        prev = "2026-10-20"
        (self.out / f"{prev}-{h}.md").write_text("alice の前日分", encoding="utf-8")
        (self.out / f"2026-10-01-{h}.md").write_text("範囲外は触らない", encoding="utf-8")
        quiet(p.prepare, self.root, DAY, "bob")
        self.assertFalse((self.out / f"{prev}-{h}.md").exists())
        self.assertTrue((self.out / f"2026-10-01-{h}.md").exists())
        (self.root / "sent" / "bob").mkdir(parents=True)
        (self.root / "sent" / "bob" / f"{prev}.md").write_text("bob の前日分", encoding="utf-8")
        quiet(p.prepare, self.root, DAY, "bob")
        self.assertEqual((self.out / f"{prev}-{h}.md").read_text(encoding="utf-8"), "bob の前日分")

    def test_summary_is_counts_only_and_leaks_are_caught(self):
        self.readers(self.reader("alice"), self.reader("bob", profile_text=None))
        self.run_reader("alice")
        quiet(p.prepare, self.root, DAY, "bob")
        with mock.patch.object(p.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")):
            rc, out, err = quiet(p.check, self.root, DAY, "")
            self.assertEqual(rc, 0, err)
            self.assertEqual(out.strip(), "有料フィード: 読者 2人中 1人成功・1人失敗（dry-run）")
            for bad in ("alice は成功", "sub_bob に送れず", "打ち上げ会社が初の黒字 を配信", "見る https://example.com/a",
                        "関心は宇宙開発と半導体の供給網"):
                rc, _, err = quiet(p.check, self.root, DAY, bad)
                self.assertEqual(rc, 1, bad)
                self.assertIn("--text に公開してはいけない語", err)
            # 部分一致では誤爆しない（alice → malice、件数の数字）
            self.assertEqual(quiet(p.check, self.root, DAY, "malice は無関係。2人中1人")[0], 0)

    def test_check_fails_when_worktree_is_dirty(self):
        self.readers(self.reader("alice"))
        dirty = subprocess.CompletedProcess([], 0, "?? _posts/2026-10-21-news-paid.md\n M index.md\n", "")
        with mock.patch.object(p.subprocess, "run", return_value=dirty):
            rc, _, err = quiet(p.check, self.root, DAY, "")
        self.assertEqual(rc, 1)
        self.assertIn("clean でない: 2 件（うち _posts/ 1 件）", err)

    def test_reader_ids_are_validated(self):
        for bad in ("../x", "1", "a b", ""):
            self.readers({"reader_id": bad, "subscriber_id": "s", "profile": "p.md"})
            with self.assertRaises(SystemExit, msg=bad):
                p.load_readers(self.root)
        self.readers(self.reader("alice"), self.reader("alice"))
        with self.assertRaises(SystemExit):
            p.load_readers(self.root)

    def test_cli_rejects_root_inside_worktree(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "check", "--root", str(ROOT), "--date", DAY],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("作業ツリーの中", r.stderr)


if __name__ == "__main__":
    unittest.main()
