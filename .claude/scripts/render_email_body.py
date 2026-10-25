#!/usr/bin/env python3
"""curate-news の出力（output/ 配下の .md）から、有料読者向けメール本文（HTML/テキスト）を作る (#528)。

決定的: 同じ入力から常に同じ出力。記事本文・画像は扱わず、リンクと既存の要約（リード・読みどころ）と、--footer で渡したフッタだけを使う。
入力・出力とも gitignore 対象の `.claude/skills/curate-news/output/` に置き、公開 repo にコミットしない。
入力・出力先とも、resolve した実体が `.claude/skills/curate-news/output/` の下にないと拒否する（`_posts/` や公開物の下に書かない）。

使い方: python3 .claude/scripts/render_email_body.py <output/{日付}-{ハッシュ}.md> [--out-dir DIR] [--footer FOOTER.json]
出力: <out-dir>/{入力の stem}.html と .txt（既定の out-dir は入力と同じディレクトリ）

--footer を渡すと、本文の末尾に送信者の名称と配信停止の案内を入れる（特定電子メール法 4 条の表示。#595）。
文面は公開 repo に置かず、有料 run の ROOT_DIR（private repo）の footer.json から渡す:
  {"sender": "送信者の氏名又は名称", "unsubscribe_url": "{{ unsubscribe_url }}", "lines": ["住所: ...", "問い合わせ: ..."]}
unsubscribe_url は https の URL か、配信サービスが購読者ごとに差し込む配信停止リンクの変数（`{{ unsubscribe_url }}`）。lines は任意。
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ITEM_RE = re.compile(
    r"^\d+\.\s+\[(?P<title>.+?)\]\((?P<url>https?://\S+)\)(?:\s+\((?P<source>[^)]*)\))?\s*(?:<br>\s*(?P<note>.*))?$"
)
NUMBERED_RE = re.compile(r"^\d+\.\s")
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / ".claude" / "skills" / "curate-news" / "output"
HEADING_RE = re.compile(r"^##\s+(?P<heading>.+?)\s*$")
# 配信停止の案内先: https の URL か、配信サービスが購読者ごとに差し込む配信停止リンクの変数（Buttondown の
# {{ unsubscribe_url }}）。別の変数（{{ subscriber.email }} 等）の書き間違いを通さないよう、変数名はこれだけにする。
# 配信サービスを変えたら send_email.py の PROVIDER と一緒にここを差し替える
UNSUBSCRIBE_RE = re.compile(r"^(?:https://\S+|\{\{\s*unsubscribe_url\s*\}\})$")
# フッタを入れた HTML の印。send_email.py --send はこれの無い本文を送らない（記事由来の文字列はエスケープされるので偽造されない）
FOOTER_MARK = "<!-- footer: sender, unsubscribe -->"


def load_footer(path):
    """footer.json を読み、{sender, unsubscribe_url, lines} を返す。未設定・空・不正なら ValueError。"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError:
        raise ValueError(f"{Path(path).name} が無いか読めない")
    except ValueError as e:
        raise ValueError(f"{Path(path).name} が JSON でない: {e}")
    if not isinstance(data, dict):
        raise ValueError("フッタは {\"sender\": ..., \"unsubscribe_url\": ...} の形にする")

    def one_line(v):
        return isinstance(v, str) and v.strip() and "\n" not in v and "\r" not in v

    sender = data.get("sender")
    if not one_line(sender):
        raise ValueError("sender（送信者の氏名又は名称）が無いか空")
    url = data.get("unsubscribe_url")
    if not isinstance(url, str) or not UNSUBSCRIBE_RE.match(url.strip()):
        raise ValueError("unsubscribe_url（配信停止の案内先）が無いか、https の URL・テンプレート変数のどちらでもない")
    lines = data.get("lines", [])
    if not isinstance(lines, list) or not all(one_line(x) for x in lines):
        raise ValueError("lines は空でない1行の文字列の配列にする")
    return {"sender": sender.strip(), "unsubscribe_url": url.strip(), "lines": [x.strip() for x in lines]}


def footer_text_lines(footer):
    return [
        f"このメールは {footer['sender']} がお送りしています。",
        f"配信を停止する（今後受け取らない）場合: {footer['unsubscribe_url']}",
        *footer["lines"],
    ]


def parse(text):
    """output の markdown を {heading, lead, items[{title,url,source,note}]} に分解する。"""
    heading = ""
    lead = []
    items = []
    for raw in text.splitlines():
        line = raw.rstrip()
        m = ITEM_RE.match(line)
        if m:
            items.append({"title": m["title"], "url": m["url"], "source": m["source"] or "", "note": (m["note"] or "").strip()})
            continue
        if items and line.startswith((" ", "\t")) and line.strip():
            note = line.strip()
            items[-1]["note"] = (items[-1]["note"] + " " + note).strip()
            continue
        h = HEADING_RE.match(line)
        if h and not heading:
            heading = h["heading"]
            continue
        if not items and line.strip() and not line.startswith("---"):
            lead.append(line.strip())
    return {"heading": heading, "lead": " ".join(lead), "items": items}


