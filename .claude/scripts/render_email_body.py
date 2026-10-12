#!/usr/bin/env python3
"""curate-news の出力（output/ 配下の .md）から、有料読者向けメール本文（HTML/テキスト）を作る (#528)。

決定的: 同じ入力から常に同じ出力。記事本文・画像は扱わず、リンクと既存の要約（リード・読みどころ）だけを使う。
入力・出力とも gitignore 対象の `.claude/skills/curate-news/output/` に置き、公開 repo にコミットしない。
入力・出力先とも、resolve した実体が `.claude/skills/curate-news/output/` の下にないと拒否する（`_posts/` や公開物の下に書かない）。

使い方: python3 .claude/scripts/render_email_body.py <output/{日付}-{ハッシュ}.md> [--out-dir DIR]
出力: <out-dir>/{入力の stem}.html と .txt（既定の out-dir は入力と同じディレクトリ）
"""
import argparse
import html
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


def _under_output(p):
    return p.resolve().is_relative_to(OUTPUT_DIR.resolve())


def check_paths(src, out_dir):
    """入力ファイル・出力先とも、curate-news の output/ の下にあること。

    この output/ は gitignore 対象なので、公開 repo・Pages に出ない。名前が `output` なだけの別の
    ディレクトリ（`_posts/output`、repo ルートの `output` など）は gitignore されないので受け付けない。
    """
    if not _under_output(src.parent):
        raise SystemExit(f"入力 {src} が {OUTPUT_DIR.relative_to(ROOT)}/ の下にない")
    if not _under_output(out_dir):
        raise SystemExit(f"出力先 {out_dir} が {OUTPUT_DIR.relative_to(ROOT)}/ の下にない。公開される場所に書かないため、ここだけ受け付ける")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path)
    args = ap.parse_args(argv)
    src = args.input
    out_dir = args.out_dir or src.parent
    check_paths(src, out_dir)
    text = src.read_text(encoding="utf-8")
    doc = parse(text)
    numbered = sum(1 for ln in text.splitlines() if NUMBERED_RE.match(ln))
    if numbered != len(doc["items"]):
        raise SystemExit(f"番号付き行 {numbered} 件に対し記事を {len(doc['items'])} 件しか読めなかった（記事を取りこぼしている）")
    if not doc["items"]:
        raise SystemExit(f"{src} から記事を1件も読めなかった（形式が curate-news の出力と違う）")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{src.stem}.html").write_text(render_html(doc), encoding="utf-8")
    (out_dir / f"{src.stem}.txt").write_text(render_text(doc), encoding="utf-8")
    print(f"{src.stem}: {len(doc['items'])} 件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
