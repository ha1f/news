#!/usr/bin/env python3
"""daily-loop: 評価前の配信状態・ループ健全性を機械判定して JSON で出力する。

使い方: python3 check_state.py
出力: {"config", "today", "post_in_main", "publish_in_progress", "pages_url",
       "pages_build", "status_issue", "open_issues", "health",
       "recent_status_comments"}
  - health: 前日の各ステージ (evaluate/develop/review) の start/end/ok 集計。
    status issue コメントの1行目 JSON（GUARDRAILS.md 参照）から機械判定する。
    missing = start も end も無いステージ（trigger 停止やセッション起動失敗の疑い）
  - pages_build: 最新の pages.yml run（main のビルドが壊れていないかの判定材料）
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


def gh_json(path, ok_404=False, paginate=True):
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + [path]
    proc = subprocess.run(cmd, capture_output=True, text=True)
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
    """open issue から status issue 番号と issue 数（status 除く）を出す（純関数）"""
    status_issue, open_count = None, 0
    for issue in issues:
        if "pull_request" in issue:
            continue
        if STATUS_TITLE in issue["title"]:
            status_issue = issue["number"]
            continue
        open_count += 1
    return status_issue, open_count


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
    no_records = not any(v["start"] or v["end"] for v in stages.values())
    return {
        "yesterday": yesterday,
        "stages": stages,
        "incomplete": [s for s, v in stages.items() if v["start"] and not v["end"]],
        "failed": [s for s, v in stages.items() if v["ok"] is False],
        "missing": [] if no_records else
                   [s for s, v in stages.items() if not v["start"] and not v["end"]],
        "no_records": no_records,
    }


def assemble_output(config, today, post_exists, pages, pages_build,
                    prs, issues, comments):
    """取得済みデータから出力 JSON を組み立てる（純関数）。"""
    publish_in_progress = (
        any(pr.get("head", {}).get("ref", "").startswith("pages/") for pr in prs)
        or (pages_build is not None and pages_build.get("status") != "completed"))
    status_issue, open_count = summarize_issues(issues)
    records = parse_status_records(comments)
    return {
        "config": config,
        "today": today,
        "post_in_main": post_exists,
        "publish_in_progress": publish_in_progress,
        "pages_url": (pages or {}).get("html_url"),
        "pages_build": pages_build,
        "status_issue": status_issue,
        "open_issues": open_count,
        "health": summarize_health(records, today),
        "recent_status_comments": [
            {"created_at": c["created_at"], "body": c["body"][:BODY_LIMIT]}
            for c in comments[-COMMENT_LIMIT:]
        ],
    }


def fetch_via_gh(config, today, now):
    """gh CLI でデータを取得し assemble_output に渡す。"""
    post = gh_json(f"repos/{{owner}}/{{repo}}/contents/_posts/{today}-news.md", ok_404=True)
    pages = gh_json("repos/{owner}/{repo}/pages", ok_404=True, paginate=False)
    runs = gh_json("repos/{owner}/{repo}/actions/workflows/pages.yml/runs?per_page=1",
                   ok_404=True, paginate=False)
    latest_run = (runs or {}).get("workflow_runs") or []
    pages_build = None
    if latest_run:
        pages_build = {key: latest_run[0][key]
                       for key in ("status", "conclusion", "head_sha", "updated_at")}
    prs = gh_json("repos/{owner}/{repo}/pulls?state=open&per_page=100")
    issues = gh_json("repos/{owner}/{repo}/issues?state=open&per_page=100")
    status_issue, _ = summarize_issues(issues)
    comments = []
    if status_issue:
        since = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()
        comments = gh_json(
            f"repos/{{owner}}/{{repo}}/issues/{status_issue}/comments"
            f"?per_page=100&since={since}")
    return assemble_output(config, today, post is not None, pages, pages_build,
                           prs, issues, comments)


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    now = datetime.now(JST)
    today = now.strftime("%Y-%m-%d")

    if "--stdin" in sys.argv or not sys.stdin.isatty():
        data = json.load(sys.stdin)
        result = assemble_output(
            config, today,
            post_exists=data["post_exists"],
            pages=data.get("pages"),
            pages_build=data.get("pages_build"),
            prs=data.get("prs", []),
            issues=data.get("issues", []),
            comments=data.get("comments", []),
        )
    else:
        result = fetch_via_gh(config, today, now)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
