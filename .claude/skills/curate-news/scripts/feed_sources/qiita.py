from feed_config import FeedConfig

FEEDS = [
    FeedConfig("qiita", "人気記事",
               "https://qiita.com/popular-items/feed", "atom", 720,
               description_field="content"),
    FeedConfig("qiita", "Swift",
               "https://qiita.com/tags/swift/feed", "atom", 720,
               description_field="content"),
    FeedConfig("qiita", "LLM",
               "https://qiita.com/tags/llm/feed", "atom", 720,
               description_field="content"),
]
