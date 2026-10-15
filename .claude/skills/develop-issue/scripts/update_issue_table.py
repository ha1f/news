#!/usr/bin/env python3
"""issue 本文の Markdown 表の行を、1 列目の値（行 ID）で探して書き換える。

古い本文で上書きしないよう、本文は書き換えの直前に取り直す。取り直してから書き戻すまでの
数秒の間に入った編集は消える。指定した行 ID がどれも 1 か所だけに当たるときだけ書き戻す。
GitHub とのやりとりは `gh api`（REST）だけなので、GraphQL が通らない環境でも動く。

rows の JSON: {"<行 ID>": {"<列番号>": "<新しい値>", ...}, ...}
  列番号は 0 始まりで、負の数は末尾から数える（-1 が最後の列）。
  値の中の `|` はエスケープする。改行を含む値は受け付けない。

使い方:
  python3 update_issue_table.py --repo owner/name --issue 123 --rows rows.json [--dry-run]

exit 1: 行 ID が見つからない、2 か所以上に当たる、列がない、値に改行がある（どれも書き戻さない）
"""
import argparse
import difflib
import json
import re
import subprocess
import sys


def fetch_body(repo, issue):
    result = subprocess.run(["gh", "api", f"repos/{repo}/issues/{issue}"],
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)["body"] or ""


def split_row(line):
    # 先頭と末尾の `|` を除いてセルに分ける。セル内の `\|` は区切りとして扱わない
    cells, current, escaped = [], "", False
    for char in line.strip()[1:-1]:
        if char == "|" and not escaped:
            cells.append(current.strip())
            current = ""
        else:
            current += char
        escaped = char == "\\"
    cells.append(current.strip())
    return cells


def escape_cell(value):
    if "\n" in value or "\r" in value:
        sys.exit(f"値に改行がある: {value!r}")
    return re.sub(r"(?<!\\)\|", r"\\|", value)


def update_rows(body, rows):
    lines = body.split("\n")
    hits = {row_id: 0 for row_id in rows}
    for index, line in enumerate(lines):
        if not line.startswith("| "):
            continue
        cells = split_row(line)
        row_id = cells[0]
        if row_id not in rows:
            continue
        hits[row_id] += 1
        for column, value in rows[row_id].items():
            if not -len(cells) <= int(column) < len(cells):
                sys.exit(f"{row_id} の行に列 {column} がない（{len(cells)} 列）")
            cells[int(column)] = escape_cell(value)
        lines[index] = "| " + " | ".join(cells) + " |"
    bad = {row_id: count for row_id, count in hits.items() if count != 1}
    return "\n".join(lines), bad


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--rows", required=True, help="行 ID → {列番号: 値} の JSON ファイル")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with open(args.rows) as file:
        rows = json.load(file)
    body = fetch_body(args.repo, args.issue)
    updated, bad = update_rows(body, rows)
    if bad:
        sys.exit(f"1 か所だけに当たらない行 ID がある（ID: 当たった数）: {bad}")

    diff = difflib.unified_diff(body.split("\n"), updated.split("\n"), lineterm="", n=0)
    print("\n".join(line for line in diff if line.startswith(("+|", "-|"))))
    if args.dry_run:
        return
    subprocess.run(["gh", "api", "-X", "PATCH", f"repos/{args.repo}/issues/{args.issue}", "--input", "-"],
                   input=json.dumps({"body": updated}), text=True, check=True, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
