"""Copy Mutopia Bach files into the repo, render 15 s previews, write parts/BATCH1_claude_rows.csv.

Run: venv python, with PYTHONPATH=<repo>/src (for musiclib.audio). Downloaded data is read only.
"""
import csv, json, os, shutil, subprocess, sys, tempfile, wave, concurrent.futures as cf
from pathlib import Path

sys.path.insert(0, "/tmp/bachwork/scripts")
from meta import ROWS
REPO = Path("/workspace/music/library")
sys.path.insert(0, str(REPO / "src"))
from musiclib import audio

W = Path("/tmp/bachwork")
RDF = {r["path"].strip("/").replace("/", "__"): r for r in json.load(open(W / "rdfs.json"))}
PAGE = {p.strip("/").replace("/", "__"): (pid, lic) for p, pid, lic in json.load(open(W / "pageverify.json"))}
HEADER = open(REPO / "library.csv", encoding="utf-8").readline().strip().split(",")
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
ONLY = set(sys.argv[1:])


def mmss(t):
    return f"{int(t // 60):02d}:{t % 60:06.3f}"


def lead_silence(wav):
    with wave.open(str(wav)) as w:
        n, ch, sw, rate = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        data = w.readframes(n)
    import array
    a = array.array("h", data)
    thr = 300
    for i in range(0, len(a), ch * 64):
        if abs(a[i]) > thr or (ch > 1 and abs(a[i + 1]) > thr):
            return (i // ch) / rate, n / rate
    return 0.0, n / rate


def files_for(key, midi, rid, movement):
    d = W / "dl" / key
    out = []
    dst = REPO / "files/scores"
    shutil.copyfile(W / "midx" / key / midi, dst / f"{rid}.mid"); out.append(f"{rid}.mid")
    lys = [f for f in os.listdir(d) if f.endswith("-lys.zip")]
    lyf = [f for f in os.listdir(d) if f.endswith(".ly")]
    if lys:
        shutil.copyfile(d / lys[0], dst / f"{rid}_lilypond.zip"); out.append(f"{rid}_lilypond.zip")
    elif lyf:
        shutil.copyfile(d / lyf[0], dst / f"{rid}.ly"); out.append(f"{rid}.ly")
    mids = [f for f in os.listdir(d) if f.endswith("-mids.zip")]
    if "render_midi" in movement and mids:
        shutil.copyfile(d / mids[0], dst / f"{rid}_all_movements_midi.zip"); out.append(f"{rid}_all_movements_midi.zip")
    if midi == "rectus.mid":
        shutil.copyfile(W / "midx" / key / "inversus.mid", dst / f"{rid}_inversus.mid"); out.append(f"{rid}_inversus.mid")
    return out


def legal(key, rid, note):
    r = RDF[key]
    pid, lic = PAGE[key]
    src = (r.get("source") or "").replace("&amp;", "&").strip() or "not stated"
    who = r.get("maintainer") or "the typesetter"
    comp = "Composition PD worldwide (J. S. Bach d.1750)."
    extra = ""
    if note == "PETZOLD":
        comp = ("Composition PD worldwide. Long attributed to J. S. Bach (BWV Anh. numbering) and copied into the "
                "1725 Anna Magdalena Bach Notebook; now credited to Christian Petzold (d.1733).")
    elif note:
        extra = note + " "
    if lic == "Public Domain":
        lictxt = (f"Mutopia piece {pid} ('{r['title']}', for {r.get('for','')}); licence shown as Public Domain on the "
                  f"piece page, in the Mutopia RDF and in the .ly header (placed in the public domain by typesetter {who}). "
                  f"Edition source: {src}.")
        elic = "PD"
    else:
        lictxt = (f"Mutopia piece {pid} ('{r['title']}'); score licensed {lic} (piece page, RDF and .ly header), "
                  f"typeset by {who}. Credit when you use the score or your own render of it: "
                  f"'Score: {who} / Mutopia Project (www.mutopiaproject.org, piece {pid}), CC BY 3.0, "
                  f"https://creativecommons.org/licenses/by/3.0/' and say what you changed. Edition source: {src}.")
        elic = "CC-BY 3.0"
    tail = ("Preview is an own FluidSynth (FluidR3_GM) render of the Mutopia MIDI, not a human performance; "
            "no recording in this row.")
    return f"{comp} {lictxt} {extra}{tail}".replace("  ", " "), elic, pid


def one(row):
    key, midi, rid, title, cat, mov, moods, tempo, use, start, note = row
    files = files_for(key, midi, rid, mov)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "r.wav"
        audio.midi_to_wav(W / "midx" / key / midi, wav, SF2, 0.8)
        lead, total = lead_silence(wav)
        s = round(lead + start, 3)
        dur = min(15.0, max(5.0, total - s - 0.2))
        audio.finish(wav, REPO / "previews" / f"{rid}.mp3", start=s, duration=dur,
                     fade_in=0.3, fade_out=0.5, lufs=-16.0, bitrate="192k")
    notes, elic, pid = legal(key, rid, note)
    composer, death = ("Christian Petzold", "1733") if note == "PETZOLD" else ("Johann Sebastian Bach", "1750")
    exc = f"MIDI render {mmss(s)}–{mmss(s + dur)} ({'opening' if start == 0 else 'excerpt'})"
    fmt = "MIDI; LilyPond" + (" (zip)" if any(f.endswith("_lilypond.zip") for f in files) else "")
    rec = dict.fromkeys(HEADER, "")
    rec.update(id=rid, composer=composer, death_year=death, title=title, catalog=cat, movement=mov,
               mood_tags=moods, tempo_energy=tempo, notable_excerpt=exc, video_use_ideas=use,
               editable_source_url=f"https://www.mutopiaproject.org/cgibin/piece-info.cgi?id={pid}",
               editable_format=fmt, editable_license=elic, legal_notes=notes,
               local_score_path=f"files/scores/{rid}.mid", preview_path=f"previews/{rid}.mp3",
               verified="yes", added_by="claude")
    return rec, round(total, 1)


rows = [r for r in ROWS if not ONLY or r[2] in ONLY]
with cf.ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, rows))
out = REPO / "parts" / "BATCH1_claude_rows.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=HEADER)
    w.writeheader()
    for rec, _ in res:
        w.writerow(rec)
json.dump({rec["id"]: total for rec, total in res}, open(W / "durations.json", "w"), indent=0)
print(len(res), "rows ->", out)
