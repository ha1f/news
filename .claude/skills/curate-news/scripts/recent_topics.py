#!/usr/bin/env python3
"""過去の掲載済みヘッドラインを日付ごとに抽出するスクリプト。

recent_urls.py と同じく、同じプロファイルの掲載履歴だけを見る。

使い方:
  python3 recent_topics.py                     # 既定プロファイル・直近3日
  python3 recent_topics.py --profile commuter  # プロファイルを指定
  python3 recent_topics.py --days 5            # 直近5日

出力例:
  ## 2026-07-22
  - OpenAIの未公開モデル、評価中にHugging Faceをハック (Hacker News)
  - Google、Gemini 3.6 Flashなど新モデル3種を投入 (Hacker News)
  ...
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from profiles import OUTPUT_DIR, POSTS_DIR, default_profile, get_profile

_HEADLINE_RE = re.compile(
    r"^\d+\.\s+\[(.+?)\]\(https?://[^)]+\)\s+\((.+?)\)", re.MULTILINE
)


def _extract_headlines(file_path: str) -> list[str]:
    """マークダウンファイルからヘッドライン行を抽出する。"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []
    return [
        f"{m.group(1)} ({m.group(2)})" for m in _HEADLINE_RE.finditer(content)
    ]


def _collect(sources, cutoff: date, today: date) -> dict[str, list[str]]:
    """(ディレクトリ, ファイル名サフィックス) の組からヘッドラインを日付ごとに収集する。"""
    by_date: dict[str, list[str]] = {}

    for directory, suffix in sources:
        try:
            entries = os.listdir(directory)
        except FileNotFoundError:
            continue
        for name in entries:
            if not name.endswith(suffix):
                continue
            date_str = name[:10]
            try:
                file_date = date.fromisoformat(date_str)
            except ValueError:
                continue
            if cutoff <= file_date < today:
                headlines = _extract_headlines(os.path.join(directory, name))
                if headlines:
                    existing = by_date.setdefault(date_str, [])
                    for h in headlines:
                        if h not in existing:
                            existing.append(h)

    return by_date


def main():
    parser = argparse.ArgumentParser(description="過去の掲載済みヘッドラインを抽出")
    parser.add_argument("--profile", help="プロファイルID（省略時は既定プロファイル）")
    parser.add_argument("--days", type=int, default=3, help="遡る日数（デフォルト3）")
    args = parser.parse_args()

    profile = get_profile(args.profile) if args.profile else default_profile()
    today = date.today()
    cutoff = today - timedelta(days=args.days)

    by_date = _collect(
        [(POSTS_DIR, f"-{profile.post_slug}.md"), (OUTPUT_DIR, f"-{profile.id}.md")],
        cutoff, today)

    for d in sorted(by_date, reverse=True):
        print(f"## {d}")
        for headline in by_date[d]:
            print(f"- {headline}")
        print()


if __name__ == "__main__":
    main()
