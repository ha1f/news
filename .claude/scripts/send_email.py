#!/usr/bin/env python3
"""render_email_body.py が作ったメール本文を、配信サービスの API で購読者1人（#555・#679）か、1つのタグを持つ購読者全員（#613）に送る。

既定は dry-run でネットワークに出ない。送る予定（宛先の購読者 ID・件名・本文のサイズ）を表示するだけ。
実送信は `--send` を明示し、API キーを環境変数に入れたときだけ行う。キーが無ければ何も送らずに非0で終わる。
本文に送信者名と配信停止の案内（render_email_body.py の --footer）が無いときも、--send は送らずに非0で終わる。
入力・ログとも、resolve した実体が `.claude/skills/curate-news/output/`（gitignore 対象）の下にないと拒否する。
宛先は配信サービス側の購読者 ID かタグ ID だけを受け付け、メールアドレスは受け付けない（repo・引数・ログに置かないため）。
購読者1人に送るときは、その人だけが持つタグ（読者専用タグ）の ID も渡す。そのタグで絞って配信し、
送る直前にタグを持つ購読者がその1人だけかを確かめる（#679）。

使い方: python3 .claude/scripts/send_email.py <output/.../{stem}.html> [--subscriber-id ID] --tag-id ID [--subject S] [--send]
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_email_body import FOOTER_MARK, OUTPUT_DIR, ROOT, _under_output  # noqa: E402

# 配信サービスに依存する部分はここだけ。サービスが決まったらこのブロックを差し替える。
# 仮の選定: Buttondown（docs/m5-paid-delivery.md の候補）。公開 OpenAPI
# https://docs.buttondown.com/openapi.json（api.buttondown.com/v1/openapi.json はここへ redirect）を 2026-10-18 に確認:
#   POST /v1/emails（EmailInput: subject 必須。status の既定は about_to_send = 全購読者への配信）
#   認証は `Authorization: Token <key>`
# 全購読者への配信にしないため、status は draft で作ってから送る。draft は配信にもアーカイブにも出ない
# （archival_mode も disabled にする）。
#
# タグで絞った配信（プレミアムフィード #613、完全パーソナライズ #679）は同じ OpenAPI（2026-10-28・2026-11-21 に確認）で組む:
#   EmailInput.filters（EmailFilterGroup: "Tag-based filter rules determining which subscribers receive this email."）に
#   {"field": "subscriber.tags", "operator": "contains", "value": <タグ ID>} を1つだけ入れる（Filter の説明:
#   "Tag filters require the tag's ID (either a UUID or TypeID), not its name."）
#   POST /v1/emails/{id}/publish（"Publishes and sends an email." 本文は EmailUpdateInput で、渡したフィールドだけを
#   更新してから送る。docs/api-emails-publish）
# 作成応答の status と filters が送ったものと一致したときだけ publish する（filters が落ちて全購読者への配信になるのを
# publish の前に止める）。publish の本文は空にして、filters を書き換えない。
#
# 完全パーソナライズは読者ごとに本文が違うので、1通ごとに email を作り、その読者だけが持つタグで絞って publish する。
# EmailFilter の field に購読者 ID は無い（subscriber.tags・subscriber.metadata.* など。2026-11-21 確認）ので、タグで絞る。
# email を作る前に GET /v1/subscribers?tag=<タグ ID>（"only return subscribers with the given tag(s)"）を type に全種を
# 並べて引き（type の既定の絞り込みで取りこぼさないため）、count が 1 で、その1人の id が渡した購読者 ID のときだけ送る。
# 以前は POST /v1/emails/{id}/send-draft で購読者 ID に送っていたが、公式 docs（docs/sending-emails、2026-11-21 確認）は
# 下書きを人に送る機能について「The draft will appear in the recipient's inbox with [PREVIEW] in the subject line.」
# 「This link renders in drafts but won't function until the email is sent.」（{{ unsubscribe_url }} のこと）と書いており、
# 有料読者への本番配信には使えない（#679）。
# 別案の status: transactional + POST /v1/subscribers/{id}/emails/{email_id} は一次情報で裏が取れない:
# EmailStatus の説明は「status は observability のためだけに公開」で、subscribers/{id}/emails/{email_id} は
# 「finalized なメール専用」（docs/api-subscribers-send-email）。
# 初回の実送信は、オーナーだけが購読するテスト用ニュースレターで、タグを持たない購読者に届かないこと・件名に [PREVIEW] が
# 付かないこと・配信停止リンクが本人用に展開されて効くことを確かめてから行う。
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


# 購読者の type の全種（OpenAPI の SubscriberType）。GET /v1/subscribers に全部並べて、既定の絞り込みで数え漏らさない
SUBSCRIBER_TYPES = ("blocked", "complained", "churning", "churned", "gifted", "unactivated", "unpaid", "undeliverable",
                    "premium", "past_due", "paused", "regular", "removed", "trialed", "unsubscribed", "upcoming")


def build_tag_holders(tag_id):
    """そのタグを持つ購読者を数えるリクエスト（type は全種）。"""
    query = urllib.parse.urlencode([("tag", tag_id), *(("type", t) for t in SUBSCRIBER_TYPES)])
    return {"method": "GET", "path": f"/subscribers?{query}", "json": None}


def check_only_holder(listed, tag_id, subscriber_id):
    """タグを持つ購読者がその1人だけでなければ SystemExit（publish すると他の人にも届くため）。"""
    if not isinstance(listed, dict):
        raise SystemExit(f"タグ {tag_id} を持つ購読者の一覧の応答が読めない")
    results = listed.get("results")
    if listed.get("count") != 1 or not isinstance(results, list) or len(results) != 1 or not isinstance(results[0], dict):
        raise SystemExit(f"タグ {tag_id} を持つ購読者が1人でない（count {listed.get('count')!r}）")
    if results[0].get("id") != subscriber_id:
        raise SystemExit(f"タグ {tag_id} を持つ購読者が {subscriber_id} でない")


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
    data = json.dumps(spec["json"]).encode() if spec["json"] is not None else None
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
    ap.add_argument("--subscriber-id", help="配信サービス側の購読者 ID（メールアドレスは不可）。--tag-id のタグを持つのが"
                    "この1人だけのときに限り送る（完全パーソナライズ）")
    ap.add_argument("--tag-id", required=True, help="配信サービス側のタグ ID（名前は不可）。そのタグを持つ購読者に送る。"
                    "--subscriber-id が無ければ、そのタグを持つ購読者全員に同じ本文を送る（プレミアムフィード）")
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
    if not TAG_ID_RE.match(args.tag_id):
        raise SystemExit("--tag-id は配信サービスのタグ ID（sub_tag_… か UUID）だけを受け付ける。タグ名は渡さない")
    if args.subscriber_id is None:
        dest, to_label = args.tag_id, f"タグ {args.tag_id} の購読者全員"
    else:
        if not SUBSCRIBER_ID_RE.match(args.subscriber_id):
            raise SystemExit("--subscriber-id は配信サービスの購読者 ID（英数字・_・-）だけを受け付ける。メールアドレスは渡さない")
        dest, to_label = args.subscriber_id, f"{args.subscriber_id}（タグ {args.tag_id} で絞る）"
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
    if args.subscriber_id is not None:
        # 読者専用タグを他の購読者も持っていると、その人にも別の読者向けの本文が届く。email を作る前に止める
        try:
            listed = request(build_tag_holders(args.tag_id), api_key, opener)
        except (OSError, ValueError) as e:
            # まだ何も作っていないので、届いたか分からない失敗ではない（呼び出し側が送信中の印を残さないよう SystemExit にする）
            raise SystemExit(f"タグ {args.tag_id} を持つ購読者を確かめられない ({type(e).__name__})。送らない")
        try:
            check_only_holder(listed, args.tag_id, args.subscriber_id)
        except SystemExit as e:
            raise SystemExit(f"{e}。送らない")
    create = build_create_for_tag(subject, body, args.tag_id)
    to = {"tag_id": args.tag_id} if args.subscriber_id is None else {"subscriber_id": args.subscriber_id, "tag_id": args.tag_id}
    created = request(create, api_key, opener)
    email_id = created.get("id")
    if not email_id:
        raise SystemExit("email の作成に失敗した（応答に id が無い）")
    record = {"provider": PROVIDER["name"], "email_id": email_id, **to}
    log_dir.mkdir(parents=True, exist_ok=True)
    # 送信の前に書く。送信の途中で落ちても、再実行が二重送信に進まずログで止まる
    log.write_text(json.dumps({**record, "sent": False}) + "\n", encoding="utf-8")
    if created.get("status") != PROVIDER["expected_status"]:
        # draft 以外（about_to_send 等）で作られた疑い。publish には進まない
        raise MaybeSent(f"作成した email {email_id} の status が {created.get('status')!r}（{PROVIDER['expected_status']} でない）。送信を中止")
    if created.get("filters") != create["json"]["filters"]:
        # 絞り込みが落ちた・変わった draft を publish すると、タグの外の購読者にも届く
        raise SystemExit(f"作成した email {email_id} の filters が送ったものと一致しない。送信を中止（draft のまま残る）")
    request(build_publish(email_id), api_key, opener)
    log.write_text(json.dumps({**record, "sent": True}) + "\n", encoding="utf-8")
    print(f"送信: {plan} / email {email_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
