#!/usr/bin/env python3
"""daily-loop: open PR をマージ候補かどうか機械判定して JSON で出力する。

使い方:
  python3 classify_prs.py                 # gh があれば gh、無ければ GitHub REST を直接叩く
  python3 classify_prs.py --stdin < prs.json  # 保険。MCP 等で取得した JSON を渡す
出力: {"config", "merge_candidates", "protected", "not_ready", "drafts", "hold", "external"}
  - merge_candidates: ready かつ信頼名義・quiescence 達成・保護パス非該当
  - protected: 上記のうち保護パスに触れる PR（auto-merge 禁止 → hold + 人間へ）
  - not_ready: ready だが quiescence 未達 → 触らない
  - drafts: draft の PR（作業中）→ 触らない
  - hold: hold ラベル付き → 触らない
  - external: 信頼名義以外の ready PR → レビューコメントのみ
信頼の軸は「この repo に書き込める名義か」で、人間・bot・AI を区別しない: head branch が
この repo にある PR（head_in_repo）は書き込み権限の証明として信頼する。head の情報が無い
入力では author_association（OWNER / MEMBER / COLLABORATOR）で代用する。
保護パスの判定は変更内容で行う: 該当ファイルの diff がバージョン・digest 文字列の置換だけ
なら安全装置の変更ではないので protected にせず、protected_version_bumps に列挙する。
diff レビュー・マージの実行はエージェントが行う。

gh 不在時の REST 直叩き（resolve_repo / parse_link_header / with_page / api_json）は
select_issues.py / check_state.py にも同じものがある（#356, PR #366）。この3つ目の複製を
足すとき、共有モジュール化するかどうかを検討した: 3スクリプトとも「エージェントの Bash から
単体で `python3 <path>` 起動できる」ことに依存しており、Bash の実行 cwd は run ごとに変わる
（.claude/notes/develop-issue.md）。共有モジュールを素朴な相対 import で足すと、その cwd 差で
import に失敗する経路が生まれる。sys.path 操作や名前空間パッケージ化はそのための足場が要り、
3ファイル・1関数ずつが安定して壊れていない現状（2026-09-22 時点、#356 以来変更なし）に対して
足場のほうが重い。よって今回は据え置きで複製し、4つ目の複製が要る・または3ファイルのどれかを
リファクタで触るタイミングで改めて判断する。
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

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)
# バージョンらしい形だけを伏せる: `@` 直後の digest / v始まり / ドットを含む数値。
# 裸の整数（quiescence_minutes: 30 等の設定値）は伏せない
VERSION_TOKEN_RE = re.compile(r"(?<=@)[0-9a-f]{7,64}\b|\bv\d+(?:\.\d+)*\b|\b\d+(?:\.\d+)+\b")
API_BASE = "https://api.github.com"
API_TIMEOUT = 15


def version_bump_only(patch):
    """diff がバージョン・digest 文字列の置換だけで構成されているか（純関数）。
    削除行と追加行が同数で、行ごとに対にしたとき「生の行は異なるが、バージョン token を
    伏せると一致する」ときだけ True（同一行の移動・並べ替えは置換ではない）。
    patch は GitHub files API の形式（@@ から始まり、ファイルヘッダを含まない）。"""
    if not patch:
        return False
    removed = [line[1:] for line in patch.splitlines() if line.startswith("-")]
    added = [line[1:] for line in patch.splitlines() if line.startswith("+")]
    if not added or len(added) != len(removed):
        return False
    return all(r != a and VERSION_TOKEN_RE.sub("§", r) == VERSION_TOKEN_RE.sub("§", a)
               for r, a in zip(removed, added))


def is_trusted(pr):
    """この repo に書き込める名義か。head branch がこの repo にあれば書き込み権限の証明。
    head_in_repo が真偽値でない入力（MCP 経路の取り違え等）は author_association で判定する。"""
    if isinstance(pr.get("head_in_repo"), bool):
        return pr["head_in_repo"]
    return pr.get("author_association") in TRUSTED


def gh_json(path):
    out = subprocess.run(["gh", "api", "--paginate", path],
                         check=True, capture_output=True, text=True).stdout
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
    proxy がこの形を 403 で弾く（.claude/notes/develop-issue.md 実測）。ヘッダの URL を
    そのまま辿らず、ページ番号だけ次に進めて `/repos/{owner}/{repo}/...` 形式を自前で組む。"""
    if re.search(r"[?&]page=\d+", url):
        return re.sub(r"([?&]page=)\d+", r"\g<1>" + str(page), url)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}page={page}"


