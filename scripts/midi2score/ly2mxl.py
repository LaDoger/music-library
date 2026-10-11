#!/usr/bin/env python3
"""MusicBot: Mutopia .ly -> MusicXML via python-ly (/home/box/.venvs/ly). Accept only if note count matches the MIDI (+-1%), 0 bad bars, >=2 parts."""
import sys,os,glob,subprocess,tempfile,zipfile,json,shutil
from music21 import converter,stream
LY='/home/box/.venvs/ly/bin/ly'
def find_ly(item_id):
    d='files/scores'; f=f'{d}/{item_id}.ly'
    if os.path.exists(f): return f,None
    zs=glob.glob(f'{d}/{item_id}_lilypond*.zip')+glob.glob(f'{d}/{item_id}*lys*.zip')
    if not zs: return None,None
    t=tempfile.mkdtemp(prefix='mbly'); zipfile.ZipFile(zs[0]).extractall(t)
    lys=[p for p in glob.glob(t+'/**/*.ly',recursive=True)]
    # main file = one containing \score
    main=[p for p in lys if '\\score' in open(p,errors='ignore').read()]
    return (main[0] if main else None),t
def convert(item_id,midi_notes,out):
    ly,tmp=find_ly(item_id)
    if not ly: return {'id':item_id,'ok':False,'why':'no ly'}
    x=tempfile.mktemp(suffix='.xml')
    try:
        r=subprocess.run(['timeout','90',LY,'musicxml',os.path.basename(ly),'-o',x],cwd=os.path.dirname(os.path.abspath(ly)),capture_output=True,text=True)
        s=converter.parse(x)
        n=sum(len(v.pitches) for v in s.recurse().notes if not (v.tie and v.tie.type in('stop','continue')))
        bad=sum(1 for p in s.parts for m in p.getElementsByClass(stream.Measure)[1:-1] if abs(m.duration.quarterLength-m.barDuration.quarterLength)>1e-6)
        ok=len(s.parts)>=1 and abs(n-midi_notes)<=max(2,0.01*midi_notes) and bad==0
        res={'id':item_id,'ok':ok,'ly_notes':n,'midi_notes':midi_notes,'bad_bars':bad,'parts':len(s.parts)}
        if ok: s.write('mxl',fp=out)
        return res
    except Exception as e: return {'id':item_id,'ok':False,'why':repr(e)[:150]}
    finally:
        if tmp: shutil.rmtree(tmp,ignore_errors=True)
        if os.path.exists(x): os.remove(x)
