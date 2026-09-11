#!/usr/bin/env python3
"""daily-loop: open PR をマージ候補かどうか機械判定して JSON で出力する。

使い方: python3 classify_prs.py
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
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
LINK_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?|refs?)\s+#(\d+)", re.I)
# commit SHA / digest と v1.2.3 形式のバージョン。置換前後でこれ以外が同じなら「バージョン更新だけ」
VERSION_TOKEN_RE = re.compile(r"\b(?:[0-9a-f]{7,64}|v?\d+(?:\.\d+)*)\b")


def version_bump_only(patch):
    """diff がバージョン・digest 文字列の置換だけで構成されているか（純関数）。
    追加行と削除行が同数で、バージョン token を伏せると一致するとき True。"""
    if not patch:
        return False
    removed, added = [], []
    for line in patch.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("-"):
            removed.append(VERSION_TOKEN_RE.sub("§", line[1:]))
        elif line.startswith("+"):
            added.append(VERSION_TOKEN_RE.sub("§", line[1:]))
    return bool(added) and sorted(added) == sorted(removed)


def is_trusted(pr):
    """この repo に書き込める名義か。head branch がこの repo にあれば書き込み権限の証明。"""
    if pr.get("head_in_repo") is not None:
        return bool(pr["head_in_repo"])
    return pr.get("author_association") in TRUSTED


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


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    if "--stdin" in sys.argv or not sys.stdin.isatty():
        prs = json.load(sys.stdin)
    else:
        prs = fetch_prs_via_gh()
    result = classify(prs, config, datetime.now(timezone.utc))
    json.dump({"config": config, **result}, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
