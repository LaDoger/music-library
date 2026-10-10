#!/usr/bin/env python3
"""Ground truth for the watch-player sync test (independent of assets/watch.js).

Unrolls a MusicXML/MXL score (repeats, voltas, D.C./D.S./Fine/Coda) into a playback list of
measures, then checks it against the piece's MIDI: every unrolled measure must match the MIDI
note onsets (pitch multiset) in the same window of MIDI quarter notes. Prints JSON:
  {"id", "measures": [{"m": idx, "u0": unrolled start q, "len": q}], "onsets": [[u q, midi pitch]],
   "score_start": [q per measure], "midi_tempos": [[sec, qpm]], "match": fraction of measures whose
   MIDI onsets agree (>= 60 % of the pitches)}  (all positions in quarter notes)
Usage: python3 scripts/watch_truth.py <id> [<id> ...]   (MIDI cross-check needs mido)
"""
import json, re, sys, zipfile
import xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_xml(path):
    if path.suffix.lower() == ".mxl":
        z = zipfile.ZipFile(path)
        cont = ET.fromstring(z.read("META-INF/container.xml"))
        name = cont.find(".//rootfile").get("full-path")
        return ET.fromstring(z.read(name))
    return ET.parse(path).getroot()


STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def parse(root):
    """Per measure: length (quarters), notes [(offset q, midi pitch, tied_stop)], barline/jump info."""
    parts = root.findall("part")
    n = len(parts[0].findall("measure"))
    meas = [{"len": F(0), "notes": [], "fwd": False, "bwd": 0, "ending": None, "ending_stop": False,
             "segno": False, "coda": False, "dc": False, "ds": False, "fine": False, "tocoda": False, "implicit": False}
            for _ in range(n)]
    for part in parts:
        div = 1; ts = F(4)
        for i, m in enumerate(part.findall("measure")):
            if i >= n:
                break
            M = meas[i]
            M.setdefault("num", m.get("number", ""))
            if m.get("implicit") == "yes":
                M["implicit"] = True
            pos = F(0); mx = F(0); last = F(0)
            for el in m:
                t = el.tag
                if t == "attributes":
                    d = el.find("divisions")
                    if d is not None:
                        div = int(float(d.text))
                    tm = el.find("time")
                    if tm is not None and tm.findtext("beats"):
                        ts = sum(F(int(b)) for b in tm.findtext("beats").split("+")) * 4 / int(tm.findtext("beat-type"))
                elif t == "note":
                    if el.find("grace") is not None:
                        continue
                    dur = F(int(float(el.findtext("duration", "0"))), div)
                    if el.find("chord") is not None:
                        start = last
                    else:
                        start = pos; last = pos; pos += dur
                    if el.find("rest") is None and el.find("pitch") is not None:
                        p = el.find("pitch")
                        midi = 12 * (int(p.findtext("octave")) + 1) + STEP[p.findtext("step")] + int(float(p.findtext("alter", "0")))
                        tied = any(x.get("type") == "stop" for x in el.findall("tie"))
                        M["notes"].append((start, midi, tied))
                    mx = max(mx, pos)
                elif t == "backup":
                    pos -= F(int(el.findtext("duration")), div)
                elif t == "forward":
                    pos += F(int(el.findtext("duration")), div); mx = max(mx, pos)
                elif t == "barline":
                    r = el.find("repeat")
                    if r is not None:
                        if r.get("direction") == "forward":
                            M["fwd"] = True
                        else:
                            M["bwd"] = max(M["bwd"], int(r.get("times", "0")) or 1)   # 1 = times not given
                    e = el.find("ending")
                    if e is not None:
                        if e.get("type") == "start":
                            M["ending"] = [int(x) for x in re.findall(r"\d+", e.get("number", "1"))] or [1]
                        else:
                            M["ending_stop"] = True
                for s in ([el] if t == "sound" else el.findall("sound") if t == "direction" else []):
                    if s.get("segno"): M["segno"] = True
                    if s.get("coda"): M["coda"] = True
                    if s.get("dacapo") == "yes": M["dc"] = True
                    if s.get("dalsegno"): M["ds"] = True
                    if s.get("fine"): M["fine"] = True
                    if s.get("tocoda"): M["tocoda"] = True
            # notated durations can be rounded (tuplets): snap to the time signature when within 3 %
            M["len"] = max(M["len"], ts if abs(mx - ts) <= ts * F(3, 100) else mx)
            M["ts"] = ts
    # ending spans: carry the start numbers until the stop
    cur = None   # an ending without a stop closes at a backward repeat or before a forward repeat
    for M in meas:
        if M["fwd"] and not M["ending"]:
            cur = None
        if M["ending"]:
            cur = M["ending"]
        M["endnums"] = cur
        if M["ending_stop"] or M["bwd"]:
            cur = None
    # repeat without times= inside a volta group: as many passes as the highest ending number
    for i, M in enumerate(meas):
        if M["bwd"] == 1:
            lo = hi = i
            while M["endnums"] and lo > 0 and meas[lo - 1]["endnums"]: lo -= 1
            while M["endnums"] and hi + 1 < len(meas) and meas[hi + 1]["endnums"]: hi += 1
            M["bwd"] = max([2] + ([x for k in range(lo, hi + 1) for x in meas[k]["endnums"]] if M["endnums"] else []))
    return meas


