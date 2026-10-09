#!/usr/bin/env python3
"""Build library_bulk.csv (the bulk layer) from parts/BULK_batch*_rows.csv.

library.csv stays the hand-curated master. Bulk imports (OpenScore, Mutopia,
PDMX) live in library_bulk.csv; scripts/sync_site_data.py reads both, and a
library.csv row wins when the same id is in both.

Gate (re-checked here, whatever the batch file says):
  licence_class clean or attribution only (no SA / NC / ND), verified=yes,
  composer death year <= 1929, no excluded composer, score file on disk,
  editable_source_url and editable_license present.

Then dedupe (scripts/bulk/dedupe.py) against library.csv and across batches:
duplicates are dropped and listed as other_editions in
library_other_editions.json; titles lose repeated composer names.

Usage: python3 scripts/bulk/build_bulk_layer.py [--check]
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "library_bulk.csv"
EDITIONS = ROOT / "library_other_editions.json"
EXCLUDED = ("orff", "prokofiev", "shostakovich", "stravinsky", "medtner", "sorabji")
PREVIEW_NOTE = re.compile(r"Preview is an own (?:FluidSynth|MIDI)[^.]*\.", re.I)
UNFINISHED = re.compile(r"\bwip\b|\bdraft\b|work in progress", re.I)
NO_PREVIEW = ("No pre-rendered preview: the site plays the score MIDI with an in-browser "
              "General MIDI synth; no third-party recording.")


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def keep(row: dict, why: Counter) -> bool:
    if (row.get("licence_class") or "") not in {"clean", "attribution"}:
        why["licence"] += 1
        return False
    lic = (row.get("editable_license") or "").lower()
    if any(bad in lic for bad in ("-sa", "sharealike", "share-alike", "-nc", "-nd", "noncommercial", "noderiv")):
        why["licence-text"] += 1
        return False
    if row.get("verified") != "yes" or not row.get("editable_source_url") or not lic:
        why["unverified"] += 1
        return False
    death = row.get("death_year") or ""
    anon = (row.get("composer") or "").lower() in {"traditional", "anonymous", "anon."}
    if (death.isdigit() and int(death) > 1929) or (not death.isdigit() and not anon):
        # A dated arranger of a traditional tune counts too (e.g. a 1930 hymn harmonisation).
        why["death>1929"] += 1
        return False
    if UNFINISHED.search(row.get("title") or ""):
        why["wip-title"] += 1
        return False
    if any(name in (row.get("composer") or "").lower() for name in EXCLUDED):
        why["excluded"] += 1
        return False
    score = row.get("local_score_path") or ""
    if not score or not (ROOT / score).is_file():
        why["no-score"] += 1
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import dedupe

    curated_rows = load(ROOT / "library.csv")
    curated = {row["id"] for row in curated_rows}
    batches = sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))
    rows, seen, why = [], set(), Counter()
    fields: list[str] = []
    for path in batches:
        for row in load(path):
            for key in row:
                if key and key not in fields:
                    fields.append(key)
            rid = row.get("id") or ""
            if not rid or rid in seen or rid in curated:
                why["dup"] += 1
                continue
            if not keep(row, why):
                continue
            # Synth-rendered previews were removed on 2026-10-09 (docs/REMOVED_SYNTH_AUDIO.md);
            # bulk rows are score-only and play via the in-browser MIDI player.
            row["preview_path"] = ""
            if not row.get("preview_path"):
                notes = PREVIEW_NOTE.sub(NO_PREVIEW, row.get("legal_notes") or "")
                if NO_PREVIEW not in notes:
                    notes = (notes + " " + NO_PREVIEW).strip()
                row["legal_notes"] = notes
                if (row.get("notable_excerpt") or "").startswith("Own MIDI render"):
                    row["notable_excerpt"] = "Opening (00:00); play the score MIDI in the browser to audition."
            for key in ("title", "movement"):
                text = row.get(key) or ""
                if re.search("[ÃÄÅÐ]", text):  # PDMX titles double-encoded as UTF-8-in-latin-1
                    try:
                        row[key] = text.encode("cp1252").decode("utf-8")
                    except UnicodeError:
                        pass
            row["title"] = row["title"].replace("DvoÅák", "Dvořák")
            row["title"] = dedupe.clean_title(row["title"], row.get("composer") or "")
            seen.add(rid)
            rows.append(row)
    gated = len(rows)
    rows, editions, manifest, stats = dedupe.dedupe(curated_rows, rows)
    why["duplicate-piece"] += gated - len(rows)
    rows.sort(key=lambda r: (r.get("composer") or "", r.get("catalog") or "", r.get("title") or "", r["id"]))
    print(f"bulk layer: {len(rows)} rows from {[p.name for p in batches]}")
    print("by source:", dict(Counter(r.get("source_name") for r in rows)))
    print("by licence:", dict(Counter(r.get("licence_class") for r in rows)))
    print("dropped:", dict(why))
    print(f"dedupe: {stats['dropped']} duplicates dropped; before {stats['before']} after {stats['after']}")
    dedupe.write_outputs(manifest, stats)
    if "--check" in argv:
        return 0
    tmp = OUT.with_suffix(".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(OUT)
    EDITIONS.write_text(json.dumps(dict(sorted(editions.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
