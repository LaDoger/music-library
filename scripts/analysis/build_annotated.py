#!/usr/bin/env python3
"""Build an annotated MusicXML + JSON + Markdown bundle from MIDI and a reviewed spec.
Usage: python3 scripts/analysis/build_annotated.py --spec scripts/analysis/specs/ID.json
Optional --midi and --start/--end override the source and absolute quarter range.
Dependencies: music21, mido. No MIDI duplication or audio rendering.
"""
import argparse, copy, json, math
from collections import defaultdict
from pathlib import Path
from fractions import Fraction
import xml.etree.ElementTree as ET
from music21 import stream, note, chord, key, clef, meter, tempo, instrument, layout, metadata, harmony, tie
from common import ROOT, PREFIXES, read_midi, sliced_notes, bars_for, spelling, json_write
from verify_chords import verify

# Both straight sixteenths and eighth-note triplets, plus sixteenth triplets.
def quantise(q,grids=(4,3,6,8)):
    return min((Fraction(round(q*g),g) for g in grids),key=lambda v:abs(float(v)-q))

def staff_notes(ns,meta):
    """Original piano staves; orchestral reduction keeps the oboe solo and
    compresses harp/string accompaniment to bass + up to four upper PCs.
    The verifier always sees the unsimplified source, independently.
    """
    if meta.get('reduction'):
        upper=[n for n in ns if n['track']==meta.get('melody_track',3)]
        lower_src=[n for n in ns if n['track'] in meta.get('accompaniment_tracks',[13,14,15,16,17,18])]
        points=sorted({quantise(n[t]) for n in lower_src for t in ('start','end')})
        lower=[]
        for a,z in zip(points,points[1:]):
            sounding=sorted({n['pitch'] for n in lower_src if n['start']<float(z)-.04 and n['end']>float(a)+.04})
            if not sounding:continue
            bass=sounding[0]; pcs=sorted({p%12 for p in sounding if p!=bass})
            voicing=[bass]+[48+pc for pc in pcs][:4]
            for p in set(voicing):lower.append(dict(start=float(a),end=float(z),pitch=p,velocity=64,track=1))
        # Merge tied sounding pitches before voice allocation.
        merged=[]
        for p in sorted({n['pitch'] for n in lower}):
            seq=sorted((n for n in lower if n['pitch']==p),key=lambda n:n['start'])
            for n in seq:
                if merged and merged[-1]['pitch']==p and abs(merged[-1]['end']-n['start'])<1e-7:merged[-1]['end']=n['end']
                else:merged.append(n.copy())
        return upper,merged
    tracks=sorted({n['track'] for n in ns})
    if len(tracks)==2:return ([n for n in ns if n['track']==tracks[0]],[n for n in ns if n['track']==tracks[1]])
    return ([n for n in ns if n['pitch']>=60],[n for n in ns if n['pitch']<60])

