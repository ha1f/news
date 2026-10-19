"""有料 run が使うソースを、ソース定義の「商用利用（課金）」で絞る (#575)。

docs/m5-paid-delivery.md の最小構成: 値が `可` のソースだけを有料フィードの材料にする。
値が欠けている・語彙に無いソースは使える側に倒さず外す。
"""

from __future__ import annotations

import os
import re

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(_SKILL_ROOT, "references", "sources")

# STYLEGUIDE.md の判定語彙。許可するのは 可 だけ
VOCABULARY = ("可", "不可", "要許諾", "要連絡", "要判断", "規定なし")
ALLOWED = ("可",)

_LINE_RE = re.compile(r"^- \*\*商用利用（課金）\*\*:\s*(.*)$", re.MULTILINE)


def read_value(source_id: str, sources_dir: str = SOURCES_DIR) -> str | None:
    """ソース定義の「商用利用（課金）」の判定語を返す。

    ファイルが無い・項目が無い・語彙に無い値のときは None（使えない側）。
    値の括弧書き（理由・窓口）は判定に使わない。
    """
    path = os.path.join(sources_dir, f"{source_id}.md")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    m = _LINE_RE.search(text)
    if not m:
        return None
    head = re.split(r"[（(\s]", m.group(1).strip(), maxsplit=1)[0]
    return head if head in VOCABULARY else None


def is_allowed(source_id: str, sources_dir: str = SOURCES_DIR) -> bool:
    return read_value(source_id, sources_dir) in ALLOWED


def filter_feeds(feeds: list, sources_dir: str = SOURCES_DIR) -> tuple[list, dict[str, str | None]]:
    """課金に使えるフィードだけ残す。除外したソースの判定語も返す（None は欠落・語彙外）。"""
    excluded: dict[str, str | None] = {}
    kept = []
    for f in feeds:
        if f.source_id in excluded:
            continue
        value = read_value(f.source_id, sources_dir)
        if value in ALLOWED:
            kept.append(f)
        else:
            excluded[f.source_id] = value
    return kept, excluded
