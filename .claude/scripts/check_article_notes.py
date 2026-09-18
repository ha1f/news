#!/usr/bin/env python3
"""記事一覧の各項目に読みどころが付いているか検証する (#325)。

読みどころが無い項目は、読者が見出しだけで「開くか」を判断することになり、
そこだけ流し読みのリズムが止まる。投稿ファイルを作ったら commit 前に実行する。

使い方:
  python3 .claude/scripts/check_article_notes.py                     # 当日 (JST) の投稿
  python3 .claude/scripts/check_article_notes.py _posts/2026-09-18-news.md ...
  python3 .claude/scripts/check_article_notes.py --all               # 全投稿（棚卸し用）

終了コード 0 なら、検査した全項目に読みどころがある。
"""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
ITEM_RE = re.compile(r"^\d+\. \[(?P<title>.*?)\]\((?P<url>[^)]*)\)(?P<rest>.*)$")


def items_of(post: Path):
    """投稿本文の記事項目を (見出し, 読みどころ) で返す"""
    text = post.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    lines = body.split("\n")
    for i, line in enumerate(lines):
        m = ITEM_RE.match(line)
        if not m:
            continue
        note = ""
        if "<br>" in m.group("rest"):
            # <br> 以降（同じ行の残り + 続く字下げ行）が読みどころ
            tail = [m.group("rest").split("<br>", 1)[1]]
            for follow in lines[i + 1:]:
                if not follow.strip() or ITEM_RE.match(follow):
                    break
                tail.append(follow)
            note = "".join(tail).strip()
        yield m.group("title"), note


def main(argv):
    if "--all" in argv:
        posts = sorted(Path("_posts").glob("*.md"))
    elif [a for a in argv if not a.startswith("--")]:
        posts = [Path(a) for a in argv if not a.startswith("--")]
    else:
        today = datetime.now(JST).strftime("%Y-%m-%d")
        posts = sorted(Path("_posts").glob(f"{today}-*.md"))
        if not posts:
            print(f"{today} の投稿がありません（_posts/{today}-*.md）", file=sys.stderr)
            return 1

    checked = missing = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            missing += 1
            continue
        for title, note in items_of(post):
            checked += 1
            if not note:
                print(f"NG {post.name}: 読みどころなし 「{title}」")
                missing += 1

    print(f"検査 {checked} 件 / 読みどころなし {missing} 件")
    return 1 if missing or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
