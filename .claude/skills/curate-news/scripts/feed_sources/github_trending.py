from feed_config import FeedConfig, MetaRule, register_ns

register_ns("media", "http://search.yahoo.com/mrss/")

# Media RSS拡張のcontent要素からリポジトリのOGP画像URLを抽出
_IMAGE = MetaRule("media:content", "image_url", "attr", "url")

FEEDS = [
    FeedConfig("github-trending", "日次・全言語",
               "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml",
               "rss2", 1440, meta_rules=[_IMAGE]),
    FeedConfig("github-trending", "日次・Swift",
               "https://mshibanami.github.io/GitHubTrendingRSS/daily/swift.xml",
               "rss2", 1440, meta_rules=[_IMAGE]),
]
