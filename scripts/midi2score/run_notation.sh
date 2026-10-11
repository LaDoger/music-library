#!/bin/bash
# MusicBot: Opus notation-fix pass, one piece at a time, after the analysis batch. Discards only the piece's own file on failure.
cd /workspace/music/wt_analysis; IDS=$1; D=/tmp/musicbot_notation; L=$D/log; mkdir -p $D
while read id; do
  [ -z "$id" ] && continue
  [ -f /tmp/musicbot_analysis.PAUSE ] && { echo "PAUSED before $id" >>$L; break; }
  f=files/scores/${id}_reconstructed.mxl; [ -f $f ] || { echo "SKIP $id no mxl" >>$L; continue; }
  [ -f $D/$id.done ] && continue
  mid=$(python3 -c "import json;print(json.load(open('data/items/$id.json'))['midi_play_url'])")
  touch $D/$id.done   # stop reconvert_all from overwriting while we edit
  cp $f $D/$id.orig.mxl
  P="Follow scripts/midi2score/BRIEF_notation_fix.md for ID=$id MXL=$f MIDI=$mid."
  timeout -k 60 2400 bash -lc "claude -p --model opus --dangerously-skip-permissions $(printf %q "$P")" >$D/$id.review.log 2>&1
  if rg -qi "usage limit|rate limit|limit reached|out of credit" $D/$id.review.log; then cp $D/$id.orig.mxl $f; rm -f $D/$id.done; echo "STOP quota at $id" >>$L; break; fi
  if python3 scripts/midi2score/check_notes.py $mid $f >>$L 2>&1 && ! cmp -s $f $D/$id.orig.mxl; then
    for t in 1 2 3 4 5; do git add $f && break; sleep 5; done
    git commit -qm "MusicBot: Opus notation fix for $id" -- $f
    flock /tmp/wt_ocr.lock scripts/midi2score/safe_push_wt.sh 2>&1 | tail -1 >>$L; echo "DONE $id $(date +%H:%M)" >>$L
  else cp $D/$id.orig.mxl $f; echo "REVERT $id" >>$L; fi
done < $IDS
echo FINISHED $(date +%H:%M) >>$L
