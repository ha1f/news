from feed_config import FeedConfig, DC_CREATOR, CATEGORIES

# 各記事から著者名(dc:creator)とカテゴリタグ(category)を抽出
_META = [DC_CREATOR, CATEGORIES]

FEEDS = [
    FeedConfig("techcrunch", "AI",
               "https://techcrunch.com/category/artificial-intelligence/feed/",
               "rss2", 720, meta_rules=_META),
    FeedConfig("techcrunch", "Apps",
               "https://techcrunch.com/category/apps/feed/",
               "rss2", 720, meta_rules=_META),
    FeedConfig("techcrunch", "全体",
               "https://techcrunch.com/feed/",
               "rss2", 720, meta_rules=_META),
]
