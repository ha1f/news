#!/usr/bin/env bash
# Fetch a GitHub issue with its comments and linked PRs/issues.
# Outputs JSON to stdout.
#
# Usage: fetch_issue.sh <issue-id-or-url>

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <issue-id-or-url>" >&2
  exit 2
fi

INPUT="$1"

# Normalize input: extract integer id from URL or #N
if [[ "$INPUT" =~ ^[0-9]+$ ]]; then
  ID="$INPUT"
elif [[ "$INPUT" =~ ^#([0-9]+)$ ]]; then
  ID="${BASH_REMATCH[1]}"
elif [[ "$INPUT" =~ /issues/([0-9]+) ]]; then
  ID="${BASH_REMATCH[1]}"
else
  echo "Could not parse issue id from: $INPUT" >&2
  exit 2
fi

# Verify gh is authenticated.
if ! gh auth status >/dev/null 2>&1; then
  echo '{"error": "gh_not_authenticated"}'
  exit 3
fi

# Fields we want from the issue.
ISSUE_JSON=$(gh issue view "$ID" \
  --json number,title,body,labels,assignees,comments,url,state,closedAt,author,createdAt,updatedAt)

# Best-effort: timeline events (linked PRs etc).
# `gh issue view --json` does not include timeline; use the REST API.
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
TIMELINE_JSON=$(gh api "repos/${REPO}/issues/${ID}/timeline" \
  -H "Accept: application/vnd.github.mockingbird-preview+json" 2>/dev/null || echo '[]')

# Merge.
jq -n \
  --argjson issue "$ISSUE_JSON" \
  --argjson timeline "$TIMELINE_JSON" \
  --arg repo "$REPO" \
  '{repo: $repo, issue: $issue, timeline: $timeline}'
