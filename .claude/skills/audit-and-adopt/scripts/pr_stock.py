#!/usr/bin/env python3
"""audit-and-adopt: open PR の在庫を、誰が動かすべきかで分類して JSON で出力する。

使い方:
  python3 pr_stock.py                   # gh CLI でデータ取得
  python3 pr_stock.py --stdin < stock.json  # MCP 等で取得した JSON を渡す
出力: {"summary", "superseded", "stale_drafts", "hold", "stalled"}
  - superseded: 後継 PR がマージ済みの PR → ループが close する
  - stale_drafts: STALE_DAYS 以上動きがなく、open な linked issue も無い draft
    → 作業中とみなさず、ループが ready 化か close で終わらせる
  - hold: hold の PR すべて（人間の預かり）→ オーナー向けの判断リストに載せる
  - stalled: STALE_DAYS 以上動きがないが、本来ループが動かしているはずの PR
    （ready なのに review が終端化していない、linked issue が open なのに develop が拾っていない）
    → 手順の異常として原因を調べる
close や判断リストの作成はエージェントが行う。
"""
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

# audit は週次なので、前回の audit から一度も動いていない PR を滞留とみなす
STALE_DAYS = 7
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)
# develop-issue の後継 PR は「PR #N（経緯）の後継」と書く（body 冒頭とタイトル）
SUCCESSOR_RE = re.compile(r"PR #(\d+)\s*(?:（[^）\n]*）)?\s*の後継")


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def days_since(value, now):
    return (now - parse_time(value)).days


def successors_of(merged_prs):
    """マージ済み PR が後継として置き換えた PR の番号 → 後継の番号"""
    successors = {}
    for pr in sorted(merged_prs, key=lambda p: p["number"]):
        text = f"{pr.get('title') or ''}\n{pr.get('body') or ''}"
        for m in SUCCESSOR_RE.finditer(text):
            successors[int(m.group(1))] = pr["number"]
    return successors


def classify_stock(open_prs, merged_prs, open_issues, now):
    """open PR を分類する（純関数）。open_prs の各要素は number/title/draft/labels/body/
    created_at/updated_at、merged_prs は number/title/body/merged_at を持つ dict。
    open_issues は open な issue の番号の列。"""
    successors = successors_of(merged_prs)
    open_issue_set = set(open_issues)
    result = {"superseded": [], "stale_drafts": [], "hold": [], "stalled": []}
    counts = {"draft": 0, "hold": 0, "ready": 0}
    for pr in sorted(open_prs, key=lambda p: p["created_at"]):
        idle_days = days_since(pr["updated_at"], now)
        summary = {"number": pr["number"], "title": pr["title"], "idle_days": idle_days}
        successor = successors.get(pr["number"])
        if "hold" in pr["labels"]:
            counts["hold"] += 1
            entry = {**summary, "draft": pr["draft"],
                     "age_days": days_since(pr["created_at"], now)}
            if successor:
                entry["superseded_by"] = successor
            result["hold"].append(entry)
            continue
        counts["draft" if pr["draft"] else "ready"] += 1
        if successor:
            result["superseded"].append({**summary, "successor": successor})
            continue
        if idle_days < STALE_DAYS:
            continue
        linked_open = sorted({int(m.group(1)) for m in LINK_RE.finditer(pr.get("body") or "")}
                             & open_issue_set)
        if pr["draft"] and not linked_open:
            result["stale_drafts"].append(summary)
        else:
            result["stalled"].append({**summary, "draft": pr["draft"],
                                      "linked_open_issues": linked_open})
    result["summary"] = {"open": len(open_prs), **counts,
                         "oldest_age_days": max((days_since(pr["created_at"], now)
                                                 for pr in open_prs), default=0)}
    return result


def gh_json(path, paginate=True):
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + [path]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def fetch_via_gh():
    open_prs = [{"number": pr["number"], "title": pr["title"], "draft": pr["draft"],
                 "labels": [label["name"] for label in pr["labels"]],
                 "body": pr.get("body") or "",
                 "created_at": pr["created_at"], "updated_at": pr["updated_at"]}
                for pr in gh_json("repos/{owner}/{repo}/pulls?state=open&per_page=100")]
    # 後継の照合には直近の分で足りるので、closed は更新順の1ページだけ読む
    closed = gh_json("repos/{owner}/{repo}/pulls?state=closed&sort=updated&direction=desc"
                     "&per_page=100", paginate=False)
    merged_prs = [{"number": pr["number"], "title": pr["title"], "body": pr.get("body") or "",
                   "merged_at": pr["merged_at"]}
                  for pr in closed if pr.get("merged_at")]
    open_issues = [issue["number"]
                   for issue in gh_json("repos/{owner}/{repo}/issues?state=open&per_page=100")
                   if "pull_request" not in issue]
    return {"open_prs": open_prs, "merged_prs": merged_prs, "open_issues": open_issues}


USAGE_WITHOUT_GH = """gh CLI が見つかりません。MCP ツール等でデータを取得し、--stdin で渡してください:

  python3 .claude/skills/audit-and-adopt/scripts/pr_stock.py --stdin < stock.json

stock.json は {"open_prs": [...], "merged_prs": [...], "open_issues": [...]}。
各要素の形は classify_stock() の docstring を参照。"""


def main():
    # エージェントの Bash ツールから起動すると stdin は常に非 tty になるため、明示フラグで切り替える
    if "--stdin" in sys.argv:
        data = json.load(sys.stdin)
    elif shutil.which("gh"):
        data = fetch_via_gh()
    else:
        print(USAGE_WITHOUT_GH, file=sys.stderr)
        return 1
    result = classify_stock(data["open_prs"], data["merged_prs"], data["open_issues"],
                            datetime.now(timezone.utc))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
