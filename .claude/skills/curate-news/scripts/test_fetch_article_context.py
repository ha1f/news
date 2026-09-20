import unittest
import urllib.robotparser

import fetch_article_context as mod


def _parser(text):
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(text.splitlines())
    return parser


class RobotsAllowsTest(unittest.TestCase):
    """robots.txt の照合が製品トークン（ha1f-news）で行われること（週次 audit 2026-09-20）"""

    def setUp(self):
        mod._ROBOTS_CACHE.clear()

    def tearDown(self):
        mod._ROBOTS_CACHE.clear()

    def test_named_disallow_is_respected(self):
        mod._ROBOTS_CACHE["https://example.com/robots.txt"] = _parser(
            "User-agent: ha1f-news\nDisallow: /\n\nUser-agent: *\nAllow: /\n")
        self.assertFalse(mod._robots_allows("https://example.com/article"))

    def test_wildcard_disallow_is_respected(self):
        mod._ROBOTS_CACHE["https://example.com/robots.txt"] = _parser(
            "User-agent: *\nDisallow: /private/\n")
        self.assertFalse(mod._robots_allows("https://example.com/private/x"))
        self.assertTrue(mod._robots_allows("https://example.com/article"))

    def test_ai_crawler_names_do_not_match_this_token(self):
        # 他社 AI クローラの名指し拒否は、このトークンには字義どおり及ばない（方針判断は #241）
        mod._ROBOTS_CACHE["https://example.com/robots.txt"] = _parser(
            "User-agent: ClaudeBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n")
        self.assertTrue(mod._robots_allows("https://example.com/article"))

    def test_token_matches_user_agent_product_name(self):
        self.assertIn(mod.ROBOTS_TOKEN + "/", mod.USER_AGENT)


if __name__ == "__main__":
    unittest.main()
