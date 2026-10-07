#!/usr/bin/env python3
"""daily-loop: 実装候補 issue を機械抽出して JSON で出力する。

使い方:
  python3 select_issues.py                    # gh CLI があれば gh、無ければ REST 直叩きでデータ取得
  python3 select_issues.py --stdin < data.json # 保険。MCP 等で取得した JSON を渡す

--stdin の JSON に "collaborators" (login の文字列リスト) を含めると、
issue の author_association が欠落していても author が collaborator なら
信頼済みと判定する (MCP list_issues が author_association を返さない問題の回避策)。

出力: {"config", "status_issue", "open_issues", "in_progress", "backlog"}
  - open_issues: open issue の総数（status issue と bot の issue を除く。`hold` は数える）。
    `config.open_issue_cap` と突き合わせる用。数え方の正本は evaluate ステージの
    check_state.py:summarize_issues で、ここはそれを読み込んで使う
  - open_issues_note: open_issues をそのまま信じてよくないときだけ出る1行。
    数えられなかったときは open_issues が null になる（候補の出力は止めない）
  - in_progress: open な linked PR を持つ issue（要対応かはエージェントが判断）
    linked_open_prs の各要素は {number, draft, hold}。hold は人間の判断待ちの印
  - backlog: linked PR の無い issue。作成日の古い順
  - 各 issue の linked_merged_prs: **マージ済み**で、その issue を本文で `Closes`/`Refs` 等
    でリンクしている PR（{number, title, merged_at}）。`Refs` で issue を閉じずに一部だけ
    入れた PR は open でも closed でもなく本文にも出ないので、これが無いと「切り出し A は
    済んでいる」と気づけず作り直す。issue の timeline から取るので全期間が見える
    （`pulls?state=closed` の1ページ目は直近14日しか覆わない）。空なら該当なし
  - linked_merged_prs_note: timeline を取れなかったときだけ出る1行（候補の出力は止めない。
    その場合 linked_merged_prs は付かない＝「無い」とは読めない）
  - recent_status_records: status issue コメント1行目の stage レコードを直近 RECORDS_LIMIT 件
    （古い順）。前段 run の結論（evaluate のグルーミング判断等）をこの run が読み返す経路。
    読み方の正本は check_state.py:parse_status_records で、ここはそれを読み込んで使う
  - recent_status_records_note: レコードを取れなかったときだけ出る1行（候補の出力は止めない）
フィルタ（collaborator 名義のみ・hold と status issue を除外）は適用済み。
優先度・着手順の判断はエージェントが issue を読んで行う。
"""
import importlib.util
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

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
STATUS_TITLE = "daily-loop status"
BRANCH_ISSUE_RE = re.compile(r"(?:^|/)(\d+)[-_]")
API_BASE = "https://api.github.com"
API_TIMEOUT = 15
# 1日あたりのレコードは最大10件（evaluate 1 run + develop / review 各2 run の start/end）。
# 12 なら当日ぶんは常に全部入り、前日の終わりも数件残る
RECORDS_LIMIT = 12
RECORDS_SINCE_DAYS = 2  # status issue コメントを何日ぶん取るか


def gh_json(path, paginate=True):
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + [path]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    return json.loads(out)


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


def api_json(path):
    """gh CLI 不在の環境向けに GitHub REST API を直接叩く（全ページ取得）。

    cloud proxy が素の HTTPS にも GitHub 認証を注入するため、トークンが無くても動く
    （実測 2026-09-20、.claude/notes/develop-issue.md）。GH_TOKEN / GITHUB_TOKEN が
    環境にあれば Authorization ヘッダに載せる。

    この取得部（resolve_repo / parse_link_header / with_page / api_json）は
    check_state.py にも同じものがある。スキルのスクリプトを単体で動かせる状態に
    保つための意図的な重複で、3つ目の複製が要るときに共有モジュール化を判断する。"""
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


def fetch_status_comments_via_api(status_issue, since):
    owner, repo = resolve_repo()
    return api_json(f"repos/{owner}/{repo}/issues/{status_issue}/comments"
                    f"?per_page=100&since={since}")


TIMELINE_PAGE_SIZE = 100
TIMELINE_MAX_PAGES = 20  # 暴走防止。2,000 イベントを超える issue は想定しない


