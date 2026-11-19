#!/usr/bin/env python3
"""読みどころの形式（1 文・20〜40 字の目安）からの外れを、投稿・出力ファイルごとに数える (#670)。

curate-news の手順5は読みどころを「1文」「20〜40字程度」と決めている。形どうしの品質を比べるとき
（docs/m5-paid-delivery.md の X と T）、この 2 点は検査役の subagent に数えさせると数え方が揺れるので、
決定的に数える。数えるのは目安からの外れであって、読みどころの良し悪しではない。

- 文の数: 「続報（…掲載）。」の前置きを除いた本文を「。」「！」「？」で区切り、空でない断片の数
- 字数: 同じ本文の文字数（末尾の句点を除く。空白も 1 字と数える）

使い方:
  python3 .claude/scripts/note_format_stats.py <投稿 or output/*.md> [...] [--json]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_article_notes import items_of  # noqa: E402

FOLLOW_UP_RE = re.compile(r"^続報（[^）]*）。\s*")
SENTENCE_END_RE = re.compile(r"[。！？]")
LONG_THRESHOLD = 50


def body_of(note: str) -> str:
    return FOLLOW_UP_RE.sub("", note.strip()).rstrip("。").strip()


def sentences_of(note: str) -> int:
    return sum(1 for s in SENTENCE_END_RE.split(body_of(note)) if s.strip())


def stats_of(path: Path) -> dict:
    notes = [note for _title, _label, note in items_of(path)]
    lengths = [len(body_of(n)) for n in notes]
    return {
        "file": str(path),
        "items": len(notes),
        "multi_sentence": sum(1 for n in notes if sentences_of(n) >= 2),
        "over_50": sum(1 for x in lengths if x > LONG_THRESHOLD),
        "max_len": max(lengths, default=0),
        "mean_len": round(sum(lengths) / len(lengths), 1) if lengths else 0,
    }


def main(argv):
    as_json = "--json" in argv
    paths = [Path(a) for a in argv if a != "--json"]
    if not paths:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    rows = [stats_of(p) for p in paths]
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print("file\titems\t2文以上\t50字超\t最大\t平均")
        for r in rows:
            print(f"{r['file']}\t{r['items']}\t{r['multi_sentence']}\t{r['over_50']}\t{r['max_len']}\t{r['mean_len']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
