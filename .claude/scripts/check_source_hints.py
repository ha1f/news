#!/usr/bin/env python3
"""記事リストのソース表記に、読者向け属性（言語・購読）が付いているか検証する (#327)。

読者はリンクを開くまで、着地先が外国語か・購読が必要かを知る手段がない。
属性はソース定義 (`.claude/skills/curate-news/references/sources/*.md`) の
「読者向け属性」で決まるので、投稿側の表記がそれと一致しているかを機械で確かめる。

使い方:
  python3 .claude/scripts/check_source_hints.py                    # 当日 (JST) の投稿
  python3 .claude/scripts/check_source_hints.py _posts/....md ...
  python3 .claude/scripts/check_source_hints.py --all              # 全投稿（棚卸し用）
"""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
SOURCES_DIR = Path(".claude/skills/curate-news/references/sources")
# 出力で使われてきた表示名のゆれ。正規の表示名はソース定義の「表示名」が正。
ALIASES = {
    "Hacker News": "HN",
    "はてなブックマーク": "はてブ",
    "Product Hunt": "PH",
    "日経新聞": "日経",
    "MIT Technology Review": "MIT TR",
    "MIT Tech Review": "MIT TR",
    "Nature Machine Intelligence": "Nature",
    "Nature MI": "Nature",
}
ITEM_RE = re.compile(r"^\d+\. \[(?P<title>.*?)\]\([^)]*\)\s*\((?P<label>[^)]*)\)")
DISPLAY_RE = re.compile(r"^## 表示名\s*\n+`(?P<name>[^`]+)`", re.M)
LANG_RE = re.compile(r"^- \*\*リンク先の言語\*\*:\s*(?P<v>.+)$", re.M)
ACCESS_RE = re.compile(r"^- \*\*購読\*\*:\s*(?P<v>.+)$", re.M)


def expected_labels():
    """{表示名: [付けるべきラベル]} を返す"""
    table = {}
    for path in sorted(SOURCES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        name = DISPLAY_RE.search(text)
        lang = LANG_RE.search(text)
        access = ACCESS_RE.search(text)
        if not (name and lang and access):
            print(f"NG {path}: 表示名 / 読者向け属性 が読み取れません")
            return None
        labels = []
        if lang.group("v").strip() != "日本語":
            labels.append(lang.group("v").strip())
        if access.group("v").strip() != "無料":
            labels.append(access.group("v").strip())
        table[name.group("name").strip()] = labels
    return table


def items_of(post: Path):
    text = post.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for line in body.split("\n"):
        m = ITEM_RE.match(line)
        if m:
            yield m.group("title"), m.group("label")


def main(argv):
    table = expected_labels()
    if table is None:
        return 1

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

    checked = failures = 0
    for post in posts:
        for title, label in items_of(post):
            checked += 1
            parts = [p.strip() for p in label.split("・")]
            name = ALIASES.get(parts[0], parts[0])
            if name not in table:
                print(f"NG {post.name}: 未知のソース名「{parts[0]}」 （{title}）")
                failures += 1
                continue
            got = [x for p in parts[1:] for x in p.split("/")]
            want = table[name]
            if got != want:
                shown = "・".join([parts[0]] + (["/".join(want)] if want else []))
                print(f"NG {post.name}: ソース表記が定義と違う "
                      f"（{title} — いま「{label}」/ あるべき「{shown}」）")
                failures += 1

    print(f"検査 {checked} 件 / 不一致 {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
