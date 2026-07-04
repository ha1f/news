from feed_config import FeedConfig, MetaRule

FEEDS = [
    FeedConfig("publickey", "全体",
               "https://www.publickey1.jp/atom.xml", "atom", 720,
               meta_rules=[MetaRule("author", "author")]),
]
