#!/usr/bin/env python3
"""GUARDRAILS.md の protected_paths に該当するファイルがあるか判定する。
UI 変更パス（.claude/rules/ui-changes.md の paths）への該当も検出する。

使い方:
  python3 check_protected_paths.py file1 file2 ...
  python3 check_protected_paths.py --diff origin/main
  echo '["file1", "file2"]' | python3 check_protected_paths.py --stdin

exit 0: 保護パス該当なし
exit 1: 保護パス該当あり
stdout: JSON（protected, files, patterns に加え ui_changes）
"""
import json
import re
import subprocess
import sys
from fnmatch import fnmatch
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


def parse_rule_paths(rule_path):
    """ルールファイルの YAML front matter から paths を抽出する。"""
    if not rule_path.exists():
        return []
    text = rule_path.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return []
    paths = []
    in_paths = False
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("paths:"):
            in_paths = True
            continue
        if in_paths:
            if stripped.startswith("- "):
                val = stripped[2:].strip().strip('"').strip("'")
                paths.append(val)
            else:
                break
    return paths


def protected_hits(files, patterns):
    hits = []
    for pattern in patterns:
        if pattern.endswith("/**"):
            prefix = pattern[:-3]
            hits += [f for f in files if f == prefix or f.startswith(prefix + "/")]
        else:
            hits += [f for f in files if f == pattern]
    return sorted(set(hits))


def ui_hits(files, ui_patterns):
    """fnmatch でファイルを UI パターンに照合する。"""
    hits = []
    for f in files:
        for pattern in ui_patterns:
            if fnmatch(f, pattern):
                hits.append(f)
                break
    return sorted(set(hits))


def main():
    base_dir = Path(__file__).resolve().parents[1]
    guardrails_path = base_dir / "GUARDRAILS.md"
    config = parse_guardrails(guardrails_path.read_text())
    patterns = config.get("protected_paths", [])

    ui_rule_path = base_dir / "rules" / "ui-changes.md"
    ui_patterns = parse_rule_paths(ui_rule_path)

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
    ui_changed = ui_hits(files, ui_patterns) if ui_patterns else []

    result = {
        "protected": bool(hits),
        "files": hits,
        "patterns": patterns,
    }
    if ui_changed:
        result["ui_changes"] = ui_changed

    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    print()
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
