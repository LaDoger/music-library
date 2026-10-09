#!/usr/bin/env python3
"""Pre-render full-length FluidSynth MP3s (FluidR3_GM) for editor's picks with a playable MIDI.

Output: release_staging/synth/<id>_synth.mp3 (not committed). Upload with
  gh release upload synth-v1 release_staging/synth/*_synth.mp3 --clobber
then this script (--record) writes data/cache/synth_renders.json, which
sync_site_data.py turns into stream_synth_url. Long pieces are capped at CAP_S
seconds with a 3 s fade-out. A render carries the score's licence (score_status).

Usage: python3 scripts/render_synth.py [--ids a,b] [--all-scored] [--record]
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "data", "library.json")
OUT = os.path.join(ROOT, "release_staging", "synth")
CACHE = os.path.join(ROOT, "data", "cache", "synth_renders.json")
RELEASE = "https://github.com/LaDoger/music-library/releases/download/synth-v1/"
CAP_S = 300


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 2)


def main():
    rows = json.load(open(LIB, encoding="utf-8"))
    ids = sys.argv[sys.argv.index("--ids") + 1].split(",") if "--ids" in sys.argv else None
    want = [r for r in rows if r.get("midi_play_url") and (
        (ids and r["id"] in ids) or (not ids and ("--all-scored" in sys.argv or r.get("editors_pick_rank"))))]
    os.makedirs(OUT, exist_ok=True)
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    for r in want:
        dst = os.path.join(OUT, r["id"] + "_synth.mp3")
        if "--record" not in sys.argv and not os.path.exists(dst):
            import mido
            length = mido.MidiFile(os.path.join(ROOT, r["midi_play_url"])).length
            cmd = [sys.executable, "-m", "musiclib", "render", "--midi", os.path.join(ROOT, r["midi_play_url"]), "--out", dst]
            if length > CAP_S + 5:
                cmd += ["--duration", str(CAP_S), "--fade-out", "3"]
            env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
            subprocess.run(cmd, check=True, env=env)
            print(f"rendered {r['id']} ({min(length, CAP_S):.0f}s of {length:.0f}s)")
        if "--record" in sys.argv and os.path.exists(dst):
            cache[r["id"]] = {"url": RELEASE + os.path.basename(dst), "duration": duration(dst),
                              "bytes": os.path.getsize(dst), "midi": r["midi_play_url"],
                              "capped": duration(dst) < mido_len(r) - 5, "soundfont": "FluidR3_GM"}
    if "--record" in sys.argv:
        with open(CACHE + ".tmp", "w", encoding="utf-8") as f:
            json.dump(dict(sorted(cache.items())), f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(CACHE + ".tmp", CACHE)
        print(f"{len(cache)} synth renders recorded in {os.path.relpath(CACHE, ROOT)}")


def mido_len(r):
    import mido
    return mido.MidiFile(os.path.join(ROOT, r["midi_play_url"])).length


if __name__ == "__main__":
    main()