def _http_get(url, headers):
    """1 リクエスト分の実 HTTP 取得（本体バイト列, Link ヘッダー）を返す。差し替え可能にして
    api_json のページング組み立てをネットワーク無しでテストできるようにする。"""
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=API_TIMEOUT) as resp:
            return resp.read(), resp.headers.get("Link")
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"GitHub API {error.code} {url}: "
            f"{error.read().decode('utf-8', 'replace')[:300]}") from error


def api_json(path, http_get=_http_get):
    """gh CLI 不在の環境向けに GitHub REST API を直接叩く（全ページ取得）。

    cloud proxy が素の HTTPS にも GitHub 認証を注入するため、トークンが無くても動く
    （実測 .claude/notes/develop-issue.md）。GH_TOKEN / GITHUB_TOKEN が環境にあれば
    Authorization ヘッダに載せる。

    この取得部（resolve_repo / parse_link_header / with_page / api_json）は
    select_issues.py / check_state.py にも同じものがある。意図的な重複について
    このファイルの docstring 末尾を参照。"""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ha1f-news-daily-loop"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request_url = f"{API_BASE}/{path}"
    items, page = [], 1
    while request_url:
        body, link = http_get(request_url, headers)
        items.extend(json.loads(body))
        if "next" in parse_link_header(link):
            page += 1
            request_url = with_page(f"{API_BASE}/{path}", page)
        else:
            request_url = None
    return items


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


def protected_hits(files, patterns):
    hits = []
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            hits += [f for f in files if f == prefix or f.startswith(prefix + "/")]
        else:
            hits += [f for f in files if f == pattern]
    return sorted(set(hits))


def classify(prs, config, now):
    """PR リストを分類する（純関数）。各 PR は number/title/draft/labels/
    author_association/author/head_in_repo/body/files/patches/last_commit_at を持つ dict
    （patches は {filename: unified diff}。無ければ保護パスの変更内容判定は行わない）。"""
    quiescence = timedelta(minutes=config["quiescence_minutes"])
    result = {"merge_candidates": [], "protected": [], "not_ready": [],
              "drafts": [], "hold": [], "external": []}
    for pr in sorted(prs, key=lambda p: p["number"]):
        summary = {
            "number": pr["number"],
            "title": pr["title"],
            "author": pr.get("author"),
            "author_association": pr.get("author_association"),
            "linked_issues": sorted({int(m.group(1))
                                     for m in LINK_RE.finditer(pr.get("body") or "")}),
        }
        if pr["draft"]:
            result["drafts"].append(summary)
            continue
        if "hold" in pr["labels"]:
            result["hold"].append(summary)
            continue
        if not is_trusted(pr):
            result["external"].append(summary)
            continue
        last_commit = datetime.fromisoformat(pr["last_commit_at"].replace("Z", "+00:00"))
        if now - last_commit < quiescence:
            result["not_ready"].append({**summary, "reason": "quiescence 未達"})
            continue
        # 保護パスはループ自身の安全装置を守る仕組み。バージョン・digest の置換だけの変更は
        # 安全装置を変えないので protected にせず、レビューで上流の changelog を確認する
        patches = pr.get("patches") or {}
        hits = protected_hits(pr["files"], config["protected_paths"])
        bumps = [f for f in hits if version_bump_only(patches.get(f))]
        hits = [f for f in hits if f not in bumps]
        if bumps:
            summary["protected_version_bumps"] = bumps
        if hits:
            result["protected"].append({**summary, "protected_files": hits})
        else:
            result["merge_candidates"].append(summary)
    return result


