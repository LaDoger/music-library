#!/usr/bin/env python3
"""Conservative draft generator for <=64-bar piano MIDI items (never auto-reviewed).
Chordify on a half-bar grid; windowed Krumhansl key estimation; heuristic key
changes/cadences/pedals. Every candidate needs a human note-level review.
"""
import argparse,json,math
from pathlib import Path
from music21 import stream,note,chord,key,harmony,roman
from common import ROOT,read_midi,weights,bars_for,json_write
from build_annotated import build

def draft(item_id,out_root,spec_dir):
    item=json.loads((ROOT/'data/items'/f'{item_id}.json').read_text())
    if item.get('verified')!='yes' or item.get('score_status') not in ('clean','attribution'):
        raise ValueError('Only verified clean/attribution scores can enter the draft queue')
    source=item.get('midi_play_url')
    if not source:raise ValueError('No directly playable MIDI; convert MusicXML first with build_midi_play.py')
    ns,marks,tracks=read_midi(ROOT/source)
    if not ns or any(n['program']>7 for n in ns) or len({n['track'] for n in ns})>3:
        raise ValueError('Piano-only eligibility failed (<=3 pitched tracks, GM programs 0–7)')
    times=[m for m in marks if m['type']=='time_signature'];tm=times[0] if times else {'numerator':4,'denominator':4}
    length=tm['numerator']*4/tm['denominator'];total=max(n['end'] for n in ns)
    if any((m['numerator'],m['denominator'])!=(tm['numerator'],tm['denominator']) for m in times):
        raise ValueError('Changing meter needs a hand-written bar layout')
    end=math.ceil((total-1e-5)/length)*length;n_bars=round(end/length)
    if n_bars>64:raise ValueError(f'{n_bars} bars > 64; review/excerpt manually')
    # Actual MIDI notes enter music21; chordify and Krumhansl work independently
    # of the labelled-chord verification, which reads original notes again.
    score=stream.Stream()
    for n in ns:score.insert(n['start'],note.Note(n['pitch'],quarterLength=n['end']-n['start']))
    initial=score.analyze('Krumhansl');kname=initial.tonic.name+('m' if initial.mode=='minor' else '')
    keyarg=initial.tonic.name.lower() if initial.mode=='minor' else initial.tonic.name
    meta={'id':item_id,'parent_item_id':item_id,'title':item['title'],'composer':item['composer'],'source_file':source,
          'quarter_range':[0,end],'bar_quarters':length,'time_signature':f"{tm['numerator']}/{tm['denominator']}",
          'key':keyarg,'tempo':100,'midi_play_url':source,'source_licence':item['editable_license'],
          'notation_notes':'DRAFT. MIDI quantisation and key/chord estimates need human review. No notes or rights are independently corrected.'}
    bars=bars_for(meta);flags=[];lastkey=keyarg;last_symbol=None;bass_history=[]
    for b in bars:
        a=b['start_quarter'];z=a+b['duration_quarters']
        if (b['bar']-1)%8==0:
            window=stream.Stream()
            for n in ns:
                lo,hi=max(a,n['start']),min(a+8*length,n['end'])
                if hi>lo:window.insert(lo-a,note.Note(n['pitch'],quarterLength=hi-lo))
            if window.notes:
                k=window.analyze('Krumhansl');local=k.tonic.name.lower() if k.mode=='minor' else k.tonic.name
            else:local=lastkey
        b.update(key=local,chords=[],events=[])
        if local!=lastkey:
            b['events'].append({'type':'modulation','technique':'direct_phrase_modulation','text':f'DRAFT key estimate {lastkey} → {local}; confirm tonicization vs modulation','from_key':lastkey,'to_key':local})
            flags.append({'bar':b['bar'],'reason':'Windowed Krumhansl key change is a candidate only.'})
        lastkey=local
        for start,stop in [(a,a+length/2),(a+length/2,z)]:
            span=stream.Stream()
            for n in ns:
                lo,hi=max(start,n['start']),min(stop,n['end'])
                if hi>lo:span.insert(lo-start,note.Note(n['pitch'],quarterLength=hi-lo))
            segments=list(span.chordify().recurse().getElementsByClass(chord.Chord))
            candidate=max(segments,key=lambda c:c.quarterLength) if segments else None
            symbol='?';rn='?'
            if candidate and len(set(candidate.pitchClasses))>=3:
                try:
                    h=harmony.chordSymbolFromChord(candidate)
                    if 'cannot' not in h.figure.lower():symbol=h.figure;rn=roman.romanNumeralFromChord(h,key.Key(local)).figure
                except Exception:pass
            b['chords'].append({'beat':start-a+1,'symbol':symbol,'rn':rn,'function':'DRAFT estimate; review','reason':'No confident complete sonority in the half-bar' if symbol=='?' else ''})
        # Collapse duplicate harmony at the same local key to its full harmonic span.
        if len(b['chords'])==2 and b['chords'][0]['symbol']==b['chords'][1]['symbol']:b['chords'].pop()
        symbol=b['chords'][-1]['symbol']
        if symbol!='?':
            h=harmony.ChordSymbol(symbol);root=h.root().pitchClass;k=key.Key(local)
            if root==(k.tonic.pitchClass+7)%12 and b['bar']%4==0:
                b['events'].append({'type':'cadence','technique':'HC','text':'DRAFT half-cadence candidate; confirm phrase end'})
            if last_symbol and last_symbol!='?':
                prev=harmony.ChordSymbol(last_symbol)
                if prev.root().pitchClass==(k.tonic.pitchClass+7)%12 and root==k.tonic.pitchClass:
                    b['events'].append({'type':'cadence','technique':'IAC','text':'DRAFT dominant–tonic candidate; check melody, bass and phrase boundary'})
        last_symbol=symbol
        low=[n['pitch'] for n in ns if n['start']<z and n['end']>a]
        bass_history.append(min(low)%12 if low else None)
        if len(bass_history)>=3 and bass_history[-1] is not None and len(set(bass_history[-3:]))==1:
            b['events'].append({'type':'bass_line','technique':'pedal','text':'DRAFT repeated lowest pitch class across three bars; confirm a real pedal'})
    spec={'meta':meta,'draft':True,'reviewed_by':None,'summary':'Automatic draft: musical function, events, phrasing and expressive use remain unreviewed.',
          'sections':[{'name':'Draft phrase','start_bar':1,'end_bar':n_bars,'mood':[],'description':'Add human form/story and section mood.'}],
          'bars':bars,'mood':[],'tricks':[],'loop_candidates':[],'hook_candidates':[],'kpop_uses':[],'review_flags':flags}
    spec_path=Path(spec_dir)/f'{item_id}.draft.json';json_write(spec_path,spec)
    bundle=build(spec,out_root)
    print(f'Draft spec: {spec_path}; reviewed_by=null; not exposed by sync_site_data.py')
    return bundle

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('id');ap.add_argument('--out-root',default=str(ROOT/'files/analysis'));ap.add_argument('--spec-dir',default=str(ROOT/'scripts/analysis/specs'))
    a=ap.parse_args();draft(a.id,a.out_root,a.spec_dir)
if __name__=='__main__':main()
