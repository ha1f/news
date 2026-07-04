from feed_config import FeedConfig, DC_CREATOR, CATEGORIES

# 各記事から著者名(dc:creator)とカテゴリタグ(category)を抽出
_META = [DC_CREATOR, CATEGORIES]

FEEDS = [
    FeedConfig("infoq", "Architecture",
               "https://feed.infoq.com/architecture-design/",
               "rss2", 720, strip_utm=True, meta_rules=_META),
    FeedConfig("infoq", "AI/ML",
               "https://feed.infoq.com/ai-ml-data-eng/",
               "rss2", 720, strip_utm=True, meta_rules=_META),
]