def fetch_prs_via_gh():
    prs = []
    for pr in gh_json("repos/{owner}/{repo}/pulls?state=open&per_page=100"):
        commits = gh_json(f"repos/{{owner}}/{{repo}}/pulls/{pr['number']}/commits?per_page=100")
        files = gh_json(f"repos/{{owner}}/{{repo}}/pulls/{pr['number']}/files?per_page=100")
        prs.append({
            "number": pr["number"],
            "title": pr["title"],
            "draft": pr["draft"],
            "labels": [label["name"] for label in pr["labels"]],
            "author": (pr.get("user") or {}).get("login"),
            "author_association": pr["author_association"],
            "head_in_repo": ((pr.get("head") or {}).get("repo") or {}).get("full_name")
            == ((pr.get("base") or {}).get("repo") or {}).get("full_name"),
            "body": pr.get("body") or "",
            "files": [f["filename"] for f in files],
            "patches": {f["filename"]: f.get("patch") or "" for f in files},
            "last_commit_at": commits[-1]["commit"]["committer"]["date"],
        })
    return prs


def fetch_prs_via_api():
    """gh CLI 不在の環境向けに GitHub REST API を直接叩いて取得する。fetch_prs_via_gh() と
    同じ3エンドポイント（実測 .claude/notes/develop-issue.md: open PR 3件 = 7 リクエスト /
    2.8 秒）。files / commits が per_page=100 を超える PR は api_json が自動でページを辿る。"""
    owner, repo = resolve_repo()
    prs = []
    for pr in api_json(f"repos/{owner}/{repo}/pulls?state=open&per_page=100"):
        commits = api_json(f"repos/{owner}/{repo}/pulls/{pr['number']}/commits?per_page=100")
        files = api_json(f"repos/{owner}/{repo}/pulls/{pr['number']}/files?per_page=100")
        prs.append({
            "number": pr["number"],
            "title": pr["title"],
            "draft": pr["draft"],
            "labels": [label["name"] for label in pr["labels"]],
            "author": (pr.get("user") or {}).get("login"),
            "author_association": pr["author_association"],
            "head_in_repo": ((pr.get("head") or {}).get("repo") or {}).get("full_name")
            == ((pr.get("base") or {}).get("repo") or {}).get("full_name"),
            "body": pr.get("body") or "",
            "files": [f["filename"] for f in files],
            "patches": {f["filename"]: f.get("patch") or "" for f in files},
            "last_commit_at": commits[-1]["commit"]["committer"]["date"],
        })
    return prs


USAGE_WITHOUT_GH = """gh CLI も REST 直叩きも使えませんでした。MCP ツール等でデータを取得し、--stdin で渡してください:

  python3 .claude/skills/review-and-merge/scripts/classify_prs.py --stdin < prs.json

prs.json は PR の JSON 配列。各要素の形は classify() の docstring を参照。"""


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    # エージェントの Bash ツールから起動すると stdin は常に非 tty になるため、
    # tty 判定では JSON を渡していなくても stdin モードに入ってしまう (PR #329 と同じ罠)
    if "--stdin" in sys.argv:
        prs = json.load(sys.stdin)
    elif shutil.which("gh"):
        try:
            prs = fetch_prs_via_gh()
        except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
            print(f"gh でのデータ取得に失敗しました: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
    else:
        try:
            prs = fetch_prs_via_api()
        except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
            print(f"REST API でのデータ取得に失敗しました: "
                  f"{type(error).__name__} {error}\n", file=sys.stderr)
            print(USAGE_WITHOUT_GH, file=sys.stderr)
            return 1
    result = classify(prs, config, datetime.now(timezone.utc))
    json.dump({"config": config, **result}, sys.stdout, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
