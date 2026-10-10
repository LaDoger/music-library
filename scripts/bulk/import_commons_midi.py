#!/usr/bin/env python3
"""Import hand-vetted complete-piece MIDI files from Wikimedia Commons (depth run 1).

Each ACCEPT row names a Commons file whose licence tag (API extmetadata LicenseShortName) is
Public domain / CC0 and whose MIDI is a complete piece (>= 60 s), not an analysis excerpt.
CC BY-SA / GPL / NC files are never listed. Source: Commons file page; rows are score-only.

  python3 scripts/bulk/import_commons_midi.py [--dry-run]
Reads .tmp/depth1/commons_cands.json (+ commons_cands2.json if present), writes
parts/BULK_batchP8_rows.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dedup import allocate_id, existing_from_paths  # noqa: E402
from import_depth_us_pd import BATCH_COLUMNS  # noqa: E402
from schema import CANDIDATE_COLUMNS, composer_record, mood_tags, slugify, tempo_energy  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "parts" / "BULK_batchP8_rows.csv"
UA = {"User-Agent": "music-library-depth1/1.0 (LaDoger/music-library)"}

# commons title -> (canon, display title, catalogue, movement, genre)
ACCEPT = {
    "Debussy, Children's Corner, No. 2.mid": ("claude debussy", "Children's Corner: Jimbo's Lullaby", "L. 113", "No. 2 Jimbo's Lullaby"),
    "Debussy, Children's Corner, No. 3.mid": ("claude debussy", "Children's Corner: Serenade for the Doll", "L. 113", "No. 3 Serenade for the Doll"),
    "Debussy, Children's Corner, No. 4.mid": ("claude debussy", "Children's Corner: The Snow Is Dancing", "L. 113", "No. 4 The Snow Is Dancing"),
    "Debussy, Children's Corner, No. 5.mid": ("claude debussy", "Children's Corner: The Little Shepherd", "L. 113", "No. 5 The Little Shepherd"),
    "Grieg, Holberg Suite, No. 1.mid": ("edvard grieg", "Holberg Suite: Praeludium", "Op. 40", "No. 1 Praeludium"),
    "Grieg, Holberg Suite, No. 2.mid": ("edvard grieg", "Holberg Suite: Sarabande", "Op. 40", "No. 2 Sarabande"),
    "Grieg, Holberg Suite, No. 3.mid": ("edvard grieg", "Holberg Suite: Gavotte", "Op. 40", "No. 3 Gavotte"),
    "Grieg, Holberg Suite, No. 4.mid": ("edvard grieg", "Holberg Suite: Air", "Op. 40", "No. 4 Air"),
    "Grieg, Holberg Suite, No. 5.mid": ("edvard grieg", "Holberg Suite: Rigaudon", "Op. 40", "No. 5 Rigaudon"),
    "Grieg, Lyric Pieces, Op. 43, No. 6.mid": ("edvard grieg", "Lyric Pieces: To the Spring", "Op. 43 No. 6", "To the Spring"),
    "Grieg, Lyric Pieces, Op. 54, No. 3.mid": ("edvard grieg", "Lyric Pieces: March of the Trolls", "Op. 54 No. 3", "March of the Trolls"),
    "Humoresk Dvorak.mid": ("antonin dvorak", "Humoresque in G-flat major", "Op. 101 No. 7", ""),
    "Liszt, Valse-Impromptu, S. 213.mid": ("franz liszt", "Valse-Impromptu", "S. 213", ""),
    "Il vecchio castello.mid": ("modest mussorgsky", "Pictures at an Exhibition: Il vecchio castello", "", "Il vecchio castello"),
    "Promenade.mid": ("modest mussorgsky", "Pictures at an Exhibition: Promenade", "", "Promenade"),
    "Erik Satie - Ogive No.1.mid": ("erik satie", "Ogive No. 1", "", ""),
    "Erik Satie - Ogive No.2.mid": ("erik satie", "Ogive No. 2", "", ""),
    "Erik Satie - Ogive No.3.mid": ("erik satie", "Ogive No. 3", "", ""),
    "Erik Satie - Ogive No.4.mid": ("erik satie", "Ogive No. 4", "", ""),
    "Alexander Scriabin - Fantasie in B minor, Op28 (Floril).mid": ("alexander scriabin", "Fantasy in B minor", "Op. 28", ""),
    "Scriabin, Sonata No. 5, Op. 53.mid": ("alexander scriabin", "Piano Sonata No. 5", "Op. 53", ""),
    "Scriabin, Sonata No. 9, Op. 68.mid": ("alexander scriabin", "Piano Sonata No. 9 (Black Mass)", "Op. 68", ""),
    "Stigliani.-.scriabin.08.12.mid": ("alexander scriabin", "Étude Op. 8 No. 12", "Op. 8 No. 12", ""),
    "Stigliani.-.scriabin.42.05.mid": ("alexander scriabin", "Étude Op. 42 No. 5", "Op. 42 No. 5", ""),
    "Winitzky.-.scriabin.13.01.mid": ("alexander scriabin", "Prelude Op. 13 No. 1", "Op. 13 No. 1", ""),
    "Winitzky.-.scriabin.15.02.mid": ("alexander scriabin", "Prelude Op. 15 No. 2", "Op. 15 No. 2", ""),
    "Winitzky.-.scriabin.25.03.mid": ("alexander scriabin", "Mazurka Op. 25 No. 3", "Op. 25 No. 3", ""),
    "Winitzky.-.scriabin.25.09.mid": ("alexander scriabin", "Mazurka Op. 25 No. 9", "Op. 25 No. 9", ""),
    "Winitzky.-.scriabin.32.01.mid": ("alexander scriabin", "Poème Op. 32 No. 1", "Op. 32 No. 1", ""),
    "Winitzky.-.scriabin.40.02.mid": ("alexander scriabin", "Mazurka Op. 40 No. 2", "Op. 40 No. 2", ""),
    "Winitzky.-.scriabin.42.01.mid": ("alexander scriabin", "Étude Op. 42 No. 1", "Op. 42 No. 1", ""),
    "Winitzky.-.scriabin.42.06.mid": ("alexander scriabin", "Étude Op. 42 No. 6", "Op. 42 No. 6", ""),
    "Wagner, Kaisermarsch, Schlussgesang.mid": ("richard wagner", "Kaisermarsch: Schlussgesang (Heil! Heil dem Kaiser!)", "WWV 104", "Schlussgesang"),
}
ACCEPT_EXTRA: dict = {}
extra_path = ROOT / ".tmp" / "depth1" / "commons_accept_extra.json"
if extra_path.is_file():
    ACCEPT_EXTRA = {k: tuple(v) for k, v in json.loads(extra_path.read_text(encoding="utf-8")).items()}
ACCEPT.update(ACCEPT_EXTRA)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cands = {}
    for name in ("commons_cands.json", "commons_cands2.json"):
        path = ROOT / ".tmp" / "depth1" / name
        if path.is_file():
            for comp, title, mime, lic, size, secs, artist in json.loads(path.read_text(encoding="utf-8")):
                cands[title.removeprefix("File:")] = dict(lic=lic, size=size, secs=secs, artist=artist, mime=mime)
    index = existing_from_paths([ROOT / "library.csv", *sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))])
    for p in (ROOT / "files" / "scores").iterdir():
        if p.is_file():
            index.add_stem(p.stem)
    used: set[str] = set()
    rows, missing = [], []
    for fname, (canon, title, catalog, movement) in ACCEPT.items():
        info = cands.get(fname)
        if not info:
            missing.append(fname)
            continue
        if info["lic"] not in {"Public domain", "CC0"} or (info["secs"] or 0) < 60:
            missing.append(f"{fname} (licence {info['lic']!r}, {info['secs']} s)")
            continue
        rec = composer_record(canon)
        url = "https://upload.wikimedia.org/wikipedia/commons/" + ""  # resolved below via the API url
        rows.append((fname, canon, title, catalog, movement, rec, info))
    print(f"{len(rows)} accepted, {len(missing)} not usable: {missing}")
    if args.dry_run:
        return 0
    done, failures = [], []
    for fname, canon, title, catalog, movement, rec, info in rows:
        api = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&format=json&titles="
               + urllib.parse.quote("File:" + fname))
        try:
            meta = json.load(urllib.request.urlopen(urllib.request.Request(api, headers=UA), timeout=60))
            furl = next(iter(meta["query"]["pages"].values()))["imageinfo"][0]["url"]
            data = urllib.request.urlopen(urllib.request.Request(furl, headers=UA), timeout=60).read()
            if data[:4] != b"MThd":
                raise RuntimeError("not MIDI")
            time.sleep(0.5)
        except Exception as exc:  # noqa: BLE001
            failures.append((fname, str(exc)))
            continue
        ident = allocate_id(f"{rec['prefix']}_{slugify((catalog + ' ' + title).strip(), 48)}", index, used)
        (ROOT / "files" / "scores" / f"{ident}.mid").write_bytes(data)
        page = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(fname.replace(" ", "_"))
        row = {c: "" for c in CANDIDATE_COLUMNS}
        lic = info["lic"]
        row.update({
            "id": ident, "composer": rec["name"], "death_year": str(rec["death"]), "title": title, "catalog": catalog,
            "movement": movement, "mood_tags": mood_tags(title, "", "classical"), "tempo_energy": tempo_energy(title, ""),
            "notable_excerpt": "Opening (00:00); play the score MIDI in the browser to audition.",
            "video_use_ideas": "Underscore a short scene with the opening bars.",
            "editable_source_url": page, "editable_format": "MIDI", "editable_license": "CC0" if lic == "CC0" else "PD",
            "legal_notes": (f"Composer died {rec['death']}. Wikimedia Commons file page licence tag: {lic} (Commons API extmetadata). "
                            "User-made MIDI sequence, not a critical edition or a recording. "
                            "No pre-rendered preview: the site plays the score MIDI with an in-browser General MIDI synth; no third-party recording."),
            "local_score_path": f"files/scores/{ident}.mid", "verified": "yes", "added_by": "bulk",
            "source_rank": "8", "source_name": "commons", "licence_class": "clean", "instrumentation": "piano/MIDI sequence",
            "genre": "classical", "era": "",
        })
        done.append({c: row.get(c, "") for c in BATCH_COLUMNS})
        index.add_stem(ident)
        print("OK", ident)
    with OUT.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=BATCH_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(done)
    print(f"wrote {len(done)} rows -> {OUT}; failures {failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
