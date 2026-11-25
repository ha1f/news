#!/usr/bin/env python3
"""配信済みの `_posts/` 1件から、有料読者に届くメール本文の評価用コピーを作る (#700)。

有料 run は curate-news の出力（`output/` の .md、先頭が `## ニュース (...)` 見出し）を
render_email_body.py に渡して本文を作る。`_posts/` はそれを Jekyll の投稿形式に変換したもの
（front matter を足し、見出し行を落とす）なので、そのまま渡すと front matter がリード文に混ざり、
件名（HTML の <title>）も決まらない。ここで front matter を剥がして見出しを戻してから同じ
render_email_body.py に通し、送られる本文と同じ組み版で評価できるようにする。

使い方: python3 .claude/skills/evaluate-and-triage/scripts/email_preview.py _posts/{日付}-news-{プロファイル}.md [--footer FOOTER.json]
出力: .claude/skills/curate-news/output/eval-email/{入力の stem}.txt と .html（gitignore 対象。公開物に書かない）

--footer を省くと（公開 repo の作業環境には footer.json が無い。本物は有料 run の private な ROOT_DIR にある）、
送信者名と配信停止の案内を評価用の仮の文面で入れる。位置と体裁は本物と同じで、文面だけが仮になる。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / ".claude" / "scripts"))
import paid_daily  # noqa: E402
import render_email_body  # noqa: E402

EVAL_DIR = render_email_body.OUTPUT_DIR / "eval-email"
PROFILES_DIR = ROOT / ".claude" / "skills" / "curate-news" / "profiles"
POST_NAME_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})-news(?:-(?P<profile>[a-z0-9-]+))?\.md$")
PLACEHOLDER_FOOTER = {"sender": "（送信者名・評価用の仮の文面）", "unsubscribe_url": "https://example.invalid/unsubscribe", "lines": []}


def to_curated(text, date):
    """`_posts/` の本文から front matter を剥がし、curate-news の出力と同じ見出し行を先頭に戻す。"""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        except StopIteration:
            raise ValueError("front matter が閉じていない")
        lines = lines[end + 1:]
    body = "\n".join(lines).strip("\n")
    return f"## ニュース ({date} JST)\n\n{body}\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("post", type=Path, help="_posts/{日付}-news[-{プロファイル}].md")
    ap.add_argument("--footer", type=Path, help="本物の footer.json（省くと評価用の仮の文面）")
    args = ap.parse_args(argv)
    m = POST_NAME_RE.match(args.post.name)
    if not m:
        raise SystemExit(f"{args.post.name} は _posts/{{日付}}-news[-{{プロファイル}}].md の形でない")
    try:
        curated = to_curated(args.post.read_text(encoding="utf-8"), m["date"])
    except OSError as e:
        raise SystemExit(f"{args.post} を読めない: {e}")
    except ValueError as e:
        raise SystemExit(f"{args.post}: {e}")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    src = EVAL_DIR / args.post.name
    src.write_text(curated, encoding="utf-8")
    footer = args.footer
    if footer is None:
        footer = EVAL_DIR / "footer.placeholder.json"
        footer.write_text(json.dumps(PLACEHOLDER_FOOTER, ensure_ascii=False), encoding="utf-8")
    # 有料 run と同じく、プロファイルの front matter の title をフィード名にする（メインのフィードには無い）
    name = paid_daily.profile_name(PROFILES_DIR / f"{m['profile']}.md") if m["profile"] else None
    render_email_body.main([str(src), "--footer", str(footer), *(["--name", name] if name else [])])
    for ext in ("txt", "html"):
        print(EVAL_DIR.relative_to(ROOT) / f"{src.stem}.{ext}")
    print("フッタ: " + ("本物（--footer）" if args.footer else "評価用の仮の文面（送信者名・配信停止の文面は語らせない）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
