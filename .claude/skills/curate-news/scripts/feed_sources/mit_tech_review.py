from feed_config import FeedConfig, DC_CREATOR, CATEGORIES

FEEDS = [
    FeedConfig("mit-tech-review", "全体",
               "https://www.technologyreview.com/feed/",
               "rss2", 720, meta_rules=[DC_CREATOR, CATEGORIES]),
]
