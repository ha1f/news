#!/usr/bin/env python3
"""候補記事の description だけをキャッシュから抜き出して表示する。

最終選定では description を読む必要があるが、キャッシュJSONを丸ごと読むと
1ファイル数万バイトかかる。このスクリプトは指定したURLの記事だけを、
HTMLタグを落として指定文字数までに切り詰めて出力する。

使い方:
  python3 show_descriptions.py URL [URL...]
  python3 show_descriptions.py --chars 200 URL...   # 切り詰める長さ（デフォルト400）
  cat urls.txt | python3 show_descriptions.py       # 標準入力から1行1URL

見つからなかったURLは末尾に「未取得」として並べる（キャッシュに無い＝取得対象外だった）。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(_SKILL_ROOT, "cache")

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def clean(text: str, limit: int) -> str:
    """HTMLタグ・実体参照・連続空白を落として limit 文字までに切り詰める（純関数）。"""
    if not text:
        return ""
    text = html.unescape(_TAG_RE.sub(" ", text))
    text = _SPACE_RE.sub(" ", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def build_index(cache_files: dict[str, dict]) -> dict[str, dict]:
    """{ファイル名: キャッシュJSON} から URL → 記事 の索引を作る（純関数）。

    同じURLが複数ソースにある場合は最初に見つかったものを採用する。"""
    index: dict[str, dict] = {}
    for name, data in cache_files.items():
        key = name[:-5] if name.endswith(".json") else name
        for item in data.get("items", []):
            url = item.get("url")
            if url and url not in index:
                index[url] = {**item, "cache_key": key}
    return index


def load_cache() -> dict[str, dict]:
    files = {}
    try:
        entries = sorted(os.listdir(CACHE_DIR))
    except FileNotFoundError:
        return files
    for name in entries:
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(CACHE_DIR, name), encoding="utf-8") as f:
                files[name] = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
    return files


def main():
    parser = argparse.ArgumentParser(description="候補記事の description を表示")
    parser.add_argument("urls", nargs="*", help="表示する記事のURL")
    parser.add_argument("--chars", type=int, default=400, help="description の最大文字数")
    args = parser.parse_args()

    urls = list(args.urls)
    if not sys.stdin.isatty():
        urls += [line.strip() for line in sys.stdin if line.strip()]
    if not urls:
        parser.error("URLを引数か標準入力で指定する")

    index = build_index(load_cache())

    missing = []
    for url in urls:
        item = index.get(url)
        if item is None:
            missing.append(url)
            continue
        print(f"[{item['cache_key']}] {item.get('title', '')}")
        print(f"  {url}")
        description = clean(item.get("description") or "", args.chars)
        if description:
            print(f"  {description}")
        print()

    if missing:
        print("未取得（キャッシュに無い）:")
        for url in missing:
            print(f"  {url}")


if __name__ == "__main__":
    main()
