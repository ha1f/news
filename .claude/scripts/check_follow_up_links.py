#!/usr/bin/env python3
"""ビルド済みサイトの「続報（M/D掲載）」が、同じフィードのその日の日次ページへリンクしているか検証する (#559)。

読みどころ冒頭の `続報（M/D掲載）。` は、_layouts/post.html がビルド時に掲載日部分をリンクにする。
リンクが無い・別フィードや別の日を指す・404 になると、前回を読んでいない読者は元の出来事に戻れない。

検査すること:
  1. リンクの着地先が実在し、同じフィード（メインならメイン、プロファイルなら同じプロファイル）の日次ページである
  2. 着地先の日付が表記の M/D と一致し、このページより前で1年以内である（年またぎも正しい年に飛ぶ）
  3. リンクの付いていない表記について、同じフィードにその日のページがあるなら NG（付け損ね）。
     無ければ文字のまま残るのが正しいので件数だけ報告する

使い方:
  python3 .claude/scripts/check_follow_up_links.py [_site]
"""
import datetime
import re
import sys
from pathlib import Path

PAGE_RE = re.compile(r"(\d{4})/(\d{2})/(\d{2})/(news(?:-[\w-]+)?)\.html$")
LINKED_RE = re.compile(r'続報（<a class="follow-up-link" href="(?P<href>[^"]+)">(?P<m>\d{1,2})/(?P<d>\d{1,2})掲載</a>）')
# 見出しのリンク文字列の先頭（`">続報（`）にある表記は読みどころではないので数えない
BARE_RE = re.compile(r'(?<!">)続報（(?P<m>\d{1,2})/(?P<d>\d{1,2})掲載）')
# 検査するのは本文だけ。meta description や JSON-LD に入った抜粋はリンクにできない場所なので外す
BODY_RE = re.compile(r'itemprop="articleBody">(.*?)</article>', re.S)


def page_key(path):
    """'.../YYYY/MM/DD/news-xxx.html' → (date, フィード名)。日次ページでなければ None"""
    m = PAGE_RE.search(str(path).replace("\\", "/"))
    if not m:
        return None
    return datetime.date(int(m[1]), int(m[2]), int(m[3])), m[4]


def nearest_prior(page_date, month, day):
    """page_date より前で最も近い month/day の日付"""
    try:
        cand = datetime.date(page_date.year, month, day)
    except ValueError:
        cand = None
    if cand is None or cand >= page_date:
        try:
            cand = datetime.date(page_date.year - 1, month, day)
        except ValueError:
            return None
    return cand


def check(site):
    site = Path(site)
    pages = {}
    for path in site.glob("[0-9][0-9][0-9][0-9]/*/*/news*.html"):
        key = page_key(path.relative_to(site))
        if key:
            pages[key] = path
    errors, linked, unlinked = [], 0, 0
    for (page_date, feed), path in sorted(pages.items()):
        rel = path.relative_to(site)
        body = BODY_RE.search(path.read_text(encoding="utf-8"))
        text = body[1] if body else ""
        for m in LINKED_RE.finditer(text):
            linked += 1
            target = page_key(m["href"])
            label = f'{m["m"]}/{m["d"]}'
            if target is None:
                errors.append(f"{rel}: 続報（{label}掲載）のリンク先が日次ページでない: {m['href']}")
                continue
            t_date, t_feed = target
            if t_feed != feed:
                errors.append(f"{rel}: 続報（{label}掲載）が別フィードを指す: {m['href']}")
            if (t_date.month, t_date.day) != (int(m["m"]), int(m["d"])):
                errors.append(f"{rel}: 続報（{label}掲載）が別の日を指す: {m['href']}")
            if t_date != nearest_prior(page_date, int(m["m"]), int(m["d"])):
                errors.append(f"{rel}: 続報（{label}掲載）がこのページより前の直近1年の日付でない: {m['href']}")
            if target not in pages:
                errors.append(f"{rel}: 続報（{label}掲載）のリンク先が存在しない: {m['href']}")
        for m in BARE_RE.finditer(text):
            unlinked += 1
            prior = nearest_prior(page_date, int(m["m"]), int(m["d"]))
            if prior and (prior, feed) in pages:
                errors.append(f'{rel}: 続報（{m["m"]}/{m["d"]}掲載）にリンクが無い（同じフィードの {prior} は実在する）')
    return errors, linked, unlinked


def main():
    site = sys.argv[1] if len(sys.argv) > 1 else "_site"
    errors, linked, unlinked = check(site)
    for e in errors:
        print("NG", e)
    print(f"リンク {linked} 件 / 同じフィードに掲載日のページが無く文字のまま {unlinked - sum('リンクが無い' in e for e in errors)} 件 / 失敗 {len(errors)} 件")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
