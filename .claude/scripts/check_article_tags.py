#!/usr/bin/env python3
"""投稿の front matter `article_tags`（記事単位のトピック）が本文と揃っているか検証する (#354)。

`tags` は投稿＝その日のフィード全体に付くので、1日のフィードが多様なほど全部付き、
主要トピック（AI・開発）で絞っても1日も減らない。`article_tags` は番号付きの記事
1本ずつにトピックを持たせ、アーカイブの絞り込みが記事にたどり着けるようにする。

  article_tags:
    - [AI, 社会]        # 1本目
    - [セキュリティ]    # 2本目
    - []                # 該当なし

検査するのは次の4つ:
  1. `article_tags` の要素数が、本文の番号付き記事の数と一致する
     （表示側は N 本目の `<li>` に N 番目の要素を当てるので、ずれると全部ずれる）
  2. 各トピックが語彙（publish-pages/SKILL.md のトピック一覧）に入っている
  3. 1本に付けるトピックは3個まで（全部付けると絞り込みとして働かない）
  4. `tags` が `article_tags` の和集合と一致する（日単位の導線と記事単位の導線で
     同じ日が出たり出なかったりしないように）

「トピックが記事の主題に合っているか」は機械では判定できないので検査しない。

使い方:
  python3 .claude/scripts/check_article_tags.py                    # 当日 (JST) の投稿
  python3 .claude/scripts/check_article_tags.py _posts/....md ...
  python3 .claude/scripts/check_article_tags.py --all              # article_tags を持つ全投稿

当日分・明示したファイルでは `article_tags` が無いことも違反にする。`--all` は
導入前の投稿（`article_tags` を持たない）を飛ばす。
終了コード 0 なら、検査した全投稿が規約どおり。
"""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
VOCAB = ("AI", "開発", "セキュリティ", "ビジネス", "科学", "デザイン", "経済", "ハードウェア", "社会")
MAX_PER_ARTICLE = 3
# 本文の番号付き記事。kramdown が `<li>` にするのは行頭（3字までの字下げ）の `N. `
ITEM_RE = re.compile(r"^ {0,3}\d+\.\s", re.M)
TAGS_RE = re.compile(r"^tags:\s*\[(?P<body>[^\]]*)\]\s*$", re.M)
ARTICLE_TAGS_HEAD_RE = re.compile(r"^article_tags:\s*$", re.M)
ARTICLE_TAGS_ITEM_RE = re.compile(r"^\s+-\s*\[(?P<body>[^\]]*)\]\s*$")


def split_list(body: str):
    return [t.strip().strip("\"'") for t in body.split(",") if t.strip()]


def parse(text: str):
    """(tags, article_tags, 記事数) を返す。front matter が無ければ None。

    article_tags が無ければ None、あるが書式が崩れていれば ValueError"""
    if not text.startswith("---"):
        return None
    _, front, body = text.split("---", 2)
    m = TAGS_RE.search(front)
    tags = split_list(m.group("body")) if m else None
    article_tags = None
    head = ARTICLE_TAGS_HEAD_RE.search(front)
    if head:
        article_tags = []
        for line in front[head.end():].splitlines()[1:]:
            if not line.strip():
                continue
            im = ARTICLE_TAGS_ITEM_RE.match(line)
            if im:
                article_tags.append(split_list(im.group("body")))
            elif line[:1] in (" ", "\t", "-"):
                raise ValueError(f"article_tags の行を読めない: {line.strip()}")
            else:
                break
    return tags, article_tags, len(ITEM_RE.findall(body))


def check(text: str, require: bool):
    """違反の説明のリストを返す（空なら合格）"""
    parsed = parse(text)
    if parsed is None:
        return ["front matter が無い"]
    tags, article_tags, count = parsed
    if article_tags is None:
        return ["article_tags が無い"] if require else []
    errors = []
    if len(article_tags) != count:
        errors.append(f"article_tags が {len(article_tags)} 件、本文の記事は {count} 本")
    for i, topics in enumerate(article_tags, 1):
        unknown = [t for t in topics if t not in VOCAB]
        if unknown:
            errors.append(f"{i}本目: 語彙に無いトピック {unknown}")
        if len(topics) > MAX_PER_ARTICLE:
            errors.append(f"{i}本目: トピックが {len(topics)} 個（{MAX_PER_ARTICLE} 個まで）")
        if len(set(topics)) != len(topics):
            errors.append(f"{i}本目: トピックが重複している {topics}")
    union = {t for topics in article_tags for t in topics}
    if tags is None or set(tags) != union:
        errors.append(f"tags {tags} が article_tags の和集合 {sorted(union)} と一致しない")
    return errors


def main(argv):
    if "--all" in argv:
        posts, require = sorted(Path("_posts").glob("*.md")), False
    elif argv:
        posts, require = [Path(a) for a in argv], True
    else:
        today = datetime.now(JST).strftime("%Y-%m-%d")
        posts, require = sorted(Path("_posts").glob(f"{today}-*.md")), True
        if not posts:
            print(f"{today} の投稿が _posts/ に無い", file=sys.stderr)
            return 1
    failed = 0
    checked = 0
    for post in posts:
        text = post.read_text(encoding="utf-8")
        try:
            errors = check(text, require)
            if require or parse(text)[1] is not None:
                checked += 1
        except ValueError as e:
            errors = [str(e)]
        if errors:
            failed += 1
            for e in errors:
                print(f"NG {post}: {e}")
    if failed:
        print(f"{failed}/{len(posts)} 件が規約違反", file=sys.stderr)
        return 1
    print(f"OK: {checked} 件の article_tags が本文・tags と一致")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
