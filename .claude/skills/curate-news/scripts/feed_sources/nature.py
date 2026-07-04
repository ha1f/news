from feed_config import FeedConfig, DC_CREATOR_LIST, MetaRule, register_ns

register_ns("prism", "http://prismstandard.org/namespaces/basic/2.0/")

FEEDS = [
    FeedConfig("nature", "Nature Machine Intelligence",
               "https://www.nature.com/natmachintell.rss", "rdf", 1440,
               meta_rules=[
                   DC_CREATOR_LIST,
                   MetaRule("prism:doi", "doi"),
                   MetaRule("prism:publicationName", "journal"),
               ]),
]
