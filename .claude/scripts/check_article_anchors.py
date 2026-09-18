#!/usr/bin/env python3
"""ビルド済みサイトの見出しリンクが、着地先ページに実在するアンカーを指しているか検証する。

トップページ・プロファイルページの記事見出しは `<記事ページ>#article-N` を指す。
N が記事ページ側の `<li id="article-N">` と一致していなければ、読者は日付ページの
先頭に着地して見出しを探し直すことになる (これが #326 の症状)。

検査する3点:
  1. 見出しリンクが fragment を持つ (持たなければ #326 以前の状態への退行)
  2. その fragment が着地先ページに実在する
  3. リンクテキストと着地先の記事見出しが一致する (番号のずれの検出)
「他N件」はページ全体への導線なので fragment を持たないことを確認する
(受け入れ条件の「見出しと着地点が区別できる」に対応)。

使い方:
  python3 .claude/scripts/check_article_anchors.py [_site]
"""
import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote

LIST_RE = re.compile(r'<ul class="archive-article-titles">(.*?)</ul>', re.S)
ITEM_RE = re.compile(r'<li(?P<attrs>[^>]*)>\s*<a href="(?P<href>[^"]+)">(?P<label>.*?)</a>\s*</li>', re.S)
MORE_RE = re.compile(r'class="[^"]*archive-article-more')
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


def baseurl():
    """_config.yml の baseurl (無ければ空文字)"""
    config = Path("_config.yml")
    if config.is_file():
        m = re.search(r'^baseurl:\s*"?([^"\n]*)"?\s*$', config.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip().strip("/")
    return ""


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not site.is_dir():
        print(f"ビルド結果が見つかりません: {site}", file=sys.stderr)
        return 1
    prefix = baseurl()

    anchors_cache = {}
    checked = failures = 0
    for page in sorted(site.rglob("*.html")):
        source = page.relative_to(site)
        for block in LIST_RE.findall(page.read_text(encoding="utf-8")):
            for item in ITEM_RE.finditer(block):
                href, label = item.group("href"), text_of(item.group("label"))
                is_more = bool(MORE_RE.search(item.group("attrs")))
                path, _, fragment = href.partition("#")
                checked += 1

                if is_more:
                    # 「他N件」はページ先頭への導線。fragment を持ってはいけない
                    if fragment:
                        print(f"NG {source}: 「{label}」にアンカーが付いている ({href})")
                        failures += 1
                    continue
                if not fragment:
                    print(f"NG {source}: 見出し「{label}」が記事アンカーを指していない ({href})")
                    failures += 1
                    continue

                target = site / unquote(path).lstrip("/")
                if prefix:
                    target = site / unquote(path).lstrip("/").removeprefix(prefix + "/")
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
                elif found[fragment] != label:
                    print(f"NG {source}: #{fragment} の見出しが不一致 "
                          f"(リンク={label!r} / 着地先={found[fragment]!r})")
                    failures += 1

    print(f"検査 {checked} 件 / 失敗 {failures} 件")
    return 1 if failures or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
