#!/usr/bin/env python3
"""MIDI -> editable MusicXML reconstruction (MusicBot). Piano: hand split, key-aware spelling,
quantize (16ths + triplets), pickup detection, makeNotation (beams/ties/tuplets), sanity checks."""
import sys,json,copy,mido
from music21 import converter,stream,instrument,clef,key,pitch,meter,note,chord,metadata
def midi_notes(p):
    mf=mido.MidiFile(p);n=0
    for t in mf.tracks:
        for m in t:
            if m.type=='note_on' and m.velocity:n+=1
    return n
CHROM={'major':{1:'A1',3:'m3',6:'A4',8:'m6',10:'m7'},'minor':{1:'m2',4:'M3',6:'A4',9:'M6',11:'M7'}}
def respell(s,k):
    from music21 import interval
    t=pitch.Pitch(k.tonic.name)
    sc={p.name for p in k.getScale(k.mode).getPitches()}|{t.transpose(iv).name for iv in CHROM.get(k.mode,{}).values()}
    for n in s.recurse().notes:
        for p in n.pitches:
            p.spellingIsInferred=False
            if p.name in sc: continue
            for e in (p.getEnharmonic(),p.getHigherEnharmonic(),p.getLowerEnharmonic()):
                if e and e.name in sc and abs(e.alter)<=1: p.name=e.name;p.octave=e.octave;break
            else:
                if k.sharps<0 and p.accidental and p.accidental.name=='sharp': e=p.getEnharmonic();p.name=e.name;p.octave=e.octave
def midi_tracks(mid):
    """Raw note lists per note-bearing track straight from mido (no tie artefacts), quantised to 16ths/8th-triplets."""
    from fractions import Fraction
    mf=mido.MidiFile(mid); tpb=mf.ticks_per_beat; out=[]
    def q(x):
        return float(min((Fraction(round(x*g),g) for g in (4,3)),key=lambda v:abs(float(v)-x)))
    for t in mf.tracks:
        T=0; on={}; ns=[]
        for m in t:
            T+=m.time
            if m.type=='note_on' and m.velocity: on.setdefault(m.note,[]).append(T)
            elif m.type in('note_off','note_on') and on.get(m.note):
                st=on[m.note].pop(0); a=q(st/tpb); b=q(T/tpb)
                if b<=a: b=a+0.25
                ns.append([a,b-a,m.note,pitch.Pitch(midi=m.note)])
        if ns: out.append(ns)
    return out
def tidy(parts):
    """Rule fixes for 2-hand piano: move far-out-of-range notes to the other staff, trim legato/pedal
    overlaps inside a hand (fewer phantom voices and stray rests), and regroup same-onset notes into chords."""
    from music21 import duration as d
    hands=parts
    move=[[],[]]
    for x in hands[1]:
        if x[2]>=69: move[0].append(x)
    for x in hands[0]:
        if x[2]<=48: move[1].append(x)
    for h in (0,1):
        for x in move[h]: hands[1-h].remove(x); hands[h].append(x)
    out=[]
    for h in (0,1):
        ns=sorted(hands[h]); onsets=sorted({x[0] for x in ns})
        for x in ns:
            nxt=next((o for o in onsets if o>x[0]+1e-6),None)
            if nxt is not None and x[0]+x[1]>nxt+1e-6:
                ov=x[0]+x[1]-nxt
                if ov<=0.5 or ov<=0.34*x[1]: x[1]=nxt-x[0]
        groups={}
        for x in ns: groups.setdefault((x[0],x[1]),[]).append(x[3])
        P=stream.Part()
        for (o,l),pl in sorted(groups.items()):
            if l<=0: continue
            m=note.Note(pl[0]) if len(pl)==1 else chord.Chord(sorted(pl,key=lambda q:q.midi))
            m.quarterLength=l; P.insert(o,m)
        out.append(P)
    return out
def fix_keys(sc,k=None):
    """Key signature (+confident key changes), spelling against it, accidentals only where needed."""
    if k is None:
        k=sc.analyze('key'); k=key.Key(k.tonic.name,k.mode)
    # Key regions: 8-bar windows; a change needs 2+ consecutive confident windows in the same new key.
    regions=[(0,k)]
    try:
        p0=sc.parts[0]; nm=len(p0.getElementsByClass(stream.Measure)); W=8; wins=[]
        for a in range(0,nm,W):
            seg=stream.Score([pp.measures(a,a+W-1) for pp in sc.parts])
            kk=seg.analyze('key'); wins.append((a,key.Key(kk.tonic.name,kk.mode),kk.correlationCoefficient))
        cur=k
        for i in range(len(wins)-1):
            (a,ka,ca),(b,kb,cb)=wins[i],wins[i+1]
            if ka.sharps!=cur.sharps and ka.sharps==kb.sharps and min(ca,cb)>0.8 and abs(ka.sharps)<=6:
                cur=ka; regions.append((a,ka))
    except Exception: regions=[(0,k)]
    for p in sc.parts:
        ms=list(p.getElementsByClass(stream.Measure))
        for m in ms:
            for ks in list(m.recurse().getElementsByClass(key.KeySignature)): ks.activeSite.remove(ks)
        for i,(a,kk) in enumerate(regions):
            end=regions[i+1][0] if i+1<len(regions) else len(ms)
            seg=stream.Stream(); [seg.append(m) for m in ms[a:end]] if False else None
            for m in ms[a:end]: respell(m,kk)
            if a<len(ms): ms[a].insert(0,key.KeySignature(kk.sharps))
        for m in ms:
            for n in m.recurse().notes:
                for pt in n.pitches:
                    if pt.accidental: pt.accidental.displayStatus=None
        p.makeAccidentals(inPlace=True,overrideStatus=True,cautionaryPitchClass=False,cautionaryNotImmediateRepeat=False)
