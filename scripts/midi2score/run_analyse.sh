#!/bin/bash
# MusicBot: draft analysis -> Grok 4.7 review -> build -> verify -> commit -> locked safe push. One piece at a time.
cd /workspace/music/wt_analysis; N=${1:-30}; n=0
S=/tmp/musicbot_analysis; mkdir -p $S
python3 - > $S/ids.txt <<'PY'
import json
ok={}
for l in open('logs/midi2score.jsonl'):
    r=json.loads(l)
    if r.get('ok') and r['measures']<=64: ok[r['id']]=1
for k in open('/tmp/mb_pilot/ids.txt').read().split()+open('scripts/midi2score/queue.txt').read().split():
    if (k in ok or k in ('bach_bwv846_prelude','bach_bwv773_invention2','chopin_op28_suffocation','schumann_op15_7_traumerei')): print(k)
PY
while read id; do
  [ $n -ge $N ] && break
  [ -d files/analysis/$id ] && continue
  python3 scripts/analysis/auto_analyse.py "$id" --out-root $S/bundles --spec-dir $S/specs >>$S/log 2>&1 || { echo "SKIP $id draft" >>$S/log; continue; }
  match=$(grep -m1 ",$id," ../library_study/MATCHES.csv | cut -d, -f11)
  P="You are reviewing one annotated-score draft for the music library. Follow scripts/analysis/BRIEF_analyse.md exactly. ID=$id DRAFT_SPEC=$S/specs/$id.draft.json REVIEWED_SPEC=scripts/analysis/specs/$id.json. The score was reconstructed from MIDI. ${match:+A study-only expert analysis exists at ../library_study/$match : use it ONLY to check and correct your own chord labels; never copy its text, comments or labels wholesale into the spec, and do not cite it.} Write the reviewed spec, build it, run verify_chords.py. Do not commit, push, or touch other files. Keep notes concise."
  timeout 1500 grok -m grok-4.7 --always-approve --cwd "$PWD" -p "$P" >>$S/log 2>&1
  python3 -c "import json,sys;s=json.load(open('scripts/analysis/specs/$id.json'));assert s.get('draft') is False and s.get('reviewed_by')" 2>/dev/null || { echo "SKIP $id review" >>$S/log; git checkout -q -- . ; rm -rf files/analysis/$id scripts/analysis/specs/$id.json; continue; }
  python3 scripts/analysis/build_annotated.py --spec scripts/analysis/specs/$id.json >>$S/log 2>&1 && python3 scripts/analysis/verify_chords.py files/analysis/$id/$id.analysis.json >>$S/log 2>&1 || { echo "SKIP $id verify" >>$S/log; rm -rf files/analysis/$id scripts/analysis/specs/$id.json; continue; }
  git add scripts/analysis/specs/$id.json files/analysis/$id && git commit -qm "MusicBot: draft analysis (Grok 4.7 reviewed) for $id"
  flock /tmp/wt_ocr.lock scripts/midi2score/safe_push_wt.sh | tail -1 >>$S/log
  n=$((n+1)); echo "DONE $id $(date +%H:%M)" >>$S/log
done < $S/ids.txt
echo "FINISHED $n" >>$S/log
