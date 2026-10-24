#!/usr/bin/env python3
"""repo 内に散らばった Python ユニットテストをまとめて走らせる。

使い方: python3 .claude/scripts/run_unit_tests.py [--list] [--root <dir>]

なぜスクリプトなのか（#413）: テストはスキルごとのディレクトリに分かれており、
repo ルートからの `unittest discover` は 0 件になる（各ディレクトリが package でなく、
テストが `sys.path.insert(Path(__file__).parent)` で隣のモジュールを読むため）。
置き場を列挙して回す必要があるが、列挙を CI の yaml に焼き込むと
新しいスキルのテストが黙って回らなくなる。**`test_*.py` が在るディレクトリを
その場で見つけて全部回す**ことで、置き場が増えても取りこぼさない。

ディレクトリが1つも見つからなければ失敗する（glob の破綻を「テスト0件で green」
として通さないため）。
"""
import argparse
import subprocess
import sys
from pathlib import Path

TEST_GLOB = "test_*.py"
# 生成物・依存のツリーは探索しない（_site には投稿のビルド結果が入る）
SKIP_DIRS = {".git", "_site", "node_modules", "cache", "output", ".venv", "__pycache__"}


def find_test_dirs(root):
    """`test_*.py` を含むディレクトリを repo-relative でソートして返す（純関数）。"""
    root = Path(root)
    found = set()
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name not in SKIP_DIRS:
                    stack.append(entry)
            elif entry.match(TEST_GLOB):
                found.add(current)
    return sorted(str(path.relative_to(root)) for path in found)


def run_one(root, rel_dir):
    """1 ディレクトリ分を走らせ、(ok, 出力) を返す。

    `-s` と `-t` の両方にそのディレクトリを渡す。top level を repo ルートにすると
    package でないディレクトリのテストを import できない。"""
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", ".", "-t", ".", "-p", TEST_GLOB],
        cwd=str(Path(root) / rel_dir), capture_output=True, text=True)
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="repo 内の Python ユニットテストを置き場ごとにまとめて走らせる")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]),
                       help="探索の起点（既定は repo ルート）")
    parser.add_argument("--list", action="store_true", help="走らせずに置き場を列挙する")
    args = parser.parse_args(argv)

    dirs = find_test_dirs(args.root)
    if not dirs:
        print(f"テストの置き場が1つも見つかりません（root={args.root}、glob={TEST_GLOB}）。"
              "探索が壊れている可能性があるため失敗として扱います。", file=sys.stderr)
        return 1
    if args.list:
        print("\n".join(dirs))
        return 0

    failed = []
    for rel_dir in dirs:
        ok, output = run_one(args.root, rel_dir)
        # 失敗したときだけ詳細を出す（成功ログでログを埋めない）
        print(f"{'ok  ' if ok else 'FAIL'} {rel_dir}: {output.splitlines()[-1] if output else '(出力なし)'}")
        if not ok:
            failed.append(rel_dir)
            print(output)
    print(f"\n置き場 {len(dirs)} 件、失敗 {len(failed)} 件")
    if failed:
        print("失敗した置き場: " + ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
