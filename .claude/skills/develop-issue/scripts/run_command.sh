#!/usr/bin/env bash
# Run a command defined in repo-profile.json for the current task.
#
# Usage:
#   run_command.sh <action> [extra-args]
#
# Actions:
#   format | lint | test | build | install
#       Looks up commands.<action> in repo-profile.json and runs it.
#   codegen <trigger-glob>
#       Finds the matching commands.codegen[] entry by trigger and runs
#       its command.
#   check_human_owned
#       Reads conventions.human_owned[] and runs each entry's `detection`
#       against `git diff --cached`. Exits 1 (and prints the offending kind)
#       on the first hit. Exits 0 otherwise.
#
# Required env:
#   STATE_DIR    Absolute path to <repo-root>/.claude/tmp/impl-<id>/
#
# Exit codes:
#   0   success
#   1   command failed / detection hit
#   2   usage error
#   3   profile missing or required action not defined
#   4   missing required tool (jq)
#   5   command unavailable in local environment AND CI covers this action
#       (caller should treat as "skipped, CI will verify"; only emitted for
#       format/lint/test/build when shell exit 127 = command not found AND
#       repo-profile.json .ci.covered_actions includes this action)

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <action> [args...]" >&2
  exit 2
fi

ACTION="$1"; shift || true

# Resolve repo-profile.json path.
: "${STATE_DIR:?STATE_DIR must be set (path to .claude/tmp/impl-<id>/)}"
PROFILE="${STATE_DIR%/}/repo-profile.json"

if [ ! -f "$PROFILE" ]; then
  echo "repo-profile.json not found at $PROFILE" >&2
  echo "gather-agent must produce both repo-profile.md and repo-profile.json." >&2
  exit 3
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required but not installed." >&2
  exit 4
fi

run_or_skip() {
  local action="$1"
  local cmd
  cmd=$(jq -r --arg a "$action" '.commands[$a] // empty' "$PROFILE")
  if [ -z "$cmd" ]; then
    echo "[run_command.sh] commands.$action not defined in repo-profile.json; skipping." >&2
    return 0
  fi
  echo "[run_command.sh] $action: $cmd"
  local rc
  set +e
  bash -c "$cmd"
  rc=$?
  set -e
  # Exit 127 = command not found in PATH. If CI covers this action, we treat
  # it as a deferrable skip (R36-R39): the caller (implement-agent) records
  # verify_skipped and lets CI take over after the PR is opened. Any other
  # non-zero exit is a real failure and must be surfaced as-is.
  if [ "$rc" -eq 127 ]; then
    if jq -e --arg a "$action" '(.ci.covered_actions // []) | index($a)' "$PROFILE" >/dev/null 2>&1; then
      echo "[run_command.sh] $action: tool unavailable (exit 127). CI covers this action — emitting skip (exit 5)." >&2
      return 5
    fi
    echo "[run_command.sh] $action: tool unavailable (exit 127) and CI does NOT cover this action — treating as failure." >&2
  fi
  return "$rc"
}

case "$ACTION" in
  format|lint|test|build|install)
    run_or_skip "$ACTION"
    ;;

  codegen)
    TRIGGER="${1:-}"
    if [ -z "$TRIGGER" ]; then
      echo "Usage: $0 codegen <trigger-glob>" >&2
      exit 2
    fi
    CMD=$(jq -r --arg t "$TRIGGER" \
      '.commands.codegen[]? | select(.trigger == $t) | .command' "$PROFILE")
    if [ -z "$CMD" ]; then
      echo "[run_command.sh] no codegen entry for trigger=$TRIGGER" >&2
      exit 3
    fi
    echo "[run_command.sh] codegen ($TRIGGER): $CMD"
    bash -c "$CMD"
    ;;

  check_human_owned)
    # For each human_owned entry, run its detection against staged changes.
    # Detection can be one of: path_glob, content_match, command_check.
    COUNT=$(jq '(.conventions.human_owned // []) | length' "$PROFILE")
    if [ "$COUNT" -eq 0 ]; then
      exit 0
    fi
    for i in $(seq 0 $((COUNT - 1))); do
      KIND=$(jq -r ".conventions.human_owned[$i].kind" "$PROFILE")
      PATH_GLOB=$(jq -r ".conventions.human_owned[$i].detection.path_glob // empty" "$PROFILE")
      CONTENT_MATCH=$(jq -r ".conventions.human_owned[$i].detection.content_match // empty" "$PROFILE")
      COMMAND_CHECK=$(jq -r ".conventions.human_owned[$i].detection.command_check // empty" "$PROFILE")

      if [ -n "$PATH_GLOB" ]; then
        # Use git to apply the glob against staged paths.
        if git diff --cached --no-color --name-only -- "$PATH_GLOB" | grep -q .; then
          echo "human_owned hit: kind=$KIND (path_glob=$PATH_GLOB)" >&2
          exit 1
        fi
      fi
      if [ -n "$CONTENT_MATCH" ]; then
        # --no-color: ユーザ git config で escape 入ると正規表現が壊れる
        if git diff --cached --no-color --unified=0 | grep -E "$CONTENT_MATCH" >/dev/null; then
          echo "human_owned hit: kind=$KIND (content_match=$CONTENT_MATCH)" >&2
          exit 1
        fi
      fi
      if [ -n "$COMMAND_CHECK" ]; then
        if bash -c "$COMMAND_CHECK" >/dev/null 2>&1; then
          echo "human_owned hit: kind=$KIND (command_check)" >&2
          exit 1
        fi
      fi
    done
    exit 0
    ;;

  *)
    echo "Unknown action: $ACTION" >&2
    exit 2
    ;;
esac
