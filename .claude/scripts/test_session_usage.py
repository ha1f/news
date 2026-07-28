#!/usr/bin/env python3
"""session_usage.py の純関数のユニットテスト。実行: python3 test_session_usage.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_usage import estimate_usd, summarize


def assistant(model="claude-opus-5", **usage):
    base = {"input_tokens": 0, "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0, "output_tokens": 0}
    return json.dumps({"type": "assistant",
                       "message": {"model": model, "usage": {**base, **usage}}})


class SummarizeTest(unittest.TestCase):
    def test_sums_usage_across_assistant_turns(self):
        result = summarize([
            assistant(input_tokens=10, output_tokens=100),
            assistant(cache_creation_input_tokens=1000, cache_read_input_tokens=5000,
                      output_tokens=200),
        ])
        self.assertEqual(result["in"], 10)
        self.assertEqual(result["out"], 300)
        self.assertEqual(result["cache_write"], 1000)
        self.assertEqual(result["cache_read"], 5000)
        self.assertEqual(result["turns"], 2)
        self.assertEqual(result["models"], ["claude-opus-5"])

    def test_ignores_user_rows_and_malformed_lines(self):
        result = summarize([
            json.dumps({"type": "user", "message": {"content": "hi"}}),
            "これはJSONではない",
            json.dumps({"type": "assistant", "message": {}}),  # usage 無し
            assistant(output_tokens=5),
        ])
        self.assertEqual(result["turns"], 1)
        self.assertEqual(result["out"], 5)

    def test_empty_transcript(self):
        result = summarize([])
        self.assertEqual(result["turns"], 0)
        self.assertEqual(result["usd"], None)


class EstimateUsdTest(unittest.TestCase):
    def test_prices_a_single_known_model(self):
        total = {"in": 1_000_000, "out": 1_000_000, "cache_write": 0, "cache_read": 0}
        self.assertEqual(estimate_usd(total, {"claude-opus-5"}), 30.0)

    def test_prices_cache_tokens(self):
        total = {"in": 0, "out": 0, "cache_write": 1_000_000, "cache_read": 10_000_000}
        self.assertEqual(estimate_usd(total, {"claude-opus-5"}), 15.0)

    def test_unknown_or_mixed_models_are_not_priced(self):
        total = {"in": 1_000_000, "out": 0, "cache_write": 0, "cache_read": 0}
        self.assertIsNone(estimate_usd(total, {"some-future-model"}))
        self.assertIsNone(estimate_usd(total, {"claude-opus-5", "claude-haiku-4-5"}))
        self.assertIsNone(estimate_usd(total, set()))


if __name__ == "__main__":
    unittest.main()
