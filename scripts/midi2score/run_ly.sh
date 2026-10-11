#!/bin/bash
# MusicBot: swap in LilyPond-converted scores for items the MIDI job has already processed. Loops until the MIDI job ends, then one final pass.
cd /workspace/music/wt_analysis
while :; do
  alive=0; pgrep -f run_convert.sh >/dev/null && alive=1
  python3 - <<'PY'
import json,os,sys,subprocess
sys.path.insert(0,'scripts/midi2score'); from ly2mxl import convert
seen={json.loads(l)['id'] for l in open('logs/ly2mxl.jsonl')} if os.path.exists('logs/ly2mxl.jsonl') else set()
done=[json.loads(l) for l in open('logs/midi2score.jsonl')]
log=open('logs/ly2mxl.jsonl','a'); add=[]; rm=[]
for r in done:
    k=r['id']
    if k in seen or 'midi_notes' not in r: continue
    res=convert(k,r['midi_notes'],f'files/scores/{k}_fromly.mxl'); seen.add(k)
    log.write(json.dumps(res)+'\n'); log.flush()
    if res['ok']:
        add.append(f'files/scores/{k}_fromly.mxl')
        old=f'files/scores/{k}_reconstructed.mxl'
        if os.path.exists(old): rm.append(old)
if add:
    import time
    for f in rm:
        if subprocess.run(['git','ls-files','--error-unmatch',f],capture_output=True).returncode==0: subprocess.run(['git','rm','-q','--cached',f])
        if os.path.exists(f): os.remove(f)
    for _ in range(5):
        if subprocess.run(['git','add']+add).returncode==0: break
        time.sleep(5)
    subprocess.run(['git','commit','-qm',f'MusicBot: {len(add)} scores converted from LilyPond source (replace MIDI reconstructions)','--']+add+rm)
    subprocess.run('flock /tmp/wt_ocr.lock scripts/midi2score/safe_push_wt.sh | tail -1',shell=True)
print('pass',len(add))
PY
  [ $alive = 0 ] && break; sleep 300
done
