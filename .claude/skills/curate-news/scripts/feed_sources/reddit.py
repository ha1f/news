from feed_config import FeedConfig, BROWSER_UA

FEEDS = [
    FeedConfig("reddit", "swift",
               "https://www.reddit.com/r/swift/hot/.rss",
               "atom", 720, user_agent=BROWSER_UA,
               description_field="content"),
    FeedConfig("reddit", "MachineLearning",
               "https://www.reddit.com/r/MachineLearning/hot/.rss",
               "atom", 720, user_agent=BROWSER_UA,
               description_field="content"),
    FeedConfig("reddit", "programming",
               "https://www.reddit.com/r/programming/hot/.rss",
               "atom", 720, user_agent=BROWSER_UA,
               description_field="content"),
]
