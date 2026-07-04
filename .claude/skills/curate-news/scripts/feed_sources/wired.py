from feed_config import FeedConfig, BROWSER_UA, DC_CREATOR, CATEGORIES

# 各記事から著者名(dc:creator)とカテゴリタグ(category)を抽出
_META = [DC_CREATOR, CATEGORIES]

FEEDS = [
    FeedConfig("wired", "AI",
               "https://www.wired.com/feed/tag/ai/latest/rss",
               "rss2", 720, user_agent=BROWSER_UA, meta_rules=_META),
    FeedConfig("wired", "ビジネス",
               "https://www.wired.com/feed/category/business/latest/rss",
               "rss2", 720, user_agent=BROWSER_UA, meta_rules=_META),
]
