from feed_config import FeedConfig, BROWSER_UA, MetaRule

FEEDS = [
    FeedConfig("gigazine", "全体",
               "https://gigazine.net/news/rss_2.0/", "rss2", 720,
               user_agent=BROWSER_UA,
               meta_rules=[MetaRule("dc:subject", "categories", "categories")]),
]