def render_text(doc, footer=None):
    out = []
    if doc["heading"]:
        out += [doc["heading"], ""]
    if doc["lead"]:
        out += [doc["lead"], ""]
    for i, it in enumerate(doc["items"], 1):
        src = f" ({it['source']})" if it["source"] else ""
        out.append(f"{i}. {it['title']}{src}")
        if it["note"]:
            out.append(f"   {it['note']}")
        out += [f"   {it['url']}", ""]
    if footer:
        out += ["--", *footer_text_lines(footer)]
    return "\n".join(out).rstrip() + "\n"


def render_html(doc, footer=None):
    e = html.escape
    parts = [
        '<!DOCTYPE html>',
        '<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{e(doc['heading'] or 'ニュース')}</title></head>",
        '<body style="margin:0;padding:16px;font-family:sans-serif;line-height:1.6;color:#222;">',
        '<div style="max-width:640px;margin:0 auto;">',
    ]
    if doc["heading"]:
        parts.append(f'<h2 style="font-size:18px;margin:0 0 12px;">{e(doc["heading"])}</h2>')
    if doc["lead"]:
        parts.append(f'<p style="margin:0 0 16px;">{e(doc["lead"])}</p>')
    parts.append('<ol style="padding-left:20px;margin:0;">')
    for it in doc["items"]:
        src = f' <span style="color:#666;">({e(it["source"])})</span>' if it["source"] else ""
        note = f'<br><span>{e(it["note"])}</span>' if it["note"] else ""
        parts.append(
            f'<li style="margin:0 0 14px;"><a href="{e(it["url"], quote=True)}">{e(it["title"])}</a>{src}{note}</li>'
        )
    parts.append("</ol>")
    if footer:
        url = e(footer["unsubscribe_url"], quote=True)
        parts += [
            FOOTER_MARK,
            '<hr style="border:none;border-top:1px solid #ddd;margin:24px 0 12px;">',
            '<p style="margin:0;font-size:12px;color:#666;">',
            f"このメールは {e(footer['sender'])} がお送りしています。<br>",
            f'配信を停止する（今後受け取らない）場合: <a href="{url}">配信停止</a>',
            *(f"<br>{e(x)}" for x in footer["lines"]),
            "</p>",
        ]
    parts += ["</div>", "</body></html>"]
    return "\n".join(parts) + "\n"


def _under_output(p):
    return p.resolve().is_relative_to(OUTPUT_DIR.resolve())


def check_paths(src, out_dir):
    """入力ファイル・出力先とも、curate-news の output/ の下にあること。

    この output/ は gitignore 対象なので、公開 repo・Pages に出ない。名前が `output` なだけの別の
    ディレクトリ（`_posts/output`、repo ルートの `output` など）は gitignore されないので受け付けない。
    """
    if not _under_output(src):
        raise SystemExit(f"入力 {src} が {OUTPUT_DIR.relative_to(ROOT)}/ の下にない")
    if not _under_output(out_dir):
        raise SystemExit(f"出力先 {out_dir} が {OUTPUT_DIR.relative_to(ROOT)}/ の下にない。公開される場所に書かないため、ここだけ受け付ける")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--footer", type=Path, help="送信者の名称と配信停止の案内（footer.json）")
    args = ap.parse_args(argv)
    src = args.input
    out_dir = args.out_dir or src.parent
    check_paths(src, out_dir)
    footer = None
    if args.footer:
        try:
            footer = load_footer(args.footer)
        except ValueError as e:
            raise SystemExit(f"フッタを読めない: {e}")
    text = src.read_text(encoding="utf-8")
    doc = parse(text)
    numbered = sum(1 for ln in text.splitlines() if NUMBERED_RE.match(ln))
    if numbered != len(doc["items"]):
        raise SystemExit(f"番号付き行 {numbered} 件に対し記事を {len(doc['items'])} 件しか読めなかった（記事を取りこぼしている）")
    if not doc["items"]:
        raise SystemExit(f"{src} から記事を1件も読めなかった（形式が curate-news の出力と違う）")
    outs = {out_dir / f"{src.stem}.html": render_html(doc, footer), out_dir / f"{src.stem}.txt": render_text(doc, footer)}
    for dst in outs:
        # 出力ファイル自体が output/ の外への symlink でないこと、入力を上書きしないこと
        if not _under_output(dst) or dst.resolve() == src.resolve():
            raise SystemExit(f"書き込み先 {dst} が {OUTPUT_DIR.relative_to(ROOT)}/ の外を指すか、入力と同じ")
    out_dir.mkdir(parents=True, exist_ok=True)
    for dst, body in outs.items():
        dst.write_text(body, encoding="utf-8")
    print(f"{src.stem}: {len(doc['items'])} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
