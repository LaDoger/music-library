#!/usr/bin/env bash
# Sequential drafting/review/build/commit; safe rebase+regeneration+push.
set -euo pipefail
cd "$(dirname "$0")/../.."
count=${1:-1}; shift || true
mode=push
for arg in "$@"; do
  case "$arg" in --draft-only) mode=draft;; --no-push) mode=local;; *) echo "Unknown option: $arg" >&2; exit 2;; esac
done
[[ "$count" =~ ^[1-9][0-9]*$ ]] || { echo 'N must be a positive integer' >&2; exit 2; }
if [[ "$mode" != draft ]]; then
  [[ -n "${MUSICLIB_ANALYSIS_REVIEW_CMD:-}" ]] || { echo 'Set MUSICLIB_ANALYSIS_REVIEW_CMD; automatic drafts cannot publish.' >&2; exit 2; }
  [[ -z "$(git status --porcelain)" ]] || { echo 'Start with a clean worktree.' >&2; exit 2; }
fi
scratch=$(mktemp -d /tmp/music-analysis-queue.XXXXXX)
echo "Draft directory: $scratch"
# Keep the output for inspection; caller deletes it after review. No big caches/audio.
processed=0
while IFS= read -r id; do
  [[ -z "$id" || "$id" == \#* ]] && continue
  [[ "$id" =~ ^[a-z0-9_]+$ ]] || { echo 'Unsafe queue id' >&2; exit 2; }
  python3 scripts/analysis/auto_analyse.py "$id" --out-root "$scratch/bundles" --spec-dir "$scratch/specs"
  if [[ "$mode" != draft ]]; then
    draft_spec="$scratch/specs/$id.draft.json"
    reviewed_spec="scripts/analysis/specs/$id.json"
    python3 - "$id" "$draft_spec" "$reviewed_spec" <<'PY'
import os,shlex,subprocess,sys
values=dict(zip(('id','draft_spec','reviewed_spec'),sys.argv[1:]));values['brief']='scripts/analysis/BRIEF_analyse.md'
cmd=os.environ['MUSICLIB_ANALYSIS_REVIEW_CMD']
for name,value in values.items():cmd=cmd.replace('{'+name+'}',shlex.quote(value))
subprocess.run(cmd,shell=True,check=True)
PY
    python3 - "$reviewed_spec" <<'PY'
import json,sys
s=json.load(open(sys.argv[1]));assert s.get('draft') is False and s.get('reviewed_by'), 'Review required'
PY
    python3 scripts/analysis/build_annotated.py --spec "$reviewed_spec"
    python3 scripts/analysis/verify_chords.py "files/analysis/$id/$id.analysis.json"
    python3 scripts/sync_site_data.py
    python3 scripts/build_catalog.py
    git add -- "$reviewed_spec" "files/analysis/$id" data
    git commit -m "Add reviewed score analysis: $id"
    if [[ "$mode" == push ]]; then
      pushed=0
      for attempt in 1 2 3; do
        git fetch origin main
        if ! git rebase origin/main; then
          conflict=0
          while IFS= read -r f; do
            case "$f" in data/*) git checkout --theirs -- "$f"; git add -- "$f";; *) conflict=1;; esac
          done < <(git diff --name-only --diff-filter=U)
          if [[ "$conflict" == 1 ]]; then git rebase --abort; echo 'Non-generated rebase conflict; review manually.' >&2; exit 1; fi
          GIT_EDITOR=true git rebase --continue || { git rebase --abort; exit 1; }
        fi
        python3 scripts/sync_site_data.py
        python3 scripts/build_catalog.py
        python3 scripts/analysis/verify_chords.py "files/analysis/$id/$id.analysis.json"
        node --check assets/watch.js
        git add -- data
        git diff --cached --quiet || git commit -m 'Rebuild analysis site data after rebase'
        if git push origin HEAD:main; then pushed=1; break; fi
      done
      [[ "$pushed" == 1 ]] || { echo 'Push failed after three attempts' >&2; exit 1; }
    fi
  fi
  processed=$((processed+1))
  [[ "$processed" -ge "$count" ]] && break
done < data/analysis_queue.txt
echo "Processed $processed items ($mode); drafts retained at $scratch"
