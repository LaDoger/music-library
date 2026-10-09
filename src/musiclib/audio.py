"""MIDI rendering (FluidSynth) and trimming / loudness (ffmpeg)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

DEFAULT_SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


class ToolMissing(RuntimeError):
    pass


def need(tool: str, hint: str):
    if not shutil.which(tool):
        raise ToolMissing(f"{tool} not found on PATH. {hint}")


def soundfont(path: str | None) -> str:
    sf2 = path or os.environ.get("MUSICLIB_SF2") or DEFAULT_SF2
    if not Path(sf2).is_file():
        raise ToolMissing(f"soundfont {sf2} not found. Install fluid-soundfont-gm "
                          "(apt install fluidsynth fluid-soundfont-gm) or pass --sf2 / set MUSICLIB_SF2.")
    return sf2


def extract_member(zip_path: Path, member: str, dest_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        if member not in names:
            mids = [n for n in names if n.lower().endswith((".mid", ".midi"))]
            raise KeyError(f"{member!r} not in {zip_path.name}. MIDI members: {', '.join(mids)}")
        out = dest_dir / Path(member).name
        out.write_bytes(z.read(member))
        return out


def midi_to_wav(midi: Path, wav: Path, sf2: str, gain: float = 0.8, rate: int = 44100):
    need("fluidsynth", "Install it: apt install fluidsynth (macOS: brew install fluid-synth).")
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", str(gain), "-r", str(rate), "-F", str(wav), sf2, str(midi)],
                   check=True, stdout=subprocess.DEVNULL)


def _loudnorm_filter(src: Path, pre: str, lufs: float) -> str:
    """Two-pass loudnorm: measure, then linear gain to the target."""
    base = f"loudnorm=I={lufs}:TP=-1.5:LRA=11"
    af = f"{pre},{base}:print_format=json" if pre else f"{base}:print_format=json"
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", af, "-f", "null", "-"],
                         check=True, capture_output=True, text=True).stderr
    m = json.loads(err[err.rindex("{"): err.rindex("}") + 1])
    return (f"{base}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


def finish(src: Path, out: Path, start: float = 0.0, duration: float | None = None,
           fade_in: float = 0.0, fade_out: float = 0.0, lufs: float | None = -16.0, bitrate: str = "320k"):
    """Trim, fade, normalise and encode src -> out (format from out's suffix: .wav/.mp3/.flac/.m4a/.ogg)."""
    need("ffmpeg", "Install it: apt install ffmpeg (macOS: brew install ffmpeg).")
    out.parent.mkdir(parents=True, exist_ok=True)
    filters = []
    if start or duration:
        trim = f"atrim=start={start}" + (f":duration={duration}" if duration else "")
        filters += [trim, "asetpts=PTS-STARTPTS"]
    if fade_in:
        filters.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out:
        if duration:
            filters.append(f"afade=t=out:st={max(0.0, duration - fade_out)}:d={fade_out}")
        else:
            # fade the tail: reverse trick avoids needing the length up front
            filters += ["areverse", f"afade=t=in:st=0:d={fade_out}", "areverse"]
    pre = ",".join(filters)
    chain = pre
    if lufs is not None:
        norm = _loudnorm_filter(src, pre, lufs)
        chain = f"{pre},{norm}" if pre else norm
        chain += ",aresample=44100"
    codec = {".wav": ["-c:a", "pcm_s16le"], ".flac": ["-c:a", "flac"], ".mp3": ["-c:a", "libmp3lame", "-b:a", bitrate],
             ".m4a": ["-c:a", "aac", "-b:a", "256k"], ".ogg": ["-c:a", "libvorbis", "-q:a", "6"]}.get(out.suffix.lower())
    if codec is None:
        raise ValueError(f"unsupported output type {out.suffix!r}; use .wav .mp3 .flac .m4a or .ogg")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vn"]
    if chain:
        cmd += ["-af", chain]
    subprocess.run(cmd + ["-ar", "44100", "-ac", "2", *codec, str(out)], check=True)
    return out


def render(midi: Path, out: Path, *, sf2: str | None = None, gain: float = 0.8, **finish_kw) -> Path:
    sf = soundfont(sf2)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "render.wav"
        midi_to_wav(midi, wav, sf, gain)
        return finish(wav, out, **finish_kw)
