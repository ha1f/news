#!/usr/bin/env python3
"""detect_tells.py の純関数のユニットテストと CLI の結合テスト。実行: python3 -m unittest test_detect_tells"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from detect_tells import (MAX_HITS_PER_ID, compare, detect, detect_lang,  # noqa: E402
                          load_lexicon, metrics, parse_lexicon,
                          repeated_phrases)

SCRIPT = Path(__file__).resolve().parent / "detect_tells.py"
REFS = Path(__file__).resolve().parent.parent / "references"

COMMON_MD = """# 共通

```lexicon prose
em-dash: —
```
"""

EN_MD = """# English

説明の段落。

### en-rather-than: rather than の対比

- 種別: JUDGMENT

```lexicon
delve: \\bdelv(?:e|es|ed|ing)\\b
not-just-but: \\bnot (?:just|only) [^,.;]{1,40},? but\\b
```
"""

JA_MD = """# 日本語

```lexicon
silently-break: 静かに壊れ
```
"""


def write_refs(files: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    for name, text in files.items():
        (d / name).write_text(text, encoding="utf-8")
    return d


def write_text(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as f:
        f.write(text)
    return f.name


class TestParseLexicon(unittest.TestCase):
    def test_reads_id_pattern_and_scope(self):
        self.assertEqual(
            parse_lexicon(EN_MD),
            [("delve", r"\bdelv(?:e|es|ed|ing)\b", "all"),
             ("not-just-but", r"\bnot (?:just|only) [^,.;]{1,40},? but\b",
              "all")])

    def test_prose_block_has_prose_scope(self):
        self.assertEqual(parse_lexicon(COMMON_MD), [("em-dash", "—", "prose")])

    def test_ignores_comments_blank_lines_and_other_blocks(self):
        md = "```python\nx: y\n```\n\n```lexicon\n\n# c\na: b\n```\n"
        self.assertEqual(parse_lexicon(md), [("a", "b", "all")])

    def test_collects_every_lexicon_block(self):
        md = "```lexicon\na: 1\n```\ntext\n```lexicon prose\nb: 2\n```\n"
        self.assertEqual(parse_lexicon(md), [("a", "1", "all"),
                                             ("b", "2", "prose")])

    def test_line_without_separator_is_an_error_showing_the_line(self):
        with self.assertRaisesRegex(ValueError, "no-separator"):
            parse_lexicon("```lexicon\nno-separator\n```\n")

    def test_pattern_may_contain_colon(self):
        self.assertEqual(parse_lexicon("```lexicon\ncolon: \\w: \\w\n```\n"),
                         [("colon", r"\w: \w", "all")])


class TestLoadLexicon(unittest.TestCase):
    def test_merges_common_and_language_file(self):
        refs = write_refs({"common.md": COMMON_MD, "en.md": EN_MD})
        ids = [(e["id"], e["source"]) for e in load_lexicon(refs, "en")]
        self.assertEqual(ids, [("em-dash", "common"), ("delve", "en"),
                               ("not-just-but", "en")])

    def test_missing_language_file_uses_common_only(self):
        refs = write_refs({"common.md": COMMON_MD})
        self.assertEqual([e["id"] for e in load_lexicon(refs, "fr")],
                         ["em-dash"])

    def test_duplicate_id_is_an_error(self):
        refs = write_refs({"common.md": COMMON_MD,
                           "en.md": "```lexicon\nem-dash: --\n```\n"})
        with self.assertRaises(ValueError):
            load_lexicon(refs, "en")

    def test_invalid_regex_is_an_error_naming_the_id(self):
        refs = write_refs({"common.md": "```lexicon\nbroken: (\n```\n"})
        with self.assertRaisesRegex(ValueError, "broken"):
            load_lexicon(refs, "en")

    def test_missing_references_directory_is_an_error(self):
        # パスを間違えたときに、観点の一覧が黙って空になるのを防ぐ
        with self.assertRaisesRegex(FileNotFoundError, "references"):
            load_lexicon(Path(tempfile.mkdtemp()) / "nowhere", "en")

    def test_real_references_load_and_ids_are_unique(self):
        """references/ の lexicon ブロックが全言語で読め、id が言語をまたいでも重複しないこと"""
        langs = [p.stem for p in REFS.glob("*.md") if p.stem != "common"]
        seen = {}
        for lang in langs:
            for e in load_lexicon(REFS, lang):
                if e["source"] == "common":
                    continue
                self.assertNotIn(e["id"], seen, f"{lang} と {seen.get(e['id'])}")
                seen[e["id"]] = lang


class TestDetectLang(unittest.TestCase):
    def test_english(self):
        self.assertEqual(detect_lang("We shipped the feature in May."), "en")

    def test_japanese_with_english_terms(self):
        self.assertEqual(detect_lang("SwiftUI で iOS アプリを再設計した。"), "ja")


class TestDetect(unittest.TestCase):
    def setUp(self):
        self.refs = write_refs({"common.md": COMMON_MD, "en.md": EN_MD,
                                "ja.md": JA_MD})

    def test_reports_hits_in_text_order_with_context(self):
        text = "First line.\nLet us delve into it — quickly.\n"
        result = detect(text, self.refs, "en")
        hits = [(h["id"], h["line"], h["match"]) for h in result["hits"]]
        self.assertEqual(hits, [("delve", 2, "delve"), ("em-dash", 2, "—")])
        self.assertEqual(result["hits"][0]["context"],
                         "Let us delve into it — quickly.")
        self.assertEqual(result["counts"], {"em-dash": 1, "delve": 1})

    def test_english_patterns_ignore_case(self):
        result = detect("Delved deep.", self.refs, "en")
        self.assertEqual([h["match"] for h in result["hits"]], ["Delved"])

    def test_japanese_pattern(self):
        result = detect("設定が静かに壊れる。", self.refs, "ja")
        self.assertEqual([h["id"] for h in result["hits"]], ["silently-break"])

    def test_no_hits(self):
        self.assertEqual(detect("Plain text.", self.refs, "en")["hits"], [])

    def test_mixed_languages_use_every_listed_lexicon(self):
        # 日英が混ざる文章で、片方の言語のパターンが黙って漏れないようにする
        text = "設定が静かに壊れる。We delve.\n"
        result = detect(text, self.refs, "ja,en")
        self.assertEqual(sorted(h["id"] for h in result["hits"]),
                         ["delve", "silently-break"])

    def test_lists_judgment_checks_of_the_languages(self):
        # 目で確かめる観点を、references を見て回らなくても分かるようにする
        self.assertEqual(detect("Plain.", self.refs, "en")["judgment_checks"],
                         [{"id": "en-rather-than", "title": "rather than の対比"}])
        self.assertEqual(detect("普通。", self.refs, "ja")["judgment_checks"], [])

    def test_prose_patterns_skip_headings(self):
        # 見出しの「社名 — 役職」の区切りは慣例なので数えない
        text = "### Example Corp — Engineer\nIt works — mostly.\n"
        self.assertEqual([h["line"] for h in detect(text, self.refs, "en")["hits"]],
                         [2])

    def test_all_scope_patterns_check_headings(self):
        self.assertEqual(
            [h["id"] for h in detect("## Let us delve\n", self.refs, "en")["hits"]],
            ["delve"])

    def test_code_quotes_inline_code_and_urls_are_not_checked(self):
        text = ("```\nwe delve\n```\n"
                "> they delve, said the author\n"
                "Call `delve()` or see https://example.com/delve-guide now.\n"
                "We delve.\n")
        hits = detect(text, self.refs, "en")["hits"]
        self.assertEqual([(h["line"], h["column"]) for h in hits], [(6, 4)])

    def test_hits_per_id_are_capped_but_counted(self):
        text = "We delve.\n" * (MAX_HITS_PER_ID + 5)
        result = detect(text, self.refs, "en")
        self.assertEqual(len(result["hits"]), MAX_HITS_PER_ID)
        self.assertEqual(result["counts"]["delve"], MAX_HITS_PER_ID + 5)


class TestRepeatedPhrases(unittest.TestCase):
    def test_english_phrase_repeated_across_lines(self):
        text = ("I own them end to end.\n"
                "Owned that feature end to end: design and deploy.\n"
                "Built video end to end.\n")
        phrases = {p["phrase"]: p for p in repeated_phrases(text, "en")}
        self.assertEqual(phrases["end to end"]["count"], 3)
        self.assertEqual(phrases["end to end"]["lines"], [1, 2, 3])

    def test_keeps_longest_phrase_only(self):
        text = "the details specs rarely capture\nwhat specs rarely capture\n"
        self.assertEqual([p["phrase"] for p in repeated_phrases(text, "en")],
                         ["specs rarely capture"])

    def test_stopword_only_phrases_are_ignored(self):
        self.assertEqual(
            repeated_phrases("It is in the box.\nIt is in the car.\n", "en"), [])

    def test_heading_lines_are_ignored(self):
        text = ("### Example Corp — Senior Software Engineer\n"
                "### Sample Inc — Senior Software Engineer\n")
        self.assertEqual(repeated_phrases(text, "en"), [])

    def test_japanese_ignores_latin_only_terms(self):
        text = "GitHub Actions で検査した。\nGitHub Actions を使った。\n"
        self.assertEqual(repeated_phrases(text, "ja"), [])

    def test_japanese_ignores_dates_and_bare_terms(self):
        text = ("2024年11月にアーキテクチャガイドを書いた。\n"
                "2024年11月にアーキテクチャガイドを直した。\n")
        self.assertEqual([p["phrase"] for p in repeated_phrases(text, "ja")],
                         ["月にアーキテクチャガイドを"])

    def test_japanese_does_not_split_latin_words(self):
        text = "コスメのアプリである LUMA。\nメッセージのアプリである LUNA。\n"
        self.assertEqual([p["phrase"] for p in repeated_phrases(text, "ja")],
                         ["のアプリである"])

    def test_japanese_repeated_phrase(self):
        text = "仕様にはめったに書かれない細部。\n仕様にはめったに書かれない部分。\n"
        self.assertEqual([p["phrase"] for p in repeated_phrases(text, "ja")],
                         ["仕様にはめったに書かれない"])


class TestMetrics(unittest.TestCase):
    def test_uniform_rhythm_has_lower_variation(self):
        uniform = "One two three four. Five six seven eight. Nine ten one two.\n"
        varied = "One. Two three four five six seven eight nine ten. Eleven twelve.\n"
        self.assertLess(metrics(uniform, "en")["sentence_length_cv"],
                        metrics(varied, "en")["sentence_length_cv"])

    def test_bullets_bold_and_commas(self):
        text = "- **a**, b.\n- c.\nplain **d**.\n\nplain e, f, g.\n"
        m = metrics(text, "en")
        self.assertEqual(m["bullet_line_ratio"], 0.5)
        self.assertEqual(m["bold_count"], 2)
        self.assertEqual(m["sentences"], 4)
        self.assertEqual(m["commas_per_sentence"], 0.75)

    def test_japanese_commas_per_sentence(self):
        self.assertEqual(metrics("a、b、c。d。\n", "ja")["commas_per_sentence"],
                         1.0)

    def test_length_counts_body_words_and_chars(self):
        # 件数を文書の長さと比べて読むため。見出しとコードブロックは数えない
        text = "# Title here\nWe shipped it.\n```\ncode line\n```\n"
        m = metrics(text, "en")
        self.assertEqual(m["words"], 3)
        self.assertEqual(m["chars"], 12)

    def test_empty_text(self):
        self.assertEqual(metrics("", "en")["sentences"], 0)


class TestCompare(unittest.TestCase):
    def test_removed_number_and_hedge(self):
        before = "The rate rose from about 70% to 100% and may keep rising.\n"
        after = "The rate rose to 100% and keeps rising.\n"
        result = compare(before, after, "en")
        self.assertEqual(result["removed"]["numbers"], ["70%"])
        self.assertEqual(result["removed"]["hedges"], ["about", "may"])
        self.assertEqual(result["added"]["numbers"], [])

    def test_one_of_two_equal_numbers_removed_is_reported(self):
        # 同じ数字が 2 回あって 1 回だけ消えた変化も、意味の変化として拾う
        result = compare("It took 3 days, then 3 more.\n", "It took 3 days.\n", "en")
        self.assertEqual(result["removed"]["numbers"], ["3"])

    def test_added_number_is_reported(self):
        result = compare("Cut build time.\n", "Cut build time by 40%.\n", "en")
        self.assertEqual(result["added"]["numbers"], ["40%"])

    def test_negation_flip(self):
        result = compare("It can complete bookings.\n",
                         "It cannot complete bookings.\n", "en")
        self.assertEqual(result["added"]["negations"], ["cannot"])

    def test_names_ignore_sentence_initial_words(self):
        before = "Built the pipeline on Cloud Pub/Sub. It uses GitHub Actions.\n"
        after = "Built the pipeline. It uses GitHub Actions.\n"
        result = compare(before, after, "en")
        self.assertEqual(result["removed"]["names"], ["Cloud Pub/Sub"])
        self.assertEqual(result["added"]["names"], [])

    def test_names_drop_possessive_and_pronoun_i(self):
        before = "At Example I led the team.\n"
        after = "I led Example's team.\n"
        result = compare(before, after, "en")
        self.assertEqual(result["removed"]["names"], [])
        self.assertEqual(result["added"]["names"], [])

    def test_urls(self):
        result = compare("See https://example.com/a for details.\n",
                         "See the docs for details.\n", "en")
        self.assertEqual(result["removed"]["urls"], ["https://example.com/a"])

    def test_japanese_facts(self):
        before = "約7割の通話を、数名のチームで処理できる可能性がある。\n"
        after = "7割の通話を処理できない。\n"
        result = compare(before, after, "ja")
        self.assertEqual(result["removed"]["hedges"], ["約", "数名", "可能性"])
        self.assertEqual(result["added"]["negations"], ["ない"])

    def test_unchanged_text_has_no_differences(self):
        text = "We shipped 3 features on GitHub, maybe 4.\n"
        result = compare(text, text, "en")
        self.assertTrue(all(v == [] for v in result["removed"].values()))
        self.assertTrue(all(v == [] for v in result["added"].values()))


class TestCli(unittest.TestCase):
    def test_scan_outputs_json_with_detected_language(self):
        refs = write_refs({"common.md": COMMON_MD, "en.md": EN_MD})
        path = write_text("We delve — twice we delve.\n")
        out = subprocess.run(
            [sys.executable, str(SCRIPT), path, "--refs", str(refs)],
            capture_output=True, text=True, check=True)
        result = json.loads(out.stdout)
        self.assertEqual(result["lang"], "en")
        self.assertEqual(result["counts"], {"em-dash": 1, "delve": 2})
        self.assertIn("metrics", result)

    def test_stdin_only_when_requested(self):
        refs = write_refs({"common.md": COMMON_MD, "en.md": EN_MD})
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--stdin", "--refs", str(refs)],
            input="We delve.\n", capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(out.stdout)["counts"], {"delve": 1})

    def test_compare_mode(self):
        before = write_text("Rose from about 70% to 100%.\n")
        after = write_text("Rose to 100%.\n")
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--compare", before, after],
            capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(out.stdout)["removed"]["numbers"], ["70%"])

    def test_wrong_refs_path_fails_loudly(self):
        path = write_text("We delve.\n")
        out = subprocess.run([sys.executable, str(SCRIPT), path, "--refs", "/nonexistent"],
                             capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("references", out.stderr)

    def test_missing_input_is_a_usage_error(self):
        out = subprocess.run([sys.executable, str(SCRIPT)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main()
