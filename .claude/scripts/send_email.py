#!/usr/bin/env python3
"""render_email_body.py が作ったメール本文を、配信サービスの API で購読者1人（#555）か、1つのタグを持つ購読者全員（#613）に送る。

既定は dry-run でネットワークに出ない。送る予定（宛先の購読者 ID・件名・本文のサイズ）を表示するだけ。
実送信は `--send` を明示し、API キーを環境変数に入れたときだけ行う。キーが無ければ何も送らずに非0で終わる。
本文に送信者名と配信停止の案内（render_email_body.py の --footer）が無いときも、--send は送らずに非0で終わる。
入力・ログとも、resolve した実体が `.claude/skills/curate-news/output/`（gitignore 対象）の下にないと拒否する。
宛先は配信サービス側の購読者 ID かタグ ID だけを受け付け、メールアドレスは受け付けない（repo・引数・ログに置かないため）。

使い方: python3 .claude/scripts/send_email.py <output/.../{stem}.html> (--subscriber-id ID | --tag-id ID) [--subject S] [--send]
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_email_body import FOOTER_MARK, OUTPUT_DIR, ROOT, _under_output  # noqa: E402

# 配信サービスに依存する部分はここだけ。サービスが決まったらこのブロックを差し替える。
# 仮の選定: Buttondown（docs/m5-paid-delivery.md の候補）。公開 OpenAPI
# https://docs.buttondown.com/openapi.json（api.buttondown.com/v1/openapi.json はここへ redirect）を 2026-10-18 に確認:
#   POST /v1/emails（EmailInput: subject 必須。status の既定は about_to_send = 全購読者への配信）
#   POST /v1/emails/{id}/send-draft（SendDraftInput: `subscribers` に購読者 ID の配列。"Send a draft email to specific recipients"）
#   認証は `Authorization: Token <key>`
# 一斉配信にしないため status は draft で作り、send-draft でその 1 人にだけ送る。draft は配信にもアーカイブにも出ない
# （archival_mode も disabled にする）。読者ごとに本文が違うので、1通ごとに email を作ってその1人に送る。
# 以前の案（status を transactional にして POST /v1/subscribers/{id}/emails/{email_id} で送る）は一次情報で裏が取れない:
# EmailStatus の説明は「status は observability のためだけに公開」で、API changelog 2025-04-17 は transactional を
# 「core workflow / automation が送ったメール」の表示値としてしか説明していない。また subscribers/{id}/emails/{email_id} は
# 「finalized なメール専用」（docs/api-subscribers-send-email。draft は 2024-06-27 から email_invalid_status で拒否）。
# 作成応答の status 確認は事後検知で、作成時点で一斉配信の status にされた場合は取り消せない。
#
# タグへの一斉配信（プレミアムフィード。#613）も同じ OpenAPI（2026-10-28 に確認）で組む:
#   EmailInput.filters（EmailFilterGroup: "Tag-based filter rules determining which subscribers receive this email."）に
#   {"field": "subscriber.tags", "operator": "contains", "value": <タグ ID>} を1つだけ入れる（Filter の説明:
#   "Tag filters require the tag's ID (either a UUID or TypeID), not its name."）
#   POST /v1/emails/{id}/publish（"Publishes and sends an email." 本文は EmailUpdateInput で、渡したフィールドだけを
#   更新してから送る。docs/api-emails-publish）
# こちらも draft で作り、作成応答の status と filters が送ったものと一致したときだけ publish する（filters が落ちて
# 全購読者への配信になるのを publish の前に止める）。publish の本文は空にして、filters を書き換えない。
# ただし send-draft は公式 docs 上「下書きをレビュー用に送る」機能で、有料読者への本番配信に使えるか
# （下書き表示が付かないか、配信停止リンクとフッタが付くか、配信記録に残るか）は未確認。
# 初回の実送信は、オーナーだけが購読するテスト用ニュースレターで draft のまま作られ、send-draft が本人にだけ届き、
# 下書き表示が無く配信停止リンクが付くことを確かめてから行う。
PROVIDER = {
    "name": "buttondown",
    "api_key_env": "BUTTONDOWN_API_KEY",
    "base_url": "https://api.buttondown.com/v1",
    "expected_status": "draft",
}


def build_create(subject, body):
    """1通分の email を作るリクエスト（購読者全体へは送らない形）。"""
    return {
        "method": "POST",
        "path": "/emails",
        "json": {
            "subject": subject,
            "body": body,
            "status": PROVIDER["expected_status"],
            "archival_mode": "disabled",
        },
    }


def build_send(email_id, subscriber_id):
    """作った draft を購読者1人にだけ送るリクエスト（send-draft。宛先は購読者 ID の配列で渡す）。"""
    return {"method": "POST", "path": f"/emails/{email_id}/send-draft", "json": {"subscribers": [subscriber_id]}}


class MaybeSent(SystemExit):
    """email を作った後の中止のうち、配信がもう始まっているかもしれないもの（呼び出し側は再送しない）。"""


def tag_filters(tag_id):
    """そのタグを持つ購読者だけに絞る audience（EmailFilterGroup）。"""
    return {"filters": [{"field": "subscriber.tags", "operator": "contains", "value": tag_id}], "groups": [], "predicate": "and"}


def build_create_for_tag(subject, body, tag_id):
    """タグの購読者に送る email を draft で作るリクエスト（作った時点ではまだ誰にも送らない）。"""
    spec = build_create(subject, body)
    spec["json"]["filters"] = tag_filters(tag_id)
    return spec


def build_publish(email_id):
    """draft を filters の audience に送るリクエスト。本文を空にして、作成時の filters をそのまま使う。"""
    return {"method": "POST", "path": f"/emails/{email_id}/publish", "json": {}}


def auth_headers(api_key):
    return {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}


# 購読者 ID は英数字・_・- だけ（`@` を含むメールアドレスや、パスを壊す `/` を受け付けない）
SUBSCRIBER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
# タグ ID は OpenAPI の ID の pattern（UUID か TypeID）のうち sub_tag_ の形だけ。タグ名は受け付けない
_UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
TAG_ID_RE = re.compile(rf"^(?:{_UUID}|sub_tag_(?:[0-7][0-9abcdefghjkmnpqrstvwxyz]{{25}}|{_UUID}))$")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)


def request(spec, api_key, opener=urllib.request.urlopen):
    data = json.dumps(spec["json"]).encode() if spec["json"] is not None else b""
    req = urllib.request.Request(
        PROVIDER["base_url"] + spec["path"], data=data, method=spec["method"], headers=auth_headers(api_key)
    )
    with opener(req, timeout=30) as res:
        raw = res.read()
    return json.loads(raw) if raw.strip() else {}


def check_paths(src, log_dir):
    rel = OUTPUT_DIR.relative_to(ROOT)
    if not _under_output(src):
        raise SystemExit(f"入力 {src} が {rel}/ の下にない")
    if not _under_output(log_dir):
        raise SystemExit(f"ログの置き場 {log_dir} が {rel}/ の下にない。公開される場所に書かないため、ここだけ受け付ける")


def subject_of(body, override):
    if override:
        return override
    m = TITLE_RE.search(body)
    if not m or not m.group(1).strip():
        raise SystemExit("件名が決まらない（本文に <title> が無い）。--subject で渡す")
    return html.unescape(m.group(1).strip())


def main(argv=None, opener=urllib.request.urlopen):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", type=Path, help="render_email_body.py が出力した .html")
    to = ap.add_mutually_exclusive_group(required=True)
    to.add_argument("--subscriber-id", help="配信サービス側の購読者 ID（メールアドレスは不可）。その1人にだけ送る")
    to.add_argument("--tag-id", help="配信サービス側のタグ ID（名前は不可）。そのタグを持つ購読者全員に同じ本文を送る")
    ap.add_argument("--subject")
    ap.add_argument("--log-dir", type=Path, help="実送信の記録の置き場（既定は入力と同じディレクトリ）")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="既定。送る予定を表示するだけ")
    mode.add_argument("--send", action="store_true", help="実際に送る（API キーが要る）")
    args = ap.parse_args(argv)

    src = args.input
    log_dir = args.log_dir or src.parent
    check_paths(src, log_dir)
    if src.suffix != ".html":
        raise SystemExit(f"入力は render_email_body.py が出力した .html だけを受け付ける: {src.name}")
    if args.tag_id is not None:
        if not TAG_ID_RE.match(args.tag_id):
            raise SystemExit("--tag-id は配信サービスのタグ ID（sub_tag_… か UUID）だけを受け付ける。タグ名は渡さない")
        dest, to_label = args.tag_id, f"タグ {args.tag_id} の購読者全員"
    else:
        if not SUBSCRIBER_ID_RE.match(args.subscriber_id):
            raise SystemExit("--subscriber-id は配信サービスの購読者 ID（英数字・_・-）だけを受け付ける。メールアドレスは渡さない")
        dest, to_label = args.subscriber_id, args.subscriber_id
    body = src.read_text(encoding="utf-8")
    if not body.strip():
        raise SystemExit(f"{src} が空")
    subject = subject_of(body, args.subject)
    plan = f"宛先 {to_label} / 件名 {subject} / 本文 {len(body.encode('utf-8'))} bytes ({PROVIDER['name']})"

    footer_missing = FOOTER_MARK not in body
    if not args.send:
        print(f"[dry-run] {plan}")
        if footer_missing:
            print("警告: 本文に送信者名と配信停止の案内（render_email_body.py --footer）が無い。--send では送らない", file=sys.stderr)
        return 0

    if footer_missing:
        # 特定電子メール法 4 条の表示（送信者名・配信停止の案内）を欠いたメールは送らない (#595)
        print("本文に送信者名と配信停止の案内（render_email_body.py --footer）が無いので送らない", file=sys.stderr)
        return 2

    api_key = os.environ.get(PROVIDER["api_key_env"], "").strip()
    if not api_key:
        print(f"{PROVIDER['api_key_env']} が無いので送らない", file=sys.stderr)
        return 2
    log = log_dir / f"{src.stem}.{dest}.sent.json"
    if not _under_output(log):
        raise SystemExit(f"ログ {log} が {OUTPUT_DIR.relative_to(ROOT)}/ の外を指す")
    if log.exists():
        raise SystemExit(f"{log.name} があるので送らない（同じ宛先に同じ本文を二重に送らないため）")
    if args.tag_id is not None:
        create, to = build_create_for_tag(subject, body, args.tag_id), {"tag_id": args.tag_id}
    else:
        create, to = build_create(subject, body), {"subscriber_id": args.subscriber_id}
    created = request(create, api_key, opener)
    email_id = created.get("id")
    if not email_id:
        raise SystemExit("email の作成に失敗した（応答に id が無い）")
    record = {"provider": PROVIDER["name"], "email_id": email_id, **to}
    log_dir.mkdir(parents=True, exist_ok=True)
    # 送信の前に書く。送信の途中で落ちても、再実行が二重送信に進まずログで止まる
    log.write_text(json.dumps({**record, "sent": False}) + "\n", encoding="utf-8")
    if created.get("status") != PROVIDER["expected_status"]:
        # draft 以外（about_to_send 等）で作られた疑い。購読者1人への送信には進まない
        raise MaybeSent(f"作成した email {email_id} の status が {created.get('status')!r}（{PROVIDER['expected_status']} でない）。送信を中止")
    if args.tag_id is not None:
        if created.get("filters") != create["json"]["filters"]:
            # 絞り込みが落ちた・変わった draft を publish すると、タグの外の購読者にも届く
            raise SystemExit(f"作成した email {email_id} の filters が送ったものと一致しない。送信を中止（draft のまま残る）")
        request(build_publish(email_id), api_key, opener)
    else:
        request(build_send(email_id, args.subscriber_id), api_key, opener)
    log.write_text(json.dumps({**record, "sent": True}) + "\n", encoding="utf-8")
    print(f"送信: {plan} / email {email_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
