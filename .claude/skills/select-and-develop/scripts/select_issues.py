#!/usr/bin/env python3
"""daily-loop: 実装候補 issue を機械抽出して JSON で出力する。

使い方:
  python3 select_issues.py                    # gh CLI でデータ取得
  echo '{"issues": [...], "prs": [...]}' | python3 select_issues.py --stdin

--stdin の JSON に "collaborators" (login の文字列リスト) を含めると、
issue の author_association が欠落していても author が collaborator なら
信頼済みと判定する (MCP list_issues が author_association を返さない問題の回避策)。

出力: {"config", "status_issue", "in_progress", "backlog"}
  - in_progress: open な linked PR を持つ issue（要対応かはエージェントが判断）
  - backlog: linked PR の無い issue。作成日の古い順
フィルタ（collaborator 名義のみ・hold と status issue を除外）は適用済み。
優先度・着手順の判断はエージェントが issue を読んで行う。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
STATUS_TITLE = "daily-loop status"
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)
BRANCH_ISSUE_RE = re.compile(r"(?:^|/)(\d+)[-_]")


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


def _is_trusted(issue, collaborators):
    """author_association があればそれで判定、なければ collaborators リストで補完。"""
    assoc = issue.get("author_association", "")
    if assoc:
        return assoc in TRUSTED
    if collaborators:
        login = (issue.get("user") or {}).get("login", "")
        return login in collaborators
    return False


def build_candidates(issues, prs, collaborators=None):
    """issue を status / in_progress / backlog に分類する（純関数）"""
    collaborators = frozenset(collaborators) if collaborators else frozenset()
    links = {}
    for pr in prs:
        seen = set()
        for m in LINK_RE.finditer(pr.get("body") or ""):
            seen.add(int(m.group(1)))
        branch = ((pr.get("head") or {}).get("ref") or "")
        for m in BRANCH_ISSUE_RE.finditer(branch):
            seen.add(int(m.group(1)))
        for issue_num in seen:
            links.setdefault(issue_num, []).append({
                "number": pr["number"],
                "draft": pr["draft"],
            })
    status_issue, in_progress, backlog = None, [], []
    for issue in issues:
        if "pull_request" in issue:
            continue
        if STATUS_TITLE in issue["title"]:
            status_issue = issue["number"]
            continue
        labels = {(label["name"] if isinstance(label, dict) else label)
                  for label in issue.get("labels", [])}
        if not _is_trusted(issue, collaborators) or "hold" in labels:
            continue
        entry = {
            "number": issue["number"],
            "title": issue["title"],
            "created_at": issue["created_at"],
            "linked_open_prs": links.get(issue["number"], []),
        }
        (in_progress if entry["linked_open_prs"] else backlog).append(entry)
    sort_key = lambda e: e["created_at"]
    return status_issue, sorted(in_progress, key=sort_key), sorted(backlog, key=sort_key)


def fetch_via_gh():
    """gh CLI でデータを取得する。"""
    issues = gh_json("repos/{owner}/{repo}/issues?state=open&per_page=100")
    prs = gh_json("repos/{owner}/{repo}/pulls?state=open&per_page=100")
    return issues, prs


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())

    use_stdin = "--stdin" in sys.argv or not sys.stdin.isatty()
    if use_stdin:
        data = json.load(sys.stdin)
        issues = data["issues"]
        prs = data["prs"]
        collaborators = data.get("collaborators")
    else:
        issues, prs = fetch_via_gh()
        collaborators = None

    status_issue, in_progress, backlog = build_candidates(issues, prs, collaborators)
    json.dump({
        "config": config,
        "status_issue": status_issue,
        "in_progress": in_progress,
        "backlog": backlog,
    }, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
