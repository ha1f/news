#!/usr/bin/env python3
"""draft PR を作り（同じ head の open な PR があれば本文を更新し）、本文が参照する画像や動画を添付する。

本文中の `](./<file>)` を --evidence-dir のファイルとして `gh pr edit --attach` で上げ、
user-attachments の URL に置き換えさせる。`--attach` は画像と動画しか受け付けないので、
それ以外の参照や見つからないファイルがあれば、PR を作る前に止まる。

動画は `![](./x.mp4)` が 1 行だけの段落にあるときしかプレーヤーとして埋め込まれない。
表の中や文中、alt 付きで書かれた動画は「（下の動画）」に置き換え、単独の段落として
--video-anchor の行の前（なければ本文の末尾）に移す。

`gh pr` のサブコマンドを使うので、`--attach` がある版の gh と、GraphQL が通る環境が要る。

使い方:
  python3 create_draft_pr.py --repo owner/name --head <branch> --title-file t.txt \\
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

ATTACHABLE = {".png", ".gif", ".jpg", ".jpeg", ".svg", ".mp4", ".mov", ".webm"}
VIDEO = re.compile(r"!\[[^\]]*\]\(\./([^)\s]+\.(?:mp4|mov|webm))\)")
STANDALONE_VIDEO = re.compile(r"\s*!\[\]\(\./([^)\s]+\.(?:mp4|mov|webm))\)\s*")


def gh(*args, cwd=None):
    return subprocess.run(["gh", *args], capture_output=True, text=True, cwd=cwd)


def is_own_paragraph(lines, index):
    before = index == 0 or not lines[index - 1].strip()
    after = index == len(lines) - 1 or not lines[index + 1].strip()
    return before and after


def move_videos_to_own_paragraphs(body, anchor=None):
    lines = body.split("\n")
    placed = {match.group(1) for index, line in enumerate(lines)
              if (match := STANDALONE_VIDEO.fullmatch(line)) and is_own_paragraph(lines, index)}
    to_move = []
    for index, line in enumerate(lines):
        if STANDALONE_VIDEO.fullmatch(line) and is_own_paragraph(lines, index):
            continue
        for video in VIDEO.findall(line):
            if video not in placed and video not in to_move:
                to_move.append(video)
        lines[index] = VIDEO.sub("（下の動画）", line)
    if not to_move:
        return "\n".join(lines)

    anchors = [index for index, line in enumerate(lines) if anchor and line.strip() == anchor.strip()]
    at = anchors[0] if anchors else len(lines)
    block = [] if at == 0 or not lines[at - 1].strip() else [""]
    for video in to_move:
        block += [f"![](./{video})", ""]
    lines[at:at] = block
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--title-file", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--evidence-dir")
    parser.add_argument("--video-anchor", help="動画をこの行（見出しなど）の前に置く。本文にこの行がなければ末尾に置く")
    args = parser.parse_args()

    title = Path(args.title_file).read_text().strip()
    body = move_videos_to_own_paragraphs(Path(args.body_file).read_text(), args.video_anchor)

    refs = sorted(set(re.findall(r"\]\(\./([^)\s]+)\)", body)))
    missing = [ref for ref in refs if not (Path(args.evidence_dir or ".") / ref).is_file()]
    if missing:
        sys.exit(f"証跡のファイルがない: {missing}")
    not_attachable = [ref for ref in refs if Path(ref).suffix.lower() not in ATTACHABLE]
    if not_attachable:
        sys.exit(f"--attach で上げられるのは画像と動画だけ（{sorted(ATTACHABLE)}）: {not_attachable}")
    if refs and "--attach" not in gh("pr", "edit", "--help").stdout:
        sys.exit("この gh の pr edit には --attach がない。gh を更新する")

    listed = gh("pr", "list", "--repo", args.repo, "--head", args.head, "--state", "open", "--json", "number")
    if listed.returncode != 0:
        sys.exit(listed.stderr)
    numbers = [pr["number"] for pr in json.loads(listed.stdout)]

    # gh の --attach は cwd からのパスでファイルを探すので、本文と証跡を 1 つの一時ディレクトリに集める
    with tempfile.TemporaryDirectory() as workdir:
        (Path(workdir) / "body.md").write_text(body)
        attach_args = []
        for ref in refs:
            target = Path(workdir) / ref
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(Path(args.evidence_dir or ".") / ref, target)
            attach_args += ["--attach", f"./{ref}"]

        placeholder = not numbers
        if numbers:
            number = str(numbers[0])
        else:
            # 添付には PR が先に要るので、仮の本文で作ってから書き換える
            created = gh("pr", "create", "--repo", args.repo, "--draft", "--base", args.base,
                         "--head", args.head, "--title", title, "--body", "（本文を更新中）", cwd=workdir)
            if created.returncode != 0:
                sys.exit(created.stderr)
            number = re.search(r"/pull/(\d+)", created.stdout).group(1)

        edited = gh("pr", "edit", number, "--repo", args.repo, "--title", title,
                    "--body-file", "body.md", *attach_args, cwd=workdir)
        if edited.returncode != 0:
            state = "仮の本文のまま" if placeholder else "本文は前のまま"
            sys.exit(f"PR #{number} の本文を更新できなかった（{state}）: {edited.stderr}")

    view = gh("pr", "view", number, "--repo", args.repo, "--json", "url,closingIssuesReferences")
    info = json.loads(view.stdout)
    closes = ",".join(str(issue["number"]) for issue in info["closingIssuesReferences"])
    print(f"{info['url']} closes={closes}")


if __name__ == "__main__":
    main()
