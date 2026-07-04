#!/usr/bin/env python3
"""preferences.md のハッシュサフィックスを計算する。

出力ファイル名や掲載履歴の識別子として使う。
好みファイルが存在しない場合は 'default' を返す。

使い方:
  python3 preference_hash.py              # サフィックスを標準出力に表示
"""

from __future__ import annotations

import hashlib
import os

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFERENCES_PATH = os.path.join(_SKILL_ROOT, "preferences.md")


def compute_suffix() -> str:
    """preferences.md の MD5 先頭8文字を返す。存在しなければ 'default'。"""
    try:
        with open(PREFERENCES_PATH, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "default"


if __name__ == "__main__":
    print(compute_suffix())
