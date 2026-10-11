"""Small, deterministic MIDI reader shared by drafting, building and verification.
No audio renders or music21 MIDI disk cache. Offsets and beats are quarter notes.
"""
from pathlib import Path
from collections import defaultdict
import json
import mido
from music21 import key, pitch, stream, note, chord, meter, instrument, clef, tempo

ROOT = Path(__file__).resolve().parents[2]
PREFIXES = {'modulation':'mod','counterpoint':'cpt','voicing_orchestration':'voi',
 'tension_release':'ten','rhythm_phrase':'rhy','motif':'mot','texture_dynamics':'tex',
 'bass_line':'bass','colour_chord':'col','cadence':'cad','form':'form','story':'story',
 'hook':'hook','mood':'mood','pedal':'ped','texture':'tex'}

def read_midi(path):
    midi = mido.MidiFile(path)
    notes, marks, tracks = [], [], []
    for ti, track in enumerate(midi.tracks):
        tick = 0; active = defaultdict(list); program = 0; name = ''
        for msg in track:
            tick += msg.time; q = tick / midi.ticks_per_beat
            if msg.type == 'track_name': name = msg.name.rstrip('\x00')
            if msg.type == 'program_change': program = msg.program
            if msg.type in ('set_tempo','time_signature','key_signature'):
                marks.append({'q':q,'type':msg.type, **msg.dict()})
            if msg.type == 'note_on' and msg.velocity:
                active[(msg.channel,msg.note)].append((q,msg.velocity,program))
            elif msg.type in ('note_on','note_off'):
                k = (msg.channel,msg.note)
                if active[k]:
                    start, vel, prog = active[k].pop(0)
                    if q > start and msg.channel != 9:
                        notes.append({'start':start,'end':q,'pitch':msg.note,'track':ti,'velocity':vel,'program':prog})
        tracks.append(name)
    return notes, sorted(marks,key=lambda m:m['q']), tracks

def sliced_notes(notes,start,end):
    return [dict(n,start=max(n['start'],start)-start,end=min(n['end'],end)-start)
            for n in notes if n['start'] < end-1e-8 and n['end'] > start+1e-8]

def weights(notes,start,end):
    out=defaultdict(float)
    for n in notes:
        overlap=min(end,n['end'])-max(start,n['start'])
        if overlap>1e-8: out[n['pitch']%12]+=overlap
    return dict(out)

def bars_for(meta):
    if meta.get('bar_layout'): return [dict(b) for b in meta['bar_layout']]
    start,end = meta['quarter_range']; length=meta['bar_quarters']; pickup=meta.get('pickup_quarters',0)
    bars=[]; q=0
    if pickup:
        bars.append({'bar':0,'start_quarter':0,'duration_quarters':pickup});q=pickup
    number=1
    while q < end-start-1e-6:
        duration=min(length,end-start-q)
        bars.append({'bar':number,'start_quarter':round(q,8),'duration_quarters':round(duration,8)})
        q+=duration;number+=1
    return bars

def spelling(midi,key_name):
    """Prefer diatonic spelling, retaining minor leading tone (Fx in G# minor)."""
    k=key.Key(key_name); p=pitch.Pitch(midi=midi)
    candidates=[p,p.getEnharmonic()]
    if p.accidental and p.accidental.alter != 0:
        try: candidates.extend(p.getAllCommonEnharmonics(alterLimit=2))
        except Exception: pass
    scale={x.pitchClass:x.name for x in k.pitches}
    if k.mode=='minor':
        leading=k.pitchFromDegree(7)
        leading.accidental=pitch.Accidental((leading.accidental.alter if leading.accidental else 0)+1)
        scale[leading.pitchClass]=leading.name
    preferred=scale.get(midi%12)
    if preferred:
        r=pitch.Pitch(preferred);r.octave=(midi-r.pitchClass)//12-1
        # B# / Cb belong to the adjacent written octave.
        r.octave += round((midi-r.midi)/12)
        return r
    accidental_sign=1 if k.sharps>=0 else -1
    return min(candidates,key=lambda x: abs(x.accidental.alter if x.accidental else 0)+
               (0.4 if x.accidental and x.accidental.alter*accidental_sign<0 else 0))

def json_write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
