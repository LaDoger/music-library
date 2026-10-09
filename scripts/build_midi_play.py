#!/usr/bin/env python3
"""Prepare a browser-fetchable MIDI for every scored row that lacks a plain .mid.

Writes files/midi_play/<id>.mid (committed, served by Pages) for:
  - rows whose MIDI only lives inside a shared zip (member from build_catalog.MIDI_MEMBERS)
  - rows with MusicXML only (.mxl / .musicxml / .xml), converted with MuseScore 3
    (mscore3 -o out.mid in.mxl, headless via QT_QPA_PLATFORM=offscreen)

Rows that already have files/scores/*.mid are left alone (the site plays that file).
The derived MIDI carries the score's licence (score_status). Idempotent; never touches
files/scores/. Run before scripts/sync_site_data.py.

Usage: python3 scripts/build_midi_play.py [--check]
"""
import csv
import os
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalog  # noqa: E402
import sync_site_data  # noqa: E402

ROOT = sync_site_data.ROOT
OUT_DIR = sync_site_data.MIDI_PLAY_DIR
XML_EXT = (".mxl", ".musicxml", ".xml")


def mscore():
    return shutil.which("mscore3") or shutil.which("musescore3") or shutil.which("mscore") or shutil.which("musescore")


def main():
    check = "--check" in sys.argv
    os.makedirs(OUT_DIR, exist_ok=True)
    made, problems = 0, []
    for r in csv.DictReader(open(sync_site_data.CSV_PATH, encoding="utf-8", newline="")):
        rid = r["id"].strip()
        if not r.get("local_score_path") or not os.path.exists(os.path.join(ROOT, r["local_score_path"])):
            continue
        files = sync_site_data.score_files_for({**r, "id": rid})
        if any(f.lower().endswith((".mid", ".midi")) for f in files):
            continue
        out = os.path.join(OUT_DIR, rid + ".mid")
        if os.path.exists(out):
            continue
        zips = [f for f in files if f.lower().endswith(".zip") and "mid" in os.path.basename(f).lower()]
        xmls = [f for f in files if f.lower().endswith(XML_EXT)]
        if check:
            print("would build", rid, zips[:1] or xmls[:1] or "(no source)")
            continue
        if zips and build_catalog.MIDI_MEMBERS.get(rid):
            member = build_catalog.MIDI_MEMBERS[rid]
            with zipfile.ZipFile(os.path.join(ROOT, zips[0])) as z, open(out + ".tmp", "wb") as f:
                f.write(z.read(member))
            os.replace(out + ".tmp", out)
            print(f"zip  {rid}: {zips[0]}!{member}")
            made += 1
        elif xmls and mscore():
            env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
            res = subprocess.run([mscore(), "-o", out, os.path.join(ROOT, xmls[0])], env=env,
                                 capture_output=True, text=True, timeout=300)
            if res.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0:
                print(f"xml  {rid}: {xmls[0]}")
                made += 1
            else:
                problems.append(f"{rid}: MuseScore conversion failed ({res.stderr.strip()[-200:]})")
        else:
            problems.append(f"{rid}: no MIDI, zip member or MusicXML to play in the browser")
    print(f"built {made} file(s) in {os.path.relpath(OUT_DIR, ROOT)}")
    for p in problems:
        print("WARN", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
