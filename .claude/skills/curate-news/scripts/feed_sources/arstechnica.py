from feed_config import FeedConfig, DC_CREATOR, SLASH_COMMENTS, register_ns

register_ns("slash", "http://purl.org/rss/1.0/modules/slash/")

# 各記事から著者名(dc:creator)とコメント数(slash:comments)を抽出
_META = [DC_CREATOR, SLASH_COMMENTS]

FEEDS = [
    FeedConfig("arstechnica", "AI",
               "https://arstechnica.com/ai/feed/",
               "rss2", 720, meta_rules=_META),
    FeedConfig("arstechnica", "全体",
               "https://arstechnica.com/feed/",
               "rss2", 720, meta_rules=_META),
]
