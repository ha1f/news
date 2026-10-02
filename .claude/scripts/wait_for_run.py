#!/usr/bin/env python3
"""GitHub Actions の run が完了するまで待ち、結果を機械判定できる形で返す。

使い方:
    python3 .claude/scripts/wait_for_run.py <workflow ファイル> <sha> [options]
    python3 .claude/scripts/wait_for_run.py jekyll-build-check.yml 7819e16c…   # PR の CI
    python3 .claude/scripts/wait_for_run.py pages.yml HEAD                     # マージ後の main
    python3 .claude/scripts/wait_for_run.py pages.yml <sha> --once             # 待たずに1回見る

なぜスクリプトなのか（#426）: 「run が終わるのを待つ」は決定的な状態確認で、
GUARDRAILS.md の設計原則どおりスクリプトに寄せる側。同じ事故（表示用に短縮した SHA を
API に渡し、HTTP 200 / `total_count: 0` を「まだ終わっていない」と読んで永久に待つ）が
3度観測され、3度目は警告をノートに書いた run 自身が踏んだ。

このスクリプトが構造的に塞ぐもの:

- **短縮 SHA で待ち続けられない。** 40桁でない引数は `git rev-parse` で展開を試み、
  展開できなければ即座に終了する（exit 2）。短縮 SHA のまま API を叩くことがない
- **「run が無い」と「run が未完了」を出力で区別する。** どちらも API 上は
  `total_count: 0` と `status != completed` で別物だが、素で引くと「空」に見える
- `gh` があれば `gh api`、無ければ REST 直叩き（cloud proxy が認証を注入する）。
  check_state.py / select_issues.py と同じ方式（#356）

出力: 1行の JSON を stdout に出す。
    {"state", "sha", "workflow", "repo", "run_id", "status", "conclusion",
     "html_url", "polls", "waited_seconds", "transport", "message"}

state と exit code:
    success     0  run が completed・conclusion が success
    failed      1  run が completed・conclusion が success 以外（failure/cancelled/…）
    usage       2  引数が不正、SHA を40桁にできない、API に到達できない
    not_found   3  待ち切っても run が現れなかった（SHA 違いか workflow が起動していない）
    running     4  run は在るが待ち切っても completed にならなかった
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.github.com"
API_TIMEOUT = 15
FULL_SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")

# 既定値は実測に合わせる（.claude/notes/develop-issue.md）:
#   - PR の jekyll-build-check は push から2分弱で completed（実測 2026-09-26）
#   - マージ後の pages.yml は run の出現がマージ後 2〜19 秒、completed まで 47〜77 秒
#     （実測 2026-09-22、12件）
# 30 秒間隔なら pages.yml は2〜3回、build は4回前後で収束する。
DEFAULT_INTERVAL = 30
DEFAULT_TIMEOUT = 600
# run の出現は実測で最大19秒。120 秒待って現れないのは「まだ」ではなく、SHA 違いか
# workflow が起動していない（base が main でない PR には CI が付かない等）ので、
# 全体の timeout を使い切る前に not_found として返す。
DEFAULT_APPEAR_TIMEOUT = 120

EXIT = {"success": 0, "failed": 1, "usage": 2, "not_found": 3, "running": 4}


def resolve_repo(explicit=None):
    """`owner/repo` を決める。--repo 指定が無ければ origin の remote URL から起こす。"""
    if explicit:
        if "/" not in explicit:
            raise ValueError(f"--repo は owner/repo の形で渡してください: {explicit}")
        owner, _, repo = explicit.partition("/")
        return owner, repo
    root = Path(__file__).resolve().parents[2]
    url = subprocess.run(["git", "-C", str(root), "config", "--get", "remote.origin.url"],
                         capture_output=True, text=True, check=True).stdout.strip()
    m = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$", url)
    if not m:
        raise ValueError(f"origin の remote URL から owner/repo を特定できません: {url}")
    return m.group("owner"), m.group("repo")


def expand_sha(raw, git_root=None):
    """40桁の SHA を返す。短縮 SHA・ref は git で展開し、できなければ ValueError。

    短縮 SHA をそのまま API に渡すと HTTP 200 / `total_count: 0` が返り、run 待ちの
    ループが永久に回る（実測: 7桁・12桁とも0件、40桁で1件）。ここで必ず弾く。"""
    candidate = (raw or "").strip()
    if not candidate:
        raise ValueError("SHA が空です")
    if FULL_SHA_RE.match(candidate):
        return candidate
    if FULL_SHA_RE.match(candidate.lower()):
        # 大文字混じりの40桁は API が受けるが、比較のため小文字に正規化する
        return candidate.lower()
    root = git_root or str(Path(__file__).resolve().parents[2])
    proc = subprocess.run(["git", "-C", root, "rev-parse", "--verify", f"{candidate}^{{commit}}"],
                          capture_output=True, text=True)
    expanded = proc.stdout.strip().lower()
    if proc.returncode != 0 or not FULL_SHA_RE.match(expanded):
        raise ValueError(
            f"40桁の SHA にできません: {candidate!r}\n"
            "表示用に短縮した SHA を API の入力に使い回さないでください。"
            "短縮 SHA はエラーにならず `total_count: 0` を返すため、run 待ちが永久に回ります。"
            "ローカルに無い commit は `git fetch` してから渡すか、40桁をそのまま渡してください。")
    return expanded


def runs_path(owner, repo, workflow, sha):
    """workflow と head_sha で run を引く REST のパス（純関数）。"""
    return (f"repos/{owner}/{repo}/actions/workflows/{workflow}/runs"
            f"?head_sha={sha}&per_page=100")


def pick_latest(payload):
    """runs API のレスポンスから最新の run を選ぶ（純関数）。

    一覧は新しい順に返るが、順序に頼らず `run_attempt` → `created_at` で最大を取る
    （再実行した run を取り違えないため）。`total_count` は見ず `workflow_runs` の実体で
    判定する（total_count だけが非 0 のレスポンスを待ちの根拠にしない）。"""
    runs = (payload or {}).get("workflow_runs") or []
    if not runs:
        return None
    return max(runs, key=lambda run: (run.get("run_attempt") or 0, run.get("created_at") or ""))


def classify(run):
    """run から (state, conclusion) を決める（純関数）。run が None なら not_found。"""
    if run is None:
        return "not_found", None
    conclusion = run.get("conclusion")
    if run.get("status") != "completed":
        return "running", conclusion
    return ("success" if conclusion == "success" else "failed"), conclusion


def gh_json(path):
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:300])
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def api_json(path):
    """REST 直叩き。cloud proxy が GitHub 認証を注入するのでトークン無しでも通る。"""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ha1f-news-daily-loop"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{API_BASE}/{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT) as resp:
            body = resp.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"GitHub API {error.code}: "
            f"{error.read().decode('utf-8', 'replace')[:200]}") from error
    return json.loads(body) if body else None


def make_fetcher(prefer_gh=True):
    """(path -> payload, transport 名) を返す。gh が落ちたら REST に自動で落ちる。"""
    state = {"transport": "gh" if (prefer_gh and shutil.which("gh")) else "rest"}

    def fetch(path):
        if state["transport"] == "gh":
            try:
                return gh_json(path)
            except (RuntimeError, json.JSONDecodeError, OSError):
                # gh が使えない環境（GraphQL 403 / token 不正など）では REST に落ちる。
                # 一度落ちたら以後も REST を使う（毎回の往復を無駄にしない）
                state["transport"] = "rest"
        return api_json(path)

    return fetch, state


def wait(fetch, owner, repo, workflow, sha, interval, timeout, appear_timeout, once, log=None):
    """run が completed になるまで待つ。戻り値は出力用の dict。"""
    path = runs_path(owner, repo, workflow, sha)
    started = time.monotonic()
    polls, run = 0, None
    while True:
        payload = fetch(path)
        polls += 1
        run = pick_latest(payload)
        state, conclusion = classify(run)
        waited = round(time.monotonic() - started, 1)
        if log:
            log(f"poll {polls}: state={state} conclusion={conclusion} waited={waited}s")
        if state in ("success", "failed") or once:
            break
        if state == "not_found" and waited >= appear_timeout:
            break
        if waited >= timeout:
            break
        time.sleep(interval)

    state, conclusion = classify(run)
    waited = round(time.monotonic() - started, 1)
    if state == "not_found":
        message = (f"{workflow} の run が head_sha={sha} に見つかりません。"
                   "SHA が違うか、workflow がこの commit で起動していません"
                   "（base が main でない PR には CI が付かない等）。"
                   if not once else
                   f"{workflow} の run はまだ head_sha={sha} に現れていません。")
    elif state == "running":
        message = (f"{workflow} の run は在りますが status={run.get('status')} のままです"
                   f"（{waited}s 待機）。待てば完了します。")
    else:
        message = f"{workflow} の run は completed / {conclusion} です。"
    return {
        "state": state,
        "sha": sha,
        "workflow": workflow,
        "repo": f"{owner}/{repo}",
        "run_id": (run or {}).get("id"),
        "status": (run or {}).get("status"),
        "conclusion": conclusion,
        "html_url": (run or {}).get("html_url"),
        "polls": polls,
        "waited_seconds": waited,
        "message": message,
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="GitHub Actions の run が完了するまで待ち、結果を JSON で返す",
        epilog="state と exit code: success 0 / failed 1 / usage 2 / not_found 3 / running 4")
    parser.add_argument("workflow", help="workflow のファイル名（例 pages.yml）または ID")
    parser.add_argument("sha", help="head SHA。40桁でなければ git rev-parse で展開を試みる")
    parser.add_argument("--repo", help="owner/repo（既定は origin の remote URL から解決）")
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                        help=f"ポーリング間隔（秒、既定 {DEFAULT_INTERVAL}）")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"全体の待ち上限（秒、既定 {DEFAULT_TIMEOUT}）")
    parser.add_argument("--appear-timeout", type=float, default=DEFAULT_APPEAR_TIMEOUT,
                        help=f"run が現れるまでの上限（秒、既定 {DEFAULT_APPEAR_TIMEOUT}）。"
                             "超えたら not_found で返す")
    parser.add_argument("--once", action="store_true", help="待たずに1回だけ状態を見る")
    parser.add_argument("--no-gh", action="store_true", help="gh を使わず REST 直叩きにする")
    parser.add_argument("--quiet", action="store_true", help="進捗を stderr に出さない")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        owner, repo = resolve_repo(args.repo)
        sha = expand_sha(args.sha)
    except (ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({"state": "usage", "message": str(error)}, ensure_ascii=False))
        print(error, file=sys.stderr)
        return EXIT["usage"]

    fetch, transport = make_fetcher(prefer_gh=not args.no_gh)
    log = None if args.quiet else (lambda line: print(line, file=sys.stderr))
    try:
        result = wait(fetch, owner, repo, args.workflow, sha,
                      interval=args.interval, timeout=args.timeout,
                      appear_timeout=args.appear_timeout, once=args.once, log=log)
    except (RuntimeError, OSError) as error:
        print(json.dumps({"state": "usage", "sha": sha, "workflow": args.workflow,
                          "message": f"run を取得できません: {error}"}, ensure_ascii=False))
        print(error, file=sys.stderr)
        return EXIT["usage"]
    result["transport"] = transport["transport"]
    print(json.dumps(result, ensure_ascii=False))
    return EXIT[result["state"]]


if __name__ == "__main__":
    sys.exit(main())
