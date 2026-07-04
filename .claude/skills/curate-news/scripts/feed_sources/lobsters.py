from feed_config import FeedConfig

FEEDS = [
    FeedConfig("lobsters", "Swift",
               "https://lobste.rs/t/swift.rss", "rss2", 720),
    FeedConfig("lobsters", "AI",
               "https://lobste.rs/t/ai.rss", "rss2", 720),
    FeedConfig("lobsters", "全体",
               "https://lobste.rs/rss", "rss2", 720),
]