def make_staff(ns,bars,meta,upper):
    part=stream.PartStaff(id='RH' if upper else 'LH');part.partName='Piano' if upper else ''
    part.insert(0,instrument.Piano())
    # Equal onsets/durations become chords; independent held notes retain voices.
    groups=defaultdict(list)
    for n in ns:
        if n['end']-n['start']<.10:continue  # MIDI grace/turn notes; documented
        grids=meta.get('quantisation_divisors',(4,3,6,8))
        a,z=quantise(n['start'],grids),quantise(n['end'],grids)
        # Long MIDI notes are often gated ~0.1–0.21 q before a notated release.
        # Restore that release to avoid spurious 11:12 tuplets in sustained notes.
        next_straight=math.ceil(n['end']*4)/4
        intended=next_straight-float(a)
        if n['end']-n['start']>1.7 and abs(intended-round(intended))<1e-7 and 0<next_straight-n['end']<.22:
            z=Fraction(round(next_straight*4),4)
        if z<=a:continue
        groups[(a,z)].append(n)
    voices=[];ends=[]
    for (a,z),group in sorted(groups.items()):
        vi=next((i for i,t in enumerate(ends) if t<=a),len(ends))
        if vi==len(ends):ends.append(z);voices.append([])
        else:ends[vi]=z
        voices[vi].append((a,z,group))
    previous_key=None; previous_time=None
    for bi,b in enumerate(bars):
        m=stream.Measure(number=b['bar']);a=Fraction(str(b['start_quarter']));z=a+Fraction(str(b['duration_quarters']))
        kname=b['key'];ts=b.get('time_signature',meta['time_signature'])
        if bi==0:m.insert(0,clef.TrebleClef() if upper else clef.BassClef())
        if kname!=previous_key:m.insert(0,key.Key(kname));previous_key=kname
        if ts!=previous_time:m.insert(0,meter.TimeSignature(ts));previous_time=ts
        if b['bar']==0:m.paddingLeft=Fraction(str(meta['bar_quarters']))-(z-a)
        for vi,vnotes in enumerate(voices):
            v=stream.Voice(id=vi+1);pos=a
            for na,nz,group in vnotes:
                lo,hi=max(a,na),min(z,nz)
                if hi<=lo:continue
                if lo>pos:v.insert(pos-a,note.Rest(quarterLength=lo-pos))
                current=next((c for c in reversed(b['chords']) if c['beat']-1<=float(lo-a)+1e-6),None)
                preferred={}
                if current and current['symbol']!='?':
                    preferred={p.pitchClass:p.name for p in harmony.ChordSymbol(current['symbol']).pitches}
                ps=[]
                for midi_pitch in sorted({n['pitch'] for n in group}):
                    p=spelling(midi_pitch,kname)
                    if midi_pitch%12 in preferred:
                        from music21 import pitch
                        p=pitch.Pitch(preferred[midi_pitch%12]);p.octave=midi_pitch//12-1
                        p.octave+=round((midi_pitch-p.midi)/12)
                    ps.append(p)
                n=note.Note(ps[0]) if len(ps)==1 else chord.Chord(ps)
                n.duration.quarterLength=hi-lo;n.volume.velocity=round(sum(g['velocity'] for g in group)/len(group))
                if na<a or nz>z:n.tie=tie.Tie('continue' if na<a and nz>z else 'stop' if na<a else 'start')
                v.insert(lo-a,n);pos=hi
            if pos<z:v.insert(pos-a,note.Rest(quarterLength=z-pos))
            m.insert(0,v)
        if not voices:m.insert(0,note.Rest(quarterLength=z-a))
        part.append(m)
    return part

def annotate_xml(path,bundle):
    tree=ET.parse(path);root=tree.getroot();parts=root.findall('part')
    ident=root.find('identification')
    if ident is not None:
        rights=ET.Element('rights');rights.text='Source MIDI: '+bundle['meta'].get('source_licence','see parent item')+'; new annotations: '+bundle['meta'].get('analysis_licence','see parent item')
        position=next((i for i,e in enumerate(ident) if e.tag=='encoding'),len(ident));ident.insert(position,rights)
        ET.SubElement(ident,'source').text=bundle['meta'].get('source_page',bundle['meta']['source_file'])
        misc=ET.SubElement(ident,'miscellaneous')
        ET.SubElement(misc,'miscellaneous-field',name='analysis-json').text=json.dumps(bundle,ensure_ascii=False,separators=(',',':'))
    # m21 consolidates the two PartStaff objects into one part with two staves.
    for pi,part in enumerate(parts):
        div=1
        for b,m in zip(bundle['bars'],part.findall('measure')):
            if b['bar']==0:m.set('implicit','yes')
            div=int(m.findtext('attributes/divisions',str(div)))
            if pi!=0:continue
            # Insert harmony/directions at measure beginning with explicit offsets.
            insertion=next((i for i,e in enumerate(m) if e.tag not in ('attributes','print')),len(m))
            annotations=[]
            bass_staff='2' if len(parts)==1 else None
            for c in b['chords']:
                offset=round((c['beat']-1)*div)
                if c['symbol']!='?':
                    from music21.musicxml.m21ToXml import GeneralObjectExporter
                    hx=ET.fromstring(GeneralObjectExporter(harmony.ChordSymbol(c['symbol'])).parse()).find('.//harmony')
                    if hx is not None:
                        hx.set('placement','above');ET.SubElement(hx,'offset').text=str(offset)
                        if bass_staff:ET.SubElement(hx,'staff').text='1'
                        annotations.append(hx)
                # RN on a bass onset when one exists; otherwise an analysis words direction.
                pos=0;last=0;target=None
                for n in m:
                    if n.tag=='backup':pos-=int(n.findtext('duration','0'))
                    elif n.tag=='forward':pos+=int(n.findtext('duration','0'))
                    elif n.tag=='note' and n.find('grace') is None:
                        on=last if n.find('chord') is not None else pos
                        if n.find('chord') is None:last=pos;pos+=int(n.findtext('duration','0'))
                        if on==offset and n.find('rest') is None and (not bass_staff or n.findtext('staff')=='2'):target=n;break
                if target is not None:
                    lyric=ET.SubElement(target,'lyric',number='rn',name='rn',placement='below')
                    ET.SubElement(lyric,'syllabic').text='single';ET.SubElement(lyric,'text').text=c['rn']
                else:annotations.append(words('[rn] '+c['rn'],offset,bass_staff,'below'))
            for ev in b['events']:
                text='['+PREFIXES[ev['type']]+'] '+ev['text']
                annotations.append(words(text,round((ev.get('beat',1)-1)*div),'1' if bass_staff else None,'above'))
            for el in reversed(annotations):m.insert(insertion,el)
    ids={}
    for el in root.iter():
        if el.get('id'):
            old=el.get('id')
            if old not in ids:ids[old]=('P' if el.tag in ('part','score-part') else 'I')+str(len(ids)+1)
            el.set('id',ids[old])
    ET.indent(tree,space='  ');tree.write(path,encoding='utf-8',xml_declaration=True)

