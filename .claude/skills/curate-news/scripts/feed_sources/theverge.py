from feed_config import FeedConfig, BROWSER_UA, MetaRule

# Atom category要素からカテゴリタグを抽出
_CATEGORIES = MetaRule("category", "categories", "categories")

FEEDS = [
    FeedConfig("theverge", "テック",
               "https://www.theverge.com/rss/tech/index.xml", "atom", 720,
               user_agent=BROWSER_UA, meta_rules=[_CATEGORIES]),
    FeedConfig("theverge", "全体",
               "https://www.theverge.com/rss/index.xml", "atom", 720,
               user_agent=BROWSER_UA, meta_rules=[_CATEGORIES]),
]
