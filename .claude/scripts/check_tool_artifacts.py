#!/usr/bin/env python3
"""投稿にツール呼び出し構文が残っていないか検証する (#408)。

記事を書き出したときの道具立て（ツール呼び出しのシリアライズ）が、本文の一部
として保存されてしまうことがある。実測 2026-09-24 と 2026-09-26: 各5プロファイル
の計10本が、本文の最終行に `</content>` を持ったまま main に入り、読者の見える
ページに `</content>` が段落として描画された（記事末尾と前後記事リンクの間）。
単発の保存でも並列の保存でも起きており、特定の保存ツールに限った欠陥ではない。

既存の品質検査（`check_article_notes.py` / `check_source_hints.py`）は本文の
「番号付き記事項目」だけを見るので、項目の形をしていないこの行には何も言わず
exit 0 で素通りする。CI の "Check article quality" に両方が入った後も同じだった。
決定的に判定できる欠陥なので、目視の手順ではなくこの検査で塞ぐ。

検査は2つ。どちらもコードブロックとインラインコードを外してから当てる
（投稿は `` `<usermedia>` `` のようにタグ名をコードとして引用することがあり、
そこまで拾うと記事の話題そのものを誤検知する）。

  1. ツール呼び出し語彙のタグ（`<invoke>` `</content>` `<parameter>` 等）が
     本文のどこかに現れる
  2. 行全体がひとつのタグだけでできている（`<br>` `<hr>` を除く）

2 は語彙を知らない新しいツール構文を拾うための網。投稿は markdown で書かれ、
HTML は行末の `<br>` しか使わない（実測 2026-09-30、全 408 本で行全体がタグ
だけの行は上記の `</content>` 10 本のみ、本文に現れる HTML タグは `<br>` 4,042 個
と、コードとして引用された `<usermedia>` / `<NonZeroU8>` だけ）。

使い方:
  python3 .claude/scripts/check_tool_artifacts.py                  # 全投稿
  python3 .claude/scripts/check_tool_artifacts.py _posts/....md ...
  python3 .claude/scripts/check_tool_artifacts.py --all            # 全投稿（明示）

引数なしを「当日分」ではなく「全投稿」にしてあるのは、他の検査と違ってこの検査
が誤検知を持たず、かつ過去に入った混入を残したままにしないため。混入は間欠的に
起きるので、「今日は出ていない」は収束の根拠にならない。

終了コード 0 なら、検査した全投稿にツール呼び出し構文が残っていない。
"""
import re
import sys
from pathlib import Path

# ツール呼び出しのシリアライズに現れるタグ名。`antml:` 付きの名前空間も同じ扱い。
TOOL_TAG_NAMES = (
    "invoke",
    "parameter",
    "function_calls",
    "function_results",
    "content",
)
TOOL_TAG_RE = re.compile(
    r"</?\s*(?:antml:)?(?:" + "|".join(TOOL_TAG_NAMES) + r")\b[^>]*>",
    re.IGNORECASE,
)
# `antml:` は記事本文に現れない名前空間なので、タグの形を成していなくても拾う。
# TOOL_TAG_RE 側の `(?:antml:)?` と重なるが、あちらはタグの形になっているものしか
# 見ないので、素の文字列として残った場合はこちらだけが効く
ANTML_RE = re.compile(r"antml:[A-Za-z_][\w.-]*")
# 行全体がひとつのタグ。開き・閉じ・自己閉じのいずれも見る
LONE_TAG_RE = re.compile(r"^\s*</?\s*([A-Za-z_][\w.:-]*)[^>]*?/?>\s*$")
# 記事本文が実際に使う block/inline HTML。ここに無いタグが行全体を占めていたら混入を疑う
ALLOWED_LONE_TAGS = {"br", "hr"}

FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> list:
    """コードブロックとインラインコードを空白に潰した行のリストを返す。

    行番号を保ちたいので行を削らず、中身だけを落とす。閉じられていないフェンスは
    そこから末尾までをコードとして扱う（開いたままの投稿は無いが、あったときに
    本文として誤検知するより、検査しないほうが安全側）。
    """
    out = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line))
    return out


def problems_of(post: Path):
    """その投稿に残っているツール呼び出し構文を (行番号, 説明) で返す"""
    found = []
    for lineno, line in enumerate(strip_code(post.read_text(encoding="utf-8")), 1):
        for m in TOOL_TAG_RE.finditer(line):
            found.append((lineno, f"ツール呼び出し構文が残っています（{m.group(0)}）"))
        for m in ANTML_RE.finditer(line):
            found.append((lineno, f"ツール呼び出しの名前空間が残っています（{m.group(0)}）"))
        m = LONE_TAG_RE.match(line)
        if m and m.group(1).lower() not in ALLOWED_LONE_TAGS:
            found.append((lineno, f"行全体がタグだけです（{line.strip()}）"))
    # 同じ行で複数の規則が当たっても報告は1件にする（直す箇所は1つなので）
    seen = set()
    unique = []
    for lineno, message in found:
        if lineno in seen:
            continue
        seen.add(lineno)
        unique.append((lineno, message))
    return unique


def main(argv):
    paths = [a for a in argv if not a.startswith("--")]
    if paths:
        posts = [Path(a) for a in paths]
    else:
        posts = sorted(Path("_posts").glob("*.md"))

    checked = failures = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            failures += 1
            continue
        checked += 1
        for lineno, message in problems_of(post):
            print(f"NG {post}:{lineno}: {message}")
            failures += 1

    print(f"検査 {checked} 件 / 混入 {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
