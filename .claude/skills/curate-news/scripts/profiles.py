#!/usr/bin/env python3
"""読者プロファイル（好みのプロファイル）の定義を読み込む。

定義の唯一の情報源は `_data/profiles.json`（Jekyll のテンプレートも同じファイルを読む）。
好みの本文は `profiles/{id}.md`、キュレーション結果は `output/{YYYY-MM-DD}-{id}.md`、
公開後の記事は `_posts/{YYYY-MM-DD}-{post_slug}.md` に対応する。

使い方:
  python3 profiles.py            # 一覧（id / 名前 / 好みファイル / 出力先）
  python3 profiles.py --json     # 同じ内容を JSON で
  python3 profiles.py --id owner # 1件だけ
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _SKILL_ROOT.parents[2]

PROFILES_JSON = _REPO_ROOT / "_data" / "profiles.json"
PROFILES_DIR = _SKILL_ROOT / "profiles"
OUTPUT_DIR = _SKILL_ROOT / "output"
POSTS_DIR = _REPO_ROOT / "_posts"

REQUIRED_KEYS = ("id", "post_slug", "name", "tagline", "base")


@dataclass(frozen=True)
class Profile:
    id: str
    post_slug: str
    name: str
    tagline: str
    base: str
    is_default: bool

    @property
    def preferences_path(self) -> Path:
        """好みファイル（このプロファイルの読者像・興味・関心）"""
        return PROFILES_DIR / f"{self.id}.md"

    @property
    def output_glob(self) -> str:
        """output/ 内のキュレーション結果のファイル名パターン"""
        return f"*-{self.id}.md"

    @property
    def post_glob(self) -> str:
        """_posts/ 内の公開済み記事のファイル名パターン"""
        return f"*-{self.post_slug}.md"

    def output_path(self, date_str: str) -> Path:
        return OUTPUT_DIR / f"{date_str}-{self.id}.md"

    def post_path(self, date_str: str) -> Path:
        return POSTS_DIR / f"{date_str}-{self.post_slug}.md"


def parse_profiles(data) -> list[Profile]:
    """profiles.json の内容を検証して Profile のリストにする（純関数）。"""
    if not isinstance(data, list) or not data:
        raise ValueError("profiles.json は1件以上のプロファイルの配列である必要がある")

    profiles = []
    for entry in data:
        missing = [key for key in REQUIRED_KEYS if not entry.get(key)]
        if missing:
            raise ValueError(f"プロファイル {entry.get('id', '?')} に必須キーが無い: {missing}")
        base = entry["base"]
        if not (base.startswith("/") and base.endswith("/")):
            raise ValueError(f"プロファイル {entry['id']} の base は / で始まり / で終わる必要がある: {base}")
        profiles.append(Profile(
            id=entry["id"],
            post_slug=entry["post_slug"],
            name=entry["name"],
            tagline=entry["tagline"],
            base=base,
            is_default=bool(entry.get("default")),
        ))

    for key in ("id", "post_slug", "base"):
        values = [getattr(p, key) for p in profiles]
        duplicated = {v for v in values if values.count(v) > 1}
        if duplicated:
            raise ValueError(f"{key} が重複している: {sorted(duplicated)}")

    defaults = [p.id for p in profiles if p.is_default]
    if len(defaults) != 1:
        raise ValueError(f"default: true のプロファイルは1件である必要がある: {defaults}")

    return profiles


def load_profiles() -> list[Profile]:
    """_data/profiles.json を読み込む。既定プロファイルが先頭に来る。"""
    profiles = parse_profiles(json.loads(PROFILES_JSON.read_text(encoding="utf-8")))
    return sorted(profiles, key=lambda p: not p.is_default)


def get_profile(profile_id: str) -> Profile:
    for profile in load_profiles():
        if profile.id == profile_id:
            return profile
    known = ", ".join(p.id for p in load_profiles())
    raise KeyError(f"プロファイル '{profile_id}' は未定義（定義済み: {known}）")


def default_profile() -> Profile:
    return load_profiles()[0]


def _describe(profile: Profile) -> dict:
    data = asdict(profile)
    data["preferences"] = str(profile.preferences_path.relative_to(_REPO_ROOT))
    data["preferences_exists"] = profile.preferences_path.exists()
    return data


def main():
    parser = argparse.ArgumentParser(description="読者プロファイルの一覧")
    parser.add_argument("--id", help="1件だけ表示する")
    parser.add_argument("--json", action="store_true", help="JSON で出力する")
    args = parser.parse_args()

    profiles = [get_profile(args.id)] if args.id else load_profiles()
    described = [_describe(p) for p in profiles]

    if args.json:
        json.dump(described, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        for data in described:
            mark = " (既定)" if data["is_default"] else ""
            status = "" if data["preferences_exists"] else "  ← 好みファイルが無い"
            print(f"{data['id']}{mark}\t{data['name']}\t{data['preferences']}"
                  f"\toutput/{{YYYY-MM-DD}}-{data['id']}.md{status}")

    if not all(d["preferences_exists"] for d in described):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
