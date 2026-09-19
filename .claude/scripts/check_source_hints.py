#!/usr/bin/env python3
"""記事リストのソース表記に、読者向け属性（言語・購読）が付いているか検証する (#327)。

読者はリンクを開くまで、着地先が外国語か・購読が必要かを知る手段がない。
属性はソース定義 (`.claude/skills/curate-news/references/sources/*.md`) の
「読者向け属性」で決まるので、投稿側の表記がそれと一致しているかを機械で確かめる。

アグリゲータ（はてブ・HN・Reddit 等）の項目はリンク先が外部サイトなので、
ソース名だけで判定すると「(はてブ)」のまま会員限定の記事に飛ばしてしまう。
リンク先のドメインがソース定義の「記事ドメイン」に一致する場合は、そのソースの
属性を優先する（記事ごとの判断ではなく、ドメインからの決定的な導出）。

使い方:
  python3 .claude/scripts/check_source_hints.py                    # 当日 (JST) の投稿
  python3 .claude/scripts/check_source_hints.py _posts/....md ...
  python3 .claude/scripts/check_source_hints.py --all              # 全投稿（棚卸し用）

終了コード 0 なら、検査した全項目の表記がソース定義と一致している。
番号付き項目に見えて ITEM_RE に一致しない行は検査から漏れるため、
`check_article_notes.py` と同じく警告として別途出力する（exit code には影響しない）。
"""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

JST = timezone(timedelta(hours=9))
SOURCES_DIR = Path(".claude/skills/curate-news/references/sources")
# 出力で使われてきた表示名のゆれ。正規の表示名はソース定義の「表示名」が正。
ALIASES = {
    "Hacker News": "HN",
    "はてなブックマーク": "はてブ",
    "Product Hunt": "PH",
    "日経新聞": "日経",
    "MIT Technology Review": "MIT TR",
    "MIT Tech Review": "MIT TR",
    "Nature Machine Intelligence": "Nature",
    "Nature MI": "Nature",
}
# URL 部は check_article_notes.py と同じ形にし、ラベルは rest から取る。
# ラベルを必須にすると「ソース表記が丸ごと無い項目」が検査から漏れる。
ITEM_RE = re.compile(r"^\d+\. \[(?P<title>.*?)\]\((?P<url>[^)]*)\)(?P<rest>.*)$")
# ITEM_RE に一致しないが、番号付き/箇条書きリンク項目に見える行（検査漏れの検出用）
POSSIBLE_ITEM_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s*\*{0,2}\[")
LABEL_RE = re.compile(r"\((?P<label>[^()]*)\)\s*$")
BR_RE = re.compile(r"(?i)<br\s*/?>")
DISPLAY_RE = re.compile(r"^## 表示名\s*\n+`(?P<name>[^`]+)`", re.M)
LANG_RE = re.compile(r"^- \*\*リンク先の言語\*\*:\s*(?P<v>.+)$", re.M)
ACCESS_RE = re.compile(r"^- \*\*購読\*\*:\s*(?P<v>.+)$", re.M)
DOMAIN_RE = re.compile(r"^- \*\*記事ドメイン\*\*:\s*(?P<v>.+)$", re.M)


def _labels(lang: str, access: str):
    """読者にとっての新情報だけを並べる（日本語・無料は既定なので何も付けない）"""
    labels = []
    if lang.strip() != "日本語":
        labels.append(lang.strip())
    if access.strip() != "無料":
        labels.append(access.strip())
    return labels


def source_tables():
    """({表示名: ラベル}, {記事ドメイン: (ラベル, 表示名)}) を返す"""
    by_name, by_domain = {}, {}
    for path in sorted(SOURCES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        name = DISPLAY_RE.search(text)
        lang = LANG_RE.search(text)
        access = ACCESS_RE.search(text)
        domain = DOMAIN_RE.search(text)
        if not (name and lang and access and domain):
            print(f"NG {path}: 表示名 / 読者向け属性 が読み取れません")
            return None, None
        display = name.group("name").strip()
        if display in by_name:
            print(f"NG {path}: 表示名「{display}」が他のソースと重複しています")
            return None, None
        labels = _labels(lang.group("v"), access.group("v"))
        by_name[display] = labels
        for host in domain.group("v").split("/"):
            host = host.strip().lower()
            if host:
                by_domain[host] = (labels, display)
    return by_name, by_domain


def items_of(post: Path):
    """投稿本文の記事項目を (見出し, URL, ソース表記) で返す。表記が無ければ None"""
    text = post.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for line in body.split("\n"):
        m = ITEM_RE.match(line)
        if not m:
            continue
        head = BR_RE.split(m.group("rest"))[0].strip()
        label = LABEL_RE.search(head)
        yield m.group("title"), m.group("url"), (
            label.group("label").strip() if label else None)


def malformed_lines_of(post: Path):
    """ITEM_RE に一致しない、番号付き/箇条書きリンクに見える行を返す"""
    text = post.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for line in body.split("\n"):
        if not ITEM_RE.match(line) and POSSIBLE_ITEM_RE.match(line):
            yield line


def resolve(url: str, name: str, by_name, by_domain):
    """その項目に付けるべきラベルを返す。リンク先ドメインが既知ならそちらを優先する"""
    host = urlparse(url).netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    # 最長一致にして、サブドメインを持つ定義があっても決定的に選ばれるようにする
    for domain in sorted(by_domain, key=len, reverse=True):
        if host == domain or host.endswith("." + domain):
            return by_domain[domain][0]
    return by_name.get(name)


def expected_text(name: str, labels) -> str:
    return "・".join([name] + (["/".join(labels)] if labels else []))


def main(argv):
    by_name, by_domain = source_tables()
    if by_name is None:
        return 1

    if "--all" in argv:
        posts = sorted(Path("_posts").glob("*.md"))
    elif [a for a in argv if not a.startswith("--")]:
        posts = [Path(a) for a in argv if not a.startswith("--")]
    else:
        today = datetime.now(JST).strftime("%Y-%m-%d")
        posts = sorted(Path("_posts").glob(f"{today}-*.md"))
        if not posts:
            print(f"{today} の投稿がありません（_posts/{today}-*.md）", file=sys.stderr)
            return 1

    checked = failures = warned = 0
    for post in posts:
        if not post.is_file():
            print(f"NG {post}: ファイルがありません")
            failures += 1
            continue
        for title, url, label in items_of(post):
            checked += 1
            if label is None:
                print(f"NG {post.name}: ソース表記がありません （{title}）")
                failures += 1
                continue
            parts = [p.strip() for p in label.split("・")]
            name = ALIASES.get(parts[0], parts[0])
            if name not in by_name:
                print(f"NG {post.name}: 未知のソース名「{parts[0]}」 （{title}）")
                failures += 1
                continue
            got = [x.strip() for p in parts[1:] for x in p.split("/")]
            want = resolve(url, name, by_name, by_domain)
            if got != want:
                print(f"NG {post.name}: ソース表記が定義と違う "
                      f"（{title} — いま「{label}」/ "
                      f"あるべき「{expected_text(parts[0], want)}」）")
                failures += 1
        for line in malformed_lines_of(post):
            warned += 1
            print(f"WARN {post.name}: 番号付き項目に見えるが検査できない行 「{line.strip()}」")

    print(f"検査 {checked} 件 / 不一致 {failures} 件 / 検査できない行 {warned} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
