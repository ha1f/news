#!/usr/bin/env python3
"""GUARDRAILS.md の protected_paths に該当するファイルがあるか判定する。

使い方:
  python3 check_protected_paths.py file1 file2 ...
  python3 check_protected_paths.py --diff origin/main
  echo '["file1", "file2"]' | python3 check_protected_paths.py --stdin

exit 0: 該当なし
exit 1: 該当あり（該当ファイルを JSON で stdout に出力）
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def parse_guardrails(text):
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


def main():
    guardrails_path = Path(__file__).resolve().parents[1] / "GUARDRAILS.md"
    config = parse_guardrails(guardrails_path.read_text())
    patterns = config.get("protected_paths", [])

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--diff" in sys.argv:
        idx = sys.argv.index("--diff")
        base = sys.argv[idx + 1] if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--") else "origin/main"
        out = subprocess.run(
            ["git", "diff", "--name-only", base],
            capture_output=True, text=True, check=True,
        )
        files = [f for f in out.stdout.strip().splitlines() if f]
    elif "--stdin" in sys.argv:
        files = json.load(sys.stdin)
    elif args:
        files = args
    elif not sys.stdin.isatty():
        files = json.load(sys.stdin)
    else:
        files = []

    hits = protected_hits(files, patterns)
    if hits:
        json.dump({"protected": True, "files": hits, "patterns": patterns},
                  sys.stdout, ensure_ascii=False, indent=1)
        print()
        sys.exit(1)
    else:
        json.dump({"protected": False, "files": [], "patterns": patterns},
                  sys.stdout, ensure_ascii=False, indent=1)
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
