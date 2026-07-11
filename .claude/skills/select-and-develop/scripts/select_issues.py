#!/usr/bin/env python3
"""daily-loop: 実装候補 issue を機械判定して JSON で出力する。

使い方: python3 select_issues.py
出力: {"config", "status_issue", "in_progress", "backlog"}
  - in_progress: open な linked PR を持つ issue（要対応かはエージェントが判断）
  - backlog: 未着手 issue。優先度 (P1>P2>P3、無ラベルは P2 相当)・古い順にソート済み
  - 上位候補には attempts (develop-issue の試行回数) を付与済み
フィルタ（collaborator 名義のみ・hold/needs-human 除外・status issue 除外）は適用済み。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
EXCLUDE_LABELS = {"hold", "needs-human"}
STATUS_TITLE = "daily-loop status"
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)
ATTEMPT_RE = re.compile(r"develop-issue attempt", re.I)
ATTEMPT_CHECK_TOP_N = 5  # attempt 数を取得する上位候補数（API 呼び出しを絞る）


def gh_json(path):
    out = subprocess.run(["gh", "api", "--paginate", path],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def parse_guardrails(text):
    """GUARDRAILS.md の ```yaml ブロックを設定 dict にする（依存なしの簡易パーサ）"""
    m = re.search(r"```yaml\n(.*?)```", text, re.S)
    block = m.group(1) if m else text
    config, current_list = {}, None
    for line in block.splitlines():
        line = line.split("#")[0].rstrip()
        if not line.strip():
            continue
        if line.strip().startswith("- ") and current_list is not None:
            config[current_list].append(line.strip()[2:].strip())
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            config[key] = []
            current_list = key
        else:
            config[key] = int(value) if value.isdigit() else value
            current_list = None
    return config


def build_candidates(issues, prs):
    """issue を status/in_progress/backlog に分類する（純関数）"""
    links = {}
    for pr in prs:
        for m in LINK_RE.finditer(pr.get("body") or ""):
            links.setdefault(int(m.group(1)), []).append({
                "number": pr["number"],
                "draft": pr["draft"],
                "labels": sorted(label["name"] for label in pr["labels"]),
            })
    status_issue, in_progress, backlog = None, [], []
    for issue in issues:
        if "pull_request" in issue:
            continue
        if STATUS_TITLE in issue["title"]:
            status_issue = issue["number"]
            continue
        labels = {label["name"] for label in issue["labels"]}
        if issue["author_association"] not in TRUSTED or labels & EXCLUDE_LABELS:
            continue
        priority = next((int(name[1]) for name in labels if re.fullmatch(r"P[123]", name)), 2)
        entry = {
            "number": issue["number"],
            "title": issue["title"],
            "priority": priority,
            "created_at": issue["created_at"],
            "labels": sorted(labels),
            "linked_open_prs": links.get(issue["number"], []),
        }
        (in_progress if entry["linked_open_prs"] else backlog).append(entry)
    sort_key = lambda e: (e["priority"], e["created_at"])
    return status_issue, sorted(in_progress, key=sort_key), sorted(backlog, key=sort_key)


def count_attempts(issue_number):
    comments = gh_json(f"repos/{{owner}}/{{repo}}/issues/{issue_number}/comments?per_page=100")
    return sum(1 for c in comments if ATTEMPT_RE.search(c.get("body") or ""))


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    issues = gh_json("repos/{owner}/{repo}/issues?state=open&per_page=100")
    prs = gh_json("repos/{owner}/{repo}/pulls?state=open&per_page=100")
    status_issue, in_progress, backlog = build_candidates(issues, prs)
    for entry in (in_progress + backlog)[:ATTEMPT_CHECK_TOP_N]:
        entry["attempts"] = count_attempts(entry["number"])
    json.dump({
        "config": config,
        "status_issue": status_issue,
        "in_progress": in_progress,
        "backlog": backlog,
    }, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
