#!/bin/bash
# MusicBot: draft analysis -> Claude Opus review -> build -> verify -> commit -> locked safe push. One piece at a time.
# Usage: run_analyse.sh IDS_FILE [N]. On failure only that piece's own files are discarded (never a worktree-wide checkout).
cd /workspace/music/wt_analysis; IDS=${1:?ids file}; N=${2:-10}; n=0
S=/tmp/musicbot_analysis; mkdir -p $S; L=$S/log
discard(){ rm -rf "files/analysis/$1" "scripts/analysis/specs/$1.json" "$S/specs/$1.draft.json" "$S/bundles/$1"; }
while read id; do
  [ -z "$id" ] && continue; [ $n -ge $N ] && break
  [ -d files/analysis/$id ] && continue
  [ -f /tmp/musicbot_analysis.PAUSE ] && { echo "PAUSED (flag file) before $id" >>$L; break; }
  python3 scripts/analysis/auto_analyse.py "$id" --out-root $S/bundles --spec-dir $S/specs >>$L 2>&1 || { echo "SKIP $id draft" >>$L; discard $id; continue; }
  match=$(grep -m1 ",$id," ../library_study/MATCHES.csv | cut -d, -f11)
  P="You are reviewing one annotated-score draft for the music library. Follow scripts/analysis/BRIEF_analyse.md exactly. ID=$id DRAFT_SPEC=$S/specs/$id.draft.json REVIEWED_SPEC=scripts/analysis/specs/$id.json. The score was reconstructed from MIDI. ${match:+A study-only expert analysis exists at ../library_study/$match : use it ONLY to check and correct your own chord labels; never copy its text, comments or labels wholesale into the spec, and do not cite it.} Write the reviewed spec (reviewed_by: 'claude-opus-5-5 (MusicBot) $(date +%F)'), build it, run verify_chords.py. Do not commit, push, run git, or modify any other files. Keep notes concise."
  timeout -k 60 2400 bash -lc "claude -p --model opus --dangerously-skip-permissions $(printf %q "$P")" >$S/$id.review.log 2>&1
  if rg -qi "usage limit|rate limit|limit reached|out of credit|429|402" $S/$id.review.log; then echo "STOP quota at $id: $(tail -c 200 $S/$id.review.log)" >>$L; discard $id; break; fi
  python3 -c "import json;s=json.load(open('scripts/analysis/specs/$id.json'));assert s.get('draft') is False and s.get('reviewed_by')" 2>/dev/null || { echo "SKIP $id review" >>$L; discard $id; continue; }
  { python3 scripts/analysis/build_annotated.py --spec scripts/analysis/specs/$id.json && python3 scripts/analysis/verify_chords.py files/analysis/$id/$id.analysis.json; } >>$L 2>&1 || { echo "SKIP $id verify" >>$L; discard $id; continue; }
  for t in 1 2 3 4 5; do git add scripts/analysis/specs/$id.json files/analysis/$id && break; sleep 5; done
  git commit -qm "MusicBot: draft analysis (Opus reviewed) for $id" -- scripts/analysis/specs/$id.json files/analysis/$id
  flock /tmp/wt_ocr.lock scripts/midi2score/safe_push_wt.sh 2>&1 | tail -1 >>$L
  n=$((n+1)); echo "DONE $id $(date +%H:%M)" >>$L
done < $IDS
echo "FINISHED $n $(date +%H:%M)" >>$L
