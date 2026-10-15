#!/usr/bin/env python3
"""issue 本文の Markdown 表の行を、行 ID（1 列目）で書き換える。

本文は書き換えの直前に取り直し、指定した行がそれぞれちょうど 1 か所に当たることを
確かめてから書き戻す（並行して表を編集している人やセッションの変更を消さないため）。

rows の JSON: {"<行 ID>": {"<列番号>": "<新しい値>", ...}, ...}
  列番号は 0 始まり。負の数は末尾から（-1 が最後の列）。

使い方:
  python3 update_issue_table.py --repo owner/name --issue 123 --rows rows.json [--dry-run]

exit 1: 当たらない行 ID か、2 か所以上に当たる行 ID がある（何も書き戻さない）
"""
import argparse
import difflib
import json
import subprocess
import sys


def fetch_body(repo, issue):
    result = subprocess.run(["gh", "issue", "view", str(issue), "--repo", repo, "--json", "body", "--jq", ".body"],
                            capture_output=True, text=True, check=True)
    return result.stdout.rstrip("\n")


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
                sys.exit(f"{row_id} の行に列 {column} が無い（{len(cells)} 列）")
            cells[int(column)] = value
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
        sys.exit(f"行 ID がちょうど 1 か所に当たらない: {bad}")

    diff = difflib.unified_diff(body.split("\n"), updated.split("\n"), lineterm="", n=0)
    print("\n".join(line for line in diff if line.startswith(("+|", "-|"))))
    if args.dry_run:
        return
    subprocess.run(["gh", "issue", "edit", str(args.issue), "--repo", args.repo, "--body-file", "-"],
                   input=updated, text=True, check=True)


if __name__ == "__main__":
    main()
