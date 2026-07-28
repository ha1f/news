#!/usr/bin/env python3
"""実行中のセッションのトークン使用量を集計する。

daily-loop の各ステージが status issue の終了コメントに載せる `tokens` を作る。
Claude Code のセッション記録（`~/.claude/projects/{cwd}/{セッションID}.jsonl` の
assistant メッセージの usage）を合計する。subagent の消費も同じ記録に入る。

使い方:
  python3 .claude/scripts/session_usage.py            # JSON 1行（status コメント用）
  python3 .claude/scripts/session_usage.py --pretty   # 人が読む形式
  python3 .claude/scripts/session_usage.py --transcript path.jsonl

出力: {"in", "cache_write", "cache_read", "out", "turns", "usd", "models"}
記録が読めない環境では全て null の JSON を返す（記録が無いこと自体は失敗ではない）。

usd は概算。単価は下の PRICES（100万トークンあたりUSD、2026-07時点）で、
未知のモデルが混ざると null になる。単価改定時はここを更新する。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# 100万トークンあたりUSD: (入力, 出力, キャッシュ書き込み, キャッシュ読み出し)
# キャッシュ書き込みは1時間TTL（入力の2倍）を前提にした保守的な見積もり。
PRICES = {
    "claude-opus-5": (5.0, 25.0, 10.0, 0.5),
    "claude-sonnet-5": (3.0, 15.0, 6.0, 0.3),
    "claude-haiku-4-5": (1.0, 5.0, 2.0, 0.1),
}

EMPTY = {"in": None, "cache_write": None, "cache_read": None, "out": None,
         "turns": None, "usd": None, "models": None}


def find_transcript(cwd: Path, home: Path) -> Path | None:
    """cwd に対応するプロジェクトの、最後に更新された記録を返す（＝実行中のセッション）。"""
    project = home / ".claude" / "projects" / str(cwd).replace("/", "-")
    try:
        transcripts = [p for p in project.iterdir() if p.suffix == ".jsonl"]
    except OSError:
        return None
    return max(transcripts, key=lambda p: p.stat().st_mtime, default=None)


def summarize(lines) -> dict:
    """記録の各行から assistant の usage を合計する（純関数）。"""
    total = {"in": 0, "cache_write": 0, "cache_read": 0, "out": 0}
    models: set[str] = set()
    turns = 0
    for line in lines:
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if record.get("type") != "assistant":
            continue
        message = record.get("message") or {}
        usage = message.get("usage")
        if not usage:
            continue
        turns += 1
        total["in"] += usage.get("input_tokens", 0)
        total["cache_write"] += usage.get("cache_creation_input_tokens", 0)
        total["cache_read"] += usage.get("cache_read_input_tokens", 0)
        total["out"] += usage.get("output_tokens", 0)
        if message.get("model"):
            models.add(message["model"])
    return {**total, "turns": turns, "usd": estimate_usd(total, models),
            "models": sorted(models)}


def estimate_usd(total: dict, models) -> float | None:
    """単価表にある単一モデルの記録だけ概算する（純関数）。不明なら None。"""
    known = [m for m in models if m in PRICES]
    if len(known) != 1 or len(set(models)) != 1:
        return None
    price_in, price_out, price_write, price_read = PRICES[known[0]]
    usd = (total["in"] * price_in + total["out"] * price_out
           + total["cache_write"] * price_write + total["cache_read"] * price_read) / 1e6
    return round(usd, 2)


def main():
    parser = argparse.ArgumentParser(description="セッションのトークン使用量")
    parser.add_argument("--transcript", help="記録ファイルのパス（省略時は自動検出）")
    parser.add_argument("--pretty", action="store_true", help="人が読む形式で出す")
    args = parser.parse_args()

    path = Path(args.transcript) if args.transcript else find_transcript(
        Path.cwd(), Path(os.path.expanduser("~")))

    result = dict(EMPTY)
    if path is not None:
        try:
            with open(path, encoding="utf-8") as f:
                result = summarize(f)
        except OSError:
            pass

    if args.pretty:
        if result["turns"] is None:
            print("セッション記録が見つからない（この環境では計測できない）")
            return
        print(f"ターン       {result['turns']:>12,}")
        for key, label in [("in", "入力"), ("cache_write", "キャッシュ書き"),
                           ("cache_read", "キャッシュ読み"), ("out", "出力")]:
            print(f"{label:<10} {result[key]:>12,}")
        print(f"概算         {'$' + format(result['usd'], ',.2f') if result['usd'] is not None else '不明'}")
    else:
        json.dump(result, sys.stdout, ensure_ascii=False)
        print()


if __name__ == "__main__":
    main()
