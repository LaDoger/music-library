#!/usr/bin/env python3
"""check_notes.py MIDI MXL -> exit 0 if pitch multiset of MXL (tie-merged) matches MIDI within 1% and bars are full."""
import sys,collections,mido
from music21 import converter,stream
mf=mido.MidiFile(sys.argv[1]);a=collections.Counter(m.note for t in mf.tracks for m in t if m.type=='note_on' and m.velocity)
s=converter.parse(sys.argv[2]);b=collections.Counter(p.midi for n in s.recurse().notes if not(n.tie and n.tie.type in('stop','continue')) for p in n.pitches)
diff=sum(((a-b)+(b-a)).values());bad=sum(1 for p in s.parts for m in list(p.getElementsByClass(stream.Measure))[1:-1] if abs(m.duration.quarterLength-m.barDuration.quarterLength)>1e-6)
print(f'midi={sum(a.values())} score={sum(b.values())} pitch_diff={diff} bad_bars={bad}');sys.exit(0 if diff<=max(2,0.01*sum(a.values())) and bad==0 else 1)
