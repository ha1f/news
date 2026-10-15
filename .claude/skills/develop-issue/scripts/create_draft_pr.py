#!/usr/bin/env python3
"""draft PR を作り（既にあれば本文を更新し）、本文が参照する証跡を添付する。

本文の `](./<file>)` は --evidence-dir のファイルを `gh pr edit --attach` で上げ、
user-attachments の URL に書き換えさせる。動画（.mp4）は表の中や alt 付きだと
埋め込まれないため、参照を本文から外して単独行の `![](./x.mp4)` に移す。

使い方:
  python3 create_draft_pr.py --repo owner/name --head <branch> --title-file t.txt \
      --body-file body.md [--evidence-dir dir] [--base main] [--video-anchor '## 見出し']

stdout: PR の URL と、紐づいた issue（closingIssuesReferences）
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def gh(*args, cwd=None):
    return subprocess.run(["gh", *args], capture_output=True, text=True, cwd=cwd)


def move_videos_to_own_lines(body, anchor=None):
    videos = re.findall(r"!\[[^\]]*\]\(\./([^)]+\.mp4)\)", body)
    body = re.sub(r"!\[[^\]]*\]\(\./([^)]+\.mp4)\)", "（下の動画）", body)
    for video in videos:
        line = f"\n![](./{video})\n"
        if line in body:
            continue
        if anchor and anchor in body:
            body = body.replace(anchor, f"![](./{video})\n\n{anchor}", 1)
        else:
            body += line
    return body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--title-file", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--evidence-dir")
    parser.add_argument("--video-anchor", help="動画をこの行（見出し等）の直前に置く。無ければ本文の末尾")
    args = parser.parse_args()

    title = Path(args.title_file).read_text().strip()
    body = move_videos_to_own_lines(Path(args.body_file).read_text(), args.video_anchor)

    # gh の --attach は cwd 基準のパスで探すので、本文と証跡を 1 つの一時ディレクトリに集める
    workdir = Path(tempfile.mkdtemp())
    (workdir / "body.md").write_text(body)
    attach_args = []
    for ref in sorted(set(re.findall(r"\]\(\./([^)\s]+)\)", body))):
        source = Path(args.evidence_dir or ".") / ref
        if not source.exists():
            print(f"missing evidence: {ref}", file=sys.stderr)
            continue
        shutil.copy(source, workdir / ref)
        attach_args += ["--attach", f"./{ref}"]

    listed = gh("pr", "list", "--repo", args.repo, "--head", args.head, "--state", "open", "--json", "number")
    numbers = [pr["number"] for pr in json.loads(listed.stdout or "[]")]
    if numbers:
        number = str(numbers[0])
    else:
        # 証跡を添付するには既存の PR が要るので、仮の本文で作ってから書き換える
        created = gh("pr", "create", "--repo", args.repo, "--draft", "--base", args.base,
                     "--head", args.head, "--title", title, "--body", "（本文を更新中）", cwd=workdir)
        if created.returncode != 0:
            sys.exit(created.stderr)
        number = re.search(r"/pull/(\d+)", created.stdout).group(1)

    edited = gh("pr", "edit", number, "--repo", args.repo, "--title", title,
                "--body-file", "body.md", *attach_args, cwd=workdir)
    shutil.rmtree(workdir)
    if edited.returncode != 0:
        sys.exit(edited.stderr)

    view = gh("pr", "view", number, "--repo", args.repo, "--json", "url,closingIssuesReferences")
    info = json.loads(view.stdout)
    closes = ",".join(str(issue["number"]) for issue in info["closingIssuesReferences"])
    print(f"{info['url']} closes={closes}")


if __name__ == "__main__":
    main()
