#!/usr/bin/env python3
"""Harvest OpenScore Lieder and String Quartets YAML catalogues.

Both repositories release the scores under CC0 (LICENSE.txt). That is the
edition licence. A composer who died after 1929 is flagged, and one who died
after 1955 or who is on the named exclusion list is dropped from the clean
set. Files are MusicXML (.mxl) addressed as:

  Lieder:          scores/<path>/lc<id>.mxl
  StringQuartets:  scores/<path>/sq<id>.mxl

on the main branch. This script does not download the scores.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema import (  # noqa: E402
    CANDIDATE_COLUMNS,
    COMPOSERS,
    blank_candidate,
    catalog_from_text,
    combine_status,
    composer_record,
    composition_status,
    era_for,
    match_composer,
    mood_tags,
    parse_year,
    quality_penalty,
    source_rank,
    tempo_energy,
    video_use,
)

ROOT = Path(__file__).resolve().parents[2]
REPOS = {
    "openscore-lieder": {
        "repo": "OpenScore/Lieder",
        "file_prefix": "lc",
        "default_instruments": "Voice, Piano",
        "work": "song",
    },
    "openscore-quartets": {
        "repo": "OpenScore/StringQuartets",
        "file_prefix": "sq",
        "default_instruments": "String quartet",
        "work": "quartet",
    },
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "music-library-bulk/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_yaml_maps(text: str) -> dict[str, dict]:
    """Parse the flat OpenScore maps. Values are scalars; nested blocks are skipped."""
    records: dict[str, dict] = {}
    current = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" ") and raw.rstrip().endswith(":"):
            current = raw.strip()[:-1].strip("'\"")
            records[current] = {}
            continue
        if current is None or not raw.startswith("  ") or raw.startswith("   "):
            # Nested list / deeper indent: ignore.
            if raw.startswith("   "):
                continue
        match = re.match(r"^  ([A-Za-z0-9_]+):\s*(.*)$", raw)
        if not match or current is None:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in {">", "|", ""}:
            records[current][key] = ""
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        records[current][key] = value
    return records


def humanize(slug: str) -> str:
    text = slug.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+,", ",", text)
    return text


def song_bits(path: str) -> tuple[str, str, str]:
    """Return (set title, song title, movement label) from a score path."""
    parts = [part for part in path.split("/") if part and part != "_"]
    if len(parts) >= 3:
        set_title = humanize(parts[1])
        song = humanize(parts[-1])
        number = re.match(r"^(\d+[a-z]?)\s+", song)
        movement = song
        if number:
            movement = f"No. {number.group(1)}. {song[number.end():].strip()}"
        return set_title, song, movement
    if len(parts) == 2:
        return "", humanize(parts[1]), ""
    return "", humanize(parts[-1] if parts else path), ""


def load_cached(cache: Path, name: str, url: str) -> str:
    dest = cache / name
    if dest.exists() and dest.stat().st_size > 100:
        return dest.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = fetch(url)
    dest.write_text(text, encoding="utf-8")
    return text


def assert_cc0(cache: Path, repo: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/main/LICENSE.txt"
    text = load_cached(cache, repo.replace("/", "_") + "_LICENSE.txt", url)
    if "CC0 1.0" not in text and "CC0" not in text[:800]:
        raise SystemExit(f"{repo} LICENSE.txt is not CC0; refusing to mark scores CC0")
    return "CC0"


def harvest_repo(source_name: str, spec: dict, cache: Path) -> list[dict]:
    repo = spec["repo"]
    base = f"https://raw.githubusercontent.com/{repo}/main/data"
    assert_cc0(cache, repo)
    composers = parse_yaml_maps(load_cached(cache, repo.replace("/", "_") + "_composers.yaml", base + "/composers.yaml"))
    scores = parse_yaml_maps(load_cached(cache, repo.replace("/", "_") + "_scores.yaml", base + "/scores.yaml"))
    by_path = []
    for _cid, row in composers.items():
        path = row.get("path") or ""
        if path:
            by_path.append((path, row))
    by_path.sort(key=lambda item: len(item[0]), reverse=True)
    rows = []
    for score_id, score in scores.items():
        path = score.get("path") or ""
        if not path:
            continue
        composer_row = {}
        for prefix, row in by_path:
            if path == prefix or path.startswith(prefix + "/"):
                composer_row = row
                break
        display = composer_row.get("name") or humanize(path.split("/")[0])
        death = parse_year(composer_row.get("died"))
        canon = match_composer(display) or match_composer(display.replace(",", " "))
        if not canon:
            canon = re.sub(r"\s+", " ", display.lower()).strip()
            # fold accents via schema.fold
            from schema import fold
            canon = fold(display)
            canon = re.sub(r"[^a-z0-9\s]", " ", canon)
            canon = re.sub(r"\s+", " ", canon).strip()
        rec = composer_record(canon, display, death)
        if death is None:
            death = rec["death"]
        if canon in COMPOSERS:
            display = COMPOSERS[canon]["name"]
        comp_class, comp_note = composition_status(canon, death)
        licence_class = combine_status("clean", comp_class)  # edition is CC0
        set_title, song, movement = song_bits(path)
        if spec["work"] == "quartet":
            title = score.get("name") or song or set_title
            movement = ""
        else:
            song_title = re.sub(r"^\d+[a-z]?\s+", "", song).strip() or song
            title = f"{set_title}: {song_title}" if set_title else song_title
        catalog = catalog_from_text(score.get("name") or "", path, set_title, title)
        instruments = score.get("instruments") or spec["default_instruments"]
        prefix = spec["file_prefix"]
        quoted = "/".join(
            urllib.parse.quote(part) for part in path.split("/")
        )
        download = (
            f"https://raw.githubusercontent.com/{repo}/main/scores/{quoted}/{prefix}{score_id}.mxl"
        )
        blob = f"https://github.com/{repo}/blob/main/scores/{quoted}"
        musescore = score.get("link") or ""
        if "musescore.com" not in musescore:
            musescore = ""
        row = blank_candidate()
        row.update({
            "composer": display,
            "death_year": "" if death is None else str(death),
            "title": title,
            "catalog": catalog,
            "movement": movement,
            "mood_tags": mood_tags(title, movement),
            "tempo_energy": tempo_energy(title, movement),
            "notable_excerpt": "Own MIDI render 00:00-00:15 (opening)",
            "video_use_ideas": "",
            "editable_source_url": blob,
            "editable_format": "MusicXML (MXL); MIDI",
            "editable_license": "CC0",
            "musescore_url": musescore,
            "source_name": source_name,
            "licence_class": licence_class,
            "instrumentation": instruments,
            "popularity": "",
            "genre": "classical",
            "era": era_for(display, death),
            "download_url": download,
            "repo_path": f"scores/{path}",
            "external_id": score_id,
            "canon": canon,
        })
        penalty = quality_penalty(canon, title, movement, instruments)
        if spec["work"] == "quartet":
            penalty = max(0, penalty - 1)
        row["quality_penalty"] = str(penalty)
        row["source_rank"] = str(source_rank(source_name, licence_class))
        row["video_use_ideas"] = video_use(row["mood_tags"])
        row["verified"] = "yes" if licence_class in {"clean", "attribution", "sharealike"} else "unverified"
        vocal = ""
        if spec["work"] == "song":
            vocal = " Vocal lines sound as General MIDI instruments, not sung."
        row["legal_notes"] = (
            f"{comp_note} OpenScore {spec['repo'].split('/')[-1]} score CC0 1.0 "
            f"(repository LICENSE.txt checked). Instrumentation: {instruments}. "
            "Courtesy credit requested by the project: OpenScore and "
            f"https://github.com/{repo}. "
            "Preview is an own FluidSynth (FluidR3_GM) render of a MuseScore MIDI export, "
            "15 seconds, fades, loudness-normalised; no third-party recording."
            f"{vocal} source_rank={row['source_rank']}."
        )
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Harvest OpenScore YAML catalogues")
    parser.add_argument("--cache", type=Path, default=ROOT / ".tmp" / "bulk" / "openscore")
    parser.add_argument("--out", type=Path, default=ROOT / "parts" / "bulk_raw" / "openscore.csv")
    parser.add_argument("--only", choices=["lieder", "quartets", "both"], default="both")
    args = parser.parse_args()
    selected = []
    if args.only in {"lieder", "both"}:
        selected.append("openscore-lieder")
    if args.only in {"quartets", "both"}:
        selected.append("openscore-quartets")
    rows = []
    for name in selected:
        found = harvest_repo(name, REPOS[name], args.cache)
        print(f"{name} {len(found)}")
        rows.extend(found)
    write_csv(args.out, rows)
    from collections import Counter
    print("classes", dict(Counter(row["licence_class"] for row in rows)))
    print(f"wrote {len(rows)} -> {args.out}")


if __name__ == "__main__":
    main()
