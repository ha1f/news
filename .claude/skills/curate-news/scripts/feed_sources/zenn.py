from feed_config import FeedConfig, DC_CREATOR

FEEDS = [
    FeedConfig("zenn", "Swift",
               "https://zenn.dev/topics/swift/feed", "rss2", 1440,
               meta_rules=[DC_CREATOR]),
    FeedConfig("zenn", "AI/機械学習",
               "https://zenn.dev/topics/machinelearning/feed", "rss2", 1440,
               meta_rules=[DC_CREATOR]),
    FeedConfig("zenn", "トレンド（全体）",
               "https://zenn.dev/feed", "rss2", 1440,
               meta_rules=[DC_CREATOR]),
]
