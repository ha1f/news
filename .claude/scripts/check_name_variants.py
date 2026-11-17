#!/usr/bin/env python3
"""投稿の見出し・リード・読みどころ・title で、固有名が決めた表記と別の形で書かれていないか検査する (#664)。

同じ人物・会社が日によって「Anthropic」と「アンソロピック」、「フアン」と「ファン氏」のように
割れると、続く話題を追う読者は同じ主体だと結びつけられず、`check_topic_repeats.py` も
同じ話題を拾えない。日本語媒体の記事を元にした項目で、媒体の表記がそのまま入りやすい。

表記と揺れの正本は `.claude/skills/curate-news/references/names.md` の表で、ここはそれを
読んで照合するだけ（表の「揺れ」列のバッククォートで囲んだ形が NG になり、`揺れ→直した形` なら直した形を示す）。

照合のしかた:
  - 対象は front matter の `title` と本文。リンクの URL（`](...)` の中）とインラインコードは外す
  - カタカナで始まる（終わる）揺れは、直前（直後）にカタカナが続くときは数えない
    （「メタデータ」「シルクロード」の類）。英字の揺れは前後に英数字が続くときは数えず、
    大文字・小文字を区別する（`Nvidia` は NG、`NVIDIA` は通る）

使い方:
  python3 .claude/scripts/check_name_variants.py                    # 当日 (JST) の投稿
  python3 .claude/scripts/check_name_variants.py _posts/....md ...
  python3 .claude/scripts/check_name_variants.py --all              # 全投稿（棚卸し用）

終了コード 0 なら揺れなし、1 なら揺れあり（または対象の投稿が無い）、2 なら表が読めない。
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
NAMES_MD = Path(__file__).resolve().parents[1] / "skills" / "curate-news" / "references" / "names.md"

KATAKANA = "ァ-ヴー"
LINK_TARGET_RE = re.compile(r"\]\([^)\s]*\)")
CODE_RE = re.compile(r"`[^`\n]*`")
TITLE_RE = re.compile(r"^title:\s*(.*?)\s*$", re.M)


def load_table(path: Path | None = None) -> list[tuple[str, str]]:
    """names.md の表から (揺れ, 直した形) の組を返す。

    直した形は、揺れが `ファン氏→フアン氏` の形ならその右側、そうでなければ表記の列の「（」より前
    """
    pairs = []
    for line in (path or NAMES_MD).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] == "表記":
            continue
        canonical = cells[0].split("（", 1)[0].strip()
        for item in re.findall(r"`([^`]+)`", cells[1]):
            variant, _, fixed = item.partition("→")
            pairs.append((variant, fixed or canonical))
    return pairs


def variant_pattern(variant: str) -> re.Pattern:
    """揺れを、前後の境界つきの正規表現にする"""
    body = re.escape(variant)
    if re.match(f"[{KATAKANA}]", variant):
        body = f"(?<![{KATAKANA}])" + body
    elif re.match(r"[A-Za-z0-9]", variant):
        body = r"(?<![A-Za-z0-9])" + body
    if re.search(f"[{KATAKANA}]$", variant):
        body += f"(?![{KATAKANA}])"
    elif re.search(r"[A-Za-z0-9]$", variant):
        body += r"(?![A-Za-z0-9])"
    return re.compile(body)


def compiled(pairs: list[tuple[str, str]]) -> list[tuple[re.Pattern, str, str]]:
    return [(variant_pattern(v), v, c) for v, c in pairs]


def normalize(text: str, rules: list[tuple[re.Pattern, str, str]]) -> str:
    """揺れを表記に置き換える（check_topic_repeats.py が固有名の照合の前に使う）"""
    for pattern, variant, canonical in rules:
        text = pattern.sub(canonical, text)
    return text


def checked_lines(text: str) -> list[tuple[int, str]]:
    """検査する (行番号, 行) を返す。front matter は title 行だけ"""
    lines = text.splitlines()
    out = []
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
            if TITLE_RE.match(lines[i]):
                out.append((i + 1, lines[i]))
    for i in range(start, len(lines)):
        out.append((i + 1, lines[i]))
    return out


def find_variants(text: str, rules) -> list[tuple[int, str, str]]:
    """(行番号, 揺れ, 表記) を出現順に返す"""
    found = []
    for lineno, line in checked_lines(text):
        visible = CODE_RE.sub("", LINK_TARGET_RE.sub("]", line))
        hits = sorted(
            ((m.start(), -len(variant), m.end(), variant, canonical)
             for pattern, variant, canonical in rules for m in pattern.finditer(visible)),
        )
        end = -1
        for start, _, stop, variant, canonical in hits:
            if start >= end:  # 重なる短い揺れ（「ジェンスン・ファン氏」の「ファン氏」）は数えない
                found.append((lineno, variant, canonical))
                end = stop
    return found


def main(argv: list[str]) -> int:
    try:
        rules = compiled(load_table())
    except OSError as e:
        print(f"表が読めません（{NAMES_MD}）: {e}", file=sys.stderr)
        return 2
    if not rules:
        print(f"表に揺れが1つもありません（{NAMES_MD}）", file=sys.stderr)
        return 2

    args = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        posts = sorted(Path("_posts").glob("*.md"))
    elif args:
        posts = [Path(a) for a in args]
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
        checked += 1
        for lineno, variant, canonical in find_variants(post.read_text(encoding="utf-8"), rules):
            print(f"NG {post.name}:{lineno}: 「{variant}」→「{canonical}」")
            failures += 1

    print(f"検査 {checked} 件 / 表記の揺れ {failures} 件（表: .claude/skills/curate-news/references/names.md）")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
