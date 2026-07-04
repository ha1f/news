from feed_config import FeedConfig, DC_CREATOR_LIST, MetaRule, register_ns

register_ns("prism", "http://prismstandard.org/namespaces/basic/2.0/")

FEEDS = [
    FeedConfig("science", "Science本誌",
               "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
               "rdf", 1440,
               meta_rules=[
                   DC_CREATOR_LIST,
                   MetaRule("dc:type", "article_type"),
                   MetaRule("prism:doi", "doi"),
                   MetaRule("prism:publicationName", "journal"),
               ]),
]