def sections(meas):
    """Movement starts: measure numbering restarts at 1 (or 0 for a pickup)."""
    st = [0]
    for i in range(1, len(meas)):
        if meas[i]["num"] == "0" or (meas[i]["num"] == "1" and meas[i - 1]["num"] != "0"):
            st.append(i)
    return st


def unroll(meas):
    """MuseScore-style, per movement: repeats are not replayed after a D.C./D.S., the last volta is
    taken after a jump, Fine / To Coda act after a jump; D.C./segno/coda stay inside the movement."""
    out = []; n = len(meas)
    st = sections(meas) + [n]
    for s0, s1 in zip(st, st[1:]):
        i = s0; start = s0; passno = 1; jumped = False; guard = 0
        while i < s1 and guard < 20 * n:
            guard += 1
            M = meas[i]
            if M["fwd"] and start != i:
                start = i; passno = 1
            nums = M["endnums"]
            if nums and not ((passno in nums) if not jumped else nums == last_ending(meas, i)):
                i += 1; continue
            out.append(i)
            if jumped and M["fine"]:
                break
            if jumped and M["tocoda"]:
                c = next((k for k in range(i + 1, s1) if meas[k]["coda"]), None)
                if c is not None:
                    i = c; continue
            if M["bwd"] and not jumped and passno < M["bwd"]:
                passno += 1; i = start; continue
            if M["bwd"]:
                passno = 1; start = i + 1
            if (M["dc"] or M["ds"]) and not jumped:
                jumped = True; passno = 1
                i = s0 if M["dc"] else next((k for k in range(s0, s1) if meas[k]["segno"]), s0)
                continue
            i += 1
    return out


def last_ending(meas, i):
    # the ending group containing measure i: the numbers of the last ending in its group
    k = i
    while k + 1 < len(meas) and meas[k + 1]["endnums"]:
        k += 1
    return meas[k]["endnums"]


def midi_notes(path):
    import mido
    mf = mido.MidiFile(path)
    tpq = mf.ticks_per_beat
    notes = []; tempos = []
    for tr in mf.tracks:
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type == "set_tempo":
                tempos.append((t, msg.tempo))
            elif msg.type == "note_on" and msg.velocity > 0 and getattr(msg, "channel", 0) != 9:
                notes.append((F(t, tpq), msg.note))
    tempos.sort()
    # seconds for each tempo change (tick based)
    tl = []; sec = 0.0; lt = 0; us = 500000
    for tk, u in tempos:
        sec += (tk - lt) / tpq * us / 1e6; lt = tk; us = u
        tl.append([round(sec, 6), 60e6 / u])
    if not tl or tl[0][0] > 0:
        tl.insert(0, [0.0, 120.0])
    return sorted(notes), tl, tpq


def main(ids):
    res = []
    for id_ in ids:
        item = json.loads((ROOT / "data/items" / (id_ + ".json")).read_text())
        xml = next(f for f in item["score_files"] if re.search(r"\.(mxl|musicxml|xml)$", f, re.I))
        meas = parse(read_xml(ROOT / xml))
        order = unroll(meas)
        score_start = []; q = F(0)
        for M in meas:
            score_start.append(q); q += M["len"]
        rows = []; onsets = []; u = F(0)
        for m in order:
            rows.append({"m": m, "u0": float(u), "len": float(meas[m]["len"])})
            onsets += [[float(u + o), p] for (o, p, tied) in meas[m]["notes"] if not tied]
            u += meas[m]["len"]
        onsets.sort()
        out = {"id": id_, "measures": rows, "onsets": onsets, "score_start": [float(x) for x in score_start],
               "unrolled_q": float(u), "n_unrolled": len(rows), "n_measures": len(meas)}
        res.append(out)
        try:
            notes, tempos, tpq = midi_notes(ROOT / item["midi_play_url"])
        except ImportError:   # mido missing: unrolled score only, no MIDI cross-check
            continue
        # MIDI onsets may start after a leading offset (pickup / count-in): align on the first onset
        first_score = next((float(r["u0"]) + float(min(n[0] for n in meas[r["m"]]["notes"])) for r in rows if meas[r["m"]]["notes"]), 0.0)
        shift = float(notes[0][0]) - first_score if notes else 0.0
        ok = 0; tot = 0
        for r in rows:
            exp = sorted(p for (o, p, tied) in meas[r["m"]]["notes"] if not tied)
            if not exp:
                continue
            lo, hi = r["u0"] + shift - 1e-3, r["u0"] + r["len"] + shift - 1e-3
            got = sorted(p for (t, p) in notes if lo <= float(t) < hi)
            tot += 1
            common = sum(min(exp.count(p), got.count(p)) for p in set(exp))
            if common >= 0.6 * max(len(exp), len(got)):
                ok += 1
        out.update({"midi_q": float(notes[-1][0]) if notes else 0, "shift_q": shift,
                    "midi_tempos": tempos, "tpq": tpq, "match": ok / max(tot, 1)})
    print(json.dumps(res))


if __name__ == "__main__":
    main(sys.argv[1:])
