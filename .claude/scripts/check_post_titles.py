#!/usr/bin/env python3
"""投稿の front matter `title` が、その日の内容を表す見出しになっているか検証する (#401)。

一覧（トップ・アーカイブ・プロファイル）は記事ページへの入口で、記事ページの
`<h1>` とブラウザのタブはこの `title` だけで作られる。ここが日付文字列のままだと、
読者は一覧で見出しを見て開いたのに、開いた先では「どの日を読んでいるか」しか
分からない。加えて一覧は日付を別途バッジ・meta で出すので、日付を含む title は
同じ日付を2回並べる。

生成側の規約は publish-pages/SKILL.md の「フロントマターの `title`」にあり、
`title` に日付を入れないことを求めている。この検査はその規約が守られているかを
機械で確かめる（規約の文面ではなく、出力を見る）。

検査するのは次の2つだけ:
  1. 見出しが空でない
  2. 見出しにその投稿自身の日付が入っていない（`（表示名）` は除いて見る）

「見出しがその日の内容を表しているか」は機械では判定できないので検査しない。
日付だけの title は 1 と 2 の両方でなく 2 で落ちる（`2026年9月21日（デザイナー）`
のように表示名が付いた形も、接尾辞を外した本体が日付なので同じく落ちる）。

使い方:
  python3 .claude/scripts/check_post_titles.py                    # 当日 (JST) の投稿
  python3 .claude/scripts/check_post_titles.py _posts/....md ...
  python3 .claude/scripts/check_post_titles.py --all              # 全投稿（棚卸し用）

終了コード 0 なら、検査した全投稿の title が規約どおり。
"""
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
TITLE_RE = re.compile(r'^title:\s*(?P<title>.*?)\s*$', re.M)
FILENAME_DATE_RE = re.compile(r'^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})-')
# 見出し末尾の `（プロファイル表示名）`。字数・日付の検査は本体だけを見る
SUFFIX_RE = re.compile(r'（[^（）]*）$')


def title_of(post: Path):
    """front matter の title を、囲みの引用符を外して返す。無ければ None"""
    text = post.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    front = text.split("---", 2)[1]
    m = TITLE_RE.search(front)
    if not m:
        return None
    title = m.group("title")
    if len(title) >= 2 and title[0] == title[-1] and title[0] in "\"'":
        title = title[1:-1]
    return title


def date_of(post: Path):
    """ファイル名の日付を返す。`_posts/` の命名規約なので front matter より確実"""
    m = FILENAME_DATE_RE.match(post.name)
    if not m:
        return None
    return date(int(m.group("y")), int(m.group("m")), int(m.group("d")))


def headline_of(title: str) -> str:
    """`（表示名）` の接尾辞を外した見出し本体"""
    return SUFFIX_RE.sub("", title).strip()


def date_forms(day: date):
    """その日付が title に現れうる表記。ゼロ埋めの有無を両方見る"""
    return [
        f"{day.year}年{day.month}月{day.day}日",
        f"{day.year}年{day.month:02d}月{day.day:02d}日",
        f"{day.month}月{day.day}日",
        f"{day.month:02d}月{day.day:02d}日",
        day.isoformat(),
        day.strftime("%Y/%m/%d"),
    ]


def problems_of(post: Path):
    """その投稿の title の問題を文字列で返す（問題が無ければ空）"""
    title = title_of(post)
    if title is None:
        return ["front matter に title がありません"]
    headline = headline_of(title)
    if not headline:
        return ["title が空です" if not title else f"title が接尾辞だけです（{title}）"]
    day = date_of(post)
    if day is None:
        return [f"ファイル名から日付が読み取れません（{post.name}）"]
    for form in date_forms(day):
        if form in headline:
            return [f"title に投稿自身の日付が入っています（{title}）"]
    return []


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

    checked = failures = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            failures += 1
            continue
        checked += 1
        for problem in problems_of(post):
            print(f"NG {post.name}: {problem}")
            failures += 1

    print(f"検査 {checked} 件 / 規約違反 {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
