#!/usr/bin/env bash
# Summarize the diff between a base ref and HEAD for a code reviewer.
# Outputs text to stdout.
#
# Usage:
#   diff_summary.sh <base-ref> [--threshold N]
#
# Behaviour:
# - Always prints `git diff --stat` and `--name-status`.
# - If total changed lines exceed THRESHOLD (default 1000), each file's diff
#   is summarized to the first/last N lines (default head=50, tail=50).
# - Otherwise the full unified diff is printed.

set -euo pipefail

BASE="${1:-}"
shift || true

THRESHOLD=1000
HEAD_LINES=50
TAIL_LINES=50

while [ "$#" -gt 0 ]; do
  case "$1" in
    --threshold) THRESHOLD="$2"; shift 2;;
    --head)      HEAD_LINES="$2"; shift 2;;
    --tail)      TAIL_LINES="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [ -z "$BASE" ]; then
  echo "Usage: $0 <base-ref> [--threshold N] [--head N] [--tail N]" >&2
  exit 2
fi

# Verify base ref exists.
if ! git rev-parse --verify "$BASE" >/dev/null 2>&1; then
  echo "Base ref not found: $BASE" >&2
  exit 2
fi

echo "## Diff stat"
git diff --no-color "${BASE}...HEAD" --stat
echo ""
echo "## Files (name-status)"
git diff --no-color "${BASE}...HEAD" --name-status
echo ""

# Decide full vs summarized.
TOTAL_LINES=$(git diff --no-color "${BASE}...HEAD" --shortstat | grep -oE '[0-9]+ insertions|[0-9]+ deletions' | grep -oE '[0-9]+' | paste -sd+ - | bc 2>/dev/null || echo 0)
TOTAL_LINES=${TOTAL_LINES:-0}

if [ "$TOTAL_LINES" -le "$THRESHOLD" ]; then
  echo "## Full diff (under threshold $THRESHOLD lines)"
  git diff --no-color "${BASE}...HEAD"
  exit 0
fi

echo "## Summarized diff (over threshold $TOTAL_LINES > $THRESHOLD)"
echo ""

# Per-file summarized diff.
git diff --no-color "${BASE}...HEAD" --name-only | while IFS= read -r file; do
  echo "### $file"
  echo '```diff'
  PATCH=$(git diff --no-color "${BASE}...HEAD" -- "$file")
  PATCH_LINES=$(echo "$PATCH" | wc -l | tr -d ' ')
  if [ "$PATCH_LINES" -le $((HEAD_LINES + TAIL_LINES + 5)) ]; then
    echo "$PATCH"
  else
    echo "$PATCH" | head -n "$HEAD_LINES"
    echo "... ($((PATCH_LINES - HEAD_LINES - TAIL_LINES)) lines omitted) ..."
    echo "$PATCH" | tail -n "$TAIL_LINES"
  fi
  echo '```'
  echo ""
done
