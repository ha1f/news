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
  - ok=false は取得できなかったもの（ネットワーク・HTTP エラー・robots.txt の拒否）。
    1 URL の失敗が他の URL の結果を巻き込むことはない
  - thin=true は本文がほとんど取れなかったページ（JS で描画する SPA 等）

フィードでなく記事ページ本体を取りに行くため、robots.txt を見て取得可否を決める。
ソースが AI クローラを拒否しているかどうかの方針判断は #241（オーナー判断）にある。

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
import urllib.parse
import urllib.request
import urllib.robotparser
import zlib
from concurrent.futures import ThreadPoolExecutor

USER_AGENT = "Mozilla/5.0 (compatible; ha1f-news/1.0; +https://ha1f.github.io/news/)"
# robots.txt の照合に使う製品トークン。RobotFileParser.can_fetch は "/" より前の先頭トークンで
# User-agent 行を選ぶため、USER_AGENT 全文を渡すと "Mozilla" として評価され、ha1f-news を
# 名指しで拒否する記述が効かない（週次 audit 2026-09-20 で実測）。USER_AGENT 内の名前と揃える
ROBOTS_TOKEN = "ha1f-news"
# 明示しないと CDN が brotli を返してくることがあり、そのまま読むと文字化けする。
# 展開できる形式だけを要求する
ACCEPT_ENCODING = "gzip, deflate, identity"
# PDF や巨大ページを丸ごとメモリに載せないための上限
MAX_BYTES = 4 * 1024 * 1024
TIMEOUT = 15
_ROBOTS_CACHE: dict = {}
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
CHARSET_RE = re.compile(rb"""(?i)<meta[^>]+charset\s*=\s*["']?([\w-]+)""")


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


def _decompress(raw: bytes, compression: str) -> bytes:
    """Content-Encoding に従って展開する。未知の形式は例外にする。

    展開できない形式を素通りさせると、文字化けした本文が ok で返り、
    「材料が取れた」と誤って扱われる。
    """
    if compression in ("", "identity"):
        return raw
    if compression == "gzip":
        return gzip.decompress(raw)
    if compression == "deflate":
        try:  # zlib ラップ形式（実サーバはこちらが多い）
            return zlib.decompress(raw)
        except zlib.error:  # raw deflate
            return zlib.decompress(raw, -zlib.MAX_WBITS)
    raise ValueError(f"未対応の Content-Encoding: {compression}")


def _charset(doc_bytes: bytes, header_charset: str | None) -> str:
    if header_charset:
        return header_charset
    found = CHARSET_RE.search(doc_bytes[:4096])
    return found.group(1).decode("ascii", "replace") if found else "utf-8"


def _fetch_robots(robots_url: str):
    """robots.txt を取得してパーサを返す。読めなければ None（＝許可扱い）。

    `RobotFileParser.read()` は urllib 既定の UA (`Python-urllib/3.x`) で
    取得するため、多くの CDN が 403 を返し、robotparser がそれを
    disallow_all に変換してしまう（許可しているサイトまで拒否になる）。
    必ずスクリプト自身の UA で robots.txt を取り、401/403 だけを
    明示的な拒否の意思表示として扱う（それ以外は「読めなかっただけ」）。
    """
    request = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            deny_all = urllib.robotparser.RobotFileParser()
            deny_all.parse(["User-agent: *", "Disallow: /"])
            return deny_all
        return None
    except Exception:
        return None
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(body.splitlines())
    return parser


def _robots_allows(url: str) -> bool:
    """robots.txt がこのクローラ（製品トークン ROBOTS_TOKEN）の取得を許しているか。

    フィードでなく記事ページ本体を取りに行くため、ソース側の意思表示に従う。
    名指しの拒否（User-agent: ha1f-news）と `*` の両方が効くよう、製品トークンで照合する。
    """
    parts = urllib.parse.urlsplit(url)
    robots_url = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, "/robots.txt", "", ""))
    if robots_url not in _ROBOTS_CACHE:
        _ROBOTS_CACHE[robots_url] = _fetch_robots(robots_url)
    parser = _ROBOTS_CACHE[robots_url]
    if parser is None:
        return True
    return parser.can_fetch(ROBOTS_TOKEN, url)


def fetch_one(url: str) -> dict:
    result = {"ok": False, "thin": False, "title": "", "meta": "", "body": "",
              "note": ""}
    try:
        if not _robots_allows(url):
            result["note"] = "robots.txt がこの User-Agent の取得を許可していません"
            return result

        request = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT, "Accept-Encoding": ACCEPT_ENCODING})
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read(MAX_BYTES)
            header_charset = response.headers.get_content_charset()
            compression = (response.headers.get("Content-Encoding") or "").lower()

        raw = _decompress(raw, compression)
        doc = raw.decode(_charset(raw, header_charset), errors="replace")
    except LookupError as error:  # 未知の charset 名
        result["note"] = f"文字コードを解釈できません: {error}"
        return result
    except Exception as error:
        # 1 URL の失敗でバッチ全体を落とさない（docstring の契約）
        result["note"] = f"取得できません: {type(error).__name__} {error}"
        return result

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
