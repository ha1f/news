#!/usr/bin/env python3
"""過去の掲載済みヘッドラインを日付ごとに抽出するスクリプト。

照合の窓は2段になっている:
  - 直近 --days 日（既定3）: 全フィード（_posts/ の全プロファイル）と output/ の同じ好みの分
  - その前の --own-days 日まで（既定14）: 自分のフィードの _posts/ と output/ の同じ好みの分だけ
    （1〜2週間前に読んだ話題が別媒体の URL で再び載るのを防ぐ #531・#695。全フィードを14日分
    出すと行数が数倍になるため、読者が実際に読んだ自分のフィードに絞る。10日では 12日・14日おいた
    再掲が窓の外になった。14日にしてメインの出力は 213 → 254 行、約4KB 増える。
    publish 前の check_topic_repeats.py の WINDOW_DAYS と揃える）

全フィードの窓では、自分のフィード以外の見出しの頭に載ったフィードを「［起業家］」の形で付ける。
「続報（M/D掲載）」の M/D は同じフィードのその日のページへのリンクになるので、別フィードの日付を
そのまま書くと、読者は前回の記事が無いページに着く（#659）。フィード名は配信ページ
profiles/{name}.md の title、メインは「メイン」。

使い方:
  python3 recent_topics.py                         # 直近3日（全フィード）+ 14日前まで（自分のフィード）
  python3 recent_topics.py --profile researcher    # 自分のフィード = _posts/*-news-researcher.md
  python3 recent_topics.py --days 5 --own-days 14  # 窓を変える
  python3 recent_topics.py --today 2026-10-08      # 「今日」を固定する（検証用）

出力例:
  ## 2026-07-22
  - OpenAIの未公開モデル、評価中にHugging Faceをハック (Hacker News)
  - ［起業家］Stripe、評価額1000億ドルで調達 (TechCrunch・英語)
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
# 配信ページ（front matter の title がフィードの表示名）。_PROFILES_DIR の好みファイルとは別物
_FEED_PAGES_DIR = os.path.join(_REPO_ROOT, "profiles")
MAIN_FEED_NAME = "メイン"
_TITLE_RE = re.compile(r'^title:\s*"?(.+?)"?\s*$', re.MULTILINE)

_HEADLINE_RE = re.compile(
    r"^\d+\.\s+\[(.+?)\]\(https?://[^)]+\)\s+\((.+?)\)", re.MULTILINE
)
_POSTS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-news(?:-.+)?\.md$")

OWN_ONLY_LABEL = "（このフィードのみ）"
OWN_DAYS = 14  # --own-days の既定


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


def feed_name(post_suffix: str) -> str:
    """_posts/ ファイル名の日付以降（`news.md` / `news-{name}.md`）をフィードの表示名にする。

    _layouts/post.html が「続報（{表示名} M/D掲載）」をリンクにするときと同じ名前（#659）。
    配信ページが無い・title が無ければ profile 名のまま返す。
    """
    if post_suffix == "news.md":
        return MAIN_FEED_NAME
    name = post_suffix[len("news-"):-len(".md")]
    try:
        with open(os.path.join(_FEED_PAGES_DIR, f"{name}.md"), encoding="utf-8") as f:
            m = _TITLE_RE.search(f.read())
    except OSError:
        return name
    return m.group(1) if m else name


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
    # 見出し → 載ったフィードの表示名（自分のフィードは None）。同じ見出しが複数のフィードにあれば並べる
    by_date: dict[str, dict[str, list]] = {}

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
            own = own_fn(name)
            if file_date < cutoff and not own:
                continue
            headlines = _extract_headlines(os.path.join(directory, name))
            if headlines:
                feeds_of = by_date.setdefault(date_str, {})
                feed = None if own else feed_name(name[11:])
                for h in headlines:
                    feeds = feeds_of.setdefault(h, [])
                    if feed not in feeds:
                        feeds.append(feed)

    return {
        d: [h if None in feeds else f"［{'・'.join(feeds)}］{h}" for h, feeds in feeds_of.items()]
        for d, feeds_of in by_date.items()
    }


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
        "--own-days", type=int, default=OWN_DAYS,
        help=f"自分のフィードを遡る日数（デフォルト{OWN_DAYS}。--days 以下なら追加なし）",
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
