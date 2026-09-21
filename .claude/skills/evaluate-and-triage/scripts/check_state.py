#!/usr/bin/env python3
"""daily-loop: 評価前の配信状態・ループ健全性を機械判定して JSON で出力する。

使い方: python3 check_state.py          # gh CLI があれば gh、無ければ REST 直叩きでデータを取得する
      cat state.json | python3 check_state.py --stdin  # 保険。渡すデータは手動で用意する
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
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUS_TITLE = "daily-loop status"
STAGES = ("evaluate", "develop", "review")
JST = timezone(timedelta(hours=9))
COMMENT_LIMIT = 10
BODY_LIMIT = 200
API_BASE = "https://api.github.com"
API_TIMEOUT = 15

NO_GH_HINT = """gh CLI も REST 直叩きも使えませんでした。MCP ツール等でデータを取得し、--stdin で渡してください:

  python3 check_state.py --stdin <<'EOF'
  {"post_exists": true,
   "pages": {"html_url": "..."},
   "pages_build": {"status": "completed", "conclusion": "success", ...},
   "prs": [...], "issues": [...], "comments": [...]}
  EOF

取得元とハマりどころは .claude/skills/evaluate-and-triage/SKILL.md の Step 0
「`--stdin` で渡すときの取得元」を参照。"""


def gh_json(path, ok_404=False, ok_missing=(), paginate=True):
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + [path]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        # gh は HTTP ステータスを本文でなくメッセージ先頭に出す。素の部分文字列一致だと
        # URL やメッセージ中の数字を拾うので、`HTTP <code>` の形に絞る
        if ((ok_404 and re.search(r"HTTP 404\b", proc.stderr))
                or any(re.search(rf"HTTP {code}\b", proc.stderr) for code in ok_missing)):
            return None
        raise RuntimeError(proc.stderr.strip())
    return json.loads(proc.stdout)


def resolve_repo():
    """git remote の origin URL から owner/repo を取り出す（gh 不在時、決定的に解決する）。

    cwd がどこでも同じ答えになるよう、repo root を明示して git に問い合わせる。"""
    root = Path(__file__).resolve().parents[4]
    url = subprocess.run(["git", "-C", str(root), "config", "--get", "remote.origin.url"],
                         capture_output=True, text=True, check=True).stdout.strip()
    m = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$", url)
    if not m:
        raise RuntimeError(f"origin の remote URL から owner/repo を特定できません: {url}")
    return m.group("owner"), m.group("repo")


def parse_link_header(header):
    """RFC 5988 の Link ヘッダーを {rel: url} にする（純関数）。"""
    links = {}
    for part in (header or "").split(","):
        m = re.match(r'\s*<([^>]+)>;\s*rel="([^"]+)"', part)
        if m:
            links[m.group(2)] = m.group(1)
    return links


def with_page(url, page):
    """url に page=N を足す（既にあれば置き換える）純関数。

    GitHub の Link ヘッダーが返す next の URL は `/repositories/{id}/...` 形式で、
    proxy がこの形を 403 で弾く（実測 2026-09-20）。ヘッダの URL をそのまま辿らず、
    ページ番号だけ次に進めて `/repos/{owner}/{repo}/...` 形式の URL を自前で組み立てる。"""
    if re.search(r"[?&]page=\d+", url):
        return re.sub(r"([?&]page=)\d+", r"\g<1>" + str(page), url)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}page={page}"


def api_json(path, ok_404=False, ok_missing=(), paginate=True):
    """gh CLI 不在の環境向けに GitHub REST API を直接叩く。

    cloud proxy が素の HTTPS にも GitHub 認証を注入するため、トークンが無くても動く
    （実測 2026-09-20、.claude/notes/develop-issue.md）。GH_TOKEN / GITHUB_TOKEN が
    環境にあれば Authorization ヘッダに載せる。

    `ok_missing` は「データが無い」以外の理由でも None 扱いにしたい HTTP ステータスの集合。
    例: `/repos/{owner}/{repo}/pages` は proxy 自体が 403 で塞ぐエンドポイントで（実測
    2026-09-20）、gh CLI 環境でも呼び出し側は元々 `pages_url` 欠落を許容している
    （evaluate-and-triage/SKILL.md 参照）。"""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ha1f-news-daily-loop"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request_url = f"{API_BASE}/{path}"
    items, is_list, page = [], False, 1
    while request_url:
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(request_url, headers=headers),
                    timeout=API_TIMEOUT) as resp:
                body = resp.read()
                link = resp.headers.get("Link")
        except urllib.error.HTTPError as error:
            if (ok_404 and error.code == 404) or error.code in ok_missing:
                return None
            raise RuntimeError(
                f"GitHub API {error.code} {request_url}: "
                f"{error.read().decode('utf-8', 'replace')[:300]}") from error
        data = json.loads(body) if body else None
        if not isinstance(data, list):
            return data
        items.extend(data)
        is_list = True
        if paginate and "next" in parse_link_header(link):
            page += 1
            request_url = with_page(f"{API_BASE}/{path}", page)
        else:
            request_url = None
    return items if is_list else None


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
    """open issue から status issue 番号と issue 数（status・bot 除く）を出す（純関数）

    bot の issue（Renovate の Dependency Dashboard 等）は実装依頼でなくトラッキング用の
    issue なので、open_issue_cap の数に入れない（bot だから信頼しないという意味ではない。
    GUARDRAILS「状態の持ち方」参照）。"""
    status_issue, open_count = None, 0
    for issue in issues:
        if "pull_request" in issue:
            continue
        if STATUS_TITLE in issue["title"]:
            status_issue = issue["number"]
            continue
        if (issue.get("user") or {}).get("type") == "Bot":
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


def since_param(now):
    """前日 0時 (JST) を GitHub の `since` に渡せる形にする（純関数）。

    `isoformat()` の `+09:00` をそのままクエリに入れると、URL の `+` がスペースとして
    解釈されて別の時刻になる。しかも GitHub は壊れた値を 422 で弾かずに黙って受け取る
    （実測 2026-09-20: 実効カットオフが前日 00:00 JST → 16:00 JST に16時間ずれ、
    10時の evaluate が毎日 health の missing に落ちた）。UTC の `Z` 形式なら
    エスケープが要らず、gh 経路・REST 経路の両方をまとめて直せる。"""
    return ((now - timedelta(days=1))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))


def fetch_data(fetch_json, config, today, now):
    """`repos/{owner}/{repo}/` 以下の相対パスを取る fetch_json を受け取り、
    gh CLI 経由でも REST 直叩き経由でも同じ組み立てをする。"""
    post = fetch_json(f"contents/_posts/{today}-news.md", ok_404=True)
    pages = fetch_json("pages", ok_404=True, ok_missing=(403,), paginate=False)
    runs = fetch_json("actions/workflows/pages.yml/runs?per_page=1", ok_404=True, paginate=False)
    latest_run = (runs or {}).get("workflow_runs") or []
    pages_build = None
    if latest_run:
        pages_build = {key: latest_run[0][key]
                       for key in ("status", "conclusion", "head_sha", "updated_at")}
    prs = fetch_json("pulls?state=open&per_page=100") or []
    issues = fetch_json("issues?state=open&per_page=100") or []
    status_issue, _ = summarize_issues(issues)
    comments = []
    if status_issue:
        comments = fetch_json(
            f"issues/{status_issue}/comments?per_page=100&since={since_param(now)}") or []
    return assemble_output(config, today, post is not None, pages, pages_build,
                           prs, issues, comments)


def fetch_via_gh(config, today, now):
    """gh CLI でデータを取得する。"""
    def fetch_json(path, **kwargs):
        return gh_json("repos/{owner}/{repo}/" + path, **kwargs)
    return fetch_data(fetch_json, config, today, now)


def fetch_via_api(config, today, now):
    """gh CLI 不在の環境向けに GitHub REST API を直接叩いて取得する。"""
    owner, repo = resolve_repo()
    def fetch_json(path, **kwargs):
        return api_json(f"repos/{owner}/{repo}/{path}", **kwargs)
    return fetch_data(fetch_json, config, today, now)


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    now = datetime.now(JST)
    today = now.strftime("%Y-%m-%d")

    if "--stdin" in sys.argv:
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
    elif shutil.which("gh"):
        result = fetch_via_gh(config, today, now)
    else:
        try:
            result = fetch_via_api(config, today, now)
        except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
            print(f"REST API でのデータ取得に失敗しました: {type(error).__name__} {error}\n",
                  file=sys.stderr)
            sys.exit(NO_GH_HINT)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
