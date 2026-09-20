#!/usr/bin/env python3
"""daily-loop: 実装候補 issue を機械抽出して JSON で出力する。

使い方:
  python3 select_issues.py                    # gh CLI があれば gh、無ければ REST 直叩きでデータ取得
  python3 select_issues.py --stdin < data.json # 保険。MCP 等で取得した JSON を渡す

--stdin の JSON に "collaborators" (login の文字列リスト) を含めると、
issue の author_association が欠落していても author が collaborator なら
信頼済みと判定する (MCP list_issues が author_association を返さない問題の回避策)。

出力: {"config", "status_issue", "in_progress", "backlog"}
  - in_progress: open な linked PR を持つ issue（要対応かはエージェントが判断）
    linked_open_prs の各要素は {number, draft, hold}。hold は人間の判断待ちの印
  - backlog: linked PR の無い issue。作成日の古い順
フィルタ（collaborator 名義のみ・hold と status issue を除外）は適用済み。
優先度・着手順の判断はエージェントが issue を読んで行う。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
STATUS_TITLE = "daily-loop status"
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)
BRANCH_ISSUE_RE = re.compile(r"(?:^|/)(\d+)[-_]")
API_BASE = "https://api.github.com"
API_TIMEOUT = 15


def gh_json(path):
    out = subprocess.run(["gh", "api", "--paginate", path],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def resolve_repo():
    """git remote の origin URL から owner/repo を取り出す（gh 不在時、決定的に解決する）。"""
    url = subprocess.run(["git", "config", "--get", "remote.origin.url"],
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


def api_json(path):
    """gh CLI 不在の環境向けに GitHub REST API を直接叩く（全ページ取得）。

    cloud proxy が素の HTTPS にも GitHub 認証を注入するため、トークンが無くても動く
    （実測 2026-09-20、.claude/notes/develop-issue.md）。GH_TOKEN / GITHUB_TOKEN が
    環境にあれば Authorization ヘッダに載せる。"""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ha1f-news-daily-loop"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request_url = f"{API_BASE}/{path}"
    items, page = [], 1
    while request_url:
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(request_url, headers=headers),
                    timeout=API_TIMEOUT) as resp:
                body = resp.read()
                link = resp.headers.get("Link")
        except urllib.error.HTTPError as error:
            raise RuntimeError(
                f"GitHub API {error.code} {request_url}: "
                f"{error.read().decode('utf-8', 'replace')[:300]}") from error
        items.extend(json.loads(body))
        if "next" in parse_link_header(link):
            page += 1
            request_url = with_page(f"{API_BASE}/{path}", page)
        else:
            request_url = None
    return items


def fetch_via_api():
    """gh CLI 不在の環境向けに GitHub REST API を直接叩いて取得する。"""
    owner, repo = resolve_repo()
    issues = api_json(f"repos/{owner}/{repo}/issues?state=open&per_page=100")
    prs = api_json(f"repos/{owner}/{repo}/pulls?state=open&per_page=100")
    return issues, prs


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
        # MCP の list_pull_requests は labels を文字列リストで返し、ラベルが無い PR では
        # キー自体を返さない。gh CLI は dict のリスト。どちらでも同じ集合になるようにする
        pr_labels = {(label["name"] if isinstance(label, dict) else label)
                     for label in pr.get("labels", [])}
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
                "hold": "hold" in pr_labels,
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


USAGE_WITHOUT_GH = """gh CLI も REST 直叩きも使えませんでした。MCP ツール等でデータを取得し、--stdin で渡してください:

  python3 .claude/skills/select-and-develop/scripts/select_issues.py --stdin < data.json

data.json の形:
  {"issues": [...],          # list_issues (state=OPEN) の結果
   "prs": [...],             # list_pull_requests (state=open) の結果
   "collaborators": ["..."]}  # list_repository_collaborators の login のリスト (任意)
"""


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())

    # エージェントの Bash ツールから起動すると stdin は常に非 tty になるため、
    # tty 判定では JSON を渡していなくても stdin モードに入ってしまう (PR #329 と同じ罠)
    if "--stdin" in sys.argv:
        try:
            data = json.load(sys.stdin)
            issues = data["issues"]
            prs = data["prs"]
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"--stdin に渡された JSON を読めません: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
        collaborators = data.get("collaborators")
    elif shutil.which("gh"):
        try:
            issues, prs = fetch_via_gh()
        except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
            print(f"gh でのデータ取得に失敗しました: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
        collaborators = None
    else:
        try:
            issues, prs = fetch_via_api()
        except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
            print(f"REST API でのデータ取得に失敗しました: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
        collaborators = None

    status_issue, in_progress, backlog = build_candidates(issues, prs, collaborators)
    json.dump({
        "config": config,
        "status_issue": status_issue,
        "in_progress": in_progress,
        "backlog": backlog,
    }, sys.stdout, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
