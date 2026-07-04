from feed_config import FeedConfig, BROWSER_UA

FEEDS = [
    FeedConfig("producthunt", "全体",
               "https://www.producthunt.com/feed", "atom", 720,
               user_agent=BROWSER_UA),
]
