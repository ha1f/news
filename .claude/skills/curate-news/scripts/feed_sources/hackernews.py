"""Hacker News のフィード定義。

JSON API（Firebase）から2段階で取得する。
1. フィードURL（例: topstories.json）からID配列を取得
2. 上位20件のIDに対して個別にアイテムを並列取得（ThreadPoolExecutor）
仕様: references/sources/hackernews.md を参照。
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from feed_config import FeedConfig, JST
from feed_parsers import fetch_url


def _fetch_items(feed: FeedConfig) -> list[dict]:
    """Hacker News JSON APIからアイテムを取得する。"""
    ids = json.loads(fetch_url(feed.feed_url))[:20]

    def _fetch_one(item_id: int) -> dict | None:
        try:
            data = json.loads(fetch_url(
                f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
            ))
            if not data:
                return None
            return {
                "title": data.get("title", ""),
                "url": (data.get("url")
                        or f"https://news.ycombinator.com/item?id={item_id}"),
                "description": None,
                "published_at": (
                    datetime.fromtimestamp(data["time"], tz=JST).isoformat()
                    if data.get("time") else None
                ),
                "meta": {
                    "score": data.get("score"),
                    "comments": data.get("descendants"),
                },
            }
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(_fetch_one, ids))
    return [r for r in results if r is not None]


FEEDS = [
    FeedConfig("hackernews", "トップ",
               "https://hacker-news.firebaseio.com/v0/topstories.json",
               "custom", 720, custom_fetcher=_fetch_items),
    FeedConfig("hackernews", "Show HN",
               "https://hacker-news.firebaseio.com/v0/showstories.json",
               "custom", 720, custom_fetcher=_fetch_items),
]
