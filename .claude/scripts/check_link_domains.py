#!/usr/bin/env python3
"""ビルド済みの記事ページで、遷移先ドメインの表示が「ラベルと遷移先が違う項目だけ」に付いているか検証する (#183)。

`_layouts/post.html` は Liquid で、項目のラベルが示す媒体（ソース定義の「記事ドメイン」）と
リンク先のホストが一致しないときだけ、見出しリンクの直後に `<span class="link-domain">` を出す。
この検査は同じ規則を Python でソース定義から直接組み立て、生成結果と突き合わせる:

- 一致しない項目（はてブ → itmedia.co.jp 等）: 表示があり、中身がリンク先のホスト（www. を除く）
- 一致する項目（TechCrunch → techcrunch.com 等）: 表示が無い（#294 の二重表示を出さない）

あわせて `_data/source_domains.json` がソース定義と一致しているか（gen_source_domains.py --check と同じ）も見る。

使い方:
  python3 .claude/scripts/check_link_domains.py _site
終了コード 0 なら全項目が規則どおり。
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import gen_source_domains

ITEM_RE = re.compile(r'<li id="article-\d+">\s*(?:<p>)?(?P<head>.*?)(?:<br|</p>|</li>)', re.S)
# Liquid と同じく、項目の中で最初のリンクを見出しとみなす（前に <strong> 等があっても拾う）
LINK_RE = re.compile(r'<a href="(?P<href>[^"]*)"[^>]*>.*?</a>(?P<rest>.*)$', re.S)
DOMAIN_RE = re.compile(r'^<span class="link-domain">(?P<host>[^<]*)</span>(?P<rest>.*)$', re.S)
LABEL_RE = re.compile(r"\((?P<label>[^()]*)\)\s*$")
# 記事ごとのトピック (#567)。ラベルの直後に入るので、ラベルを取る前に外す
TOPICS_RE = re.compile(r'<span class="article-topics">(?:<span class="article-topic">[^<]*</span>)*</span>')


def host_of(href: str) -> str:
    host = (urlparse(href).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


GENERIC_WORDS = {"the", "and", "blog", "news", "tech", "notes", "security", "japan"}


def label_matches(host: str, name: str, table) -> bool:
    domains = table.get(name)
    if domains is None:
        domains = table.get(name.split(" ")[0])
    if domains is not None:
        return any(host == d or host.endswith("." + d) for d in domains)
    # 対応表に無いラベル（ソース定義より前の過去の投稿）は、汎用語を除いた3文字以上の語が
    # 英数字にしてホストに含まれるかで見る
    host_compact = re.sub(r"[.\-]", "", host)
    for word in name.lower().split(" "):
        w = re.sub(r"[.\-\[\]/_:]", "", word)
        if len(w) >= 3 and w not in GENERIC_WORDS and w in host_compact:
            return True
    return False


def check_item(head: str, table):
    """1項目を検査し、問題があればその説明を返す。検査対象外の項目は None と同じ扱い"""
    link = LINK_RE.search(TOPICS_RE.sub("", head))
    if not link or "://" not in link.group("href"):
        return None
    host = host_of(link.group("href"))
    rest = link.group("rest")
    shown = DOMAIN_RE.match(rest)
    label_part = shown.group("rest") if shown else rest
    label = LABEL_RE.search(label_part.strip())
    name = label.group("label").split("・")[0].strip() if label else ""
    want = not label_matches(host, name, table)
    if want and not shown:
        return f"遷移先の表示がありません（{name or 'ラベルなし'} → {host}）"
    if not want and shown:
        return f"ラベルと遷移先が一致するのに表示があります（{name} → {host}）"
    if shown and shown.group("host") != host:
        return f"表示が遷移先と違います（{shown.group('host')} ≠ {host}）"
    return None


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip().split("\n\n")[-2], file=sys.stderr)
        return 2
    site = Path(argv[0])
    table = gen_source_domains.build()
    if table is None:
        return 1
    failures = 0
    current = gen_source_domains.OUT
    if not current.is_file() or current.read_text(encoding="utf-8") != gen_source_domains.render(table):
        print(f"NG {current} がソース定義と一致しません（gen_source_domains.py で書き直す）")
        failures += 1

    checked = shown = 0
    for page in sorted(site.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        if 'id="article-' not in text:
            continue
        for m in ITEM_RE.finditer(text):
            head = m.group("head")
            if 'class="link-domain"' in head:
                shown += 1
            problem = check_item(head, table)
            if LINK_RE.search(head):
                checked += 1
            if problem:
                failures += 1
                print(f"NG {page.relative_to(site)}: {problem}")
    print(f"検査 {checked} 件 / 遷移先の表示あり {shown} 件 / 不一致 {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
