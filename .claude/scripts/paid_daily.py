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
  check    --root ROOT_DIR --date D [--text TEXT]  作業ツリーが clean で _posts/ に commit も増えていないか確かめ、
           公開してよい要約（件数と成否）を出す。--text は要約の書式と完全一致するときだけ通す

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
# 公開 repo に書いてよい文はこの書式だけ（読者 ID・関心・見出しが入る余地を残さない）
SUMMARY_RE = re.compile(r"^有料フィード: 読者 \d+人中 \d+人成功・\d+人失敗（(?:dry-run|送信 \d+人)）$")
PUBLIC_PROFILES = [ROOT / ".claude" / "skills" / "curate-news" / "preferences.md",
                   *sorted((ROOT / ".claude" / "skills" / "curate-news" / "profiles").glob("*.md"))]


class Fail(Exception):
    """この読者だけを失敗にする（他の読者は続ける）。"""


def check_root(root):
    r = root.resolve()
    if r.is_relative_to(ROOT.resolve()) or ROOT.resolve().is_relative_to(r):
        raise SystemExit(f"--root が公開 repo の作業ツリーの中にあるか、作業ツリーを含む。作業ツリーの外に置く: {root}")
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
    if not path.is_relative_to(root) or path.is_relative_to(ROOT.resolve()):
        raise Fail("profile が --root の外か、公開 repo の作業ツリーの中を指す")
    try:
        data = path.read_bytes()
    except OSError:
        raise Fail("プロファイルのファイルが無いか読めない")
    if not data.strip():
        raise Fail("プロファイルが空")
    # preference_hash.compute_suffix と同じ計算（同じファイルなら curate-news の出力名と一致する）
    h = hashlib.md5(data).hexdigest()[:8]
    # 公開フィードと同じハッシュだと、prepare が公開フィードの output/ の履歴を消して書き換える
    if any(f.is_file() and hashlib.md5(f.read_bytes()).hexdigest()[:8] == h for f in PUBLIC_PROFILES):
        raise Fail("プロファイルが公開フィードのプロファイルと同じ内容")
    return path, h


def store_of(root, reader_id):
    """送信済みの出力の置き場。symlink で --root の外（公開 repo など）に出ていないこと。"""
    store = root / "sent" / reader_id
    if not store.resolve().is_relative_to(root):
        raise Fail("sent/ の置き場が --root の外を指す")
    return store


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
    try:
        store = store_of(root, reader_id)
    except Fail as e:
        record(day, reader_id, ok=False, stage="prepare", reason=str(e))
        print(f"失敗 {reader_id}: {e}。この読者には送らない", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    start = run_dir(day) / "start_head"
    if not start.exists():
        # check が「この run の間に _posts/ へ commit が増えていないか」を見る起点
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        run_dir(day).mkdir(parents=True, exist_ok=True)
        start.write_text(head.stdout.strip() + "\n", encoding="utf-8")
    today = date.fromisoformat(day)
    restored = 0
    # 同じハッシュの出力は他の読者のものかもしれないので、この読者の送信済み分で置き換える（無い日は消す）
    for i in range(1, RESTORE_DAYS + 1):
        d = (today - timedelta(days=i)).isoformat()
        dst = OUTPUT_DIR / f"{d}-{h}.md"
        src = store / f"{d}.md"
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
        store = store_of(root, reader_id)
        sending = store / f"{day}.sending"
        if send and (store / f"{day}.md").exists():
            raise Fail("この日の分は送信済み")
        if send and sending.exists():
            raise Fail(f"前回の送信の結果が不明（{sending.name} が残っている）。配信サービス側で届いたか確かめてから消す")
        d = run_dir(day)
        md = d / f"{reader_id}.md"
        shutil.copyfile(src, md)
        try:
            render_email_body.main([str(md)])
        except SystemExit as e:
            raise Fail(f"本文生成に失敗: {e}")
        args = [str(d / f"{reader_id}.html"), "--subscriber-id", sid, "--send" if send else "--dry-run"]
        if send:
            # output/ は run をまたいで残らないので、送信中の印は private repo 側に置く。届いたか分からない
            # 失敗（通信の例外）ではこれを残し、次の run が同じ読者に二重に送らないようにする
            store.mkdir(parents=True, exist_ok=True)
            sending.write_text("", encoding="utf-8")
        try:
            rc = send_email.main(args)
        except SystemExit as e:
            sending.unlink(missing_ok=True)  # send_email が自分で止めた（送る前、または送信を中止した）
            raise Fail(f"送信に失敗: {e}")
        except Exception as e:
            raise Fail(f"送信の結果が不明 ({type(e).__name__})。{sending.name} を残したので再送しない")
        if rc != 0:
            sending.unlink(missing_ok=True)
            raise Fail(f"送信に失敗 (exit {rc})")
    except Fail as e:
        record(day, reader_id, ok=False, stage="finalize", reason=str(e))
        print(f"失敗 {reader_id}: {e}", file=sys.stderr)
        return 1
    if send:
        store.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(md, store / f"{day}.md")
        sending.unlink(missing_ok=True)
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


def check(root, day, text):
    readers = load_readers(root)
    runs = run_state(day)
    problems = []
    git = lambda *a: subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout
    st = git("status", "--porcelain", "--untracked-files=all").splitlines()
    if st:
        posts = sum(1 for ln in st if ln[3:].startswith("_posts/"))
        problems.append(f"公開 repo の作業ツリーが clean でない: {len(st)} 件（うち _posts/ {posts} 件）")
    start = run_dir(day) / "start_head"
    if not start.exists():
        problems.append("prepare を1度も回していない（run の起点の commit が無い）")
    else:
        added = git("diff", "--name-only", f"{start.read_text(encoding='utf-8').strip()}..HEAD", "--", "_posts/").split()
        if added:
            problems.append(f"run の間に _posts/ への commit が {len(added)} 件増えた")
    line = summary(list(readers), runs)
    if text and not SUMMARY_RE.match(text):
        problems.append("--text が要約の書式（件数と成否だけ）と一致しない。公開 repo には check が出した要約だけを書く")
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
            p.add_argument("--text", default="", help="公開 repo に書く予定の文。要約の書式と完全一致するときだけ通す")
    a = ap.parse_args(argv)
    root = check_root(a.root)
    if a.cmd == "prepare":
        return prepare(root, a.date, a.reader)
    if a.cmd == "finalize":
        return finalize(root, a.date, a.reader, a.send)
    return check(root, a.date, a.text)


if __name__ == "__main__":
    sys.exit(main())
