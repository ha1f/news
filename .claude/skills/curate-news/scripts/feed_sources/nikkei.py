from feed_config import FeedConfig, BROWSER_UA

FEEDS = [
    FeedConfig("nikkei", "速報",
               "https://assets.wor.jp/rss/rdf/nikkei/news.rdf", "rdf", 720,
               user_agent=BROWSER_UA),
]
