#!/usr/bin/env python3
"""profiles.py のユニットテスト。実行: python3 test_profiles.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profiles import load_profiles, parse_profiles


def entry(profile_id, **overrides):
    data = {
        "id": profile_id,
        "post_slug": profile_id,
        "name": f"{profile_id} の名前",
        "tagline": f"{profile_id} の一行説明",
        "base": f"/feeds/{profile_id}/",
    }
    data.update(overrides)
    return data


VALID = [entry("owner", post_slug="news", base="/", default=True), entry("commuter")]


class ParseProfilesTest(unittest.TestCase):
    def test_parses_valid_definition(self):
        profiles = parse_profiles(VALID)
        self.assertEqual([p.id for p in profiles], ["owner", "commuter"])
        self.assertTrue(profiles[0].is_default)
        self.assertFalse(profiles[1].is_default)

    def test_paths_follow_profile(self):
        owner, commuter = parse_profiles(VALID)
        self.assertTrue(str(owner.post_path("2026-07-27")).endswith("_posts/2026-07-27-news.md"))
        self.assertTrue(str(owner.output_path("2026-07-27")).endswith("output/2026-07-27-owner.md"))
        self.assertTrue(str(commuter.preferences_path).endswith("profiles/commuter.md"))
        self.assertEqual(commuter.post_glob, "*-commuter.md")

    def test_rejects_missing_key(self):
        with self.assertRaises(ValueError):
            parse_profiles([entry("owner", base="/", default=True), {"id": "x"}])

    def test_rejects_duplicated_id_or_slug(self):
        with self.assertRaises(ValueError):
            parse_profiles([entry("owner", base="/", default=True), entry("owner")])
        with self.assertRaises(ValueError):
            parse_profiles([entry("owner", post_slug="news", base="/", default=True),
                            entry("commuter", post_slug="news")])

    def test_rejects_malformed_base(self):
        with self.assertRaises(ValueError):
            parse_profiles([entry("owner", base="feeds/owner", default=True)])

    def test_requires_exactly_one_default(self):
        with self.assertRaises(ValueError):
            parse_profiles([entry("owner"), entry("commuter")])
        with self.assertRaises(ValueError):
            parse_profiles([entry("owner", default=True), entry("commuter", default=True)])

    def test_rejects_empty_definition(self):
        with self.assertRaises(ValueError):
            parse_profiles([])


class RepositoryProfilesTest(unittest.TestCase):
    """リポジトリ同梱の _data/profiles.json 自体の健全性"""

    def test_definition_is_valid_and_default_comes_first(self):
        profiles = load_profiles()
        self.assertTrue(profiles[0].is_default)

    def test_every_profile_has_preferences(self):
        for profile in load_profiles():
            with self.subTest(profile=profile.id):
                self.assertTrue(profile.preferences_path.exists(),
                                f"{profile.preferences_path} が無い")


if __name__ == "__main__":
    unittest.main()
