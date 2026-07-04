from feed_config import FeedConfig, BROWSER_UA, DC_CREATOR, CATEGORIES

FEEDS = [
    FeedConfig("devto", "AI",
               "https://dev.to/feed/tag/ai", "rss2", 720,
               user_agent=BROWSER_UA,
               meta_rules=[DC_CREATOR, CATEGORIES]),
]
