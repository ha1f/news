#!/usr/bin/env python3
"""過去の掲載済みヘッドラインを日付ごとに抽出するスクリプト。

照合の窓は2段になっている:
  - 直近 --days 日（既定3）: 全フィード（_posts/ の全プロファイル）と output/ の同じ好みの分
  - その前の --own-days 日まで（既定10）: 自分のフィードの _posts/ と output/ の同じ好みの分だけ
    （1週間ほど前に読んだ話題が別媒体の URL で再び載るのを防ぐ #531。全フィードを10日分
    出すと行数が3倍以上になるため、読者が実際に読んだ自分のフィードに絞る）

使い方:
  python3 recent_topics.py                         # 直近3日（全フィード）+ 10日前まで（自分のフィード）
  python3 recent_topics.py --profile researcher    # 自分のフィード = _posts/*-news-researcher.md
  python3 recent_topics.py --days 5 --own-days 14  # 窓を変える
  python3 recent_topics.py --today 2026-10-08      # 「今日」を固定する（検証用）

出力例:
  ## 2026-07-22
  - OpenAIの未公開モデル、評価中にHugging Faceをハック (Hacker News)
  ...
  ## 2026-07-18（このフィードのみ）
  - Google、Gemini 3.6 Flashなど新モデル3種を投入 (Hacker News)
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
_PROFILES_DIR = os.path.join(_SKILL_ROOT, "profiles")
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SKILL_ROOT)))
_POSTS_DIR = os.path.join(_REPO_ROOT, "_posts")

_HEADLINE_RE = re.compile(
    r"^\d+\.\s+\[(.+?)\]\(https?://[^)]+\)\s+\((.+?)\)", re.MULTILINE
)
_POSTS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-news(?:-.+)?\.md$")

OWN_ONLY_LABEL = "（このフィードのみ）"


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


def own_posts_suffix(profile: str | None) -> str | None:
    """自分のフィードの _posts/ ファイル名の日付以降の部分を返す。

    None（デフォルト）→ "news.md"、profiles/ にある名前・パス → "news-{name}.md"。
    repo 外の好みファイルは _posts/ に出ないので None（output/ だけで照合する）。
    """
    if profile is None:
        return "news.md"
    if os.path.isfile(os.path.join(_PROFILES_DIR, f"{profile}.md")):
        return f"news-{profile}.md"
    path = os.path.abspath(profile)
    if os.path.dirname(path) == os.path.abspath(_PROFILES_DIR) and path.endswith(".md"):
        return f"news-{os.path.basename(path)[:-3]}.md"
    return None


def _collect(
    cutoff: date,
    today: date,
    pref_hash: str,
    own_cutoff: date | None = None,
    own_suffix: str | None = None,
) -> dict[str, list[str]]:
    """_posts/ と output/ からヘッドラインを日付ごとに収集する。

    cutoff 以降は全フィード、own_cutoff 以上 cutoff 未満は自分のフィード
    （_posts/ の own_suffix と output/ の pref_hash）だけを読む。
    """
    if own_cutoff is None or own_cutoff > cutoff:
        own_cutoff = cutoff
    by_date: dict[str, list[str]] = {}

    def is_own_post(name: str) -> bool:
        return own_suffix is not None and name[11:] == own_suffix

    for directory, match_fn, own_fn in [
        (_POSTS_DIR, lambda n: bool(_POSTS_RE.match(n)), is_own_post),
        (_OUTPUT_DIR, lambda n: n.endswith(f"-{pref_hash}.md"), lambda n: True),
    ]:
        try:
            entries = sorted(os.listdir(directory))
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
            if file_date >= today or file_date < own_cutoff:
                continue
            if file_date < cutoff and not own_fn(name):
                continue
            headlines = _extract_headlines(os.path.join(directory, name))
            if headlines:
                existing = by_date.setdefault(date_str, [])
                for h in headlines:
                    if h not in existing:
                        existing.append(h)

    return by_date


def render(by_date: dict[str, list[str]], cutoff: date) -> str:
    lines: list[str] = []
    for d in sorted(by_date, reverse=True):
        label = OWN_ONLY_LABEL if date.fromisoformat(d) < cutoff else ""
        lines.append(f"## {d}{label}")
        lines.extend(f"- {h}" for h in by_date[d])
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="過去の掲載済みヘッドラインを抽出")
    parser.add_argument("--profile", help="プロファイル名またはパス（省略時は preferences.md）")
    parser.add_argument("--hash", help="preferencesハッシュ（省略時は自動計算）")
    parser.add_argument("--days", type=int, default=3, help="全フィードを遡る日数（デフォルト3）")
    parser.add_argument(
        "--own-days", type=int, default=10,
        help="自分のフィードを遡る日数（デフォルト10。--days 以下なら追加なし）",
    )
    parser.add_argument("--today", type=date.fromisoformat, help="今日とみなす日付 YYYY-MM-DD（検証用）")
    args = parser.parse_args()

    pref_hash = args.hash or compute_suffix(args.profile)
    today = args.today or date.today()
    cutoff = today - timedelta(days=args.days)
    own_cutoff = today - timedelta(days=max(args.own_days, args.days))

    by_date = _collect(cutoff, today, pref_hash, own_cutoff, own_posts_suffix(args.profile))
    print(render(by_date, cutoff))


if __name__ == "__main__":
    main()
