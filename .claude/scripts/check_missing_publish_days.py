#!/usr/bin/env python3
"""直近の配信欠落（`_posts/` に投稿が1件も無い日）を機械的に検出する (#421)。

2026-09-25 の週次利用上限の枯渇でループが約42時間停止し、その日の配信が丸ごと
欠落した。欠落は誰にも通知されず、翌日の evaluate も気づかなかった。この検査は
その再発を機械で検出するためのもの。判定は決定的（日付ごとに `_posts/` へ1件
でも投稿があるかを見るだけ）なので、GUARDRAILS.md の設計原則どおりスクリプトに
寄せ、原因の診断（利用上限か・コードの退行か）と対応の判断は evaluate-and-triage
の Step 0 に委ねる。

working tree の checkout 状態に依存しないよう、ファイル一覧は `git ls-tree` で
指定 ref（既定 `origin/main`）から取る。呼び出し側が事前に `git fetch origin
main` していることが前提（`check_protected_paths.py` と同じ規約。fetch 無しで
古い ref を見ると、その後 main に入った投稿を「欠落」と誤検知する）。当日は
配信がまだ実行されていない可能性があるため検査対象から外す（当日分の有無は
`check_state.py` の `post_in_main` が別途見ている）。

使い方:
  python3 .claude/scripts/check_missing_publish_days.py                 # 直近14日
  python3 .claude/scripts/check_missing_publish_days.py --lookback-days 30
  python3 .claude/scripts/check_missing_publish_days.py --ref origin/main

出力: 欠落日を1行1件、古い順に標準出力へ（0件なら出力なし）。
終了コード: 欠落日が1件でもあれば1、無ければ0。
"""
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
FILENAME_DATE_RE = re.compile(r'^_posts/(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})-')
DEFAULT_LOOKBACK_DAYS = 14
DEFAULT_REF = "origin/main"


def posted_dates(filenames):
    """`_posts/` のファイル名一覧から、投稿が1件以上ある日付 (YYYY-MM-DD) の集合を作る（純関数）。"""
    dates = set()
    for name in filenames:
        m = FILENAME_DATE_RE.match(name)
        if m:
            dates.add(f"{m.group('y')}-{m.group('m')}-{m.group('d')}")
    return dates


def date_range(start, end):
    """[start, end] を1日刻みで返す（両端含む、純関数）。"""
    days, d = [], start
    while d <= end:
        days.append(d)
        d += timedelta(days=1)
    return days


def missing_days(filenames, start, end):
    """[start, end] のうち `_posts/` に1件も投稿の無い日を古い順に返す（純関数）。

    start より前の日は「配信開始前」であり得るため、呼び出し側が配信開始日以降に
    丸めてから渡す（main 側は earliest_date を使う）。"""
    existing = posted_dates(filenames)
    return [d.strftime("%Y-%m-%d") for d in date_range(start, end)
            if d.strftime("%Y-%m-%d") not in existing]


def earliest_date(filenames):
    """最初に投稿がある日付を返す（1件も無ければ None、純関数）。"""
    dates = posted_dates(filenames)
    return date.fromisoformat(min(dates)) if dates else None


def list_post_filenames(ref):
    """`git ls-tree` で `<ref>` 時点の `_posts/` 配下のファイル名一覧を取る。"""
    proc = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", "_posts/"],
        capture_output=True, text=True, check=True)
    return proc.stdout.splitlines()


def parse_args(argv):
    ref, lookback = DEFAULT_REF, DEFAULT_LOOKBACK_DAYS
    i = 0
    while i < len(argv):
        if argv[i] == "--ref" and i + 1 < len(argv):
            ref = argv[i + 1]
            i += 2
        elif argv[i] == "--lookback-days" and i + 1 < len(argv):
            lookback = int(argv[i + 1])
            i += 2
        else:
            i += 1
    return ref, lookback


def find_missing_days(ref, lookback, today=None):
    """git から取得した実データに対して、検査範囲を決めて `missing_days` を呼ぶ。

    検査範囲は当日を除く直近 `lookback` 日（[today - lookback, today - 1]）。"""
    filenames = list_post_filenames(ref)
    today = today or datetime.now(JST).date()
    start = today - timedelta(days=lookback)
    earliest = earliest_date(filenames)
    if earliest and earliest > start:
        start = earliest
    end = today - timedelta(days=1)
    if start > end:
        return []
    return missing_days(filenames, start, end)


def main(argv):
    ref, lookback = parse_args(argv)
    days = find_missing_days(ref, lookback)
    for d in days:
        print(d)
    return 1 if days else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
