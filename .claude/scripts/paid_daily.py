#!/usr/bin/env python3
"""有料フィードの日次手順の決定的な部分 (#582)。手順の全体は docs/m5-paid-delivery.md の「日次手順」。

読者ごとに prepare → （curate-news を --profile と --paid で回す）→ finalize の順に回し、最後に check を回す。
読者は1人ずつ直列に回す（同じ内容のプロファイルを持つ読者どうしは curate-news の出力ファイル名が同じになるため）。

対応表とプロファイルは、公開 repo の作業ツリーの外に置いたディレクトリ（private repo を想定。以下 ROOT_DIR）に置く:
  ROOT_DIR/readers.json  [{"reader_id": "r1", "subscriber_id": "sub_abc", "profile": "profiles/r1.md"}, ...]
  ROOT_DIR/sent/{reader_id}/{日付}.md  送信済みの出力（finalize --send が保存し、prepare が output/ に戻す）
profile は ROOT_DIR からの相対パス。ROOT_DIR の外を指すものは受け付けない。

  prepare  --root ROOT_DIR --date D --reader ID  読者のプロファイルを確かめ、送信済みの出力を output/ に戻し、当日の出力を消す
  finalize --root ROOT_DIR --date D --reader ID [--send]  当日の出力を読者 ID の名前で取り分け、本文生成 → 送信（既定は dry-run）
  check    --root ROOT_DIR --date D [--text TEXT]  作業ツリーが clean か確かめ、公開してよい要約（件数と成否）を出す

読者の結果は output/paid/{日付}/run.json に溜まる（output/ は gitignore 対象）。
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import render_email_body  # noqa: E402
import send_email  # noqa: E402
from render_email_body import OUTPUT_DIR, ROOT  # noqa: E402

# 数字だけの ID は要約の件数と見分けられないので受け付けない
READER_ID_RE = re.compile(r"^(?![0-9]+$)[A-Za-z0-9_-]{1,64}$")
# curate-news の recent_topics.py が自分のフィードを遡る日数（--own-days の既定10）を覆う
RESTORE_DAYS = 14
URL_RE = re.compile(r"https?://")


class Fail(Exception):
    """この読者だけを失敗にする（他の読者は続ける）。"""


def check_root(root):
    r = root.resolve()
    if r.is_relative_to(ROOT.resolve()):
        raise SystemExit(f"--root が公開 repo の作業ツリーの中にある。作業ツリーの外に置く: {root}")
    if not (r / "readers.json").is_file():
        raise SystemExit(f"{root}/readers.json が無い")
    return r


def load_readers(root):
    try:
        readers = json.loads((root / "readers.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"readers.json を読めない: {e}")
    if not isinstance(readers, list):
        raise SystemExit("readers.json は読者の配列にする")
    seen = set()
    for r in readers:
        rid = r.get("reader_id", "") if isinstance(r, dict) else ""
        if not READER_ID_RE.match(str(rid)) or rid in seen:
            raise SystemExit(f"readers.json の reader_id が不正か重複: {rid!r}")
        seen.add(rid)
    return {r["reader_id"]: r for r in readers}


def reader_of(root, reader_id):
    readers = load_readers(root)
    if reader_id not in readers:
        raise SystemExit(f"readers.json に {reader_id} が無い")
    return readers[reader_id]


def profile_of(root, reader):
    """プロファイルの実体と、curate-news の出力ファイル名に入るハッシュ。読めなければ Fail。

    preference_hash.py はファイルが無いと 'default' を返し、curate-news は汎用フィードを作る。その経路に入れない。
    """
    rel = reader.get("profile")
    if not rel or not isinstance(rel, str):
        raise Fail("readers.json に profile が無い")
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise Fail("profile が --root の外を指す")
    try:
        data = path.read_bytes()
    except OSError:
        raise Fail("プロファイルのファイルが無いか読めない")
    if not data.strip():
        raise Fail("プロファイルが空")
    # preference_hash.compute_suffix と同じ計算（同じファイルなら curate-news の出力名と一致する）
    return path, hashlib.md5(data).hexdigest()[:8]


def run_dir(day):
    return OUTPUT_DIR / "paid" / day


def record(day, reader_id, **result):
    d = run_dir(day)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "run.json"
    runs = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    runs[reader_id] = {**runs.get(reader_id, {}), **result}
    f.write_text(json.dumps(runs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def prepare(root, day, reader_id):
    reader = reader_of(root, reader_id)
    try:
        path, h = profile_of(root, reader)
    except Fail as e:
        record(day, reader_id, ok=False, stage="prepare", reason=str(e))
        print(f"失敗 {reader_id}: {e}。この読者には送らない", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.fromisoformat(day)
    restored = 0
    # 同じハッシュの出力は他の読者のものかもしれないので、この読者の送信済み分で置き換える（無い日は消す）
    for i in range(1, RESTORE_DAYS + 1):
        d = (today - timedelta(days=i)).isoformat()
        dst = OUTPUT_DIR / f"{d}-{h}.md"
        src = root / "sent" / reader_id / f"{d}.md"
        if src.is_file():
            shutil.copyfile(src, dst)
            restored += 1
        elif dst.exists():
            dst.unlink()
    # 当日の出力が残っていると、curate-news が書けずに終わっても前の読者の出力を送ってしまう
    (OUTPUT_DIR / f"{day}-{h}.md").unlink(missing_ok=True)
    record(day, reader_id, ok=None, stage="prepare", hash=h)
    print(f"準備 {reader_id}: 送信済み {restored} 日分を output/ に戻した")
    print(f"次: curate-news を args '--profile {path}' で、手順2・3の fetch_feeds.py に --paid を付けて回す（日付 {day} を渡す）")
    return 0


def finalize(root, day, reader_id, send):
    reader = reader_of(root, reader_id)
    try:
        _, h = profile_of(root, reader)
        sid = reader.get("subscriber_id")
        if not isinstance(sid, str) or not send_email.SUBSCRIBER_ID_RE.match(sid):
            raise Fail("subscriber_id が無いか不正")
        if run_state(day).get(reader_id, {}).get("hash") != h:
            raise Fail("prepare を通していないか、その後にプロファイルが変わった")
        src = OUTPUT_DIR / f"{day}-{h}.md"
        if not src.is_file():
            raise Fail("curate-news の当日の出力が無い")
        store = root / "sent" / reader_id
        if send and (store / f"{day}.md").exists():
            raise Fail("この日の分は送信済み")
        d = run_dir(day)
        md = d / f"{reader_id}.md"
        shutil.copyfile(src, md)
        try:
            render_email_body.main([str(md)])
        except SystemExit as e:
            raise Fail(f"本文生成に失敗: {e}")
        args = [str(d / f"{reader_id}.html"), "--subscriber-id", sid, "--send" if send else "--dry-run"]
        try:
            rc = send_email.main(args)
        except SystemExit as e:
            raise Fail(f"送信に失敗: {e}")
        if rc != 0:
            raise Fail(f"送信に失敗 (exit {rc})")
    except Fail as e:
        record(day, reader_id, ok=False, stage="finalize", reason=str(e))
        print(f"失敗 {reader_id}: {e}", file=sys.stderr)
        return 1
    if send:
        store.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(md, store / f"{day}.md")
        print(f"保存: {store / f'{day}.md'}（private repo に commit・push する）")
    record(day, reader_id, ok=True, stage="finalize", sent=bool(send))
    return 0


def run_state(day):
    f = run_dir(day) / "run.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def summary(readers, runs):
    ok = [r for r in readers if runs.get(r, {}).get("ok") is True]
    sent = sum(1 for r in ok if runs[r].get("sent"))
    failed = len(readers) - len(ok)
    mode = f"送信 {sent}人" if sent else "dry-run"
    return f"有料フィード: 読者 {len(readers)}人中 {len(ok)}人成功・{failed}人失敗（{mode}）"


def sensitive_terms(root, readers, day):
    """公開 repo に書く文に出てはいけない語: 読者 ID・購読者 ID・プロファイルの行・当日の見出し。"""
    terms = set()
    for rid, r in readers.items():
        terms.add(rid)
        if isinstance(r.get("subscriber_id"), str):
            terms.add(r["subscriber_id"])
        try:
            path, _ = profile_of(root, r)
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.lstrip().startswith("#"):
                    continue  # 見出しはプロファイルの雛形の共通文言
                s = line.strip().lstrip("-*> ").strip()
                if len(s) >= 6:
                    terms.add(s)
        except (Fail, UnicodeDecodeError):
            pass
        md = run_dir(day) / f"{rid}.md"
        if md.is_file():
            for it in render_email_body.parse(md.read_text(encoding="utf-8"))["items"]:
                terms.add(it["title"])
    return terms


def leaks(text, terms):
    found = ["URL"] if URL_RE.search(text) else []
    # 英数字の語は前後が英数字でない位置だけを見る（読者 ID「r1」を「r10」や「2人中1人」の数字に誤爆させない）
    return found + sorted(t for t in terms if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(t)}(?![A-Za-z0-9_-])", text))


def check(root, day, text):
    readers = load_readers(root)
    runs = run_state(day)
    problems = []
    st = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=all"],
                        capture_output=True, text=True, check=True).stdout.splitlines()
    if st:
        posts = sum(1 for ln in st if ln[3:].startswith("_posts/"))
        problems.append(f"公開 repo の作業ツリーが clean でない: {len(st)} 件（うち _posts/ {posts} 件）")
    line = summary(list(readers), runs)
    terms = sensitive_terms(root, readers, day)
    for label, t in (("要約", line), ("--text", text)):
        if t and leaks(t, terms):
            # 何が漏れたかは端末にだけ出す（この出力自体は公開しない前提）
            problems.append(f"{label} に公開してはいけない語がある: {leaks(t, terms)}")
    for p in problems:
        print(p, file=sys.stderr)
    print(line)
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prepare", "finalize", "check"):
        p = sub.add_parser(name)
        p.add_argument("--root", type=Path, required=True)
        p.add_argument("--date", required=True, type=lambda s: date.fromisoformat(s).isoformat())
        if name != "check":
            p.add_argument("--reader", required=True)
        if name == "finalize":
            p.add_argument("--send", action="store_true", help="実際に送る（既定は dry-run）")
        if name == "check":
            p.add_argument("--text", default="", help="公開 repo に書く予定の文。漏れが無いか確かめる")
    a = ap.parse_args(argv)
    root = check_root(a.root)
    if a.cmd == "prepare":
        return prepare(root, a.date, a.reader)
    if a.cmd == "finalize":
        return finalize(root, a.date, a.reader, a.send)
    return check(root, a.date, a.text)


if __name__ == "__main__":
    sys.exit(main())
