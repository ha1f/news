"""フィードの取得・パース・メタ抽出。

XMLベースの3パーサと、それらが使うユーティリティ（HTTP取得、日付変換、
XML前処理、メタ情報抽出）を提供する。

パーサ:
- parse_rss2: RSS 2.0（TechCrunch, Gigazine, Lobsters, Zenn 等）
- parse_rdf: RSS 1.0/RDF（はてな, 日経, Nature, Science）
- parse_atom: Atom（Publickey, Reddit, Product Hunt, The Verge, Qiita）

各パーサは (content: bytes, feed: FeedConfig) -> list[dict] のシグネチャを持つ。
PARSERS辞書で FeedConfig.fmt からパーサ関数にディスパッチする。

ソース固有の取得ロジック（Hacker News等）は feed_sources/*.py に
custom_fetcher として定義する。
"""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from feed_config import NS, JST, FeedConfig, MetaRule


# --- ユーティリティ ---

def fetch_url(url: str, user_agent: str | None = None, timeout: int = 15) -> bytes:
    """URLからコンテンツをバイト列で取得する。

    Args:
        url: 取得対象のURL。
        user_agent: HTTPリクエストのUser-Agentヘッダ。Noneの場合はurllib既定値。
        timeout: タイムアウト秒数。
    """
    headers = {"User-Agent": user_agent} if user_agent else {}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_date(text: str | None) -> str | None:
    """各種日付形式をISO 8601 JSTに統一変換する。

    対応形式: RFC 2822（RSS 2.0のpubDate）、ISO 8601（Atom/RDFのdc:date等）。
    パースできない場合は元のテキストをそのまま返す。
    """
    if not text:
        return None
    text = text.strip()
    # RFC 2822
    try:
        dt = parsedate_to_datetime(text)
        return dt.astimezone(JST).isoformat()
    except Exception:
        pass
    # ISO 8601
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt.astimezone(JST).isoformat()
    except Exception:
        pass
    return text


def strip_utm(url: str) -> str:
    """UTMパラメータを除去する。InfoQのフィードURL用。"""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    cleaned = {k: v for k, v in params.items() if not k.startswith("utm_")}
    new_query = urllib.parse.urlencode(cleaned, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))


# --- XML処理 ---

def _sanitize_xml(content: bytes) -> bytes:
    """不正なXMLを前処理。エスケープされていない & を &amp; に変換する。"""
    text = content.decode("utf-8", errors="replace")
    text = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)
    return text.encode("utf-8")


def _resolve_xpath(xpath: str) -> str:
    """'dc:creator' → '{http://...}creator' のように名前空間プレフィックスを解決する。"""
    for prefix, uri in NS.items():
        xpath = xpath.replace(f"{prefix}:", f"{{{uri}}}")
    return xpath


def extract_meta(element: ET.Element, rules: list[MetaRule]) -> dict:
    """MetaRuleのリストに従ってXML要素からメタ情報を抽出する。

    各パーサ（parse_rss2, parse_rdf, parse_atom）から呼ばれ、
    FeedConfig.meta_rules で定義されたルールを適用する。
    MetaRule.type ごとの抽出ロジックについてはMetaRuleクラスのdocstringを参照。
    """
    meta: dict = {}
    for rule in rules:
        # Atom author特殊処理
        if rule.xpath == "author":
            name_elem = element.find(f"{{{NS['atom']}}}author/{{{NS['atom']}}}name")
            if name_elem is not None and name_elem.text:
                meta[rule.key] = name_elem.text
            continue

        xpath = _resolve_xpath(rule.xpath)

        if rule.type == "text":
            elem = element.find(xpath)
            if elem is not None and elem.text:
                meta[rule.key] = elem.text.strip()

        elif rule.type == "int":
            elem = element.find(xpath)
            if elem is not None and elem.text:
                try:
                    meta[rule.key] = int(elem.text.strip())
                except ValueError:
                    pass

        elif rule.type == "list":
            values = [e.text.strip() for e in element.findall(xpath) if e.text]
            if values:
                meta[rule.key] = values

        elif rule.type == "categories":
            values = []
            for elem in element.findall(xpath):
                if elem.text and elem.text.strip() not in values:
                    values.append(elem.text.strip())
                term = elem.get("term")
                if term and term not in values:
                    values.append(term)
            if values:
                meta[rule.key] = values

        elif rule.type == "attr":
            elem = element.find(xpath)
            if elem is not None and rule.attr:
                val = elem.get(rule.attr)
                if val:
                    meta[rule.key] = val

    return meta


