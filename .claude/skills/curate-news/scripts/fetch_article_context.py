#!/usr/bin/env python3
"""記事ページから読みどころを書くための事実を取ってくる (#342)。

フィードの description が空のソース（Hacker News・日経速報・公式リリースノート・
一次論文など）は毎日フィードに入る。手元に事実が無いまま1行を書かせると、
「原文で確認できる」「〜そのもの」のような出どころの紹介にしかならず、
見出しと括弧内のソース名から既に分かること以上を読者に渡せない。

そこで記事ページから事実を取りに行く。取れなければ「取れなかった」と返し、
その項目は採用しない（curate-news/SKILL.md の「読みどころ」節）。

抽出するのは事実を書くための材料であって、転載するための本文ではない。
読みどころは GUARDRAILS.md のコンテンツの権利ガードレールに従い、
事実と論点の抽出にとどめる（原文の構成・修辞をなぞらない）。

使い方:
  python3 fetch_article_context.py URL [URL ...]
  python3 fetch_article_context.py --stdin < urls.txt

出力: {URL: {"ok": bool, "thin": bool, "title": str, "meta": str, "body": str, "note": str}}
  - ok=false は取得そのものの失敗（ネットワーク・HTTP エラー）
  - thin=true は本文がほとんど取れなかったページ（JS で描画する SPA 等）

材料から見出し以上の事実が書けるかどうかは、このスクリプトでは判定しない。
閾値で判定すると、汎用の meta（「新機能を使うようアプリを更新しましょう」等）を
事実ありと誤判定する。採否は curate-news の規則で決め、
check_article_notes.py が結果を機械的に検査する。
"""
from __future__ import annotations

import gzip
import html
import json
import re
import sys
import urllib.error
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor

USER_AGENT = "Mozilla/5.0 (compatible; ha1f-news/1.0; +https://ha1f.github.io/news/)"
# 明示しないと CDN が brotli を返してくることがあり、そのまま読むと文字化けする。
# 展開できる形式だけを要求する
ACCEPT_ENCODING = "gzip, deflate, identity"
TIMEOUT = 15
# 本文はページによって桁違いに長い。事実を拾うのに十分な範囲だけ返す
BODY_CHARS = 1500
# これ未満しか取れないページは JS で本文を描画している可能性が高い（材料としては薄い）
THIN_BODY_CHARS = 200
DROP_RE = re.compile(
    r"(?is)<(script|style|nav|header|footer|noscript|aside|form|svg)[^>]*>.*?</\1>")
TAG_RE = re.compile(r"(?s)<[^>]+>")
META_RE = re.compile(r"<meta[^>]+>", re.I)
META_KEY_RE = re.compile(
    r"""(?:property|name)\s*=\s*["'](og:description|description|twitter:description)["']""",
    re.I)
CONTENT_RE = re.compile(r"""content\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
TITLE_RE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")


def _clean(text: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def _meta_description(doc: str) -> str:
    """og:description / description のうち最も長いものを返す"""
    best = ""
    for tag in META_RE.findall(doc):
        if not META_KEY_RE.search(tag):
            continue
        found = CONTENT_RE.search(tag)
        if not found:
            continue
        value = _clean(found.group(1) or found.group(2) or "")
        if len(value) > len(best):
            best = value
    return best


def fetch_one(url: str) -> dict:
    result = {"ok": False, "thin": False, "title": "", "meta": "", "body": "",
              "note": ""}
    try:
        request = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT, "Accept-Encoding": ACCEPT_ENCODING})
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            compression = (response.headers.get("Content-Encoding") or "").lower()
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as error:
        result["note"] = f"取得できません: {type(error).__name__} {error}"
        return result

    try:
        if compression == "gzip":
            raw = gzip.decompress(raw)
        elif compression == "deflate":
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    except (OSError, zlib.error) as error:
        result["note"] = f"展開できません（Content-Encoding: {compression}）: {error}"
        return result

    doc = raw.decode(encoding, errors="replace")
    title = TITLE_RE.search(doc)
    result["title"] = _clean(TAG_RE.sub(" ", title.group(1))) if title else ""
    result["meta"] = _meta_description(doc)
    result["body"] = _clean(TAG_RE.sub(" ", DROP_RE.sub(" ", doc)))[:BODY_CHARS]
    result["ok"] = True
    if len(result["body"]) < THIN_BODY_CHARS:
        result["thin"] = True
        result["note"] = (f"本文 {len(result['body'])} 字。"
                          "JS で本文を描画するページの可能性。meta が汎用文なら材料にならない")
    return result


def main(argv) -> int:
    if "--stdin" in argv:
        urls = [line.strip() for line in sys.stdin if line.strip()]
    else:
        urls = [a for a in argv if not a.startswith("--")]
    if not urls:
        print(__doc__.split("使い方:")[1].strip(), file=sys.stderr)
        return 1

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = dict(zip(urls, executor.map(fetch_one, urls)))
    json.dump(results, sys.stdout, ensure_ascii=False, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
