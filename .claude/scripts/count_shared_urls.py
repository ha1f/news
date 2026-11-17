#!/usr/bin/env python3
"""同じ日の複数フィードが同じ記事（URL）を選んだ本数を数える（#612）。

記事ごとの作業（本文の取得・事実の確認・見出しと読みどころ）をフィード間で共有したら、
どれだけの枠を省けるかの見積もりに使う。公開フィードの `_posts/` だけを読む。

- 対象: `_posts/{YYYY-MM-DD}-news*.md`。同じ日付のファイルを 1 日のフィード群とみなす
- 本文の番号付き行 `N. [見出し](URL)` から URL を取る。URL は完全一致で比べる（正規化しない）
- 省ける枠 = その日の掲載枠（各フィードの件数の和）− 異なる URL の数

使い方:
  python3 .claude/scripts/count_shared_urls.py --since 2026-10-18 --until 2026-11-01 [--posts _posts] [--json]
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ITEM_RE = re.compile(r"^\d+\.\s+\[[^\]]*\]\((\S+?)\)", re.MULTILINE)
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-news(?:-[\w-]+)?\.md$")


def urls_in(text):
    return ITEM_RE.findall(text)


def count_day(feeds):
    """feeds: {フィード名: [URL, ...]} → その日の集計。"""
    per_url = Counter()
    slots = 0
    for urls in feeds.values():
        slots += len(urls)
        per_url.update(set(urls))
    distinct = len(per_url)
    shared = {u: n for u, n in per_url.items() if n >= 2}
    return {
        "feeds": len(feeds),
        "slots": slots,
        "distinct_urls": distinct,
        "shared_urls": len(shared),
        "saved_slots": slots - distinct,
        "shared_by_feed_count": dict(sorted(Counter(shared.values()).items())),
    }


def collect(posts_dir, since, until):
    days = defaultdict(dict)
    for path in sorted(Path(posts_dir).glob("*.md")):
        m = NAME_RE.match(path.name)
        if not m:
            continue
        day = m.group(1)
        if since and day < since or until and day > until:
            continue
        days[day][path.stem] = urls_in(path.read_text(encoding="utf-8"))
    return dict(sorted(days.items()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--posts", default="_posts")
    ap.add_argument("--since", help="YYYY-MM-DD（含む）")
    ap.add_argument("--until", help="YYYY-MM-DD（含む）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    per_day = {d: count_day(f) for d, f in collect(args.posts, args.since, args.until).items()}
    if not per_day:
        print("対象の投稿がありません", file=sys.stderr)
        return 1
    total = {k: sum(v[k] for v in per_day.values()) for k in ("slots", "distinct_urls", "shared_urls", "saved_slots")}
    by_count = Counter()
    for v in per_day.values():
        by_count.update(v["shared_by_feed_count"])
    total["shared_by_feed_count"] = dict(sorted(by_count.items()))
    total["days"] = len(per_day)
    total["saved_ratio"] = round(total["saved_slots"] / total["slots"], 4) if total["slots"] else 0.0

    if args.json:
        json.dump({"total": total, "per_day": per_day}, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    print("day\tfeeds\tslots\tdistinct\tshared_urls\tsaved_slots\tsaved_ratio")
    for d, v in per_day.items():
        ratio = v["saved_slots"] / v["slots"] if v["slots"] else 0
        print(f"{d}\t{v['feeds']}\t{v['slots']}\t{v['distinct_urls']}\t{v['shared_urls']}\t{v['saved_slots']}\t{ratio:.1%}")
    print(
        f"total\t{total['days']}日\t{total['slots']}\t{total['distinct_urls']}\t{total['shared_urls']}"
        f"\t{total['saved_slots']}\t{total['saved_ratio']:.1%}"
    )
    print(f"共有された URL のフィード数の内訳: {total['shared_by_feed_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
