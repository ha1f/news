from feed_config import FeedConfig, MetaRule, register_ns

register_ns("hatena", "http://www.hatena.ne.jp/info/xmlns#")

# はてなブックマーク数を整数で抽出
_BOOKMARKS = MetaRule("hatena:bookmarkcount", "bookmarks", "int")

FEEDS = [
    FeedConfig("hatena", "テクノロジー",
               "https://b.hatena.ne.jp/hotentry/it.rss", "rdf", 720,
               meta_rules=[_BOOKMARKS]),
    FeedConfig("hatena", "政治経済",
               "https://b.hatena.ne.jp/hotentry/economics.rss", "rdf", 720,
               meta_rules=[_BOOKMARKS]),
    FeedConfig("hatena", "総合",
               "https://b.hatena.ne.jp/hotentry.rss", "rdf", 720,
               meta_rules=[_BOOKMARKS]),
]
