from feed_config import FeedConfig, BROWSER_UA, CATEGORIES

FEEDS = [
    FeedConfig("dribbble", "Stories",
               "https://dribbble.com/stories.rss", "rss2", 1440,
               user_agent=BROWSER_UA,
               meta_rules=[CATEGORIES]),
]
