#!/usr/bin/env python3
"""subagent の transcript（JSONL）から、API 呼び出しごとの usage を集計して費用を出す。

`get_session` の usage はセッション全体の合計しか返さないため、工程別・モデル別の費用は
subagent の transcript（`~/.claude/projects/<project>/<session>/subagents/agent-*.jsonl`）から数える（#612）。

- 1 回の API 呼び出しは content block ごとに複数行に分かれて記録され、各行に同じ usage が付く。
  `message.id` で重複を除く（最後の行を使う）
- `--by-stage` を付けると、assistant のテキストに単独の行で現れる `STAGE:<名前>` を区切りにして、
  その呼び出し以降を次の区切りまでその工程に振り分ける（区切りを出した呼び出し自身も新しい工程に入れる）。
  区切りより前の呼び出しは `-`（工程外）に入る
- 費用は下の単価表で計算する。cache write は TTL ごとに入力単価の倍率が違う（5 分: 1.25 倍、1 時間: 2 倍）

使い方:
  python3 .claude/scripts/subagent_usage.py agent-a.jsonl [agent-b.jsonl ...] [--by-stage] [--json]
"""

import argparse
import json
import re
import sys
from collections import OrderedDict

# 100 万トークンあたりの USD。docs/m5-paid-delivery.md の「有料の tier と費用を下げる方針」節（#612）と同じ値。
# cache read はどちらも $0.20（issue #612 の証拠欄、2026-10-06 時点の公開価格）。
PRICES = {
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0, "cache_read": 0.20},
}
CACHE_WRITE_MULTIPLIER = {"5m": 1.25, "1h": 2.0}

STAGE_RE = re.compile(r"^\s*STAGE:(\S+)\s*$", re.MULTILINE)

TOKEN_KEYS = ("input", "cache_write_5m", "cache_write_1h", "cache_read", "output")


def _tokens(usage):
    cc = usage.get("cache_creation") or {}
    w5 = cc.get("ephemeral_5m_input_tokens")
    w1 = cc.get("ephemeral_1h_input_tokens")
    if w5 is None and w1 is None:
        # 内訳が無い記録は 5 分扱い（Claude Code の既定）
        w5, w1 = usage.get("cache_creation_input_tokens", 0), 0
    return {
        "input": usage.get("input_tokens", 0) or 0,
        "cache_write_5m": w5 or 0,
        "cache_write_1h": w1 or 0,
        "cache_read": usage.get("cache_read_input_tokens", 0) or 0,
        "output": usage.get("output_tokens", 0) or 0,
    }


def cost_usd(model, tokens):
    p = PRICES.get(model)
    if p is None:
        return None
    m = 1_000_000
    return (
        tokens["input"] * p["input"]
        + tokens["cache_write_5m"] * p["input"] * CACHE_WRITE_MULTIPLIER["5m"]
        + tokens["cache_write_1h"] * p["input"] * CACHE_WRITE_MULTIPLIER["1h"]
        + tokens["cache_read"] * p["cache_read"]
        + tokens["output"] * p["output"]
    ) / m


def read_calls(lines):
    """JSONL の行から、API 呼び出し（message.id 単位）を出現順に返す。

    各要素は {"id", "model", "usage", "stage_marks": [テキスト中の STAGE 名…]}。
    """
    calls = OrderedDict()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") != "assistant":
            continue
        msg = rec.get("message") or {}
        mid = msg.get("id")
        if not mid or msg.get("model") == "<synthetic>":
            continue
        call = calls.setdefault(mid, {"id": mid, "model": msg.get("model"), "usage": {}, "stage_marks": []})
        if msg.get("usage"):
            call["usage"] = msg["usage"]
        for block in msg.get("content") or []:
            if block.get("type") == "text":
                call["stage_marks"].extend(STAGE_RE.findall(block.get("text", "")))
    return list(calls.values())


def summarize(calls, by_stage=False):
    """呼び出しを (工程, モデル) ごとに集計する。by_stage=False なら工程は全部 `all`。"""
    groups = OrderedDict()
    stage = "-" if by_stage else "all"
    for call in calls:
        if by_stage and call["stage_marks"]:
            stage = call["stage_marks"][-1]
        key = (stage, call["model"])
        g = groups.setdefault(key, {"stage": stage, "model": call["model"], "calls": 0, **{k: 0 for k in TOKEN_KEYS}})
        g["calls"] += 1
        for k, v in _tokens(call["usage"]).items():
            g[k] += v
    out = []
    for g in groups.values():
        c = cost_usd(g["model"], g)
        g["cost_usd"] = round(c, 4) if c is not None else None
        out.append(g)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="subagent の transcript（JSONL）")
    ap.add_argument("--by-stage", action="store_true", help="STAGE:<名前> の行で工程別に分ける")
    ap.add_argument("--json", action="store_true", help="JSON で出力する")
    args = ap.parse_args(argv)

    result = []
    for path in args.files:
        with open(path, encoding="utf-8") as f:
            rows = summarize(read_calls(f), by_stage=args.by_stage)
        for r in rows:
            r["file"] = path
        result.extend(rows)

    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    header = ["file", "stage", "model", "calls", *TOKEN_KEYS, "cost_usd"]
    print("\t".join(header))
    total = 0.0
    for r in result:
        print("\t".join(str(r[h]) for h in header))
        total += r["cost_usd"] or 0
    print(f"total_cost_usd\t{total:.4f}")
    unknown = sorted({r["model"] for r in result if r["cost_usd"] is None})
    if unknown:
        print(f"単価表に無いモデル（費用に含めていない）: {', '.join(map(str, unknown))}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
