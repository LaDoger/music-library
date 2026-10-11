#!/bin/bash
# MusicBot: re-run the (improved) MIDI converter over existing *_reconstructed.mxl files; commit+push in batches.
cd /workspace/music/wt_analysis
python3 - <<'PY'
import json,glob,subprocess,time,os
it={i['id']:i for i in json.load(open('data/library.json'))}
done=[];
def push():
    if not done: return
    for _ in range(5):
        if subprocess.run(['git','add']+done).returncode==0: break
        time.sleep(5)
    subprocess.run(['git','commit','-qm',f'MusicBot: re-render {len(done)} MIDI reconstructions (staff crossings, overlap trim, 32nds)','--']+done)
    subprocess.run('flock /tmp/wt_ocr.lock scripts/midi2score/safe_push_wt.sh | tail -1',shell=True); done.clear()
for f in sorted(glob.glob('files/scores/*_reconstructed.mxl')):
    k=os.path.basename(f)[:-len('_reconstructed.mxl')]
    if k not in it or os.path.exists(f'/tmp/musicbot_notation/{k}.done'): continue
    tmp=f'/tmp/mb_re_{k}.mxl'
    r=subprocess.run(['timeout','180','python3','-c',f'import sys,json;sys.path.insert(0,"scripts/midi2score");from midi2xml import convert;print(json.dumps(convert({it[k]["midi_play_url"]!r},{tmp!r},{it[k]["title"]!r},{it[k]["composer"]!r})))'],capture_output=True,text=True)
    try: res=json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: print('fail',k); continue
    if 0.98<=res['note_match']<=1.02 and res['bad_bars']<=2: os.replace(tmp,f); done.append(f)
    elif os.path.exists(tmp): os.remove(tmp)
    if len(done)>=40: push()
push()
PY
