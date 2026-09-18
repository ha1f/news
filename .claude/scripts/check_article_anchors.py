#!/usr/bin/env python3
"""ビルド済みサイトの見出しリンクが、着地先ページに実在するアンカーを指しているか検証する。

トップページ (#326) とプロファイルページの記事見出しは `<記事ページ>#article-N` を指す。
N は記事ページ側の `<li id="article-N">` と一致していなければ、読者は日付ページの
先頭に着地して見出しを探し直すことになる (これが #326 の症状)。

使い方:
  python3 .claude/scripts/check_article_anchors.py [_site]

終了コード 0 なら、検査した全リンクが実在するアンカーを指し、かつリンクテキストが
着地先の記事見出しと一致している。1 件でも壊れていれば 1。
"""
import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# トップページ・プロファイルページの見出しリスト内のリンク
LIST_RE = re.compile(r'<ul class="archive-article-titles">(.*?)</ul>', re.S)
LINK_RE = re.compile(r'<a href="([^"]+)">(.*?)</a>', re.S)
# 記事ページ側のアンカー付き <li> と、その中の最初のリンクテキスト
ANCHOR_RE = re.compile(r'<li id="(article-\d+)">(.*?)(?=<li id="article-\d+">|</ol>|</ul>)', re.S)
FIRST_LINK_TEXT_RE = re.compile(r'<a [^>]*>(.*?)</a>', re.S)


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def anchors_of(page_html):
    """記事ページの {アンカー id: 見出しテキスト} を返す"""
    result = {}
    for anchor_id, body in ANCHOR_RE.findall(page_html):
        m = FIRST_LINK_TEXT_RE.search(body)
        result[anchor_id] = text_of(m.group(1)) if m else ""
    return result


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not site.is_dir():
        print(f"ビルド結果が見つかりません: {site}", file=sys.stderr)
        return 1

    anchors_cache = {}
    checked = failures = 0
    for page in sorted(site.rglob("*.html")):
        source = page.relative_to(site)
        for block in LIST_RE.findall(page.read_text(encoding="utf-8")):
            for href, label in LINK_RE.findall(block):
                path, _, fragment = href.partition("#")
                if not fragment:
                    continue  # 「他N件」はページ全体への導線なのでアンカーを持たない
                checked += 1
                target = site / unquote(path).lstrip("/").removeprefix("news/")
                if target.is_dir() or path.endswith("/"):
                    target = target / "index.html"
                if not target.is_file():
                    print(f"NG {source}: 着地先が存在しない {href}")
                    failures += 1
                    continue
                key = str(target)
                if key not in anchors_cache:
                    anchors_cache[key] = anchors_of(target.read_text(encoding="utf-8"))
                found = anchors_cache[key]
                if fragment not in found:
                    print(f"NG {source}: アンカー #{fragment} が {path} に無い")
                    failures += 1
                elif found[fragment] != text_of(label):
                    print(f"NG {source}: #{fragment} の見出しが不一致 "
                          f"(リンク={text_of(label)!r} / 着地先={found[fragment]!r})")
                    failures += 1

    print(f"検査 {checked} 件 / 失敗 {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
