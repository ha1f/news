#!/usr/bin/env python3
"""過去に `_posts/` へ掲載した記事 URL を、全期間ぶん集める (#40)。

キュレーション時の候補一覧（`fetch_feeds.py --show-cache-summary`）からの除外と、
publish 前の再掲検査（`.claude/scripts/check_repeat_urls.py`）が同じ判定を使う
ための共通部品。

期間を区切らないのは、更新頻度の低いフィード（publickey1・dribbble・nature 等）
の項目が8〜30日の間隔で戻ってくるため。7日窓だった頃は再掲の3分の2が窓の外
だった（実測 2026-10-08: 直近30日の再掲 90 本のうち 60 本）。

同じ日の別プロファイルの投稿は「過去」に数えない。プロファイルごとに読者が
違うので、同じ日に同じ記事を別の面に載せるのは再掲ではない。

URL は表記揺れだけを寄せて比べる（scheme・`www.`・末尾の `/`・フラグメント）。
クエリは残す（`?p=123` のように記事そのものを指すサイトがある）。
"""

from __future__ import annotations

import os
import re
from datetime import date
from urllib.parse import urlsplit

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SKILL_ROOT)))
POSTS_DIR = os.path.join(_REPO_ROOT, "_posts")

# 番号付きの記事行のリンク（`1. [見出し](URL) (ソース)`）
ITEM_URL_RE = re.compile(r"^\s*\d+\.\s+\[[^\]]*\]\((https?://[^)\s]+)\)", re.M)


def normalize(url: str) -> str:
    """表記揺れだけを寄せた比較用のキー。"""
    s = urlsplit(url.strip())
    host = s.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = s.path.rstrip("/")
    key = host + path
    if s.query:
        key += "?" + s.query
    return key


def date_of(name: str) -> date | None:
    """`_posts/` のファイル名の日付。読めなければ None。"""
    try:
        return date.fromisoformat(name[:10])
    except ValueError:
        return None


def item_urls(text: str) -> list[tuple[int, str]]:
    """記事行の (行番号, URL) を出現順に返す。"""
    found = []
    for m in ITEM_URL_RE.finditer(text):
        line = text.count("\n", 0, m.start(1)) + 1
        found.append((line, m.group(1)))
    return found


def collect(before: date, posts_dir: str = POSTS_DIR) -> dict[str, tuple[date, str]]:
    """`before` より前の日付の投稿に載った URL → (初出日, ファイル名)。"""
    published: dict[str, tuple[date, str]] = {}
    try:
        names = sorted(os.listdir(posts_dir))
    except FileNotFoundError:
        return published
    for name in names:
        if not name.endswith(".md"):
            continue
        day = date_of(name)
        if day is None or day >= before:
            continue
        try:
            with open(os.path.join(posts_dir, name), encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for _, url in item_urls(text):
            published.setdefault(normalize(url), (day, name))
    return published
