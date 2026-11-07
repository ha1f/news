#!/usr/bin/env python3
"""プレミアムフィードの切り方の候補ごとに、材料の量と無料フィードとの重なりを数える (#628)。

docs/m5-paid-delivery.md の「プレミアムフィードの切り方の候補」節の表を再現する。

2 つのモードがある。

- posts: 公開済みの `_posts/`（無料の5フィード）から、期間内に載った記事のうち
  候補に当たるものを数える。無料フィードがその関心を既にどれだけ覆っているかの値。
  入力は main に入った投稿だけなので、同じ期間を指定すれば何度でも同じ値になる。
- pool: curate-news の取得キャッシュ（`fetch_feeds.py` を走らせた直後の
  `.claude/skills/curate-news/cache/*.json`）の候補記事のうち、候補に当たるものを数え、
  そのうち公開済みの `_posts/`（全期間）に URL が載っている割合を出す。有料フィードは
  公開サイトに載った記事を既定で除外する（同文書「前提」）ため、載っていない側が
  有料フィードの実際の材料になる。キャッシュは取得した時点のスナップショット。

候補の判定は見出しへの正規表現だけで行う（`_posts/` の見出しは日本語化済み、
キャッシュの見出しは原文なので、日英両方の語を並べる）。判定は粗く、
件数は目安。有料プロファイルの定義は含まない（切り方の名前と判定語だけ）。

使い方:
  python3 .claude/scripts/premium_cut_stats.py posts --since 2026-10-07 --until 2026-11-05
  python3 .claude/skills/curate-news/scripts/fetch_feeds.py --force
  python3 .claude/scripts/premium_cut_stats.py pool
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTS_DIR = os.path.join(ROOT, "_posts")
CACHE_DIR = os.path.join(ROOT, ".claude", "skills", "curate-news", "cache")
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "curate-news", "scripts"))
from commercial_filter import read_value  # noqa: E402
from published_urls import normalize  # noqa: E402

# 切り方の候補。(id, 名前, 判定語の正規表現)。大文字小文字は区別しない
# 見出しの正規表現に加え、_posts/ の article_tags に当たる名前がある候補は TAGS にも載せる
TAGS = {"security": "セキュリティ", "chips-hardware": "ハードウェア",
        "apple-mobile": None, "ai-build": "AI", "climate-energy": None, "policy": None}
CUTS = [
    ("ai-build", "AI を作る人向け（LLM・エージェントの実装と運用）",
     r"LLM|エージェント|\bagents?\b|agentic|\bRAG\b|プロンプト|\bprompt|Claude|GPT|Gemini|"
     r"\bMCP\b|ファインチューン|fine-?tuning|推論|inference|ベンチマーク|benchmark|"
     r"\bevals?\b|オープンウェイト|open-?weight|言語モデル|language model"),
    ("security", "セキュリティ（脆弱性・攻撃・情報漏洩）",
     r"脆弱性|vulnerab|\bCVE|攻撃|attack|ハッキング|\bhack(?:ed|ers?|ing)?\b|マルウェア|malware|ランサム|ransom|"
     r"漏洩|漏えい|\bleak|breach|セキュリティ|security|フィッシング|phishing|"
     r"ゼロデイ|zero-?day|exploit|不正アクセス|サイバー|cyber"),
    ("apple-mobile", "Apple・モバイルのアプリ開発",
     r"\biOS|iPhone|iPad|macOS|\bSwift|Xcode|Apple|watchOS|visionOS|Android|"
     r"モバイル|mobile|App Store|アプリ開発"),
    ("chips-hardware", "半導体・ハードウェア",
     r"半導体|semiconductor|\bchips?\b|チップ|\bGPU|NVIDIA|TSMC|\bIntel\b|\bAMD\b|\bArm\b|"
     r"プロセッサ|processor|\bDRAM|\bHBM|メモリ|ロボット|robot|ハードウェア|hardware"),
    ("climate-energy", "気候・エネルギー",
     r"気候|climate|温暖化|脱炭素|carbon|\bCO2|再エネ|再生可能|renewable|太陽光|solar|"
     r"風力|原発|原子力|nuclear|電池|batter|\bEVs?\b|電力|energy|エネルギー|核融合|\bfusion\b"),
    ("policy", "テックの政策・規制・訴訟",
     r"規制|\bregulat(?:ion|ions|ory|ors?|e|ed)\b|法案|独禁|独占禁止|antitrust|公取|訴訟|lawsuit|\bsue[sd]?\b|裁判|court|"
     r"\bFTC\b|\bDOJ\b|欧州委員会|European Commission|著作権|copyright|省令|政府|government"),
]

# `_posts/` のソース表記 → ソースID（表記の正本は curate-news の STYLEGUIDE.md）
LABEL_TO_SOURCE = {
    "HN": "hackernews", "Hacker News": "hackernews", "TechCrunch": "techcrunch",
    "はてブ": "hatena", "GIGAZINE": "gigazine", "日経": "nikkei", "Zenn": "zenn",
    "ITmedia": "itmedia", "Publickey": "publickey", "InfoQ": "infoq", "Reddit": "reddit",
    "MIT TR": "mit-tech-review", "Science": "science", "Dribbble": "dribbble",
    "Nature": "nature", "GitHub Trending": "github-trending", "Qiita": "qiita",
    "PH": "producthunt", "Product Hunt": "producthunt",
    "はてなブックマーク": "hatena", "日経新聞": "nikkei", "Gigazine": "gigazine",
    "MIT Technology Review": "mit-tech-review", "Nature Machine Intelligence": "nature",
}
# キャッシュの見出しの先頭に付く媒体内のカテゴリ札（例: `[ITmedia Mobile]`）。判定語に当てない
PREFIX_RE = re.compile(r"^\s*\[[^\]]*\]\s*")
TAGS_RE = re.compile(r"^article_tags:\s*\n((?:\s+- \[.*\]\n?)+)", re.M)

ITEM_RE = re.compile(r"^\d+\. \[(?P<title>.+?)\]\((?P<url>\S+?)\) \((?P<label>[^)]*)\)", re.M)
POST_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-news(?:-[a-z0-9-]+)?\.md$")


def compiled_cuts():
    return [(cid, name, re.compile(pat, re.I)) for cid, name, pat in CUTS]


def iter_posts(since: str | None = None, until: str | None = None):
    """(日付, フィード名, 見出し, URL, ソースID) を返す。"""
    for path in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md"))):
        name = os.path.basename(path)
        m = POST_NAME_RE.match(name)
        if not m:
            continue
        date = m.group(1)
        if (since and date < since) or (until and date > until):
            continue
        feed = name[len(date) + 1:-3]
        with open(path, encoding="utf-8") as f:
            text = f.read()
        tm = TAGS_RE.search(text)
        tag_rows = [set(t.strip() for t in line.strip()[3:-1].split(",")) for line in tm.group(1).splitlines()] if tm else []
        for i, im in enumerate(ITEM_RE.finditer(text)):
            label = im.group("label").split("・")[0].strip()
            tags = tag_rows[i] if i < len(tag_rows) else set()
            yield (date, feed, im.group("title"), im.group("url"),
                   LABEL_TO_SOURCE.get(label, f"?{label}"), tags)


def commercial(source_id: str) -> str:
    if source_id.startswith("?"):
        return "不明"
    return read_value(source_id) or "不明"


def fmt_sources(counter: Counter, top: int = 5) -> str:
    return "、".join(f"{s}({commercial(s)}) {n}" for s, n in counter.most_common(top))


def tag_cell(cid, per_tag_urls, n):
    if not TAGS.get(cid):
        return "-"
    u = len(per_tag_urls[cid])
    return f"{u}（{u / n:.1f}）[{TAGS[cid]}]"


def run_posts(args) -> int:
    cuts = compiled_cuts()
    days = set()
    slots_all = 0
    urls_all = set()
    per_cut_urls = defaultdict(set)
    per_cut_slots = Counter()
    per_cut_sources = defaultdict(Counter)
    seen_src = {}
    per_tag_urls = defaultdict(set)
    for date, _feed, title, url, src, tags in iter_posts(args.since, args.until):
        url = normalize(url)
        days.add(date)
        slots_all += 1
        urls_all.add(url)
        for cid, _name, rx in cuts:
            if rx.search(title):
                per_cut_slots[cid] += 1
                if url not in per_cut_urls[cid]:
                    per_cut_urls[cid].add(url)
                    per_cut_sources[cid][src] += 1
        for cid, tag in TAGS.items():
            if tag and tag in tags:
                per_tag_urls[cid].add(url)
        seen_src[url] = src
    n = len(days)
    if n == 0:
        print("対象期間に投稿がありません", file=sys.stderr)
        return 1
    print(f"posts: {args.since}〜{args.until} の {n} 日、掲載枠 {slots_all}・異なる URL {len(urls_all)}")
    print("| 候補 | 見出しに当たる異なる URL（日あたり） | 掲載枠（日あたり） | article_tags に当たる異なる URL（日あたり） "
          "| 主なソース（商用利用（課金）） 本数 |")
    print("|---|---|---|---|---|")
    for cid, name, _rx in cuts:
        u = len(per_cut_urls[cid])
        print(f"| {cid} | {u}（{u / n:.1f}） | {per_cut_slots[cid]}（{per_cut_slots[cid] / n:.1f}） "
              f"| {tag_cell(cid, per_tag_urls, n)} | {fmt_sources(per_cut_sources[cid])} |")
    return 0


def _parse_time(value):
    """ISO 8601 の日時を aware datetime にする。読めなければ None（直近24時間に数えない）。"""
    if not value:
        return None
    try:
        t = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def run_pool(args) -> int:
    cuts = compiled_cuts()
    published = {normalize(x[3]) for x in iter_posts()}
    files = sorted(glob.glob(os.path.join(args.cache_dir, "*.json")))
    items = {}
    fetched = []
    for path in files:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        fetched.append(data.get("fetched_at", ""))
        for it in data.get("items", []):
            url = normalize(it["url"]) if it.get("url") else None
            if url and url not in items:
                items[url] = (PREFIX_RE.sub("", it.get("title") or ""), data.get("source_id", "?"),
                              _parse_time(it.get("published_at")))
    if not items:
        print("キャッシュに候補がありません。先に fetch_feeds.py を走らせる", file=sys.stderr)
        return 1
    sources_all = Counter(s for _t, s, _p in items.values())
    newest = max((t for t in map(_parse_time, fetched) if t), default=None)
    stamp = newest.strftime("%Y-%m-%d %H:%M %z") if newest else "?"
    recent_from = newest - dt.timedelta(hours=24) if newest else None
    print(f"pool: キャッシュ {len(files)} フィード・異なる URL {len(items)}（取得 {stamp} 頃）、"
          f"公開済み {sum(u in published for u in items)}")
    print("| 候補 | 当たる候補 | うち公開済み（割合） | 未公開（有料の材料） | うち直近24時間 "
          "| 未公開の主なソース（商用利用（課金）） 本数 |")
    print("|---|---|---|---|---|---|")
    for cid, _name, rx in cuts:
        hit = [(u, s, pt) for u, (t, s, pt) in items.items() if rx.search(t)]
        pub = sum(u in published for u, _s, _p in hit)
        rest = [(s, pt) for u, s, pt in hit if u not in published]
        recent = sum(1 for _s, pt in rest if pt and recent_from and pt >= recent_from)
        share = f"{pub / len(hit):.0%}" if hit else "-"
        print(f"| {cid} | {len(hit)} | {pub}（{share}） | {len(rest)} | {recent} "
              f"| {fmt_sources(Counter(s for s, _p in rest))} |")
    if args.show_sources:
        print("\nソース別の候補数:", ", ".join(f"{s} {n}" for s, n in sources_all.most_common()))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="mode", required=True)
    today = dt.date.today()
    pp = sub.add_parser("posts", help="公開済み _posts/ の期間内の記事を数える")
    pp.add_argument("--since", default=(today - dt.timedelta(days=29)).isoformat())
    pp.add_argument("--until", default=today.isoformat())
    pl = sub.add_parser("pool", help="取得キャッシュの候補を数える")
    pl.add_argument("--cache-dir", default=CACHE_DIR)
    pl.add_argument("--show-sources", action="store_true")
    args = p.parse_args(argv)
    return run_posts(args) if args.mode == "posts" else run_pool(args)


if __name__ == "__main__":
    sys.exit(main())
