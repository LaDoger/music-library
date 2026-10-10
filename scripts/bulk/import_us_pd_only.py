#!/usr/bin/env python3
"""Import LaDoger-approved US-PD-only composers (death 1930–1955, pub ≤1930).

Only the four composers in pdmx_composers_manual.json → approved_us_pd_only
(or the hard-coded APPROVED table below) may pass. Each row must have a
verified publication year ≤ 1930, subset:no_license_conflict, and PD/CC0.
Rows get licence_scope=US-PD-only and licence_class=flagged.

Usage:
  python3 scripts/bulk/import_us_pd_only.py
  python3 scripts/bulk/import_us_pd_only.py --dry-run
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dedup import allocate_id, existing_from_paths  # noqa: E402
from schema import (  # noqa: E402
    CANDIDATE_COLUMNS,
    fold,
    mood_tags,
    slugify,
    tempo_energy,
)

ROOT = Path(__file__).resolve().parents[2]
ZENODO = "https://zenodo.org/records/15571083"
PDMX_CSV = ROOT / ".tmp" / "pdmx" / "PDMX.csv"
MID_TAR = ROOT / ".tmp" / "pdmx" / "mid.tar.gz"
MID_ROOT = ROOT / ".tmp" / "pdmx" / "mid"
OUT = ROOT / "parts" / "BULK_batchP6_rows.csv"
FAIL = ROOT / "parts" / "bulk_raw" / "download_failures_P6.csv"

# Verified publication years (IMSLP / copyright records). Drop anything else.
APPROVED = {
    "kerry mills": {
        "display": "Kerry Mills",
        "death": 1948,
        "birth": 1869,
        "prefix": "kmills",
        "genre": "ragtime",
        "era": "Romantic",
        "aliases": ["kerry mills"],
        "works": [
            (re.compile(r"georgia\s*camp\s*meeting", re.I), 1897, "At a Georgia Camp Meeting"),
            (re.compile(r"whistling\s*rufus", re.I), 1899, "Whistling Rufus"),
        ],
    },
    "euday bowman": {
        "display": "Euday L. Bowman",
        "death": 1949,
        "birth": 1887,
        "prefix": "ebowman",
        "genre": "ragtime",
        "era": "Romantic",
        "aliases": ["euday l bowman", "euday bowman", "e l bowman"],
        "works": [
            (re.compile(r"(12th|twelfth)\s*(st(reet)?\.?)?\s*rag", re.I), 1914, "12th Street Rag"),
            (re.compile(r"11th.*published", re.I), 1918, "11th Street Rag"),
            (re.compile(r"tipperary\s*blues", re.I), 1917, "Tipperary Blues"),
        ],
    },
    "cecil macklin": {
        "display": "Cecil Macklin",
        "death": 1944,
        "birth": 1883,
        "prefix": "macklin",
        "genre": "ragtime",
        "era": "Romantic",
        "aliases": ["cecil macklin"],
        "works": [
            (re.compile(r"(moutarde|mustard)", re.I), 1911, "Très Moutarde (Too Much Mustard)"),
        ],
    },
    "ernesto de curtis": {
        "display": "Ernesto De Curtis",
        "death": 1937,
        "birth": 1875,
        "prefix": "decurtis",
        "genre": "early_popular",
        "era": "Romantic",
        "aliases": ["ernesto de curtis", "e de curtis"],
        "works": [
            (re.compile(r"(torna\s*a\s*sorrento|torna\s*a\s*surriento|come\s*back\s*to\s*sorrento)", re.I), 1902, "Torna a Sorrento"),
            (re.compile(r"voce\s*'?\s*e\s*notte", re.I), 1904, "Voce 'e notte"),
        ],
    },
}

SCOPE = "US-PD-only"
SCOPE_REASON = (
    "US public domain only (composer died {death}; work published {year}, before 1931). "
    "May still be copyrighted elsewhere, including life+70 / life+100 territories "
    "(EU/Poland and others). LaDoger approved 2026-10-10 with this flag."
)

BATCH_COLUMNS = [
    "id", "composer", "death_year", "title", "catalog", "movement",
    "mood_tags", "tempo_energy", "notable_excerpt", "video_use_ideas",
    "editable_source_url", "editable_format", "editable_license",
    "musescore_url", "recording_source_url", "recording_performer",
    "recording_license", "recording_quality", "legal_notes",
    "local_score_path", "local_audio_path", "preview_path",
    "verified", "added_by",
    "source_rank", "source_name", "licence_class", "instrumentation",
    "popularity", "genre", "era",
    "licence_scope", "publication_year", "licence_scope_reason",
]


def _match_composer(composer_name: str) -> str | None:
    c = fold(composer_name)
    if not c or c == "na":
        return None
    for canon, info in APPROVED.items():
        if canon == "euday bowman":
            if ("euday" in c and "bowman" in c) or re.search(r"\be\.?\s*l\.?\s*bowman\b", c):
                return canon
        elif canon == "ernesto de curtis":
            if "de curtis" in c:
                return canon
        else:
            if any(a in c for a in info["aliases"]):
                return canon
    return None


def _work(canon: str, title: str):
    for rx, year, name in APPROVED[canon]["works"]:
        if rx.search(title):
            return year, name
    return None, None


def _bool(v) -> bool:
    return str(v).strip().lower() == "true"


def harvest() -> list[dict]:
    rows = []
    with PDMX_CSV.open(newline="", encoding="utf-8", errors="replace") as handle:
        for raw in csv.DictReader(handle):
            if not _bool(raw.get("subset:no_license_conflict")):
                continue
            if _bool(raw.get("license_conflict")):
                continue
            lic = (raw.get("license") or "").lower().replace("_", "-")
            if lic not in {"publicdomain", "cc-zero", "cc0"}:
                continue
            canon = _match_composer(raw.get("composer_name") or "")
            if not canon:
                continue
            title_blob = f"{raw.get('title') or ''} {raw.get('song_name') or ''}"
            if re.search(r"unpublished|\bwip\b|\bdraft\b", title_blob, re.I):
                continue
            year, work = _work(canon, title_blob)
            if year is None or year > 1930:
                continue
            mid = (raw.get("mid") or "").strip()
            if not mid:
                continue
            info = APPROVED[canon]
            label = "PD" if "public" in lic else "CC0"
            rating = float(raw.get("rating") or 0)
            n_ratings = int(float(raw.get("n_ratings") or 0))
            favorites = int(float(raw.get("n_favorites") or 0))
            views = int(float(raw.get("n_views") or 0))
            reason = SCOPE_REASON.format(death=info["death"], year=year)
            notes = (
                f"{reason} PDMX Zenodo 10.5281/zenodo.15571083. "
                f"subset:no_license_conflict; file licence {raw.get('license')} "
                f"({raw.get('license_url')}). Zenodo compilation is CC BY 4.0; "
                "this file's own label is public domain or CC0. "
                "User-uploaded MuseScore arrangement, not a critical edition. "
                "No pre-rendered preview: the site plays the score MIDI with an "
                "in-browser General MIDI synth; no third-party recording. "
                f"MIDI member: {mid}."
            )
            row = {c: "" for c in CANDIDATE_COLUMNS}
            row.update({
                "composer": info["display"],
                "death_year": str(info["death"]),
                "title": work,
                "mood_tags": mood_tags(work, "", info["genre"]),
                "tempo_energy": tempo_energy(work, ""),
                "notable_excerpt": "Opening (00:00); play the score MIDI in the browser to audition.",
                "video_use_ideas": "Underscore a short scene with the opening bars.",
                "editable_source_url": ZENODO,
                "editable_format": "MIDI; MusicXML (inside PDMX archives)",
                "editable_license": label,
                "legal_notes": notes,
                "verified": "yes",
                "added_by": "bulk",
                "source_rank": "9",
                "source_name": "pdmx",
                "licence_class": "flagged",
                "instrumentation": f"{raw.get('n_tracks') or '?'} tracks; {info['genre']}",
                "popularity": f"rating={rating:.2f};ratings={n_ratings};favorites={favorites};views={views}",
                "genre": info["genre"],
                "era": info["era"],
                "download_url": mid,
                "repo_path": mid,
                "external_id": Path(mid).stem,
                "canon": canon,
                "quality_penalty": "0",
                "licence_scope": SCOPE,
                "publication_year": str(year),
                "licence_scope_reason": reason,
                "_best": 1 if _bool(raw.get("is_best_unique_arrangement")) else 0,
                "_score": (100 if _bool(raw.get("is_best_unique_arrangement")) else 0)
                          + rating + min(favorites, 30) + min(views, 5000) / 2000.0,
            })
            rows.append(row)
    # Prefer best arrangement / higher score per work title; keep all for
    # download then let build_bulk_layer dedupe fold the rest as editions.
    rows.sort(key=lambda r: (-r["_score"], r["title"], r["external_id"]))
    print(f"harvested {len(rows)} US-PD-only candidate rows")
    by = {}
    for r in rows:
        by.setdefault(r["composer"], 0)
        by[r["composer"]] += 1
    print("by composer:", by)
    return rows


def extract(rows: list[dict]):
    members = []
    for row in rows:
        member = (row.get("download_url") or "").lstrip("./")
        if member.startswith("mid/"):
            path = MID_ROOT / member
            if not path.is_file():
                members.append(member)
    if not members:
        print("all MIDI members already extracted")
        return
    MID_ROOT.mkdir(parents=True, exist_ok=True)
    list_path = MID_ROOT / "_members_p6.txt"
    list_path.write_text("\n".join(members) + "\n", encoding="utf-8")
    print(f"extracting {len(members)} members")
    subprocess.check_call(["tar", "-xzf", str(MID_TAR), "-C", str(MID_ROOT), "-T", str(list_path)])


def download(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    index = existing_from_paths([ROOT / "library.csv", *sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))])
    for folder in (ROOT / "files" / "scores",):
        if folder.is_dir():
            for path in folder.iterdir():
                if path.is_file():
                    index.add_stem(path.stem)
    used: set[str] = set()
    done, failures = [], []
    scores = ROOT / "files" / "scores"
    scores.mkdir(parents=True, exist_ok=True)
    for row in rows:
        prefix = APPROVED[row["canon"]]["prefix"]
        base = f"{prefix}_{slugify(row['title'], 40)}"
        ident = allocate_id(base, index, used)
        member = (row.get("download_url") or "").lstrip("./")
        src = MID_ROOT / member
        if not src.is_file():
            failures.append({"id": ident, "source": "pdmx", "error": f"missing {member}"})
            continue
        data = src.read_bytes()
        if data[:4] != b"MThd":
            failures.append({"id": ident, "source": "pdmx", "error": "not MIDI"})
            continue
        dest = scores / f"{ident}.mid"
        if dest.exists():
            failures.append({"id": ident, "source": "pdmx", "error": "target exists"})
            continue
        dest.write_bytes(data)
        out = {c: row.get(c, "") for c in BATCH_COLUMNS}
        out["id"] = ident
        out["local_score_path"] = f"files/scores/{ident}.mid"
        out["local_audio_path"] = ""
        out["preview_path"] = ""
        out["added_by"] = "bulk"
        done.append(out)
        used.add(ident)
        index.add_stem(ident)
        print(f"OK {ident} pub={out['publication_year']} {out['composer']}")
    return done, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not PDMX_CSV.is_file() or not MID_TAR.is_file():
        raise SystemExit("PDMX.csv / mid.tar.gz missing under .tmp/pdmx/")
    rows = harvest()
    if args.dry_run:
        for r in rows[:20]:
            print(f"  {r['composer']:22} {r['publication_year']} {r['title']}")
        return 0
    extract(rows)
    done, failures = download(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=BATCH_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(done)
    if failures:
        FAIL.parent.mkdir(parents=True, exist_ok=True)
        with FAIL.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "source", "error"])
            writer.writeheader()
            writer.writerows(failures)
        print(f"failures {len(failures)} -> {FAIL}")
    counts = {}
    for r in done:
        counts[r["composer"]] = counts.get(r["composer"], 0) + 1
    print(f"wrote {len(done)} rows -> {OUT}")
    print("counts:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
