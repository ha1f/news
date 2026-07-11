#!/usr/bin/env python3
"""daily-loop: open PR をマージ候補かどうか機械判定して JSON で出力する。

使い方: python3 classify_prs.py
出力: {"config", "merge_candidates", "protected", "not_ready", "drafts", "hold", "external"}
  - merge_candidates: ready かつ collaborator 名義・quiescence 達成・保護パス非該当
  - protected: 上記のうち保護パスに触れる PR（auto-merge 禁止 → hold + 人間へ）
  - not_ready: ready だが quiescence 未達 → 触らない
  - drafts: draft の PR（作業中）→ 触らない
  - hold: hold ラベル付き → 触らない
  - external: collaborator 以外の ready PR → レビューコメントのみ
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
    author_association/body/files/last_commit_at を持つ dict。"""
    quiescence = timedelta(minutes=config["quiescence_minutes"])
    result = {"merge_candidates": [], "protected": [], "not_ready": [],
              "drafts": [], "hold": [], "external": []}
    for pr in sorted(prs, key=lambda p: p["number"]):
        summary = {
            "number": pr["number"],
            "title": pr["title"],
            "author_association": pr["author_association"],
            "linked_issues": sorted({int(m.group(1))
                                     for m in LINK_RE.finditer(pr.get("body") or "")}),
        }
        if pr["draft"]:
            result["drafts"].append(summary)
            continue
        if "hold" in pr["labels"]:
            result["hold"].append(summary)
            continue
        if pr["author_association"] not in TRUSTED:
            result["external"].append(summary)
            continue
        last_commit = datetime.fromisoformat(pr["last_commit_at"].replace("Z", "+00:00"))
        if now - last_commit < quiescence:
            result["not_ready"].append({**summary, "reason": "quiescence 未達"})
            continue
        hits = protected_hits(pr["files"], config["protected_paths"])
        if hits:
            result["protected"].append({**summary, "protected_files": hits})
        else:
            result["merge_candidates"].append(summary)
    return result


def main():
    config = parse_guardrails(
        (Path(__file__).resolve().parents[3] / "GUARDRAILS.md").read_text())
    prs = []
    for pr in gh_json("repos/{owner}/{repo}/pulls?state=open&per_page=100"):
        commits = gh_json(f"repos/{{owner}}/{{repo}}/pulls/{pr['number']}/commits?per_page=100")
        files = gh_json(f"repos/{{owner}}/{{repo}}/pulls/{pr['number']}/files?per_page=100")
        prs.append({
            "number": pr["number"],
            "title": pr["title"],
            "draft": pr["draft"],
            "labels": [label["name"] for label in pr["labels"]],
            "author_association": pr["author_association"],
            "body": pr.get("body") or "",
            "files": [f["filename"] for f in files],
            "last_commit_at": commits[-1]["commit"]["committer"]["date"],
        })
    result = classify(prs, config, datetime.now(timezone.utc))
    json.dump({"config": config, **result}, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
