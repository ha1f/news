#!/usr/bin/env python3
"""過去の掲載済みヘッドラインを日付ごとに抽出するスクリプト。

使い方:
  python3 recent_topics.py                  # 直近3日
  python3 recent_topics.py --days 5         # 直近5日
  python3 recent_topics.py --hash 23cfb1cf  # 別のハッシュを指定

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

from preference_hash import compute_suffix

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTPUT_DIR = os.path.join(_SKILL_ROOT, "output")
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SKILL_ROOT)))
_POSTS_DIR = os.path.join(_REPO_ROOT, "_posts")

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


def _collect(cutoff: date, today: date, pref_hash: str) -> dict[str, list[str]]:
    """_posts/ と output/ からヘッドラインを日付ごとに収集する。"""
    by_date: dict[str, list[str]] = {}

    _posts_re = re.compile(r"^\d{4}-\d{2}-\d{2}-news(?:-.+)?\.md$")
    for directory, match_fn in [
        (_POSTS_DIR, lambda n: bool(_posts_re.match(n))),
        (_OUTPUT_DIR, lambda n: n.endswith(f"-{pref_hash}.md")),
    ]:
        try:
            entries = os.listdir(directory)
        except FileNotFoundError:
            continue
        for name in entries:
            if not match_fn(name):
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
    parser.add_argument("--profile", help="プロファイル名またはパス（省略時は preferences.md）")
    parser.add_argument("--hash", help="preferencesハッシュ（省略時は自動計算）")
    parser.add_argument("--days", type=int, default=3, help="遡る日数（デフォルト3）")
    args = parser.parse_args()

    pref_hash = args.hash or compute_suffix(args.profile)
    today = date.today()
    cutoff = today - timedelta(days=args.days)

    by_date = _collect(cutoff, today, pref_hash)

    for d in sorted(by_date, reverse=True):
        print(f"## {d}")
        for headline in by_date[d]:
            print(f"- {headline}")
        print()


if __name__ == "__main__":
    main()
