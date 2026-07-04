#!/usr/bin/env python3
"""過去の掲載済みURLを抽出するスクリプト。

使い方:
  python3 recent_urls.py                  # 直近7日
  python3 recent_urls.py --days 5         # 直近5日
  python3 recent_urls.py --hash 23cfb1cf  # 別のハッシュを指定
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, timedelta

# このスクリプトと同じディレクトリをモジュール検索パスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preference_hash import compute_suffix

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTPUT_DIR = os.path.join(_SKILL_ROOT, "output")

# マークダウンリンクからURLを抽出する正規表現
_URL_RE = re.compile(r"\[.*?\]\((https?://[^)]+)\)")


def _extract_urls(file_path: str) -> set[str]:
    """マークダウンファイルからURLを抽出する。"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return set(_URL_RE.findall(f.read()))
    except (OSError, UnicodeDecodeError):
        return set()


def main():
    parser = argparse.ArgumentParser(description="過去の掲載済みURLを抽出")
    parser.add_argument("--hash", help="preferencesハッシュ（省略時は自動計算）")
    parser.add_argument("--days", type=int, default=7, help="遡る日数（デフォルト7）")
    args = parser.parse_args()

    pref_hash = args.hash or compute_suffix()
    today = date.today()
    cutoff = today - timedelta(days=args.days)

    # output/ から該当ハッシュのファイルを探す
    urls: set[str] = set()
    try:
        entries = os.listdir(_OUTPUT_DIR)
    except FileNotFoundError:
        # output/ が存在しなければ何も出力しない
        return

    suffix = f"-{pref_hash}.md"
    for name in entries:
        if not name.endswith(suffix):
            continue
        # ファイル名の日付部分をパース
        date_str = name[: len("YYYY-MM-DD")]
        try:
            file_date = date.fromisoformat(date_str)
        except ValueError:
            continue
        # 当日は除外（同日再実行は上書きされるため）、cutoff以降を対象
        if cutoff <= file_date < today:
            urls |= _extract_urls(os.path.join(_OUTPUT_DIR, name))

    for url in sorted(urls):
        print(url)


if __name__ == "__main__":
    main()
