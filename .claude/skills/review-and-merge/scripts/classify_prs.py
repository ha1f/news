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
信頼名義は collaborator（OWNER / MEMBER / COLLABORATOR）と GUARDRAILS の trusted_bots
（Renovate 等の依存更新 bot）。bot の PR は各要素に "bot": true が付き、保護パス判定を
免除する（bot が書ける範囲は bot 自身の設定で縛られている。diff の範囲はレビューで確認する）。
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
    author_association/author/body/files/last_commit_at を持つ dict。"""
    quiescence = timedelta(minutes=config["quiescence_minutes"])
    trusted_bots = set(config.get("trusted_bots") or [])
    result = {"merge_candidates": [], "protected": [], "not_ready": [],
              "drafts": [], "hold": [], "external": []}
    for pr in sorted(prs, key=lambda p: p["number"]):
        is_bot = pr.get("author") in trusted_bots
        summary = {
            "number": pr["number"],
            "title": pr["title"],
            "author": pr.get("author"),
            "author_association": pr["author_association"],
            "bot": is_bot,
            "linked_issues": sorted({int(m.group(1))
                                     for m in LINK_RE.finditer(pr.get("body") or "")}),
        }
        if pr["draft"]:
            result["drafts"].append(summary)
            continue
        if "hold" in pr["labels"]:
            result["hold"].append(summary)
            continue
        if pr["author_association"] not in TRUSTED and not is_bot:
            result["external"].append(summary)
            continue
        last_commit = datetime.fromisoformat(pr["last_commit_at"].replace("Z", "+00:00"))
        if now - last_commit < quiescence:
            result["not_ready"].append({**summary, "reason": "quiescence 未達"})
            continue
        # 保護パスはループ自身の安全装置を守る仕組み。bot が書ける範囲は bot 自身の設定
        # （renovate.json5 等）で縛られているため、bot の PR は判定を免除する
        hits = [] if is_bot else protected_hits(pr["files"], config["protected_paths"])
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
            "body": pr.get("body") or "",
            "files": [f["filename"] for f in files],
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
