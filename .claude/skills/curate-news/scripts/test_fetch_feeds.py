#!/usr/bin/env python3
"""fetch_feeds のキャッシュ書き込みが並列実行に耐えるかの検証。

複数プロファイルを並列にキュレーションすると、好みが被ったソース・カテゴリを
複数プロセスが同時に取りにいく（実測: hatena-テクノロジーは5/5 プロファイル）。
このとき素朴な open(path, "w") + json.dump では

  - 書き込みが混ざった不正な JSON が残る
  - 同じフィードへ重複リクエストが飛ぶ（Reddit の 10req/分 に当たる）

の2つが起きる。ロックと atomic write でどちらも消えることを確かめる。
"""
import json
import multiprocessing
import os
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import feed_config
import fetch_feeds
from feed_config import FeedConfig


def _slow_fetcher(feed):
    """取得のたびにマーカーファイルを1つ増やす、1秒かかるフェッチャ。"""
    with tempfile.NamedTemporaryFile(
            dir=os.path.join(feed_config.CACHE_DIR, "calls"), delete=False):
        pass
    time.sleep(1)
    return [{"title": "x" * 5000, "url": "https://example.com/"}]


def _make_feed():
    return FeedConfig(source_id="dummy", category="テスト",
                      feed_url="https://example.com/feed",
                      fmt="custom", ttl_minutes=60,
                      custom_fetcher=_slow_fetcher)


def _child(cache_dir):
    """子プロセス側のエントリポイント（fork 前提にしないため引数で受け渡す）。"""
    feed_config.CACHE_DIR = cache_dir
    fetch_feeds.CACHE_DIR = cache_dir
    fetch_feeds.fetch_feed(_make_feed())


class CacheDirTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache_dir = self.tmp.name
        os.makedirs(os.path.join(self.cache_dir, "calls"), exist_ok=True)
        for module in (feed_config, fetch_feeds):
            patcher = mock.patch.object(module, "CACHE_DIR", self.cache_dir)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def _call_count(self):
        return len(os.listdir(os.path.join(self.cache_dir, "calls")))


class TestConcurrentFetch(CacheDirTestCase):
    def test_same_cache_key_is_fetched_once_and_stays_valid_json(self):
        """同じキャッシュキーを3プロセスが同時に取りにいっても、取得は1回だけ。"""
        ctx = multiprocessing.get_context("spawn")
        procs = [ctx.Process(target=_child, args=(self.cache_dir,)) for _ in range(3)]
        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=60)

        self.assertEqual([p.exitcode for p in procs], [0, 0, 0])
        # 待たされた2プロセスはロック取得後の再チェックで有効なキャッシュを見つけ skip する
        self.assertEqual(self._call_count(), 1)

        with open(_make_feed().cache_path, encoding="utf-8") as f:
            data = json.load(f)  # 混ざった JSON ならここで JSONDecodeError
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["source_id"], "dummy")

    def test_lock_and_temp_files_do_not_become_cache(self):
        """ロック用・一時ファイルがキャッシュ本体を汚さない。"""
        fetch_feeds.fetch_feed(_make_feed())
        cache_path = _make_feed().cache_path
        self.assertTrue(os.path.exists(cache_path))
        self.assertTrue(os.path.exists(cache_path + ".lock"))
        leftovers = [n for n in os.listdir(self.cache_dir) if n.startswith(".tmp-")]
        self.assertEqual(leftovers, [])


class TestWriteCacheAtomicity(CacheDirTestCase):
    """書き込みが途中で失敗しても、既存のキャッシュが壊れないこと。"""

    PAYLOAD = {"source_id": "dummy", "items": [{"title": "y" * 10000}]}

    def _existing_cache(self):
        path = os.path.join(self.cache_dir, "dummy-テスト.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"source_id": "old", "items": []}, f)
        return path

    def test_failed_write_leaves_previous_cache_readable(self):
        path = self._existing_cache()
        with mock.patch("json.dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                fetch_feeds._write_cache(path, self.PAYLOAD)

        with open(path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["source_id"], "old")
        leftovers = [n for n in os.listdir(self.cache_dir) if n.startswith(".tmp-")]
        self.assertEqual(leftovers, [])

    def test_naive_write_corrupts_previous_cache(self):
        """対照実験: 素朴な open+dump なら同じ失敗でキャッシュが壊れることを示す。

        この検証が「壊れていても green」にならないことの担保。
        """
        path = self._existing_cache()
        with mock.patch("json.dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.PAYLOAD, f)

        with open(path, encoding="utf-8") as f:
            with self.assertRaises(json.JSONDecodeError):
                json.load(f)


if __name__ == "__main__":
    unittest.main()
