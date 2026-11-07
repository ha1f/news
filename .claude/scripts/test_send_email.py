import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import send_email as s

SCRIPT = Path(__file__).parent / "send_email.py"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".claude" / "skills" / "curate-news" / "output"
BODY = '<!DOCTYPE html>\n<html lang="ja"><head><title>ニュース &amp; 要点</title></head><body><ol><li>a</li></ol>' + s.FOOTER_MARK + '</body></html>\n'
KEY = s.PROVIDER["api_key_env"]
TAG = "sub_tag_0j6hb7h40j6hb7h40j6hb7h40j"  # OpenAPI の Filter の説明にある例


def out_tmp():
    OUT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=OUT)


def run(*args, env=None):
    e = {k: v for k, v in os.environ.items() if k != KEY}
    e.update(env or {})
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, env=e)


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
    def __init__(self, created):
        self.created = created
        self.requests = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        return FakeResponse(self.created if req.full_url.endswith("/emails") else None)


def no_network(*a, **k):
    raise AssertionError("ネットワークに出た")


class SendEmailTest(unittest.TestCase):
    def setUp(self):
        self._tmp = out_tmp()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.src = self.dir / "2026-10-15-abc.html"
        self.src.write_text(BODY, encoding="utf-8")

    def test_dry_run_is_default_and_offline(self):
        # 既定の実行ではソケットも urlopen も使わない。キーがあっても dry-run なら送らない
        out = io.StringIO()
        with mock.patch.object(socket, "socket", no_network), mock.patch.object(socket, "create_connection", no_network), \
                mock.patch.dict(os.environ, {KEY: "k"}), redirect_stdout(out):
            rc = s.main([str(self.src), "--subscriber-id", "sub_123"], opener=no_network)
        self.assertEqual(rc, 0)
        self.assertIn("[dry-run] 宛先 sub_123 / 件名 ニュース & 要点 / 本文 ", out.getvalue())
        self.assertIn(f"{len(BODY.encode())} bytes", out.getvalue())
        self.assertNotIn("<ol>", out.getvalue())  # 本文そのものは出さない
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), [self.src.name])

    def test_explicit_dry_run_flag(self):
        p = run(self.src, "--subscriber-id", "sub_1", "--dry-run", env={KEY: "k"})
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("[dry-run]", p.stdout)

    def test_send_without_key_fails_and_sends_nothing(self):
        with mock.patch.dict(os.environ, {KEY: ""}):
            rc = s.main([str(self.src), "--subscriber-id", "sub_1", "--send"], opener=no_network)
        self.assertNotEqual(rc, 0)
        p = run(self.src, "--subscriber-id", "sub_1", "--send")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn(KEY, p.stderr)
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), [self.src.name])

    def test_send_refuses_body_without_footer(self):
        # 送信者名と配信停止の案内の無い本文（render_email_body.py を --footer 無しで回したもの）は送らない
        self.src.write_text(BODY.replace(s.FOOTER_MARK, ""), encoding="utf-8")
        err = io.StringIO()
        with mock.patch.dict(os.environ, {KEY: "k"}), redirect_stdout(io.StringIO()), redirect_stderr(err):
            self.assertEqual(s.main([str(self.src), "--subscriber-id", "sub_1", "--send"], opener=no_network), 2)
            self.assertIn("送信者名と配信停止の案内", err.getvalue())
            self.assertEqual(s.main([str(self.src), "--subscriber-id", "sub_1"], opener=no_network), 0)
        self.assertIn("警告", err.getvalue())
        self.assertEqual(sorted(x.name for x in self.dir.iterdir()), [self.src.name])

    def test_send_creates_unbroadcast_email_then_sends_to_one(self):
        opener = FakeOpener({"id": "em_1", "status": "draft"})
        with mock.patch.dict(os.environ, {KEY: "secret"}), redirect_stdout(io.StringIO()):
            rc = s.main([str(self.src), "--subscriber-id", "sub_9", "--send"], opener=opener)
        self.assertEqual(rc, 0)
        create, send = opener.requests
        self.assertEqual(create.full_url, "https://api.buttondown.com/v1/emails")
        self.assertEqual(create.get_header("Authorization"), "Token secret")
        payload = json.loads(create.data)
        self.assertEqual(payload["subject"], "ニュース & 要点")
        self.assertEqual(payload["body"], BODY)
        self.assertEqual(payload["status"], "draft")  # 既定の about_to_send は全購読者への配信
        self.assertEqual(payload["archival_mode"], "disabled")
        self.assertEqual(send.full_url, "https://api.buttondown.com/v1/emails/em_1/send-draft")
        self.assertEqual(send.get_method(), "POST")
        self.assertEqual(json.loads(send.data), {"subscribers": ["sub_9"]})  # 宛先は購読者 ID だけ
        log = json.loads((self.dir / "2026-10-15-abc.sub_9.sent.json").read_text(encoding="utf-8"))
        self.assertEqual(log, {"provider": "buttondown", "email_id": "em_1", "subscriber_id": "sub_9", "sent": True})
        self.assertNotIn("secret", json.dumps(log))

    def test_existing_log_blocks_resend(self):
        opener = FakeOpener({"id": "em_1", "status": "draft"})
        with mock.patch.dict(os.environ, {KEY: "k"}), redirect_stdout(io.StringIO()):
            s.main([str(self.src), "--subscriber-id", "sub_9", "--send"], opener=opener)
            with self.assertRaises(SystemExit):
                s.main([str(self.src), "--subscriber-id", "sub_9", "--send"], opener=opener)
        self.assertEqual(len(opener.requests), 2)

    def test_failed_send_leaves_unsent_record(self):
        def opener(req, timeout=None):
            if req.full_url.endswith("/emails"):
                return FakeResponse({"id": "em_1", "status": "draft"})
            raise OSError("429")
        with mock.patch.dict(os.environ, {KEY: "k"}), self.assertRaises(OSError):
            s.main([str(self.src), "--subscriber-id", "sub_9", "--send"], opener=opener)
        log = json.loads((self.dir / "2026-10-15-abc.sub_9.sent.json").read_text(encoding="utf-8"))
        self.assertEqual((log["email_id"], log["sent"]), ("em_1", False))

    def test_refuses_non_html_input(self):
        md = self.dir / "2026-10-15-abc.md"
        md.write_text("1. [a](https://e.com)\n", encoding="utf-8")
        p = run(md, "--subscriber-id", "s", "--subject", "x")
        self.assertNotEqual(p.returncode, 0)

    def test_send_stops_when_created_with_other_status(self):
        opener = FakeOpener({"id": "em_1", "status": "about_to_send"})
        with mock.patch.dict(os.environ, {KEY: "k"}), self.assertRaises(SystemExit):
            s.main([str(self.src), "--subscriber-id", "sub_9", "--send"], opener=opener)
        self.assertEqual(len(opener.requests), 1)

    def test_tag_send_creates_filtered_draft_then_publishes(self):
        expected = {"filters": [{"field": "subscriber.tags", "operator": "contains", "value": TAG}], "groups": [], "predicate": "and"}
        opener = FakeOpener({"id": "em_1", "status": "draft", "filters": expected})
        with mock.patch.dict(os.environ, {KEY: "secret"}), redirect_stdout(io.StringIO()) as out:
            rc = s.main([str(self.src), "--tag-id", TAG, "--send"], opener=opener)
        self.assertEqual(rc, 0)
        self.assertIn(f"宛先 タグ {TAG} の購読者全員", out.getvalue())
        create, publish = opener.requests
        self.assertEqual(create.full_url, "https://api.buttondown.com/v1/emails")
        payload = json.loads(create.data)
        self.assertEqual(payload["status"], "draft")  # 作った時点では誰にも送らない
        self.assertEqual(payload["archival_mode"], "disabled")
        self.assertEqual(payload["filters"], expected)
        self.assertEqual(publish.full_url, "https://api.buttondown.com/v1/emails/em_1/publish")
        self.assertEqual(publish.get_method(), "POST")
        self.assertEqual(json.loads(publish.data), {})  # filters を書き換えない
        log = json.loads((self.dir / f"2026-10-15-abc.{TAG}.sent.json").read_text(encoding="utf-8"))
        self.assertEqual(log, {"provider": "buttondown", "email_id": "em_1", "tag_id": TAG, "sent": True})

    def test_tag_send_stops_when_filters_are_not_kept(self):
        # 応答の filters が空・別のタグ・欠落なら、publish は全購読者かタグの外に届きうるので送らない
        other = {"filters": [{"field": "subscriber.tags", "operator": "contains", "value": TAG[:-1] + "k"}], "groups": [], "predicate": "and"}
        for created in ({"id": "em_1", "status": "draft"},
                        {"id": "em_1", "status": "draft", "filters": {"filters": [], "groups": [], "predicate": "and"}},
                        {"id": "em_1", "status": "draft", "filters": other}):
            opener = FakeOpener(created)
            for f in self.dir.glob("*.sent.json"):
                f.unlink()
            with mock.patch.dict(os.environ, {KEY: "k"}), self.assertRaises(SystemExit) as cm:
                s.main([str(self.src), "--tag-id", TAG, "--send"], opener=opener)
            self.assertIn("filters", str(cm.exception))
            self.assertEqual(len(opener.requests), 1, created)
            log = json.loads((self.dir / f"2026-10-15-abc.{TAG}.sent.json").read_text(encoding="utf-8"))
            self.assertIs(log["sent"], False)

    def test_tag_id_must_be_an_id_not_a_name(self):
        for bad in ("paid-space", "宇宙", "sub_123", "sub_tag_x", "someone@example.com", ""):
            p = run(self.src, "--tag-id", bad)
            self.assertNotEqual(p.returncode, 0, bad)
        self.assertEqual(run(self.src, "--tag-id", "0b0c6f2e-3a0e-4c5e-9d1a-2f3b4c5d6e7f").returncode, 0)
        # 宛先は購読者 ID かタグ ID のどちらか1つ
        self.assertEqual(run(self.src, "--tag-id", TAG, "--subscriber-id", "sub_1").returncode, 2)
        self.assertEqual(run(self.src).returncode, 2)

    def test_rejects_email_address_and_bad_ids(self):
        for bad in ("someone@example.com", "a/b", "../x", ""):
            p = run(self.src, "--subscriber-id", bad)
            self.assertNotEqual(p.returncode, 0, bad)
            self.assertNotIn("[dry-run]", p.stdout, bad)

    def test_subject_override_and_missing_title(self):
        nt = self.dir / "nt.html"
        nt.write_text("<p>x</p>", encoding="utf-8")
        self.assertNotEqual(run(nt, "--subscriber-id", "s").returncode, 0)
        p = run(nt, "--subscriber-id", "s", "--subject", "件名")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("件名 件名", p.stdout)

    def test_refuses_input_and_log_outside_curate_output(self):
        # #528 の拒否テストに倣う: 名前が output なだけの場所・公開物の下・symlink 経由は通さない
        with tempfile.TemporaryDirectory() as t:
            for d in ("output", "_posts/output"):
                src = Path(t) / d / "in.html"
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(BODY, encoding="utf-8")
                self.assertNotEqual(run(src, "--subscriber-id", "s").returncode, 0, d)
            outside = Path(t) / "outside"
            outside.mkdir()
            for d in (outside, ROOT / "_posts", OUT / ".." / "output-x"):
                p = run(self.src, "--subscriber-id", "s", "--log-dir", d)
                self.assertNotEqual(p.returncode, 0, d)
            (self.dir / "link").symlink_to(outside, target_is_directory=True)
            p = run(self.src, "--subscriber-id", "s", "--log-dir", self.dir / "link")
            self.assertNotEqual(p.returncode, 0)
            ext = outside / "post.html"
            ext.write_text(BODY, encoding="utf-8")
            (self.dir / "post.html").symlink_to(ext)
            self.assertNotEqual(run(self.dir / "post.html", "--subscriber-id", "s").returncode, 0)
        posts = sorted((ROOT / "_posts").glob("*.md"))
        if posts:
            self.assertNotEqual(run(posts[0], "--subscriber-id", "s").returncode, 0)

    def test_send_log_symlink_out_of_output_is_refused(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.dir / "2026-10-15-abc.sub_9.sent.json").symlink_to(Path(outside) / "x.json")
            opener = FakeOpener({"id": "em_1", "status": "draft"})
            with mock.patch.dict(os.environ, {KEY: "k"}), self.assertRaises(SystemExit):
                s.main([str(self.src), "--subscriber-id", "sub_9", "--send"], opener=opener)
            self.assertEqual(opener.requests, [])  # 送る前に止まる
            self.assertEqual(os.listdir(outside), [])

    def test_log_is_gitignored(self):
        p = subprocess.run(["git", "check-ignore", "-q", ".claude/skills/curate-news/output/x/a.sub_1.sent.json"], cwd=ROOT)
        self.assertEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
