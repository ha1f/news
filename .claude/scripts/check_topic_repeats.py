#!/usr/bin/env python3
"""投稿に、同じフィードで直近に載せた話題の再掲が「続報」の印なしに混ざっていないか洗い出す (#531)。

URL が違えば `check_repeat_urls.py` は通る。話題単位の照合は `recent_topics.py` の
掲載済みヘッドラインをモデルが読んで行っていたが、照合範囲に前回の掲載が入っていても
取りこぼした（実測 2026-10-20 メイン: 10/10 の Deno の Cloudflare 合流と、10/17 の
ECDSA の seed の由来が、印なしで再掲された）。ここで疑わしい組を機械で出し、
同じ話題かどうかの判断だけをモデルに残す。

照合のしかた:
  - 各項目の見出しと読みどころから固有名らしい語（英字の語・3字以上のカタカナ語・
    3字以上の漢字の連なり・「」内の名前）を取り出す。読みどころまで見るのは、
    見出しどうしでは「Claude」しか重ならない組（ECDSA の例）を拾うため
  - 同じフィードの直近 WINDOW_DAYS 日の項目と、共有する語の珍しさ（全フィードの直近
    IDF_DAYS 日での出現率の逆数の対数）の和を点数にし、MIN_SCORE 以上の最高点の組を出す。
    「AI」「Claude」のようによく出る語は点数がほとんど付かない
  - 読みどころが「続報（」で始まる項目は、すでに判断済みなので出さない

閾値は 2026-10-01〜10-20 の全フィード（約100投稿）で測った: MIN_SCORE 8 で
1投稿あたり約1.9組、#531 の4組（Gemini 4 Argon・OpenAI の研究者3人・Deno・ECDSA）は
いずれも10以上。別の話題の組も混ざるので、判断はモデルに残し、CI には載せない。

使い方:
  python3 .claude/scripts/check_topic_repeats.py _posts/2026-10-20-*.md

終了コード 0 なら判断の要る組なし、1 なら組がある（別の話題と判断した組は残してよい）、
2 なら入力の誤り。
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

WINDOW_DAYS = 10  # recent_topics.py の --own-days の既定と揃える
IDF_DAYS = 30
MIN_SCORE = 8.0

ITEM_RE = re.compile(
    r"^\d+\.\s+\[(.+?)\]\((https?://[^)\s]+)\)[^\n]*\n((?:[ \t]+\S.*(?:\n|$))*)", re.M
)
POST_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(news(?:-.+)?\.md)$")
LATIN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[.+\-][A-Za-z0-9]+)*")
KATAKANA_RE = re.compile(r"[ァ-ヴ][ァ-ヴー・]{2,}")
KANJI_RE = re.compile(r"[一-龥々]{3,}")
QUOTED_RE = re.compile(r"「([^」]{2,30})」")
FOLLOW_UP_PREFIX = "続報（"


def terms(text: str) -> set[str]:
    found = {w.lower() for w in LATIN_RE.findall(text) if len(w) >= 2}
    found.update(KATAKANA_RE.findall(text))
    found.update(KANJI_RE.findall(text))
    found.update(QUOTED_RE.findall(text))
    return found


def items(text: str) -> list[dict]:
    """投稿本文の各項目を {line, title, note, terms} で返す。"""
    out = []
    for m in ITEM_RE.finditer(text):
        note = " ".join(m.group(3).split())
        out.append({
            "line": text.count("\n", 0, m.start()) + 1,
            "title": m.group(1),
            "note": note,
            "terms": terms(f"{m.group(1)} {note}"),
        })
    return out


def parse_name(name: str) -> tuple[date, str] | None:
    """ファイル名を (日付, フィード部分) にする。フィード部分は `news.md` / `news-{name}.md`。"""
    m = POST_NAME_RE.match(name)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1)), m.group(2)
    except ValueError:
        return None


class Archive:
    """投稿ディレクトリの項目を1回だけ読んで持つ。"""

    def __init__(self, posts_dir: Path):
        self.posts: list[tuple[date, str, str, list[dict]]] = []
        for path in sorted(posts_dir.glob("*.md")):
            parsed = parse_name(path.name)
            if parsed:
                day, feed = parsed
                self.posts.append((day, feed, path.name, items(path.read_text(encoding="utf-8"))))

    def between(self, start: date, end: date, feed: str | None = None):
        """start 以上 end 未満の日付の (ファイル名, 項目) を返す。feed を渡すとそのフィードだけ。"""
        for day, f, name, its in self.posts:
            if start <= day < end and (feed is None or f == feed):
                for it in its:
                    yield name, it


def repeats_of(post: Path, archive: Archive) -> list[tuple[dict, str, dict, float, list[str]]]:
    """印の無い再掲の疑いを (項目, 前回のファイル名, 前回の項目, 点数, 共有語) で返す。"""
    parsed = parse_name(post.name)
    if parsed is None:
        raise ValueError(f"ファイル名が YYYY-MM-DD-news*.md ではありません（{post.name}）")
    day, feed = parsed
    corpus = [it for _, it in archive.between(day - timedelta(days=IDF_DAYS), day)]
    df = Counter(t for it in corpus for t in it["terms"])
    n = len(corpus)
    past = list(archive.between(day - timedelta(days=WINDOW_DAYS), day, feed))

    found = []
    for it in items(post.read_text(encoding="utf-8")):
        if it["note"].startswith(FOLLOW_UP_PREFIX):
            continue
        best = None
        for name, prev in past:
            shared = [t for t in it["terms"] & prev["terms"] if df[t]]
            score = sum(math.log(n / df[t]) for t in shared)
            if score >= MIN_SCORE and (best is None or score > best[3]):
                best = (it, name, prev, score, sorted(shared, key=lambda t: df[t]))
        if best:
            found.append(best)
    return found


def main(argv: list[str]) -> int:
    posts = [Path(a) for a in argv if not a.startswith("--")]
    if not posts:
        print("使い方: check_topic_repeats.py _posts/YYYY-MM-DD-*.md", file=sys.stderr)
        return 2
    archives: dict[Path, Archive] = {}
    pairs = errors = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            errors += 1
            continue
        archive = archives.setdefault(post.parent, Archive(post.parent))
        try:
            found = repeats_of(post, archive)
        except ValueError as e:
            print(f"NG {post}: {e}")
            errors += 1
            continue
        for it, prev_name, prev, score, shared in found:
            pairs += 1
            print(f"要判断 {post.name}:{it['line']} 「{it['title']}」")
            print(f"  今回: {it['note']}")
            print(f"  前回 {prev_name[:10]}: 「{prev['title']}」 {prev['note']}")
            print(f"  共有語: {', '.join(shared[:6])}（点数 {score:.1f}）")
    print(f"検査 {len(posts) - errors} 件 / 要判断 {pairs} 組 / 検査できなかった {errors} 件")
    if errors:
        return 2
    return 1 if pairs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
