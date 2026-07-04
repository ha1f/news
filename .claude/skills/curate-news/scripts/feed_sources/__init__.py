"""ソース定義の自動ディスカバリ。

feed_sources/ 配下の全 .py モジュールから FEEDS リストを収集する。
新しいソースを追加するには、このディレクトリに .py ファイルを置くだけ。
"""

import importlib
import pathlib


def collect_feeds():
    """全ソースモジュールからFEEDS定義を収集して返す。"""
    feeds = []
    pkg_dir = pathlib.Path(__file__).parent
    for py_file in sorted(pkg_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        module = importlib.import_module(f"feed_sources.{py_file.stem}")
        if hasattr(module, "FEEDS"):
            feeds.extend(module.FEEDS)
    return feeds
