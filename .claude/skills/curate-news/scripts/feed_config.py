"""フィード定義のデータモデル。

FeedConfig と MetaRule のデータクラス、共通MetaRuleインスタンス、
ソース固有の名前空間登録機構を提供する。
feed_sources/*.py はここからデータクラスをimportして宣言的に定義する。
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timezone, timedelta

# --- 定数 ---

JST = timezone(timedelta(hours=9))
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# scripts/ の親ディレクトリ（スキルルート）基準
_SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(_SKILL_ROOT, "cache")

# XML名前空間（パーサが直接使う共通名前空間のみ）
# ソース固有の名前空間は各 feed_sources/*.py から register_ns() で登録する。
NS = {
    "rss": "http://purl.org/rss/1.0/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def register_ns(prefix: str, uri: str) -> None:
    """ソース固有のXML名前空間を登録する。

    feed_sources/*.py のモジュールトップレベルで呼び出す。
    登録した名前空間は MetaRule の xpath 解決（extract_meta）で使われる。
    """
    NS[prefix] = uri


# --- データクラス ---

@dataclass
class MetaRule:
    """XML要素からmeta情報を抽出するルール。

    FeedConfigのmeta_rulesに指定し、extract_meta()で使われる。

    Attributes:
        xpath: 抽出対象のXPath。名前空間プレフィックス付き（例: "dc:creator", "hatena:bookmarkcount"）。
               "author" はAtomのauthor/name要素の特殊処理にマッピングされる。
        key: キャッシュJSONの meta オブジェクト内のキー名（例: "bookmarks", "author"）。
        type: 抽出方法。
              - "text": 単一要素のテキスト（デフォルト）
              - "int": テキストを整数に変換
              - "list": 同名の複数要素をリストに集約
              - "categories": RSS category要素のテキストとAtom category要素のterm属性を収集
              - "attr": 要素の属性値を取得（attrフィールドで属性名を指定）
        attr: type="attr"のとき、取得する属性名（例: "url"）。
    """
    xpath: str
    key: str
    type: str = "text"
    attr: str = ""


@dataclass
class FeedConfig:
    """1フィードの取得定義。feed_sources/*.py で宣言的に定義する。

    Attributes:
        source_id: ソースの一意識別子（例: "hatena", "hackernews"）。
                   references/sources/{source_id}.md と対応する。
        category: フィードのカテゴリ名（例: "テクノロジー", "AI"）。
                  1ソースが複数カテゴリを持てる。
        feed_url: フィードのURL。
        fmt: フィード形式。パーサの選択に使う。
             "rss2" | "rdf" | "atom" | "custom"
        ttl_minutes: キャッシュの有効期間（分）。ソース定義のTTLに合わせる。
        user_agent: HTTPリクエスト時のUser-Agentヘッダ。
                    bot制限があるソース（Gigazine, Reddit等）で設定する。
        meta_rules: キャッシュJSONのmetaフィールドに抽出する追加情報のルール。
        strip_utm: Trueの場合、記事URLからUTMパラメータを除去する（InfoQ用）。
        description_field: Atomフィードでdescriptionに使う要素名。
                           "content"を指定するとcontent要素を優先する（Reddit, Qiita用）。
                           空文字（デフォルト）はsummary→contentの順でfallback。
        custom_fetcher: ソース固有の取得関数。設定されている場合、標準のfetch_url+パーサの
                        フローを完全にバイパスし、この関数がHTTP取得からアイテム構築まで
                        すべてを行う。シグネチャ: (FeedConfig) -> list[dict]。
                        Hacker News のように標準のXMLパーサでは対応できないソースで使う。
    """
    source_id: str
    category: str
    feed_url: str
    fmt: str
    ttl_minutes: int
    user_agent: str | None = None
    meta_rules: list[MetaRule] = field(default_factory=list)
    strip_utm: bool = False
    description_field: str = ""
    custom_fetcher: Callable[["FeedConfig"], list[dict]] | None = None

    @property
    def cache_key(self) -> str:
        """キャッシュファイル名のベース。"{source_id}-{category}" 形式。"""
        return f"{self.source_id}-{self.category.replace('/', '-')}"

    @property
    def cache_path(self) -> str:
        """キャッシュファイルの絶対パス。"""
        return os.path.join(CACHE_DIR, f"{self.cache_key}.json")


# --- よく使うMetaRuleインスタンス ---
# ソース定義（feed_sources/*.py）から共有して使う。

DC_CREATOR = MetaRule("dc:creator", "author")
"""Dublin Core の著者名（単一）。TechCrunch, Zenn 等で使用。"""

DC_CREATOR_LIST = MetaRule("dc:creator", "authors", "list")
"""Dublin Core の著者名（複数）。Nature, Science 等、複数著者があるソースで使用。"""

CATEGORIES = MetaRule("category", "categories", "categories")
"""RSS/Atom のカテゴリ要素。テキストとterm属性の両方を収集する。"""
