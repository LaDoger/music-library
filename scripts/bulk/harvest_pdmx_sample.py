#!/usr/bin/env python3
"""Harvest a prioritised slice of the PDMX Zenodo table.

PDMX (Zenodo record 15571083, v9) ships one CSV, PDMX.csv, of about 225 MB.
That is the metadata. The audio-adjacent score archives are separate and much
larger (mxl.tar.gz ~1.9 GB, pdf.tar.gz ~9.6 GB, mid.tar.gz ~214 MB). Do not
download those for a metadata pass.

Filter, in order, before a row can enter the priority CSV:

1. subset:no_license_conflict is True. The authors tell users to keep this
   subset. Rows with license_conflict True are dropped even if the public
   MuseScore label says public domain.
2. license is publicdomain or cc-zero / cc0. Anything NC, ND, or BY-SA is
   dropped. The Zenodo compilation itself is CC BY 4.0; that licence covers
   the dataset, not a claim that every arrangement is a critical edition.
3. composer_name matches the priority list (Bach, Wagner, Mahler, Bruckner,
   Beethoven, Mozart, Chopin, Debussy, and the niche / depth list in
   schema.py). Ambiguous dual credits are skipped.
4. is_best_unique_arrangement is True, so piano-spam alternate versions of
   the same upload collapse. A row that fails that flag is kept only when it
   has a real rating (at least 4.5 from 3 ratings).
5. Duration 15–1800 seconds, at least 80 notes, and the title is not an
   obvious pop / tutorial upload.
6. Caps per composer (default 40, 80 for the top priority names) and a
   global cap (default 2500), ranked by rating, favourites, views, and
   whether the title contains a catalogue number.

MIDI bytes are not in the CSV. Each row's `mid` column is a path inside
mid.tar.gz, for example ./mid/1/44/<hash>.mid. Extract only those members:

  python3 scripts/bulk/harvest_pdmx_sample.py \\
      --csv .tmp/pdmx/PDMX.csv \\
      --extract-mid .tmp/pdmx/mid.tar.gz \\
      --extract-to .tmp/pdmx/mid

The download step then reads local files from --extract-to. It does not pull
the multi-gigabyte MusicXML or PDF archives.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema import (  # noqa: E402
    CANDIDATE_COLUMNS,
    COMPOSERS,
    SPAM_RE,
    blank_candidate,
    catalog_from_text,
    classify_license,
    combine_status,
    composer_record,
    composition_status,
    era_for,
    match_composer,
    mood_tags,
    quality_penalty,
    source_rank,
    tempo_energy,
    video_use,
)

ROOT = Path(__file__).resolve().parents[2]
ZENODO = "https://zenodo.org/records/15571083"
CSV_URL = ZENODO + "/files/PDMX.csv?download=1"
MID_URL = ZENODO + "/files/mid.tar.gz?download=1"
EXPECTED_CSV_BYTES = 225399738

WIDE_CAP = {
    "johann sebastian bach", "ludwig van beethoven", "wolfgang amadeus mozart",
    "frederic chopin", "franz schubert", "richard wagner", "gustav mahler",
    "anton bruckner", "claude debussy",
}


def _bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int(value: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _licence_ok(row: dict) -> tuple[bool, str, str]:
    if not _bool(row.get("subset:no_license_conflict")):
        return False, "", ""
    if _bool(row.get("license_conflict")):
        return False, "", ""
    label, klass = classify_license(row.get("license") or "")
    url = (row.get("license_url") or "").lower()
    if klass != "clean":
        # The CSV uses tokens like "publicdomain" and "cc-zero".
        blob = f"{row.get('license') or ''} {url}"
        label, klass = classify_license(blob.replace("-", " "))
    if klass != "clean":
        return False, label, klass
    if any(bad in url for bad in ("nc", "nd", "sharealike", "by-sa", "bysa")):
        return False, label, "excluded"
    return True, label or "PD", "clean"


def _score(row: dict, catalog: str) -> float:
    rating = _float(row.get("rating"))
    n_ratings = _int(row.get("n_ratings"))
    favorites = _int(row.get("n_favorites"))
    views = _int(row.get("n_views"))
    score = 0.0
    if rating >= 4.5 and n_ratings >= 3:
        score += 100 + rating
    elif rating >= 4.0 and n_ratings >= 1:
        score += 40 + rating
    score += min(favorites, 30)
    score += min(views, 5000) / 2000.0
    if catalog:
        score += 12
    if _bool(row.get("is_best_unique_arrangement")):
        score += 5
    return score


def _passes_quality(row: dict, catalog: str) -> bool:
    title = f"{row.get('title') or ''} {row.get('song_name') or ''}"
    if SPAM_RE.search(title):
        return False
    seconds = _float(row.get("song_length.seconds"))
    notes = _int(row.get("n_notes"))
    if seconds and (seconds < 15 or seconds > 1800):
        return False
    if notes and notes < 80:
        return False
    best = _bool(row.get("is_best_unique_arrangement"))
    rating = _float(row.get("rating"))
    n_ratings = _int(row.get("n_ratings"))
    if best:
        return True
    return rating >= 4.5 and n_ratings >= 3


def row_to_candidate(row: dict, label: str) -> dict | None:
    canon = match_composer(row.get("composer_name") or "")
    if not canon:
        return None
    rec = composer_record(canon)
    death = rec["death"]
    comp_class, comp_note = composition_status(canon, death)
    edition = "clean"
    licence_class = combine_status(edition, comp_class)
    if licence_class == "excluded":
        return None
    title = (row.get("title") or row.get("song_name") or "").strip()
    if not title or title.upper() == "NA":
        title = (row.get("song_name") or "").strip()
    catalog = catalog_from_text(title, row.get("song_name") or "", row.get("subtitle") or "")
    if not _passes_quality(row, catalog):
        return None
    display = COMPOSERS.get(canon, rec)["name"] if canon in COMPOSERS else rec["name"]
    instruments_bits = []
    tracks = (row.get("n_tracks") or "").strip()
    tags = (row.get("tags") or "").strip()
    genres = (row.get("genres") or "").strip()
    if tracks:
        instruments_bits.append(f"{tracks} tracks")
    if tags and tags.upper() != "NA":
        instruments_bits.append(tags.replace(",", ";"))
    if genres and genres.upper() != "NA":
        instruments_bits.append(genres)
    instrumentation = "; ".join(instruments_bits)
    rating = _float(row.get("rating"))
    n_ratings = _int(row.get("n_ratings"))
    favorites = _int(row.get("n_favorites"))
    views = _int(row.get("n_views"))
    mid_path = (row.get("mid") or "").strip()
    popularity = f"rating={rating:.2f};ratings={n_ratings};favorites={favorites};views={views}"
    penalty = quality_penalty(canon, title, "", instrumentation)
    if tracks in {"1", "2"} and any(name in canon for name in ("wagner", "mahler", "bruckner")):
        penalty += 1  # piano reduction of an orchestral work: usable, not preferred
    candidate = blank_candidate()
    candidate.update({
        "composer": display,
        "death_year": "" if death is None else str(death),
        "title": title[:180],
        "catalog": catalog,
        "movement": "",
        "mood_tags": mood_tags(title, "", genres if genres.upper() != "NA" else ""),
        "tempo_energy": tempo_energy(title, ""),
        "notable_excerpt": "Own MIDI render 00:00-00:15 (opening)",
        "editable_source_url": ZENODO,
        "editable_format": "MIDI; MusicXML (inside PDMX archives)",
        "editable_license": label,
        "musescore_url": "",
        "source_name": "pdmx",
        "licence_class": licence_class,
        "instrumentation": instrumentation[:240],
        "popularity": popularity,
        "genre": "classical",
        "era": era_for(display, death),
        "download_url": mid_path,
        "repo_path": mid_path,
        "external_id": Path(mid_path).stem if mid_path else "",
        "canon": canon,
        "quality_penalty": str(penalty),
        "source_rank": str(source_rank("pdmx", licence_class, rating, n_ratings)),
    })
    candidate["video_use_ideas"] = video_use(candidate["mood_tags"])
    candidate["verified"] = "yes" if licence_class in {"clean", "attribution"} else "unverified"
    candidate["legal_notes"] = (
        f"{comp_note} PDMX Zenodo 10.5281/zenodo.15571083. "
        f"Kept only where subset:no_license_conflict is true and the licence column is "
        f"{row.get('license')} ({row.get('license_url')}). "
        "The Zenodo compilation is CC BY 4.0; this file's own label is public domain or CC0. "
        f"Rating {rating:.2f} from {n_ratings} ratings, {favorites} favourites, {views} views. "
        f"is_best_unique_arrangement={row.get('is_best_unique_arrangement')}. "
        "User-uploaded MuseScore arrangement, not a critical edition, and not a performance. "
        "Preview is an own FluidSynth render. "
        f"MIDI member: {mid_path}. source_rank={candidate['source_rank']}."
    )
    candidate["_score"] = _score(row, catalog)
    return candidate


def harvest(csv_path: Path, per_composer: int, wide: int, limit: int) -> list[dict]:
    best: dict[str, list] = {}
    seen = 0
    kept_raw = 0
    with csv_path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            seen += 1
            ok, label, _klass = _licence_ok(row)
            if not ok:
                continue
            candidate = row_to_candidate(row, label)
            if candidate is None:
                continue
            kept_raw += 1
            canon = candidate["canon"]
            best.setdefault(canon, []).append(candidate)
    chosen = []
    for canon, items in best.items():
        cap = wide if canon in WIDE_CAP else per_composer
        items.sort(key=lambda item: item.get("_score", 0), reverse=True)
        chosen.extend(items[:cap])
    chosen.sort(key=lambda item: item.get("_score", 0), reverse=True)
    if limit:
        chosen = chosen[:limit]
    for item in chosen:
        item.pop("_score", None)
    print(f"scanned {seen} metadata rows; matched {kept_raw}; emitting {len(chosen)}")
    return chosen


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def extract_members(tar_path: Path, rows: list[dict], dest: Path, limit: int):
    import subprocess
    dest.mkdir(parents=True, exist_ok=True)
    members = []
    for row in rows:
        member = (row.get("download_url") or "").lstrip("./")
        if member.startswith("mid/"):
            members.append(member)
        if limit and len(members) >= limit:
            break
    if not members:
        print("no MIDI members to extract")
        return
    list_path = dest / "_members.txt"
    list_path.write_text("\n".join(members) + "\n", encoding="utf-8")
    print(f"extracting {len(members)} members from {tar_path}")
    subprocess.check_call(["tar", "-xzf", str(tar_path), "-C", str(dest), "-T", str(list_path)])


def main():
    parser = argparse.ArgumentParser(description="Filter PDMX metadata to a priority slice")
    parser.add_argument("--csv", type=Path, default=ROOT / ".tmp" / "pdmx" / "PDMX.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "parts" / "bulk_raw" / "pdmx_priority.csv")
    parser.add_argument("--per-composer", type=int, default=40)
    parser.add_argument("--wide", type=int, default=80)
    parser.add_argument("--limit", type=int, default=2500)
    parser.add_argument("--extract-mid", type=Path, default=None)
    parser.add_argument("--extract-to", type=Path, default=ROOT / ".tmp" / "pdmx" / "mid")
    parser.add_argument("--extract-limit", type=int, default=40)
    parser.add_argument("--print-urls", action="store_true",
                        help="Print the Zenodo URLs and the filter, then exit")
    args = parser.parse_args()
    if args.print_urls:
        print(CSV_URL)
        print(MID_URL)
        print(f"expected_csv_bytes {EXPECTED_CSV_BYTES}")
        print(__doc__)
        return
    if not args.csv.exists() or args.csv.stat().st_size < 1_000_000:
        raise SystemExit(
            "PDMX.csv is missing or still downloading.\n"
            f"  mkdir -p {args.csv.parent}\n"
            f"  curl -fL --retry 3 -o {args.csv} '{CSV_URL}'\n"
            "The file is about 225 MB. Do not download mxl.tar.gz or pdf.tar.gz for this step."
        )
    size = args.csv.stat().st_size
    if size < EXPECTED_CSV_BYTES:
        raise SystemExit(
            f"PDMX.csv is incomplete ({size} of {EXPECTED_CSV_BYTES} bytes). "
            "Wait for the download to finish before filtering."
        )
    rows = harvest(args.csv, args.per_composer, args.wide, args.limit)
    write_csv(args.out, rows)
    from collections import Counter
    print("classes", dict(Counter(row["licence_class"] for row in rows)))
    print("composers", dict(Counter(row["composer"] for row in rows).most_common(15)))
    print(f"wrote {args.out}")
    if args.extract_mid:
        if not args.extract_mid.exists():
            raise SystemExit(
                f"missing {args.extract_mid}. Download the MIDI archive only (~214 MB):\n"
                f"  curl -fL --retry 3 -o {args.extract_mid} '{MID_URL}'"
            )
        extract_members(args.extract_mid, rows, args.extract_to, args.extract_limit)


if __name__ == "__main__":
    main()
