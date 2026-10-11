#!/bin/bash
# safe_push.sh: rebase wt_ocr onto origin/main (union-merge CSV/STATUS rows, so the nightly MusicBot batch and this run never drop each other's rows), rebuild data, verify, push. Retries if origin moved.
cd "${1:-/workspace/music/wt_analysis}"; set -o pipefail
for t in 1 2 3; do
  git fetch -q origin main
  if ! git rebase -q --autostash origin/main; then
    for f in $(git diff --name-only --diff-filter=U); do case $f in data/*) git checkout --theirs -- "$f";; esac; git add "$f"; done
    GIT_EDITOR=true git rebase --continue || { git rebase --abort; echo SAFE_PUSH_CONFLICT; exit 1; }
  fi
  python3 scripts/sync_site_data.py >/dev/null && python3 scripts/build_catalog.py >/dev/null
  python3 - <<'PY' || { echo DUP_ID; exit 1; }
import csv,collections
c=collections.Counter(r['id'] for r in csv.DictReader(open('library_bulk.csv',newline='',encoding='utf-8')))
d=[k for k,v in c.items() if v>1]; print('rows',sum(c.values()),'dups',d[:5]); raise SystemExit(1 if d else 0)
PY
  python3 scripts/bulk/licence_audit.py | tail -1
  git add -A data; git diff --cached --quiet || git commit -qm "Rebuild site data after rebase"
  git push -q origin HEAD:main && { echo SAFE_PUSH_OK $(git log -1 --format=%h); exit 0; }
done; echo SAFE_PUSH_FAIL; exit 1
