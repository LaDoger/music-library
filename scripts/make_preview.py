#!/usr/bin/env python3
"""Make a ~15s audition MP3 (192k, stereo, 44.1k) at ~-16 LUFS with short fades.

Usage:
  make_preview.py --audio in.flac [--start SEC|MM:SS] --out previews/foo.mp3

Only cut previews from real recordings. --midi (FluidSynth previews) is refused:
synth-rendered audio was removed on 2026-10-09 (docs/REMOVED_SYNTH_AUDIO.md);
score-only rows play via the in-browser MIDI player.

Two-pass loudnorm (measure, then linear gain) on the faded excerpt, followed by
a check of the encoded MP3; if it lands more than 0.5 LU off target a small
gain correction pass is applied. Start is clamped so the excerpt fits.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
DUR = 15.0
FADE_IN = 0.35
FADE_OUT = 0.45
TARGET_I = -16.0
TARGET_TP = -1.5
TARGET_LRA = 11.0


def run(cmd, capture=False):
    print("+", " ".join(cmd), flush=True)
    if capture:
        return subprocess.run(cmd, check=True, capture_output=True, text=True).stderr
    subprocess.check_call(cmd)
    return ""


def parse_time(value: str) -> float:
    value = value.strip()
    if ":" in value:
        secs = 0.0
        for part in value.split(":"):
            secs = secs * 60 + float(part)
        return secs
    return float(value)


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def midi_to_wav(midi: Path, wav: Path):
    run(["fluidsynth", "-ni", "-q", "-g", "0.8", "-F", str(wav), "-r", "44100", SF2, str(midi)])


def excerpt(src: Path, wav: Path, start: float):
    af = (
        f"atrim=start={start}:duration={DUR},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d={FADE_IN},afade=t=out:st={DUR - FADE_OUT}:d={FADE_OUT}"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vn",
         "-af", af, "-ar", "44100", "-ac", "2", "-c:a", "pcm_s24le", str(wav)])


def measure_loudnorm(path: Path) -> dict:
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
               f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json",
               "-f", "null", "-"], capture=True)
    return json.loads(err[err.rindex("{"): err.rindex("}") + 1])


def integrated(path: Path) -> float:
    err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128",
               "-f", "null", "-"], capture=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def encode(wav: Path, out_mp3: Path, af: str):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav), "-af", af,
         "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k", str(out_mp3)])


def make_preview(src: Path, out_mp3: Path, start: float, midi: bool = False) -> float:
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        if midi:
            full = td / "full.wav"
            midi_to_wav(src, full)
            src = full
        total = duration(src)
        start = max(0.0, min(start, total - DUR)) if total > DUR else 0.0
        cut = td / "cut.wav"
        excerpt(src, cut, start)
        m = measure_loudnorm(cut)
        af = (
            f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}"
            f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
            f":offset={m['target_offset']}:linear=true"
        )
        encode(cut, out_mp3, af + ",aresample=44100")
        got = integrated(out_mp3)
        if abs(got - TARGET_I) > 0.5:
            # loudnorm fell back to dynamic mode or the peak limit bit; nudge gain
            fix = td / "fix.mp3"
            encode(cut, fix, af + f",volume={TARGET_I - got:.2f}dB,"
                   f"alimiter=limit={10 ** (TARGET_TP / 20):.4f}:level=disabled,aresample=44100")
            fix.replace(out_mp3)
            got = integrated(out_mp3)
    print(f"wrote {out_mp3} start={start:.2f}s I={got:.1f} LUFS")
    return got


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--audio", type=Path)
    g.add_argument("--midi", type=Path)
    ap.add_argument("--start", type=str, default="0")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.midi:
        raise SystemExit("--midi is disabled: no synth-rendered previews (docs/REMOVED_SYNTH_AUDIO.md)")
    make_preview(args.midi or args.audio, args.out, parse_time(args.start), midi=bool(args.midi))


if __name__ == "__main__":
    main()