# --- パーサ ---

def parse_rss2(content: bytes, feed: FeedConfig) -> list[dict]:
    """RSS 2.0フィードをパースしてアイテムリストを返す。

    対応ソース: TechCrunch, Ars Technica, Wired, Lobsters, Zenn, Gigazine,
    ITmedia, InfoQ, MIT TR, dev.to, GitHub Trending, Dribbble
    フィールドマッピング: title, link→url, description, pubDate→published_at
    """
    root = ET.fromstring(_sanitize_xml(content))
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        url = item.findtext("link", "").strip()
        desc = item.findtext("description", "")
        published = parse_date(item.findtext("pubDate"))

        if feed.strip_utm and url:
            url = strip_utm(url)

        items.append({
            "title": title, "url": url,
            "description": desc, "published_at": published,
            "meta": extract_meta(item, feed.meta_rules),
        })
    return items


def parse_rdf(content: bytes, feed: FeedConfig) -> list[dict]:
    """RSS 1.0 (RDF) フィードをパースしてアイテムリストを返す。

    対応ソース: はてなブックマーク, 日経, Nature, Science
    名前空間: rss, dc, content, hatena, prism（feed_config.NS で定義）
    フィールドマッピング: rss:title, rss:link→url, rss:description, dc:date→published_at
    descriptionがない場合は content:encoded にfallbackする（Nature等）。
    """
    root = ET.fromstring(_sanitize_xml(content))
    rss_ns = NS["rss"]
    dc_ns = NS["dc"]
    content_ns = NS["content"]
    items = []

    for item in root.findall(f"{{{rss_ns}}}item"):
        title = item.findtext(f"{{{rss_ns}}}title", "").strip()
        url = item.findtext(f"{{{rss_ns}}}link", "").strip()

        desc = item.findtext(f"{{{rss_ns}}}description", "")
        if not desc:
            desc = item.findtext("description", "")
        if not desc:
            desc = item.findtext(f"{{{content_ns}}}encoded", "")

        published = parse_date(item.findtext(f"{{{dc_ns}}}date"))

        items.append({
            "title": title, "url": url,
            "description": desc, "published_at": published,
            "meta": extract_meta(item, feed.meta_rules),
        })
    return items


def parse_atom(content: bytes, feed: FeedConfig) -> list[dict]:
    """Atomフィードをパースしてアイテムリストを返す。

    対応ソース: Publickey, Reddit, Product Hunt, The Verge, Qiita
    フィールドマッピング: title, link[rel=alternate]→url, summary/content→description,
                         published/updated→published_at
    FeedConfig.description_field で description の取得元を制御できる。
    "content"指定時はcontent要素を優先（Reddit, Qiita用）。
    """
    atom = NS["atom"]
    root = ET.fromstring(_sanitize_xml(content))
    items = []

    for entry in root.findall(f"{{{atom}}}entry"):
        title = entry.findtext(f"{{{atom}}}title", "").strip()

        url = ""
        for link in entry.findall(f"{{{atom}}}link"):
            href = link.get("href", "")
            if link.get("rel") == "alternate":
                url = href
                break
            if not url:
                url = href

        desc = ""
        if feed.description_field == "content":
            elem = entry.find(f"{{{atom}}}content")
            if elem is not None:
                desc = elem.text or ""
        if not desc:
            elem = entry.find(f"{{{atom}}}summary")
            if elem is not None:
                desc = elem.text or ""
        if not desc:
            elem = entry.find(f"{{{atom}}}content")
            if elem is not None:
                desc = elem.text or ""

        published = parse_date(
            entry.findtext(f"{{{atom}}}published")
            or entry.findtext(f"{{{atom}}}updated")
        )

        items.append({
            "title": title, "url": url,
            "description": desc, "published_at": published,
            "meta": extract_meta(entry, feed.meta_rules),
        })
    return items


# FeedConfig.fmt からパーサ関数へのディスパッチ辞書。
# FeedConfig.custom_fetcher が設定されている場合はこの辞書を使わずバイパスする。
PARSERS = {
    "rss2": parse_rss2,
    "rdf": parse_rdf,
    "atom": parse_atom,
}
