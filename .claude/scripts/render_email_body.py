#!/usr/bin/env python3
"""curate-news の出力（output/ 配下の .md）から、有料読者向けメール本文（HTML/テキスト）を作る (#528)。

決定的: 同じ入力から常に同じ出力。記事本文・画像は扱わず、リンクと既存の要約（リード・読みどころ）だけを使う。
入力・出力とも gitignore 対象の `.claude/skills/curate-news/output/` に置き、公開 repo にコミットしない。
`_posts/` を入力にしたり、出力を `_posts/` や公開物の下に書いたりすることは拒否する。

使い方: python3 .claude/scripts/render_email_body.py <output/{日付}-{ハッシュ}.md> [--out-dir DIR]
出力: <out-dir>/{入力の stem}.html と .txt（既定の out-dir は入力と同じディレクトリ）
"""
import argparse
import html
import re
import sys
from pathlib import Path

ITEM_RE = re.compile(r"^(\d+)\.\s+\[(?P<title>.+?)\]\((?P<url>https?://[^)\s]+)\)\s*(?:\((?P<source>.*)\))?\s*(?:<br>)?\s*$")
HEADING_RE = re.compile(r"^##\s+(?P<heading>.+?)\s*$")
FORBIDDEN_DIRS = ("_posts", "_site", "assets", "docs")


def parse(text):
    """output の markdown を {heading, lead, items[{title,url,source,note}]} に分解する。"""
    heading = ""
    lead = []
    items = []
    for raw in text.splitlines():
        line = raw.rstrip()
        m = ITEM_RE.match(line)
        if m:
            items.append({"title": m["title"], "url": m["url"], "source": m["source"] or "", "note": ""})
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


def render_text(doc):
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
    return "\n".join(out).rstrip() + "\n"


def render_html(doc):
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
    parts += ["</ol>", "</div>", "</body></html>"]
    return "\n".join(parts) + "\n"


def check_paths(src, out_dir):
    for label, p in (("入力", src), ("出力先", out_dir)):
        parts = set(p.resolve().parts)
        bad = parts & set(FORBIDDEN_DIRS)
        if bad:
            raise SystemExit(f"{label} {p} は公開される場所（{', '.join(sorted(bad))}）にある。output/ 配下を使う")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path)
    args = ap.parse_args(argv)
    src = args.input
    out_dir = args.out_dir or src.parent
    check_paths(src, out_dir)
    doc = parse(src.read_text(encoding="utf-8"))
    if not doc["items"]:
        raise SystemExit(f"{src} から記事を1件も読めなかった（形式が curate-news の出力と違う）")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{src.stem}.html").write_text(render_html(doc), encoding="utf-8")
    (out_dir / f"{src.stem}.txt").write_text(render_text(doc), encoding="utf-8")
    print(f"{src.stem}: {len(doc['items'])} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
