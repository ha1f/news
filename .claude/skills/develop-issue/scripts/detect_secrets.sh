#!/usr/bin/env bash
# Hard guardrail: detect secret-like content in staged (and optionally unstaged)
# changes before a commit.
#
# Usage:
#   detect_secrets.sh                            # scan --cached + working tree diff
#   detect_secrets.sh --cached                   # scan only --cached (staged)
#   detect_secrets.sh --staged                   # alias for --cached
#   detect_secrets.sh --allowlist <FILE>         # path-prefix allowlist (1 path per line)
#                                                # 例: test fixture / mock 値で意図的な
#                                                # dummy key を含む場合 (R71)
#
# Exit codes:
#   0 — no hits
#   1 — hits found (details printed to stderr)
#   2 — usage error
#
# Detection: filename patterns + value patterns. False positives are accepted in
# exchange for false negative reduction.
# **Allowlist は使用に depth=0 AskUserQuestion 同意必須 (SKILL.md hard rule)**.
# orchestrator が prompt なしで --allowlist を勝手に渡すことは禁止。

set -euo pipefail

MODE="all"
ALLOWLIST=""
while [ $# -gt 0 ]; do
  case "${1:-}" in
    ""|--all) MODE="all"; shift;;
    --cached|--staged) MODE="cached"; shift;;
    --allowlist) ALLOWLIST="${2:?--allowlist requires FILE}"; shift 2;;
    *) echo "Usage: $0 [--cached|--all] [--allowlist FILE]" >&2; exit 2;;
  esac
done

# File-name patterns that should almost never be committed as-is.
SECRET_FILE_PATTERNS=(
  '\.env(\.|$)'
  '\.envrc$'
  '\.pem$'
  '\.p12$'
  '\.key$'
  '\.pfx$'
  '/credentials(\..*)?$'
  '/service-account[^/]*\.json$'
  '/firebase-adminsdk[^/]*\.json$'
  'id_rsa(\..*)?$'
  'id_dsa(\..*)?$'
)

# Value patterns (extended regex). Conservative; expand as needed.
SECRET_VALUE_PATTERNS=(
  'AKIA[0-9A-Z]{16}'                              # AWS access key
  'aws_secret_access_key[[:space:]]*=[[:space:]]*[A-Za-z0-9/+=]{20,}'
  'sk_live_[a-zA-Z0-9]{24,}'                      # Stripe live secret
  'rk_live_[a-zA-Z0-9]{24,}'                      # Stripe restricted live
  'ghp_[A-Za-z0-9]{36}'                           # GitHub personal access token
  'github_pat_[A-Za-z0-9_]{82}'                   # GitHub fine-grained PAT
  'gho_[A-Za-z0-9]{36}'                           # GitHub OAuth token
  'glpat-[A-Za-z0-9_-]{20}'                       # GitLab PAT
  'xox[baprs]-[0-9A-Za-z-]{10,}'                  # Slack token
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'            # Generic private key body
  'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'  # JWT (rough)
  'AIza[0-9A-Za-z_-]{35}'                         # Google API key
)

HITS=0
HITS_LOG=$(mktemp)
trap 'rm -f "$HITS_LOG"' EXIT

is_allowlisted() {
  # path-prefix match against $ALLOWLIST (1 path per line)
  local path="$1"
  [ -z "$ALLOWLIST" ] && return 1
  [ ! -f "$ALLOWLIST" ] && return 1
  while IFS= read -r prefix; do
    [ -z "$prefix" ] && continue
    case "$path" in
      "$prefix"*) return 0;;
    esac
  done < "$ALLOWLIST"
  return 1
}

scan_files() {
  # diff_cmd は "git diff --cached" 等。--no-color を必ず付与した上で渡されることを期待。
  local diff_cmd="$1"
  local files
  files=$($diff_cmd --name-only --diff-filter=AM) || true
  if [ -z "$files" ]; then
    return 0
  fi

  # File-name based detection.
  # `grep -e <pat>` の `-e` は、`$pat` が `-` で始まる場合に grep が pattern を
  # フラグと誤認するのを防ぐ POSIX 推奨形式 (BSD grep で実害発生)。
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    # R71: allowlist 適用 (test fixture / mock 値の path-prefix 除外)
    if is_allowlisted "$f"; then
      continue
    fi
    for pat in "${SECRET_FILE_PATTERNS[@]}"; do
      if echo "$f" | grep -Eq -e "$pat"; then
        echo "FILE_PATTERN: $f matches /$pat/" >> "$HITS_LOG"
        HITS=$((HITS + 1))
      fi
    done
  done <<< "$files"

  # Value based detection per file (allowlist が value pattern にも効くように
  # file 単位で diff を取って分離処理する R71)。
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if is_allowlisted "$f"; then
      continue
    fi
    local added
    added=$($diff_cmd --unified=0 -- "$f" | grep -E '^\+' | grep -Ev '^\+\+\+') || true
    if [ -z "$added" ]; then
      continue
    fi
    for pat in "${SECRET_VALUE_PATTERNS[@]}"; do
      local matches
      # `-e "$pat"`: pattern が `-` で始まる場合の誤認回避 (BSD grep 実害)。
      matches=$(echo "$added" | grep -Eo -e "$pat" | head -n 3 || true)
      if [ -n "$matches" ]; then
        while IFS= read -r m; do
          [ -z "$m" ] && continue
          echo "VALUE_PATTERN ($f): /$pat/ matched: $(echo "$m" | head -c 80)" >> "$HITS_LOG"
          HITS=$((HITS + 1))
        done <<< "$matches"
      fi
    done
  done <<< "$files"
}

# --no-color: ユーザの git config (color.ui=always 等) で escape sequence が
# 入ると `grep '^\+'` がマッチせず secret 検知が silently スキップされる
# (実際にスモークテストで再現)。必ず付ける。
scan_files "git diff --cached --no-color"
if [ "$MODE" = "all" ]; then
  scan_files "git diff --no-color"
fi

if [ "$HITS" -gt 0 ]; then
  {
    echo "Detected $HITS secret-like signal(s):"
    cat "$HITS_LOG"
    echo ""
    echo "Refusing the commit. Either remove these files from the index or"
    echo "scrub the secret values. Do not bypass this check."
  } >&2
  exit 1
fi

exit 0
