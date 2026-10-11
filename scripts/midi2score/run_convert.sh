#!/bin/bash
# MusicBot: convert queue.txt MIDI-only items to *_reconstructed.mxl; commit+push every 40 under the OCR lock.
cd /workspace/music/wt_analysis
python3 - <<'PY'
import json,sys,os,time,subprocess
sys.path.insert(0,'scripts/midi2score'); from midi2xml import convert
it={i['id']:i for i in json.load(open('data/library.json'))}
log=open('logs/midi2score.jsonl','a'); batch=[]
def push():
    if not batch: return
    subprocess.run(['git','add']+batch+['logs/midi2score.jsonl'],check=True)
    subprocess.run(['git','commit','-qm',f'MusicBot: {len(batch)} scores reconstructed from MIDI'],check=True)
    subprocess.run('flock /tmp/wt_ocr.lock scripts/midi2score/safe_push_wt.sh | tail -1',shell=True)
    batch.clear()
for k in open('scripts/midi2score/queue.txt').read().split():
    out=f'files/scores/{k}_reconstructed.mxl'
    if os.path.exists(out) or k not in it: continue
    t=time.time()
    try:
        r=subprocess.run(['timeout','180','python3','-c',f'import sys,json;sys.path.insert(0,"scripts/midi2score");from midi2xml import convert;print(json.dumps(convert({it[k]["midi_play_url"]!r},{out!r},{it[k]["title"]!r},{it[k]["composer"]!r})))'],capture_output=True,text=True)
        res=json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode==0 else {'error':r.stderr[-300:]}
    except Exception as e: res={'error':repr(e)}
    ok='error' not in res and res['note_match']>=0.98 and res['bad_bars']<=2
    if not ok and os.path.exists(out): os.remove(out)
    res.update(id=k,ok=ok,secs=round(time.time()-t,1)); log.write(json.dumps(res)+'\n'); log.flush()
    if ok: batch.append(out)
    if len(batch)>=40: push()
push()
PY
