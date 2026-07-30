#!/usr/bin/env python3
"""preferences のハッシュサフィックスを計算する。

出力ファイル名や掲載履歴の識別子として使う。
好みファイルが存在しない場合は 'default' を返す。

使い方:
  python3 preference_hash.py                          # デフォルト (preferences.md)
  python3 preference_hash.py --profile alice           # profiles/alice.md
  python3 preference_hash.py --profile path/to/pref.md # 任意のパス
"""

from __future__ import annotations

import argparse
import hashlib
import os

_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFERENCES_PATH = os.path.join(_SKILL_ROOT, "preferences.md")


def resolve_profile(profile: str | None) -> str:
    """プロファイル指定をファイルパスに解決する。

    None → デフォルトの preferences.md
    名前 → profiles/{name}.md (スキルルート基準)
    既存ファイルパス → そのまま
    """
    if profile is None:
        return PREFERENCES_PATH
    candidate = os.path.join(_SKILL_ROOT, "profiles", f"{profile}.md")
    if os.path.isfile(candidate):
        return candidate
    if os.path.isfile(profile):
        return profile
    return profile


def compute_suffix(preferences_path: str | None = None) -> str:
    """preferences の MD5 先頭8文字を返す。存在しなければ 'default'。"""
    path = resolve_profile(preferences_path)
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "default"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="preferences のハッシュサフィックスを計算")
    parser.add_argument("--profile", help="プロファイル名またはパス（省略時は preferences.md）")
    args = parser.parse_args()
    print(compute_suffix(args.profile))
