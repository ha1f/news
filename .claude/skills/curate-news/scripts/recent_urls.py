#!/usr/bin/env python3
"""過去の掲載済みURLを抽出するスクリプト。

同じプロファイルの掲載履歴（公開済みの `_posts/` と手元の `output/`）だけを見る。
プロファイルが違えば同じ記事が載ってよいため、履歴はプロファイルごとに独立している。

使い方:
  python3 recent_urls.py                     # 既定プロファイル・直近7日
  python3 recent_urls.py --profile commuter  # プロファイルを指定
  python3 recent_urls.py --days 5            # 直近5日
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from profiles import OUTPUT_DIR, POSTS_DIR, default_profile, get_profile

_URL_RE = re.compile(r"\[.*?\]\((https?://[^)]+)\)")


def _extract_urls(file_path: str) -> set[str]:
    """マークダウンファイルからURLを抽出する。"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return set(_URL_RE.findall(f.read()))
    except (OSError, UnicodeDecodeError):
        return set()


def _collect(directory, suffix: str, cutoff: date, today: date) -> set[str]:
    """`{YYYY-MM-DD}{suffix}` 形式のファイルからURLを収集する。"""
    urls: set[str] = set()
    try:
        entries = os.listdir(directory)
    except FileNotFoundError:
        return urls

    for name in entries:
        if not name.endswith(suffix):
            continue
        try:
            file_date = date.fromisoformat(name[:10])
        except ValueError:
            continue
        if cutoff <= file_date < today:
            urls |= _extract_urls(os.path.join(directory, name))
    return urls


def main():
    parser = argparse.ArgumentParser(description="過去の掲載済みURLを抽出")
    parser.add_argument("--profile", help="プロファイルID（省略時は既定プロファイル）")
    parser.add_argument("--days", type=int, default=7, help="遡る日数（デフォルト7）")
    args = parser.parse_args()

    profile = get_profile(args.profile) if args.profile else default_profile()
    today = date.today()
    cutoff = today - timedelta(days=args.days)

    urls = _collect(POSTS_DIR, f"-{profile.post_slug}.md", cutoff, today)
    urls |= _collect(OUTPUT_DIR, f"-{profile.id}.md", cutoff, today)

    for url in sorted(urls):
        print(url)


if __name__ == "__main__":
    main()
