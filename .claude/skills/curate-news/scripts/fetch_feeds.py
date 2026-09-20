#!/usr/bin/env python3
"""全ソース対応の統合フィード取得スクリプト。

使い方:
  python3 fetch_feeds.py                          # 全フィード（キャッシュ有効はスキップ）
  python3 fetch_feeds.py --source hatena           # hatenaの全カテゴリ
  python3 fetch_feeds.py --source hatena --category テクノロジー
  python3 fetch_feeds.py --force                   # キャッシュ無視で全取得
  python3 fetch_feeds.py --list                    # 定義一覧表示
  python3 fetch_feeds.py --show-cache-summary       # キャッシュのサマリー表示
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile

# このスクリプトと同じディレクトリをモジュール検索パスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from feed_config import FeedConfig, JST, CACHE_DIR
from feed_parsers import PARSERS, fetch_url
from feed_sources import collect_feeds


def _is_cache_valid(cache_path: str, ttl_minutes: int) -> bool:
    """キャッシュが有効期間内か判定する。

    キャッシュJSONの fetched_at と ttl_minutes から有効期限を計算し、
    現在時刻と比較する。ファイルが存在しない・壊れている場合はFalseを返す。
    """
    try:
        with open(cache_path) as f:
            data = json.load(f)
        fetched = datetime.fromisoformat(data["fetched_at"]).timestamp()
        return fetched + ttl_minutes * 60 > datetime.now(timezone.utc).timestamp()
    except (FileNotFoundError, KeyError, json.JSONDecodeError, ValueError):
        return False


def _write_cache(cache_path: str, cache_data: dict) -> None:
    """キャッシュを atomic に書き出す。

    同じキャッシュを複数プロセスが同時に書くと、json.dump は複数回の write() に
    分解されるため、素の open(path, "w") では両者の内容が混ざった不正な JSON が
    残りうる。同じディレクトリの一時ファイルに書いてから os.replace で差し替える
    ことで、読み手には常に「差し替え前の完全な内容」か「差し替え後の完全な内容」
    のどちらかしか見えなくなる。
    """
    fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(cache_path), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, cache_path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def fetch_feed(feed: FeedConfig, force: bool = False) -> bool:
    """1フィードを取得してキャッシュに保存する。

    キャッシュが有効（TTL内）な場合はスキップする（forceで上書き可）。
    成功時は "ok {cache_key}" をstdoutに、失敗時は "FAIL {cache_key}" をstderrに出力する。
    """
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)

        # キャッシュキー単位の排他ロック。プロファイルの好みが被れば複数プロセスが
        # 同じソース・カテゴリを取りにいくため（実測: hatena-テクノロジーは5/5 プロファイル）、
        # 有効性チェック〜書き込みを丸ごと囲う。待たされた側はロック取得後の再チェックで
        # 有効なキャッシュを見つけて skip するので、同じフィードへの重複リクエストも消える
        # （`--force` は再チェックを飛ばすので直列化されるだけで重複は消えない）。
        # 別のキャッシュキー同士はロックを共有しないため、並列性は落ちない。
        # 取得中もロックを保持するので、custom_fetcher は必ず timeout を持たせること
        # （待つ側の flock にタイムアウトが無く、ハングすると同じキーの全員が止まる）。
        with open(feed.cache_path + ".lock", "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)

            if not force and _is_cache_valid(feed.cache_path, feed.ttl_minutes):
                print(f"  skip {feed.cache_key} (cache valid)")
                return True

            if feed.custom_fetcher:
                items = feed.custom_fetcher(feed)
            else:
                parser = PARSERS[feed.fmt]
                content = fetch_url(feed.feed_url, feed.user_agent)
                items = parser(content, feed)

            _write_cache(feed.cache_path, {
                "source_id": feed.source_id,
                "category": feed.category,
                "feed_url": feed.feed_url,
                "fetched_at": datetime.now(JST).isoformat(),
                "ttl_minutes": feed.ttl_minutes,
                "items": items,
            })

        print(f"  ok   {feed.cache_key} ({len(items)} items)")
        return True

    except Exception as e:
        print(f"  FAIL {feed.cache_key}: {e}", file=sys.stderr)
        return False


def print_summary(feeds: list[FeedConfig]) -> None:
    """キャッシュ済みフィードの記事サマリーを出力する。

    各記事をタイトル・URL・スコア・日時の1行で表示する。
    キュレーション時の候補選定に使う。
    """
    SCORE_KEYS = ("bookmarks", "points", "score", "ups", "votes")

    for feed in feeds:
        try:
            with open(feed.cache_path, encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[{feed.cache_key}] (キャッシュなし)", file=sys.stderr)
            continue

        items = data if isinstance(data, list) else data.get("items", [])
        print(f"[{feed.cache_key}] ({len(items)} items)")
        for item in items:
            title = (item.get("title") or "")[:50]
            url = item.get("url") or ""
            published = (item.get("published_at") or "")[:10]
            meta = item.get("meta") or {}
            scores = [f"{k}:{meta[k]}" for k in SCORE_KEYS if k in meta]
            score_str = f" ({', '.join(scores)})" if scores else ""
            print(f"  {title} | {url} | {published}{score_str}")
        print()


def main():
    parser = argparse.ArgumentParser(description="フィード取得スクリプト")
    parser.add_argument("--source", help="ソースIDでフィルタ")
    parser.add_argument("--category", help="カテゴリでフィルタ")
    parser.add_argument("--force", action="store_true", help="キャッシュ無視")
    parser.add_argument("--list", action="store_true", dest="list_feeds",
                        help="定義一覧を表示")
    parser.add_argument("--show-cache-summary", action="store_true",
                        help="キャッシュのサマリー表示")
    args = parser.parse_args()

    feeds = collect_feeds()

    if args.source:
        feeds = [f for f in feeds if f.source_id == args.source]
    if args.category:
        feeds = [f for f in feeds if f.category == args.category]

    if not feeds:
        print("該当するフィードがありません", file=sys.stderr)
        sys.exit(1)

    if args.list_feeds:
        for f in feeds:
            label = f"{f.source_id}-{f.category}"
            print(f"  {label:40s}  {f.fmt:12s}  ttl={f.ttl_minutes}m")
        return

    if args.show_cache_summary:
        print_summary(feeds)
        return

    print(f"取得対象: {len(feeds)} フィード")
    ok = sum(1 for f in feeds if fetch_feed(f, args.force))
    ng = len(feeds) - ok
    print(f"\n完了: {ok} 成功, {ng} 失敗")
    if ng:
        sys.exit(1)


if __name__ == "__main__":
    main()
