import mido, sys, os
for p in sys.argv[1:]:
    m=mido.MidiFile(p); ks=[];ts=[];tp=[]
    for t in m.tracks:
        for x in t:
            if x.type=='key_signature' and x.key not in ks: ks.append(x.key)
            if x.type=='time_signature':
                s=f"{x.numerator}/{x.denominator}"
                if s not in ts: ts.append(s)
            if x.type=='set_tempo' and len(tp)<2: tp.append(round(mido.tempo2bpm(x.tempo)))
    print(p.replace('/tmp/bachwork/midx/',''), round(m.length), ks[:3], ts[:3], tp)