def words(text,offset,staff,placement):
    d=ET.Element('direction',placement=placement);dt=ET.SubElement(d,'direction-type');ET.SubElement(dt,'words').text=text
    ET.SubElement(d,'offset').text=str(offset)
    if staff:ET.SubElement(d,'staff').text=staff
    return d

def build(spec,out_root=None):
    spec=copy.deepcopy(spec);meta=spec['meta'];ns,marks,_=read_midi(ROOT/meta['source_file']);ns=sliced_notes(ns,*meta['quarter_range'])
    bars=bars_for(meta);bybar={x['bar']:x for x in spec.get('bars',[])};kname=meta['key']
    for b in bars:
        b.update(bybar.get(b['bar'],{}));kname=b.get('key',kname);b['key']=kname
        b.setdefault('chords',[]);b.setdefault('events',[])
        for c in b['chords']:
            c.setdefault('function','unresolved' if c['symbol']=='?' else 'see Roman numeral')
            if not 1<=c['beat']<b['duration_quarters']+1:raise ValueError(f"Chord outside bar {b['bar']}")
        for ev in b['events']:
            if ev['type'] not in PREFIXES or not ev.get('technique'):raise ValueError(f'Invalid event {ev}')
    # Duration overrides (e.g. Schumann final 4/4) replace the normal last bars.
    if meta.get('bar_layout'):
        bars=[]
        for layout_bar in meta['bar_layout']:
            b=copy.deepcopy(layout_bar);b.update(bybar.get(b['bar'],{}));kname=b.get('key',meta['key'] if not bars else bars[-1]['key']);b['key']=kname;b.setdefault('events',[]);b.setdefault('chords',[]);bars.append(b)
    bundle={k:v for k,v in spec.items() if k!='bars'};bundle.update(schema_version=1,bars=bars)
    bundle['tags']=sorted({ev['type']+':'+ev['technique'] for b in bars for ev in b['events']})
    bundle['modulations']=[dict(bar=b['bar'],**e) for b in bars for e in b['events'] if e['type']=='modulation']
    vocabulary=json.loads((Path(__file__).parent/'vocabulary.json').read_text())
    for b in bars:
        for ev in b['events']:
            if ev['technique'] not in vocabulary.get(ev['type'],{}):raise ValueError(f'Unknown technique {ev}')
    prior_tempos=[m for m in marks if m['type']=='set_tempo' and m['q']<=meta['quarter_range'][0]]
    if prior_tempos and not meta.get('tempo_override'):
        meta['suggested_arrangement_tempo']=meta['tempo'];meta['tempo']=round(60000000/prior_tempos[-1]['tempo'],3)
    bundle['verification']=verify(bundle)
    dst=Path(out_root or ROOT/'files/analysis')/meta['id'];dst.mkdir(parents=True,exist_ok=True)
    score=stream.Score();score.metadata=metadata.Metadata(title=meta['title'],composer=meta['composer'])
    upper,lower=staff_notes(ns,meta);rh=make_staff(upper,bars,meta,True);lh=make_staff(lower,bars,meta,False)
    # Retain every source tempo change within the excerpt, with an initial mark.
    initial=meta.get('tempo',70);last=initial
    source_start,source_end=meta['quarter_range']
    prior=[m for m in marks if m['type']=='set_tempo' and m['q']<=source_start]
    if prior and not meta.get('tempo_override'):initial=60000000/prior[-1]['tempo']
    rh.measure(bars[0]['bar']).insert(0,tempo.MetronomeMark(number=round(initial,3)))
    for mark in marks:
        if mark['type']!='set_tempo' or not source_start<mark['q']<source_end or meta.get('tempo_override'):continue
        q=mark['q']-source_start;val=60000000/mark['tempo']
        b=next((b for b in bars if b['start_quarter']<=q<b['start_quarter']+b['duration_quarters']),None)
        if b:rh.measure(b['bar']).insert(quantise(q-b['start_quarter']),tempo.MetronomeMark(number=round(val,3)))
    score.insert(0,rh);score.insert(0,lh);score.insert(0,layout.StaffGroup([rh,lh],name='Piano',symbol='brace',barTogether=True))
    # makeNotation splits non-binary lengths into valid tied notation.
    path=dst/(meta['id']+'.annotated.musicxml');score.write('musicxml',fp=path);annotate_xml(path,bundle)
    # Verify score carrier length, guarding pickup-padding/last-bar export quirks.
    sys_path=ROOT/'scripts';import sys;sys.path.insert(0,str(sys_path))
    from watch_truth import parse,read_xml
    parsed=parse(read_xml(path));length=float(sum(m['len'] for m in parsed))
    expected=sum(b['duration_quarters'] for b in bars)
    if abs(length-expected)>1e-5:raise ValueError(f'XML length {length} != bar layout {expected}')
    if len(parsed)!=len(bars):raise ValueError('XML measure count differs from analysis')
    json_write(dst/(meta['id']+'.analysis.json'),bundle)
    write_summary(dst/(meta['id']+'.analysis.md'),bundle)
    v=bundle['verification'];print(f"{meta['id']}: {len(bars)} measures, {v['matched_spans']}/{v['labelled_spans']} ({v['chord_note_match_pct']}%), {v['unknown_spans']} unknown")
    return bundle