def convert(mid,out,title='',composer=''):
    s=converter.parse(mid,quantizePost=True,quarterLengthDivisors=(4,3))
    parts=[p for p in s.parts if p.recurse().notes]
    if len(parts)==1:
        flat=parts[0].flatten().stripTies().notes; rh=stream.Part();lh=stream.Part()
        for n in flat:
            ps=[p.midi for p in n.pitches]; hi=[p for p in n.pitches if p.midi>=60]; lo=[p for p in n.pitches if p.midi<60]
            for tgt,pl in ((rh,hi),(lh,lo)):
                if pl:
                    m=(note.Note(pl[0]) if len(pl)==1 else chord.Chord(pl)); m.duration=copy.deepcopy(n.duration); tgt.insert(n.offset,m)
        parts=[rh,lh]
    elif len(parts)>2:
        parts=sorted(parts,key=lambda p:-sum(x.pitches[0].midi for x in p.recurse().notes)/max(1,len(p.recurse().notes)))
    if len(parts)==2:
        tr=midi_tracks(mid)
        if len(tr)==2: parts=tidy(tr)
    ts=s.recurse().getElementsByClass(meter.TimeSignature)
    ts=ts[0] if ts else meter.TimeSignature('4/4')
    k=s.analyze('key'); k=key.Key(k.tonic.name,k.mode)
    if k.sharps>6 or (k.sharps==6 and k.mode=='major'): k=key.Key(k.tonic.getEnharmonic().name,k.mode)
    if k.sharps<-6: k=key.Key(k.tonic.getEnharmonic().name,k.mode)
    bar=ts.barDuration.quarterLength; allnotes=[n for p in parts for n in p.flatten().notes]
    firsts=sorted(min((n.offset for n in p.flatten().notes),default=0) for p in parts)
    shift=0.0
    lag=firsts[-1]%bar if len(firsts)>=2 else 0
    if len(firsts)>=2 and firsts[0]==0 and lag>=4/ts.denominator-1e-6 and firsts[-1]<2*bar: shift=(bar-lag)%bar
    sc=stream.Score();sc.metadata=metadata.Metadata(title=title,composer=composer)
    for i,p in enumerate(parts[:2] if len(parts)<=2 else parts):
        np_=stream.Part();np_.insert(0,instrument.Piano() if len(parts)<=2 else instrument.Instrument())
        np_.insert(0,copy.deepcopy(ts));np_.insert(0,key.KeySignature(k.sharps))
        np_.insert(0,clef.TrebleClef() if i==0 else clef.BassClef())
        for n in p.flatten().notesAndRests:
            if n.isRest: continue
            np_.insert(n.offset+shift,copy.deepcopy(n))
        sc.insert(0,np_)
    respell(sc,k)
    sc=sc.makeNotation()
    if shift:
        for p in sc.parts:
            m=p.getElementsByClass(stream.Measure)[0]
            conts=[m]+list(m.voices)
            for c in conts:
                for r in list(c.getElementsByClass(note.Rest)):
                    if c.elementOffset(r)+r.quarterLength<=shift+1e-6: c.remove(r)
                for e in list(c.notesAndRests): c.setElementOffset(e,c.elementOffset(e)-shift)
            m.paddingLeft=shift; m.number=0
    fix_keys(sc,k)
    for p in sc.parts:
        ms=list(p.getElementsByClass(stream.Measure))
        if shift:
            for i,m in enumerate(ms): m.number=i   # pickup = bar 0, then 1..N
        for m in ms:
            vs=list(m.voices)
            for v in vs:   # drop rest-only voices (Opus review of Fur Elise)
                if not v.notes and len(vs)>1: m.remove(v); vs.remove(v)
            if len(vs)==1:
                v=vs[0]; o=m.elementOffset(v)
                for e in list(v.notesAndRests): m.insert(o+v.elementOffset(e),e)
                m.remove(v); vs=[]
            for v in vs[1:]:
                for r in v.getElementsByClass(note.Rest): r.style.hideObjectOnPrint=True
    sc.write('mxl' if out.endswith('.mxl') else 'musicxml',fp=out)
    # sanity
    back=converter.parse(out); bad=0
    for p in back.parts:
        for m in p.getElementsByClass(stream.Measure):
            if m.number>0 and abs(m.duration.quarterLength-m.barDuration.quarterLength)>1e-6 and m is not p.getElementsByClass(stream.Measure)[-1]: bad+=1
    xn=sum(len(n.pitches) for n in back.recurse().notes if not (n.tie and n.tie.type in('stop','continue')))
    mn=midi_notes(mid)
    return dict(pickup=shift,key=str(k),ts=ts.ratioString,parts=len(back.parts),measures=len(back.parts[0].getElementsByClass(stream.Measure)),
                midi_notes=mn,xml_notes=xn,note_match=round(xn/max(1,mn),3),bad_bars=bad)
if __name__=='__main__' and sys.argv[1]=='--fix-keys':
    sc=converter.parse(sys.argv[2]); fix_keys(sc); sc.write('mxl' if sys.argv[2].endswith('.mxl') else 'musicxml',fp=sys.argv[2]); sys.exit(0)
if __name__=='__main__':
    print(json.dumps(convert(*sys.argv[1:3],*(sys.argv[3:5]))))
