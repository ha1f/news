#!/usr/bin/env python3
"""投稿に、過去の日付の投稿で既に載せた記事 URL が無いか検証する (#40)。

除外リストを読んだモデルの注意力に照合を任せていた頃は、リストに載っていた
URL まで素通りしていた（実測 2026-10-08: 前日に同じフィードが出した URL の再掲）。
ここで URL を機械で突き合わせ、既出 URL を含む投稿を publish 前に止める。

判定（期間を区切らない理由・同日の別プロファイルを数えない理由・URL の寄せ方）は
curate-news の `published_urls.py` が正本で、キュレーション時の候補一覧も同じ
判定で既出を外している。

「続報（M/D掲載）。」と書いた記事は別 URL なので、そもそも検出対象にならない。
同じ URL を続報として載せ直すのは再掲として検出する。

使い方:
  python3 .claude/scripts/check_repeat_urls.py                    # 当日 (JST) の投稿
  python3 .claude/scripts/check_repeat_urls.py _posts/....md ...
  python3 .claude/scripts/check_repeat_urls.py --all              # 全投稿（棚卸し用）

終了コード 0 なら、検査した全投稿に既出 URL が無い。
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "curate-news" / "scripts"))

import published_urls  # noqa: E402

JST = timezone(timedelta(hours=9))


def repeats_of(post: Path, posts_dir: str):
    """その投稿の既出 URL を (行番号, URL, 初出日, 初出ファイル) で返す"""
    day = published_urls.date_of(post.name)
    if day is None:
        raise ValueError(f"ファイル名から日付が読み取れません（{post.name}）")
    published = published_urls.collect(day, posts_dir)
    found = []
    for line, url in published_urls.item_urls(post.read_text(encoding="utf-8")):
        hit = published.get(published_urls.normalize(url))
        if hit:
            found.append((line, url, hit[0], hit[1]))
    return found


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        posts = sorted(Path("_posts").glob("*.md"))
    elif paths:
        posts = [Path(a) for a in paths]
    else:
        today = datetime.now(JST).strftime("%Y-%m-%d")
        posts = sorted(Path("_posts").glob(f"{today}-*.md"))
        if not posts:
            print(f"{today} の投稿がありません（_posts/{today}-*.md）", file=sys.stderr)
            return 1

    checked = failures = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            failures += 1
            continue
        try:
            found = repeats_of(post, str(post.parent))
        except ValueError as e:
            print(f"NG {post}: {e}")
            failures += 1
            continue
        checked += 1
        for line, url, first_day, first_name in found:
            print(f"NG {post.name}:{line}: 既出 URL {url}（初出 {first_day.isoformat()} {first_name}）")
            failures += 1

    print(f"検査 {checked} 件 / 既出 URL {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
