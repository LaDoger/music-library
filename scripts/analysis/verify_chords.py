#!/usr/bin/env python3
"""Check every labelled span against original, unsimplified MIDI notes.
Root, third, fifth and seventh (when present in the symbol) must occur; chord
pitch classes must cover >=70% of note-duration-weighted pitch class mass.
Non-chord tones stay in the denominator. '?' is reported, never a pass.
"""
import argparse, json
from pathlib import Path
import music21
from music21 import harmony
from common import ROOT, read_midi, sliced_notes, weights, json_write

def verify(bundle):
    meta=bundle['meta']; ns,_,_=read_midi(ROOT/meta['source_file'])
    ns=sliced_notes(ns,*meta['quarter_range']); details=[]; flags=list(bundle.get('review_flags',[]))
    for bar in bundle['bars']:
        cs=bar.get('chords',[])
        for i,c in enumerate(cs):
            a=bar['start_quarter']+c['beat']-1
            z=bar['start_quarter']+(cs[i+1]['beat']-1 if i+1<len(cs) else bar['duration_quarters'])
            w=weights(ns,a,z); d={'bar':bar['bar'],'beat':c['beat'],'symbol':c['symbol'],'start_quarter':a,'end_quarter':z,
               'sounding_pc_weights':{str(k):round(v,5) for k,v in sorted(w.items())}}
            if c['symbol']=='?':
                d.update(match=False,unknown=True,reason=c.get('reason','Sparse/ambiguous harmony; no asserted chord'))
            else:
                ch=harmony.ChordSymbol(c['symbol']); pcs={p.pitchClass for p in ch.pitches}
                required={p.pitchClass for p in [ch.root(),ch.third,ch.fifth,ch.seventh] if p is not None}
                missing=sorted(required-set(w));cov=sum(v for pc,v in w.items() if pc in pcs)/sum(w.values()) if w else 0
                d.update(match=not missing and cov>=.7-1e-8,unknown=False,required_pcs=sorted(required),missing_pcs=missing,coverage=round(cov,5))
                if not d['match']: d['reason']=f"Missing chord PCs {missing}; duration-weighted coverage {cov:.1%} (requires 70%)"
            if not d['match']: flags.append({'bar':bar['bar'],'beat':c['beat'],'reason':d['reason']})
            details.append(d)
    labelled=[d for d in details if not d['unknown']];matched=sum(d['match'] for d in labelled)
    return {'music21_version':music21.__version__,'method':'original MIDI; all tracks, no NCT removal; root+third+fifth+seventh present; duration-weighted coverage >=0.70',
            'chord_note_match_pct':round(100*matched/len(labelled),2) if labelled else 0,
            'labelled_spans':len(labelled),'matched_spans':matched,'unknown_spans':len(details)-len(labelled),
            'total_spans':len(details),'labelled_span_pct':round(100*len(labelled)/len(details),2) if details else 0,
            'flagged_bars':flags,'spans':details}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('bundle');ap.add_argument('--write',action='store_true');ap.add_argument('--min-match',type=float,default=90)
    a=ap.parse_args();p=Path(a.bundle);b=json.loads(p.read_text());v=verify(b)
    if a.write:b['verification']=v;json_write(p,b)
    print(json.dumps({k:v[k] for k in ['chord_note_match_pct','labelled_spans','matched_spans','unknown_spans','flagged_bars']},ensure_ascii=False,indent=2))
    return 0 if v['chord_note_match_pct']>=a.min_match else 1
if __name__=='__main__':raise SystemExit(main())
