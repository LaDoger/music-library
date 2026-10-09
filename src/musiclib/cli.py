"""musiclib command line. Run `musiclib -h` or `python -m musiclib -h`."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from musiclib import audio
from musiclib.data import Library

LICENCES = ["clean", "attribution", "sharealike", "flagged", "unverified"]
GENRES = ["classical", "jazz", "ragtime", "blues", "folk", "world", "marches",
          "early_popular", "film_silent", "modern_cc", "other"]


def seconds(value: str) -> float:
    """'95', '1:35' or '0:01:35' -> seconds."""
    secs = 0.0
    for part in value.strip().split(":"):
        secs = secs * 60 + float(part)
    return secs


def warn(msg: str):
    print(msg, file=sys.stderr)


def licence_warning(status: str, what: str, notes: str = ""):
    if status and status != "clean":
        warn(f"LICENCE: {what} is '{status}', not clean. Read the credit / legal notes before publishing.")
        if notes:
            warn(f"  legal_notes: {notes}")


# ---- commands -------------------------------------------------------------

def cmd_search(lib: Library, a) -> int:
    licence = set(a.licence or [])
    if a.clean:
        licence.add("clean")
    rows = lib.search(" ".join(a.query), genre=a.genre, composer=a.composer, mood=a.mood, energy=a.energy,
                      licence=licence or None, has_score=a.has_score, has_recording=a.has_recording,
                      renderable=a.renderable, verified=a.verified, top=a.top)
    if a.limit:
        rows = rows[:a.limit]
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    if not rows:
        warn("no matches")
        return 1
    for r in rows:
        parts = ("S" if r["has_editable_score"] else "-") + ("M" if r["renderable_midi"] else "-") + \
                ("R" if r["has_recording"] else "-")
        cat = f" ({r['catalog']})" if r["catalog"] else ""
        print(f"{r['id']:<42} {r['licence_status']:<11} {parts}  {r['composer']}: {r['title']}{cat}")
    warn(f"{len(rows)} match(es). Flags: S=editable score, M=renderable MIDI, R=recording. "
         "Details: musiclib get <id>")
    return 0


def cmd_get(lib: Library, a) -> int:
    it = lib.get(a.id)
    if a.json:
        print(json.dumps(it, ensure_ascii=False, indent=1))
        return 0
    loc = lib.root
    def local(rel):
        return f"  (local: {loc / rel})" if loc and rel and (loc / rel).exists() else ""
    lines = [
        f"{it['id']}  —  {it['composer']}: {it['title']}" + (f", {it['catalog']}" if it.get("catalog") else ""),
        f"genre {it['genre']} · era {it['era']} · mood {', '.join(it['mood_tags_list'])} · energy {it['energy']}",
        f"licence_status: {it['licence_status']}  (recording: {it['recording_status'] or '-'}, "
        f"score: {it['score_status'] or '-'}, verified: {it['verified']})",
        f"  {it['licence_meaning']}",
    ]
    if it.get("legal_flags"):
        lines.append("flags: " + "; ".join(it["legal_flags"]))
    lines.append(f"page:      {it['page_url']}")
    lines.append(f"preview:   {it['preview_url_abs']}{local(it['preview_url'])}")
    if it["has_recording"]:
        lines.append(f"recording: {it['release_audio_url']}"
                     f"  [{it.get('recording_quality') or '?'}; {it.get('recording_license')}]")
        lines.append(f"  performer: {it.get('recording_performer') or '-'}; source: {it.get('recording_source_url')}")
    else:
        lines.append("recording: none (render the score instead)")
    if it["has_editable_score"]:
        lines.append(f"score ({it.get('editable_format')}; {it.get('editable_license')}):")
        for rel, url in zip(it["score_files"], it["score_files_abs"]):
            lines.append(f"  {url}{local(rel)}")
        rm = it.get("render_midi")
        if rm:
            lines.append(f"  render source: {rm['file']}" + (f" -> {rm['zip_member']}" if rm["zip_member"] else ""))
    else:
        lines.append("score: none")
    if it.get("notable_excerpt"):
        lines.append(f"best excerpt: {it['notable_excerpt']}")
    if it.get("video_use_ideas"):
        lines.append(f"video idea: {it['video_use_ideas']}")
    lines.append(f"legal_notes: {it.get('legal_notes')}")
    lines.append("credit:\n  " + it["credit_text"].replace("\n", "\n  "))
    print("\n".join(lines))
    return 0


def cmd_credit(lib: Library, a) -> int:
    it = lib.get(a.id)
    if a.json:
        keys = ["id", "licence_status", "recording_status", "score_status", "verified", "licence_meaning",
                "legal_flags", "recording_license", "editable_license", "legal_notes", "credit_text"]
        print(json.dumps({k: it.get(k) for k in keys}, ensure_ascii=False, indent=1))
        return 0
    print(it["credit_text"])
    warn(f"[{it['licence_status']}] {it['licence_meaning']}")
    return 0 if it["licence_status"] in ("clean", "attribution") else 3


def cmd_download(lib: Library, a) -> int:
    it = lib.get(a.id)
    out = Path(a.out)
    what = {"all": ["recording", "score", "preview"]}.get(a.what, [a.what])
    got = []
    for kind in what:
        if kind == "recording":
            if not it["release_audio_url"]:
                warn(f"{a.id}: no recording; use `musiclib render {a.id}`")
                continue
            dest = out / it["release_audio_name"]
            if lib.root and it.get("local_audio_path") and (lib.root / it["local_audio_path"]).is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((lib.root / it["local_audio_path"]).read_bytes())
            else:
                lib.fetch(it["release_audio_url"], dest)
            got.append(dest)
            licence_warning(it["recording_status"], "the recording")
        elif kind == "score":
            if not it["score_files"]:
                warn(f"{a.id}: no editable score")
                continue
            for rel in it["score_files"]:
                dest = out / Path(rel).name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(lib.local_file(rel).read_bytes())
                got.append(dest)
            licence_warning(it["score_status"], "the score")
        elif kind == "preview":
            dest = out / Path(it["preview_url"]).name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(lib.local_file(it["preview_url"]).read_bytes())
            got.append(dest)
    for g in got:
        print(g)
    return 0 if got else 1


def _midi_for(lib: Library, it: dict, member: str | None, td: Path) -> Path:
    rm = it.get("render_midi")
    if not rm:
        raise SystemExit(f"{it['id']}: no editable score to render. Use the recording: musiclib download {it['id']}")
    path = lib.local_file(rm["file"])
    if path.suffix.lower() == ".zip":
        name = member or rm["zip_member"]
        if not name:
            raise SystemExit(f"{it['id']}: MIDI is inside {rm['file']}; pass --member <file.mid>")
        return audio.extract_member(path, name, td)
    return path


def _finish_kw(a) -> dict:
    return {"start": seconds(a.start) if a.start else 0.0,
            "duration": seconds(a.duration) if a.duration else None,
            "fade_in": a.fade_in, "fade_out": a.fade_out,
            "lufs": None if a.no_normalize else a.lufs}


def cmd_render(lib: Library, a) -> int:
    with tempfile.TemporaryDirectory() as td:
        if a.midi:
            midi, it = Path(a.midi), None
            out = Path(a.out or f"renders/{midi.stem}.mp3")
        else:
            it = lib.get(a.id)
            midi = _midi_for(lib, it, a.member, Path(td))
            out = Path(a.out or f"renders/{it['id']}.mp3")
        audio.render(midi, out, sf2=a.sf2, gain=a.gain, **_finish_kw(a))
    print(out)
    if it:
        warn(f"render licence = score licence: {it.get('editable_license')} [{it['score_status']}]")
        licence_warning(it["score_status"], "the score this render is made from")
        warn("credit:\n  " + it["credit_text"].split("\n", 1)[0] + "\n  Own FluidSynth render (FluidR3_GM soundfont)."
             + ("\n  " + it["credit_text"].split("\n")[-1] if it["has_editable_score"] else ""))
    return 0


def cmd_trim(lib: Library, a) -> int:
    src = Path(a.input)
    out = Path(a.out or src.with_name(f"{src.stem}_cut.mp3"))
    audio.finish(src, out, **_finish_kw(a))
    print(out)
    return 0


def cmd_arrange(lib: Library, a) -> int:
    """Stub hook for re-genre / re-arrangement. Delegates to $MUSICLIB_ARRANGE_CMD when set."""
    it = lib.get(a.id)
    hook = os.environ.get("MUSICLIB_ARRANGE_CMD")
    out = Path(a.out or f"renders/{it['id']}_{a.style}.mid")
    with tempfile.TemporaryDirectory() as td:
        midi = _midi_for(lib, it, a.member, Path(td))
        if not hook:
            warn("arrange is a hook, not built in yet. Set MUSICLIB_ARRANGE_CMD to a command template, e.g.\n"
                 "  export MUSICLIB_ARRANGE_CMD='my-arranger --in {midi} --style {style} --out {out}'\n"
                 "Placeholders: {midi} {style} {out} {id} {item_json}. The command must write a MIDI file to {out};\n"
                 "then: musiclib render --midi {out} --out video.mp3\n"
                 f"Source MIDI for {it['id']}: {midi if not str(midi).startswith(td) else it['render_midi']['url']}")
            licence_warning(it["score_status"], "the score")
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        item_json = Path(td) / "item.json"
        item_json.write_text(json.dumps(it, ensure_ascii=False), encoding="utf-8")
        cmd = [part.format(midi=midi, style=a.style, out=out, id=it["id"], item_json=item_json)
               for part in shlex.split(hook)]
        subprocess.run(cmd, check=True)
    print(out)
    licence_warning(it["score_status"], "the source score")
    return 0


# ---- parser ---------------------------------------------------------------

def add_finish_args(p):
    p.add_argument("--start", help="start time, seconds or MM:SS")
    p.add_argument("--duration", help="length, seconds or MM:SS (default: to the end)")
    p.add_argument("--fade-in", type=float, default=0.3, help="seconds (default 0.3)")
    p.add_argument("--fade-out", type=float, default=0.5, help="seconds (default 0.5)")
    p.add_argument("--lufs", type=float, default=-16.0, help="loudness target (default -16 LUFS)")
    p.add_argument("--no-normalize", action="store_true", help="skip loudness normalisation")


def build_parser():
    p = argparse.ArgumentParser(prog="musiclib", description=(
        "Find legally usable music, fetch recordings/scores, render MIDI with FluidSynth. "
        "Data: local checkout if found, else https://ladoger.github.io/music-library/"))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search title/composer/catalogue no./mood + filters")
    s.add_argument("query", nargs="*", help="words, e.g. bwv 565, dramatic organ, dvorak")
    s.add_argument("--genre", choices=GENRES)
    s.add_argument("--composer")
    s.add_argument("--mood", help="exact mood tag, e.g. epic, calm, dark")
    s.add_argument("--energy", choices=["low", "moderate", "high", "very_high"])
    s.add_argument("--licence", action="append", choices=LICENCES, help="repeatable")
    s.add_argument("--clean", action="store_true", help="only licence_status=clean")
    s.add_argument("--has-score", action="store_true")
    s.add_argument("--has-recording", action="store_true")
    s.add_argument("--renderable", action="store_true", help="has a MIDI `render` can use")
    s.add_argument("--verified", action="store_true")
    s.add_argument("--top", action="store_true", help="top picks for Saylor-style videos, ranked")
    s.add_argument("--limit", type=int)
    s.add_argument("--json", action="store_true")

    g = sub.add_parser("get", help="everything about one id: URLs, local paths, licence, credit")
    g.add_argument("id")
    g.add_argument("--json", action="store_true", help="full item record")

    c = sub.add_parser("credit", help="licence check + attribution text (exit 3 if not clean/attribution)")
    c.add_argument("id")
    c.add_argument("--json", action="store_true")

    d = sub.add_parser("download", help="download recording / score files / preview")
    d.add_argument("id")
    d.add_argument("--what", choices=["recording", "score", "preview", "all"], default="recording")
    d.add_argument("--out", default="downloads", help="directory (default ./downloads)")

    r = sub.add_parser("render", help="render the score's MIDI to audio (FluidSynth + FluidR3_GM)")
    r.add_argument("id", nargs="?")
    r.add_argument("--midi", help="render this MIDI file instead of an item (e.g. an arranged file)")
    r.add_argument("--member", help="MIDI file inside a zip score (default from the item record)")
    r.add_argument("--out", help="output .mp3/.wav/.flac/.m4a/.ogg (default renders/<id>.mp3)")
    r.add_argument("--sf2", help=f"soundfont (default $MUSICLIB_SF2 or {audio.DEFAULT_SF2})")
    r.add_argument("--gain", type=float, default=0.8, help="FluidSynth gain (default 0.8)")
    add_finish_args(r)

    t = sub.add_parser("trim", help="cut/fade/normalise any audio file for video")
    t.add_argument("input")
    t.add_argument("--out", help="output file (default <input>_cut.mp3)")
    add_finish_args(t)

    ar = sub.add_parser("arrange", help="(hook) re-genre / re-arrange via $MUSICLIB_ARRANGE_CMD")
    ar.add_argument("id")
    ar.add_argument("--style", required=True, help="e.g. trap, synthwave, epic-orchestral, lofi")
    ar.add_argument("--member", help="MIDI file inside a zip score")
    ar.add_argument("--out", help="output MIDI (default renders/<id>_<style>.mid)")

    sub.add_parser("info", help="where the data comes from")
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    lib = Library()
    try:
        if a.cmd == "info":
            cat = lib.catalog()
            print(f"source: {lib.source}\npages_base: {cat['pages_base']}\nitems: {cat['count']}\n"
                  f"release: {cat['release']}\nsoundfont: {os.environ.get('MUSICLIB_SF2') or audio.DEFAULT_SF2}")
            return 0
        if a.cmd == "render" and not (a.id or a.midi):
            warn("render needs an id or --midi FILE")
            return 2
        return {"search": cmd_search, "get": cmd_get, "credit": cmd_credit, "download": cmd_download,
                "render": cmd_render, "trim": cmd_trim, "arrange": cmd_arrange}[a.cmd](lib, a)
    except (KeyError, audio.ToolMissing, ValueError) as e:
        warn(f"error: {e.args[0] if e.args else e}")
        return 1
    except subprocess.CalledProcessError as e:
        warn(f"error: command failed ({e.returncode}): {' '.join(map(str, e.cmd))}")
        return 1
    except OSError as e:
        warn(f"error: {e}")
        return 1
