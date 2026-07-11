#!/usr/bin/env python3
"""daily-loop: 評価前の配信状態・ループ健全性を機械判定して JSON で出力する。

使い方: python3 check_state.py
出力: {"config", "today", "post_in_main", "status_issue", "open_daily_loop_issues",
       "health", "recent_status_comments"}
  - health: 前日の各ステージ (evaluate/develop/review) の start/end/ok 集計。
    status issue コメントの1行目 JSON（GUARDRAILS.md 参照）から機械判定する
起票するかどうかの判断はエージェントが行う。
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUS_TITLE = "daily-loop status"
STAGES = ("evaluate", "develop", "review")
JST = timezone(timedelta(hours=9))
COMMENT_LIMIT = 10
BODY_LIMIT = 200


def gh_json(path, ok_404=False):
    proc = subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True)
    if proc.returncode != 0:
        if ok_404 and "404" in proc.stderr:
            return None
        raise RuntimeError(proc.stderr.strip())
    return json.loads(proc.stdout)


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


def summarize_issues(issues):
    """open issue から status issue 番号と daily-loop issue 数を出す（純関数）"""
    status_issue, daily_loop_count = None, 0
    for issue in issues:
        if "pull_request" in issue:
            continue
        if STATUS_TITLE in issue["title"]:
            status_issue = issue["number"]
            continue
        if any(label["name"] == "daily-loop" for label in issue["labels"]):
            daily_loop_count += 1
    return status_issue, daily_loop_count


def parse_status_records(comments):
    """コメント1行目の JSON を記録として取り出す（純関数）"""
    records = []
    for comment in comments:
        body = comment.get("body") or ""
        try:
            data = json.loads(body.splitlines()[0]) if body else None
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("stage") in STAGES:
            records.append({**data, "created_at": comment["created_at"]})
    return records


def summarize_health(records, today):
    """前日 (JST) の各ステージの start/end/ok を集計する（純関数）"""
    yesterday = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    stages = {stage: {"start": False, "end": False, "ok": None} for stage in STAGES}
    for record in records:
        created = datetime.fromisoformat(record["created_at"].replace("Z", "+00:00"))
        if created.astimezone(JST).strftime("%Y-%m-%d") != yesterday:
            continue
        entry = stages[record["stage"]]
        if record.get("phase") == "start":
            entry["start"] = True
        elif record.get("phase") == "end":
            entry["end"] = True
            entry["ok"] = record.get("ok")
    return {
        "yesterday": yesterday,
        "stages": stages,
        "incomplete": [s for s, v in stages.items() if v["start"] and not v["end"]],
        "failed": [s for s, v in stages.items() if v["ok"] is False],
        "no_records": not any(v["start"] or v["end"] for v in stages.values()),
    }


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    today = datetime.now(JST).strftime("%Y-%m-%d")
    post = gh_json(f"repos/{{owner}}/{{repo}}/contents/_posts/{today}-news.md", ok_404=True)
    issues = gh_json("repos/{owner}/{repo}/issues?state=open&per_page=100")
    status_issue, daily_loop_count = summarize_issues(issues)
    comments = []
    if status_issue:
        comments = gh_json(
            f"repos/{{owner}}/{{repo}}/issues/{status_issue}/comments?per_page=100")
    json.dump({
        "config": config,
        "today": today,
        "post_in_main": post is not None,
        "status_issue": status_issue,
        "open_daily_loop_issues": daily_loop_count,
        "health": summarize_health(parse_status_records(comments), today),
        "recent_status_comments": [
            {"created_at": c["created_at"], "body": c["body"][:BODY_LIMIT]}
            for c in comments[-COMMENT_LIMIT:]
        ],
    }, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
