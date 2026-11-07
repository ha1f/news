#!/usr/bin/env python3
"""subagent_usage の検証 (#612)。"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import subagent_usage  # noqa: E402


def line(mid, model="claude-opus-5-5", text=None, tool=False, usage=None):
    content = []
    if text is not None:
        content.append({"type": "text", "text": text})
    if tool:
        content.append({"type": "tool_use", "name": "Bash", "input": {}})
    msg = {"id": mid, "model": model, "content": content}
    if usage is not None:
        msg["usage"] = usage
    return json.dumps({"type": "assistant", "message": msg})


def usage(inp=0, w5=0, w1=0, read=0, out=0):
    return {
        "input_tokens": inp,
        "cache_creation_input_tokens": w5 + w1,
        "cache_creation": {"ephemeral_5m_input_tokens": w5, "ephemeral_1h_input_tokens": w1},
        "cache_read_input_tokens": read,
        "output_tokens": out,
    }


class TestReadCalls(unittest.TestCase):
    def test_same_message_split_into_blocks_is_counted_once(self):
        u = usage(inp=10, out=100)
        lines = [line("m1", text="考える", usage=u), line("m1", tool=True, usage=u)]
        calls = subagent_usage.read_calls(lines)
        self.assertEqual(len(calls), 1)
        rows = subagent_usage.summarize(calls)
        self.assertEqual(rows[0]["calls"], 1)
        self.assertEqual(rows[0]["output"], 100)

    def test_user_and_synthetic_lines_are_ignored(self):
        lines = [
            json.dumps({"type": "user", "message": {"content": "STAGE:9"}}),
            line("s", model="<synthetic>", text="STAGE:9", usage=usage(out=5)),
            "not json",
            line("m1", usage=usage(out=1)),
        ]
        calls = subagent_usage.read_calls(lines)
        self.assertEqual([c["id"] for c in calls], ["m1"])


class TestStages(unittest.TestCase):
    def test_marker_starts_stage_including_its_own_call(self):
        lines = [
            line("m0", usage=usage(out=1)),
            line("m1", text="STAGE:1\nソースを選ぶ", tool=True, usage=usage(out=2)),
            line("m2", tool=True, usage=usage(out=3)),
            line("m3", text="STAGE:2", usage=usage(out=4)),
        ]
        rows = subagent_usage.summarize(subagent_usage.read_calls(lines), by_stage=True)
        got = {(r["stage"], r["output"]) for r in rows}
        self.assertEqual(got, {("-", 1), ("1", 5), ("2", 4)})

    def test_marker_must_be_its_own_line(self):
        lines = [line("m1", text="次は STAGE:2 に進む", usage=usage(out=1))]
        rows = subagent_usage.summarize(subagent_usage.read_calls(lines), by_stage=True)
        self.assertEqual(rows[0]["stage"], "-")

    def test_models_are_kept_apart_within_a_stage(self):
        lines = [
            line("m1", text="STAGE:1", usage=usage(out=1)),
            line("m2", model="claude-sonnet-5-5", usage=usage(out=1)),
        ]
        rows = subagent_usage.summarize(subagent_usage.read_calls(lines), by_stage=True)
        self.assertEqual(len(rows), 2)


class TestCost(unittest.TestCase):
    def test_opus_prices(self):
        t = {"input": 1_000_000, "cache_write_5m": 1_000_000, "cache_write_1h": 1_000_000,
             "cache_read": 1_000_000, "output": 1_000_000}
        # 4 + 4*1.25 + 4*2 + 0.20 + 20
        self.assertAlmostEqual(subagent_usage.cost_usd("claude-opus-5-5", t), 37.2)

    def test_sonnet_prices(self):
        t = {"input": 0, "cache_write_5m": 1_000_000, "cache_write_1h": 0, "cache_read": 1_000_000, "output": 0}
        self.assertAlmostEqual(subagent_usage.cost_usd("claude-sonnet-5-5", t), 2.5 + 0.2)

    def test_unknown_model_has_no_cost(self):
        self.assertIsNone(subagent_usage.cost_usd("other", {k: 1 for k in subagent_usage.TOKEN_KEYS}))

    def test_missing_ttl_breakdown_is_treated_as_5m(self):
        u = {"input_tokens": 0, "cache_creation_input_tokens": 1_000_000, "cache_read_input_tokens": 0, "output_tokens": 0}
        rows = subagent_usage.summarize(subagent_usage.read_calls([line("m", usage=u)]))
        self.assertEqual(rows[0]["cache_write_5m"], 1_000_000)
        self.assertAlmostEqual(rows[0]["cost_usd"], 5.0)


if __name__ == "__main__":
    unittest.main()
