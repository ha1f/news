#!/usr/bin/env python3
"""check_source_hints.py のユニットテスト"""
import tempfile
import unittest
from pathlib import Path

import io
import os
from contextlib import redirect_stdout

from check_source_hints import (expected_text, is_japanese_locale, items_of,
                                link_languages, malformed_lines_of, resolve,
                                source_tables)

FRONT_MATTER = "---\nlayout: post\ntitle: \"test\"\ndate: 2026-09-19\n---\n"

BY_NAME = {
    "はてブ": [],
    "HN": ["英語"],
    "日経": ["会員限定"],
    "Nature": ["英語", "一部会員限定"],
    "TechCrunch": ["英語"],
}
BY_DOMAIN = {
    "b.hatena.ne.jp": ([], "はてブ"),
    "nikkei.com": (["会員限定"], "日経"),
    "nature.com": (["英語", "一部会員限定"], "Nature"),
    "techcrunch.com": (["英語"], "TechCrunch"),
}
# ソース定義の無いサイトの言語の一覧 (#708)
BY_LINK = {
    "anthropic.com": ["英語"],
    "claude.com": ["英語"],
    "github.blog": ["英語"],
}


def write_post(body: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(FRONT_MATTER + body)
    tmp.close()
    return Path(tmp.name)


class TestItemsOf(unittest.TestCase):
    def test_label_present(self):
        post = write_post(
            "1. [見出し](https://techcrunch.com/a) (TechCrunch・英語)<br>\n"
            "   読みどころ\n")
        self.assertEqual(
            list(items_of(post)),
            [("見出し", "https://techcrunch.com/a", "TechCrunch・英語")])

    def test_missing_label_is_reported_not_skipped(self):
        # ラベルを必須にした正規表現だと、この行は検査から静かに消える。
        # 「ソース表記が丸ごと無い」のは一番捕まえたいケースなので None で返す
        post = write_post("1. [見出し](https://techcrunch.com/a)<br>\n")
        self.assertEqual(
            list(items_of(post)),
            [("見出し", "https://techcrunch.com/a", None)])

    def test_label_after_url_with_parenthesis(self):
        # URL に ")" を含む項目でも、末尾のラベルは取れる
        post = write_post(
            "1. [見出し](https://en.wikipedia.org/wiki/Wax_(disambiguation)) "
            "(はてブ)<br>\n")
        titles = [(t, label) for t, _, label in items_of(post)]
        self.assertEqual(titles, [("見出し", "はてブ")])

    def test_item_without_br(self):
        post = write_post("1. [見出し](https://a.example) (はてブ)\n")
        self.assertEqual(
            list(items_of(post)), [("見出し", "https://a.example", "はてブ")])


class TestMalformedLinesOf(unittest.TestCase):
    def test_bold_link_warns(self):
        post = write_post("1. **[見出し](https://a.example)** (はてブ)<br>\n")
        self.assertEqual(
            list(malformed_lines_of(post)),
            ["1. **[見出し](https://a.example)** (はてブ)<br>"])

    def test_well_formed_item_does_not_warn(self):
        post = write_post("1. [見出し](https://a.example) (はてブ)<br>\n")
        self.assertEqual(list(malformed_lines_of(post)), [])

    def test_prose_line_does_not_warn(self):
        post = write_post("今日は良い天気です。\n")
        self.assertEqual(list(malformed_lines_of(post)), [])


class TestResolve(unittest.TestCase):
    def test_own_domain_matches_own_labels(self):
        self.assertEqual(
            resolve("https://techcrunch.com/a", "TechCrunch", BY_NAME, BY_DOMAIN),
            ["英語"])

    def test_www_prefix_is_ignored(self):
        self.assertEqual(
            resolve("https://www.nikkei.com/a", "日経", BY_NAME, BY_DOMAIN),
            ["会員限定"])

    def test_aggregator_takes_link_target_labels(self):
        # はてブ経由でも、リンク先が日経なら会員限定を出す（#327 の本体）
        self.assertEqual(
            resolve("https://www.nikkei.com/article/X/", "はてブ",
                    BY_NAME, BY_DOMAIN),
            ["会員限定"])

    def test_unknown_domain_falls_back_to_source(self):
        self.assertEqual(
            resolve("https://example.com/a", "はてブ", BY_NAME, BY_DOMAIN), [])

    def test_subdomain_matches(self):
        self.assertEqual(
            resolve("https://blogs.nature.com/a", "はてブ", BY_NAME, BY_DOMAIN),
            ["英語", "一部会員限定"])


class TestResolveLinkLanguages(unittest.TestCase):
    """ソース定義の無い英語サイトに、はてブ経由でも「英語」を付ける (#708)"""

    def hatena(self, url):
        return resolve(url, "はてブ", BY_NAME, BY_DOMAIN, BY_LINK)

    def test_listed_site_gets_its_language(self):
        self.assertEqual(
            self.hatena("https://www.anthropic.com/research/migrating-api-to-rust"),
            ["英語"])
        self.assertEqual(
            self.hatena("https://github.blog/changelog/2026-10-21-x/"), ["英語"])

    def test_subdomain_of_listed_site(self):
        self.assertEqual(
            self.hatena("https://support.claude.com/en/articles/1"), ["英語"])

    def test_japanese_locale_path_is_not_english(self):
        for url in (
            "https://claude.com/ja/resources/articles/the-ai-native-sdlc-playbook",
            "https://platform.claude.com/docs/ja/build-with-claude/x",
            "https://support.claude.com/ja-jp/articles/1",
            "https://www.anthropic.com/jp",
            "https://claude.com/docs?hl=ja",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.hatena(url), [])

    def test_japanese_page_via_english_aggregator(self):
        # HN（英語が既定）経由でも、一覧のサイトの日本語版には「英語」を付けない
        self.assertEqual(
            resolve("https://claude.com/ja/resources/x", "HN", BY_NAME, BY_DOMAIN, BY_LINK),
            [])
        self.assertEqual(
            resolve("https://claude.com/resources/x", "HN", BY_NAME, BY_DOMAIN, BY_LINK),
            ["英語"])

    def test_locale_only_counts_as_whole_segment(self):
        # /japan/ や /jazz/ は日本語版の印ではない
        self.assertEqual(self.hatena("https://www.anthropic.com/japan/news"), ["英語"])
        self.assertEqual(self.hatena("https://claude.com/blog/jazz"), ["英語"])

    def test_unlisted_site_falls_back_to_aggregator(self):
        self.assertEqual(self.hatena("https://example.com/a"), [])
        self.assertEqual(self.hatena("https://notanthropic.com/a"), [])

    def test_source_domain_wins_over_list(self):
        by_link = dict(BY_LINK, **{"nikkei.com": ["英語"]})
        self.assertEqual(
            resolve("https://www.nikkei.com/a", "はてブ", BY_NAME, BY_DOMAIN, by_link),
            ["会員限定"])

    def test_without_list_keeps_old_behaviour(self):
        self.assertEqual(
            resolve("https://www.anthropic.com/a", "はてブ", BY_NAME, BY_DOMAIN), [])


class TestIsJapaneseLocale(unittest.TestCase):
    def test_query_variants(self):
        self.assertTrue(is_japanese_locale("https://a.com/x?hl=ja"))
        self.assertTrue(is_japanese_locale("https://a.com/x?lang=ja_JP"))
        self.assertTrue(is_japanese_locale("https://a.com/x?locale=ja-JP"))
        self.assertFalse(is_japanese_locale("https://a.com/x?hl=en"))
        self.assertFalse(is_japanese_locale("https://a.com/x?q=ja"))

    def test_path(self):
        self.assertTrue(is_japanese_locale("https://www.apple.com/jp/newsroom/x"))
        self.assertTrue(is_japanese_locale("https://about.gitlab.com/ja-jp/blog/x"))
        self.assertFalse(is_japanese_locale("https://a.com/en/x"))


class TestLinkLanguages(unittest.TestCase):
    def load(self, text):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8")
        tmp.write(text)
        tmp.close()
        self.addCleanup(os.unlink, tmp.name)
        out = io.StringIO()
        with redirect_stdout(out):
            table = link_languages(BY_DOMAIN, Path(tmp.name))
        return table, out.getvalue()

    def rows(self, *rows):
        # 説明の箇条書きは「## 一覧」より前に置く（実物と同じ形）
        return self.load("# x\n\n- 行の形は `` - `{ドメイン}`: {言語} ``。\n\n## 一覧\n\n"
                         + "".join(r + "\n" for r in rows))

    def test_parses_rows(self):
        table, _ = self.rows("- `anthropic.com`: 英語", "- `example.jp`: 日本語")
        self.assertEqual(table, {"anthropic.com": ["英語"], "example.jp": []})

    def test_explanation_before_section_is_not_an_entry(self):
        table, _ = self.rows("- `anthropic.com`: 英語")
        self.assertEqual(table, {"anthropic.com": ["英語"]})

    def test_malformed_row_is_an_error_not_skipped(self):
        for row in ("- `openai.com`: 英語（2026-11 確認）",
                    "- `openai.com`: 英語 # memo",
                    "- openai.com: 英語"):
            with self.subTest(row=row):
                table, out = self.rows("- `anthropic.com`: 英語", row)
                self.assertIsNone(table)
                self.assertIn("形の崩れた行", out)

    def test_unknown_language_is_an_error(self):
        table, out = self.rows("- `anthropic.com`: English")
        self.assertIsNone(table)
        self.assertIn("English", out)

    def test_rejects_source_domain(self):
        table, out = self.rows("- `nikkei.com`: 英語")
        self.assertIsNone(table)
        self.assertIn("nikkei.com", out)

    def test_rejects_subdomain_of_source_domain(self):
        self.assertIsNone(self.rows("- `asia.nikkei.com`: 英語")[0])

    def test_rejects_www_and_path(self):
        self.assertIsNone(self.rows("- `www.anthropic.com`: 英語")[0])
        self.assertIsNone(self.rows("- `claude.com/ja`: 日本語")[0])

    def test_empty_list_is_an_error(self):
        self.assertIsNone(self.rows()[0])

    def test_missing_section_is_an_error(self):
        self.assertIsNone(self.load("- `anthropic.com`: 英語\n")[0])

    def test_missing_file_is_an_error(self):
        with redirect_stdout(io.StringIO()):
            self.assertIsNone(link_languages(BY_DOMAIN, Path("/nonexistent/x.md")))


class TestRepositoryLinkLanguages(unittest.TestCase):
    """repo の一覧そのものが issue の URL を正しく判定する (#708)"""

    def setUp(self):
        root = Path(__file__).resolve().parents[2]
        cwd = os.getcwd()
        os.chdir(root)
        self.addCleanup(os.chdir, cwd)
        with redirect_stdout(io.StringIO()):
            self.by_name, self.by_domain = source_tables()
            self.by_link = link_languages(self.by_domain)
        self.assertIsNotNone(self.by_link)

    def test_issue_urls(self):
        cases = {
            "https://www.anthropic.com/research/migrating-api-to-rust": ["英語"],
            "https://claude.com/resources/articles/building-always-on-agents": ["英語"],
            "https://github.blog/changelog/2026-10-21-github-cli-x/": ["英語"],
            "https://claude.com/ja/resources/articles/the-ai-native-sdlc-playbook": [],
            "https://www.apple.com/jp/newsroom/2026/10/x/": [],
            # ソース定義のあるサイトは従来どおり
            "https://github.com/a/b": ["英語"],
        }
        for url, want in cases.items():
            with self.subTest(url=url):
                self.assertEqual(
                    resolve(url, "はてブ", self.by_name, self.by_domain, self.by_link),
                    want)


class TestMainUsesLinkLanguages(unittest.TestCase):
    """スクリプトとして走らせたときに一覧が効いている（出力そのものを見る）"""

    def run_on(self, label):
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[2]
        post = write_post(
            "1. [Anthropic、API を Rust へ移行]"
            f"(https://www.anthropic.com/research/migrating-api-to-rust) ({label})<br>\n"
            "1. [日本語版](https://claude.com/ja/resources/articles/x) (はてブ)<br>\n")
        self.addCleanup(os.unlink, post)
        return subprocess.run(
            [sys.executable, "-B", str(root / ".claude/scripts/check_source_hints.py"), str(post)],
            cwd=root, capture_output=True, text=True)

    def test_hatena_without_english_is_reported(self):
        r = self.run_on("はてブ")
        self.assertEqual(r.returncode, 1)
        self.assertIn("あるべき「はてブ・英語」", r.stdout)
        self.assertIn("不一致 1 件", r.stdout)

    def test_hatena_with_english_passes(self):
        r = self.run_on("はてブ・英語")
        self.assertEqual(r.returncode, 0, r.stdout)


class TestExpectedText(unittest.TestCase):
    def test_no_labels(self):
        self.assertEqual(expected_text("Publickey", []), "Publickey")

    def test_single_label(self):
        self.assertEqual(expected_text("TechCrunch", ["英語"]), "TechCrunch・英語")

    def test_two_labels_joined_with_slash(self):
        self.assertEqual(
            expected_text("Nature", ["英語", "一部会員限定"]),
            "Nature・英語/一部会員限定")


if __name__ == "__main__":
    unittest.main()