def write_summary(path,b):
    m=b['meta'];v=b['verification'];lines=[f"# {m['composer']}: {m['title']}",'',f"{'DRAFT — needs review. ' if b.get('draft') else ''}Source: `{m['source_file']}`, absolute quarters {m['quarter_range']}; {m['time_signature']}, {m['key']}, opening ♩≈{m['tempo']}. MIDI is referenced, not copied.",'',b.get('summary',''),'', '## Story and key journey','']
    for s in b.get('sections',[]):lines.append(f"- Bars {s['start_bar']}–{s['end_bar']}: **{s['name']}**. {s.get('description','')} Mood: {', '.join(s.get('mood',[]))}.")
    lines+=['','## Tricks checked against the notes','']
    for t in b.get('tricks',[]):lines.append('- '+t)
    lines+=['','## Loops, hooks and K-pop uses','']
    for typ in ('loop_candidates','hook_candidates'):
        for c in b.get(typ,[]):lines.append(f"- {typ.split('_')[0].title()} bars {c['start_bar']}–{c['end_bar']}: {c['why']}")
    for use in b.get('kpop_uses',[]):lines.append(f"- **{use['where']}**: {use['why']}")
    lines+=['','## Verification and limits','',f"{v['matched_spans']}/{v['labelled_spans']} asserted chord spans pass ({v['chord_note_match_pct']}%); {v['unknown_spans']} spans are explicitly `?`. All original MIDI tracks are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.",'',m.get('notation_notes','MIDI phrasing/dynamics are not a critical edition; notes quantised to straight/triplet grids. Grace notes <0.10 quarter are omitted.'),'']
    for f in b.get('review_flags',[]):lines.append(f"- Review bar {f['bar']}: {f['reason']}")
    unresolved=sorted({f['bar'] for f in v['flagged_bars'] if 'beat' in f})
    if unresolved:lines.append('- Unresolved chord spans in bars '+', '.join(map(str,unresolved))+'. Exact beats and note-support reasons are in the bundle JSON verification.')
    path.write_text('\n'.join(lines)+'\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--spec',required=True);ap.add_argument('--midi');ap.add_argument('--start',type=float);ap.add_argument('--end',type=float);ap.add_argument('--out-root')
    a=ap.parse_args();s=json.loads(Path(a.spec).read_text())
    if a.midi:s['meta']['source_file']=a.midi
    if a.start is not None:s['meta']['quarter_range'][0]=a.start
    if a.end is not None:s['meta']['quarter_range'][1]=a.end
    build(s,a.out_root)
if __name__=='__main__':main()