def collect_pages(get_page):
    """get_page(N) -> list を、1ページが満杯でなくなるまで N=1,2,… と辿って連結する（純関数）。

    timeline は古い順に返るので、100 件で打ち切ると**最も新しい参照から**落ちる
    （= 既に作業済みの可能性が最も高い直近の PR が消える）。`gh api --paginate` は
    Link ヘッダの `/repositories/{id}/...` を辿って proxy に 403 で弾かれるため、
    ページ番号を自前で進める（`with_page` と同じ理由）。"""
    items = []
    for page in range(1, TIMELINE_MAX_PAGES + 1):
        chunk = get_page(page)
        items.extend(chunk)
        if len(chunk) < TIMELINE_PAGE_SIZE:
            break
    return items


def timeline_path(owner, repo, number):
    return f"repos/{owner}/{repo}/issues/{number}/timeline?per_page={TIMELINE_PAGE_SIZE}"


def fetch_timeline_via_api(number):
    # api_json は Link ヘッダの有無でページ番号を自前で進めるので 100 件超でも全部取れる
    owner, repo = resolve_repo()
    return api_json(timeline_path(owner, repo, number))


def fetch_timeline_via_gh(number):
    path = timeline_path("{owner}", "{repo}", number)
    return collect_pages(lambda page: gh_json(with_page(path, page), paginate=False))


def merged_prs_linking(events, issue_number):
    """issue の timeline から、その issue を本文でリンクしているマージ済み PR を返す（純関数）。

    素の cross-reference は「番号に触れただけ」の PR も拾う（#354 で4件中1件、#362 で8件中1件が
    正解）ので、open PR の判定（build_candidates）と同じ LINK_RE を本文に当てて絞る。
    `source.issue.pull_request` を持たない（PR でない）参照と、マージされていない PR は落ちる。"""
    found = {}
    for event in events:
        if event.get("event") != "cross-referenced":
            continue
        source = (event.get("source") or {}).get("issue") or {}
        merged_at = (source.get("pull_request") or {}).get("merged_at")
        if not merged_at:
            continue
        linked = {int(m.group(1)) for m in LINK_RE.finditer(source.get("body") or "")}
        if issue_number in linked:
            found[source["number"]] = {"number": source["number"],
                                       "title": source.get("title", ""),
                                       "merged_at": merged_at}
    return sorted(found.values(), key=lambda pr: pr["merged_at"])


def attach_merged_prs(entries, timelines, fetch_timeline):
    """各候補に linked_merged_prs を付け、(注記 or None) を返す。

    timelines: --stdin で渡された {issue 番号(文字列): イベント配列}（無ければ None）。
    取れなかった issue には付けない（空リストにすると「該当なし」と区別がつかない）。
    付随値なので、失敗しても候補の出力は止めない。"""
    failed = []
    for entry in entries:
        number = entry["number"]
        try:
            if timelines is not None:
                events = timelines[str(number)]
            elif fetch_timeline is not None:
                events = fetch_timeline(number)
            else:
                raise KeyError(number)
        except Exception as error:  # ネットワーク・権限・--stdin に当該 issue が無い
            failed.append(f"#{number} ({type(error).__name__})")
            continue
        entry["linked_merged_prs"] = merged_prs_linking(events, number)
    if failed:
        return ("timeline を取得できなかった issue は linked_merged_prs を付けていません"
                f"（マージ済みの関連 PR が無いとは読めない）: {', '.join(failed)}")
    return None


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


def load_check_state():
    """evaluate ステージの `check_state.py` を読み込む（借りる関数はここから取る）。

    open issue の数え方（status issue と bot の issue の除外）と status issue コメントの
    読み方は evaluate ステージが正本を持っている。同じルールをここに書き写すと、片方を
    変えたときにもう片方が黙って古くなるので、関数ごと読み込んで正本を1つに保つ
    （GUARDRAILS「決定的な処理はスクリプトに寄せる」）。

    相対 import にしないのは、このスクリプトがエージェントの Bash から任意の cwd で
    単体起動されるため（`sys.path` は起動 cwd に依存する）。GUARDRAILS.md を読むのと
    同じく、`__file__` からの絶対パスで解決する。
    """
    path = (Path(__file__).resolve().parents[2]
            / "evaluate-and-triage" / "scripts" / "check_state.py")
    # spec_from_file_location は拡張子が .py なら、ファイルが無くても spec を返す。
    # 欠落は exec_module の FileNotFoundError として出るので、ここでは弾かない
    spec = importlib.util.spec_from_file_location("daily_loop_check_state", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_pr_links():
    """PR body から linked issue を取り出す正本 `.claude/scripts/pr_links.py` を読み込む。

    正本を1つにしているのは、同じ正規表現を review 側と develop 側に写した結果、
    コード引用まで linked issue に数える欠陥が両方に生まれたため (#473)。
    相対 import にしないのは `load_check_state` と同じ理由（任意の cwd から
    単体起動される）。

    読み込みに失敗したら黙って素の正規表現に戻したりはせず、そのまま落とす。
    linked issue の有無はこのスクリプトの主要な出力（in_progress / backlog の
    振り分け）そのものなので、劣化した値を返すほうが危ない。
    """
    path = Path(__file__).resolve().parents[3] / "scripts" / "pr_links.py"
    spec = importlib.util.spec_from_file_location("daily_loop_pr_links", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extract_linked_issues = load_pr_links().extract_linked_issues


def load_summarize_issues():
    """open issue の数え方の正本 `check_state.py:summarize_issues` を読み込む。"""
    return load_check_state().summarize_issues


def bot_exclusion_reliable(issues):
    """渡されたデータで bot の issue を除外できるか（純関数）。

    MCP の list_issues は `user` を落とすことがあり、その場合 bot の issue
    （Renovate の Dependency Dashboard 等）を除外できず open_issues が過大になる
    （evaluate-and-triage/SKILL.md に同じ実測がある）。数え方はここに持たず、
    「数えるのに必要な情報が揃っているか」だけを見る。
    """
    return all((issue.get("user") or {}).get("type") for issue in issues)


def count_open_issues(issues):
    """(open issue 数, 注記) を返す。数えられなければ (None, 理由)。

    cap と突き合わせるための付随値なので、ここが失敗しても候補の出力は止めない
    （他ステージのスクリプトの健全性で develop が止まると、直せる run が来なくなる）。
    """
    try:
        _, open_issues, _ = load_summarize_issues()(issues)
    except Exception as error:  # 正本が読めない・壊れている
        return None, (f"open issue の数え方の正本 (check_state.py) を読めませんでした: "
                      f"{type(error).__name__} {error}")
    if not bot_exclusion_reliable(issues):
        return open_issues, ("渡されたデータに user.type が無く bot の issue を除外できないため、"
                             "この値は過大になりえます（参考値）")
    return open_issues, None


def collect_recent_records(comments, now=None):
    """(直近の stage レコード, 注記) を返す。読めなければ ([], 理由)。

    前段 run の結論を後段が読み返すための付随値なので、ここが失敗しても候補の出力は
    止めない（count_open_issues と同じ方針）。

    RECORDS_SINCE_DAYS より古いレコードは落とす。コメントは古い順に返るので、`since`
    を付けずに1ページ目を渡すと最古の100件（この repo では2ヶ月前）が入り、後段が
    それを「直近の結論」として読む。空になるより悪いので、ここで年齢を見て弾く。
    """
    try:
        parse = load_check_state().parse_status_records
    except Exception as error:  # 正本が読めない・壊れている
        return [], (f"status issue コメントの読み方の正本 (check_state.py) を読めませんでした: "
                    f"{type(error).__name__} {error}")
    try:
        records = parse(comments)
    except Exception as error:  # 渡されたコメントの形が想定と違う
        return [], (f"渡された status issue コメントから stage レコードを取り出せませんでした: "
                    f"{type(error).__name__} {error}")
    cutoff = since_param(now)
    fresh = sorted((record for record in records if record["created_at"] >= cutoff),
                   key=lambda record: record["created_at"])
    if records and not fresh:
        return [], (f"渡された status issue コメントの stage レコードは全て {cutoff} より"
                    f"古いため落としました（`since` を付けずに1ページ目を取っていませんか。"
                    f"コメントは古い順に返ります）")
    return fresh[-RECORDS_LIMIT:], None


def resolve_status_comments(comments, fetch_comments, status_issue):
    """(status issue のコメント, 注記) を返す。取れなければ ([], 理由)。

    --stdin で渡された場合は取得しない（comments に値が入っている）。候補の抽出には
    要らない付随値なので、取得の失敗で候補の出力を止めない。
    """
    if comments is not None:
        return comments, None
    if fetch_comments is None:  # --stdin で comments を渡していない
        return [], ("--stdin に comments が無いため直近の stage レコードは空です"
                    "（前段 run の結論を読むには status issue のコメントも渡す）")
    if status_issue is None:
        return [], "status issue が見つからないため直近の stage レコードを取得していません"
    try:
        return fetch_comments(status_issue, since_param()), None
    except Exception as error:  # ネットワーク・権限・API 変更
        return [], (f"status issue のコメントを取得できませんでした: "
                    f"{type(error).__name__} {error}")


def since_param(now=None):
    """RECORDS_SINCE_DAYS 日前を GitHub の `since` に渡せる形にする（純関数）。

    `+00:00` や小数秒が入ると URL に載せたときエスケープが要るので Z 形式で出す。
    """
    now = now or datetime.now(timezone.utc)
    return (now - timedelta(days=RECORDS_SINCE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        seen = set(extract_linked_issues(pr.get("body")))
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


def fetch_status_comments_via_gh(status_issue, since):
    return gh_json(f"repos/{{owner}}/{{repo}}/issues/{status_issue}/comments"
                   f"?per_page=100&since={since}")


USAGE_WITHOUT_GH = """gh CLI も REST 直叩きも使えませんでした。MCP ツール等でデータを取得し、--stdin で渡してください:

  python3 .claude/skills/select-and-develop/scripts/select_issues.py --stdin < data.json

data.json の形:
  {"issues": [...],          # list_issues (state=OPEN) の結果
   "prs": [...],             # list_pull_requests (state=open) の結果
   "collaborators": ["..."],  # list_repository_collaborators の login のリスト (任意)
   "timelines": {"354": [...]},  # 候補 issue ごとの issues/{番号}/timeline?per_page=100 (任意。無いと linked_merged_prs が付かない)
                             #   100 件で打ち切られるので、満杯なら page=2,3… も連結して渡す (古い順なので最新の参照から落ちる)
   "comments": [...]}         # status issue のコメント (任意。無いと recent_status_records が空)
                             #   `issues/{status_issue}/comments?per_page=100&since={2日前, UTC の Z 形式}`
                             #   since を省いて1ページ目を渡すと最古の100件が入る (古いレコードは落とす)
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
        comments, fetch_comments = data.get("comments"), None
        timelines, fetch_timeline = data.get("timelines"), None
    elif shutil.which("gh"):
        try:
            issues, prs = fetch_via_gh()
        except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
            print(f"gh でのデータ取得に失敗しました: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
        collaborators = None
        comments, fetch_comments = None, fetch_status_comments_via_gh
        timelines, fetch_timeline = None, fetch_timeline_via_gh
    else:
        try:
            issues, prs = fetch_via_api()
        except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
            print(f"REST API でのデータ取得に失敗しました: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
        collaborators = None
        comments, fetch_comments = None, fetch_status_comments_via_api
        timelines, fetch_timeline = None, fetch_timeline_via_api

    status_issue, in_progress, backlog = build_candidates(issues, prs, collaborators)
    merged_note = attach_merged_prs(in_progress + backlog, timelines, fetch_timeline)
    # 候補（hold と信頼できない名義を除いたもの）とは別に、cap と突き合わせる
    # open issue の総数も出す。数え方は check_state.py が正本
    open_issues, open_issues_note = count_open_issues(issues)
    # 前段 run の結論（evaluate のグルーミング判断等）は status issue コメントの1行目に
    # ある。ここで載せることで、develop ステージは check_state.py を別に走らせずに読める
    comments, records_note = resolve_status_comments(comments, fetch_comments, status_issue)
    records, load_note = collect_recent_records(comments)
    result = {
        "config": config,
        "status_issue": status_issue,
        "open_issues": open_issues,
        "in_progress": in_progress,
        "backlog": backlog,
        "recent_status_records": records,
    }
    if open_issues_note:
        result["open_issues_note"] = open_issues_note
    if merged_note:
        result["linked_merged_prs_note"] = merged_note
    if records_note or load_note:
        result["recent_status_records_note"] = records_note or load_note
    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
