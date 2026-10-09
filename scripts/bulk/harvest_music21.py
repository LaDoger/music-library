#!/usr/bin/env python3
"""Harvest licence-gated pieces from the music21 corpus into parts/BULK_batchK_rows.csv.

Only files whose embedded MusicXML <rights> element states PD / CC0 / CC BY are
used (the corpus as a whole carries no blanket licence and says some files are
non-commercial; see docs/licences/music21_corpus.md). The allow-list below was
checked by hand on 2026-10-09. Needs music21 (run with a venv python that has it):

  /tmp/m21venv/bin/python scripts/bulk/harvest_music21.py
"""
from __future__ import annotations

import csv
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "parts" / "BULK_batchK_rows.csv"
TEMPLATE = ROOT / "parts" / "BULK_batchP_rows.csv"
RAW = "https://raw.githubusercontent.com/cuthbertLab/music21/master/"
BLOB = "https://github.com/cuthbertLab/music21/blob/master/"

# (id, corpus path, composer, death, title, catalog, rights must match, licence, class, era, credit/notes)
ALLOW = [
    ("lusitano_allor_che_ignuda", "music21/corpus/lusitano/allor_che_ignuda.mxl",
     "Vicente Lusitano", "1561", "Allor che ignuda", "", r"CC0/Public Domain", "CC0", "clean",
     "Renaissance", "Encoding rights line: 'Copyright 2022 Michael Scott Asato Cuthbert: released as CC0/Public Domain'. "
     "Lusitano died after 1561 (exact year unknown; recorded as 1561)."),
    ("weber_j109_clarinet_concertino", "music21/corpus/weber/concertino_clarinet.mxl",
     "Carl Maria von Weber", "1826", "Clarinet Concertino in E-flat", "Op. 26 (J. 109)", r"Released to Public Domain",
     "Public Domain", "clean", "Romantic",
     "Encoding rights line: 'Released to Public Domain in 1998' (arranger/encoder Oliver Seely)."),
    ("corelli_op3no1_grave", "music21/corpus/corelli/opus3no1/1grave.xml",
     "Arcangelo Corelli", "1713", "Trio Sonata Op. 3 No. 1: I. Grave", "Op. 3 No. 1", r"\(CC-BY\)",
     "CC BY", "attribution", "Baroque",
     "Encoding rights line: '(c) 2014, Creative Commons License (CC-BY)', encoder Michael Scott Cuthbert. "
     "Credit: 'Corelli Op. 3 No. 1 Grave, encoding by Michael Scott Cuthbert (music21 corpus), CC BY'."),
]


def rights_of(path: Path) -> str:
    import zipfile
    try:
        with zipfile.ZipFile(path) as z:
            text = " ".join(z.read(m).decode("utf8", "replace") for m in z.namelist() if not m.startswith("META"))
    except zipfile.BadZipFile:
        text = path.read_text(encoding="utf8", errors="replace")
    return " | ".join(re.findall(r"<rights>([^<]*)", text))


def existing_ids() -> set[str]:
    ids = set()
    for name in ("library.csv", "library_bulk.csv"):
        p = ROOT / name
        if p.exists():
            with p.open(newline="", encoding="utf-8") as h:
                ids |= {r["id"] for r in csv.DictReader(h)}
    return ids


def main() -> int:
    import music21
    with TEMPLATE.open(newline="", encoding="utf-8") as h:
        fields = csv.DictReader(h).fieldnames
    taken = existing_ids()
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for (pid, cpath, composer, death, title, cat, must, lic, cls, era, note) in ALLOW:
            if pid in taken:
                print("skip (id exists):", pid)
                continue
            src = Path(tmp) / Path(cpath).name
            urllib.request.urlretrieve(RAW + cpath, src)
            rights = rights_of(src)
            if not re.search(must, rights):
                print("skip (rights changed):", pid, rights)
                continue
            mid = ROOT / "files" / "scores" / f"{pid}.mid"
            music21.converter.parse(src).write("midi", fp=str(mid))
            row = dict.fromkeys(fields, "")
            row.update({
                "id": pid, "composer": composer, "death_year": death, "title": title, "catalog": cat,
                "mood_tags": "classical;lyrical", "tempo_energy": "moderate / opening",
                "notable_excerpt": "Own MIDI render 00:00-00:15 (opening)",
                "video_use_ideas": "Underscore a short scene with the opening bars.",
                "editable_source_url": BLOB + cpath,
                "editable_format": "MIDI (converted with music21 from corpus MusicXML)",
                "editable_license": lic,
                "legal_notes": (f"Composer died {death}. music21 corpus file {cpath}; corpus licence.txt says "
                                "individual files carry their own terms and some are non-commercial, so this row "
                                f"relies on the file's own <rights>: '{rights.strip()}'. {note} "
                                "MIDI converted locally with music21 10.5. Checked 2026-10-09; see docs/licences/music21_corpus.md."),
                "local_score_path": f"files/scores/{pid}.mid",
                "verified": "yes", "added_by": "bulk", "source_rank": "3",
                "source_name": "music21-corpus", "licence_class": cls,
                "instrumentation": "music21 corpus", "genre": "classical", "era": era,
            })
            rows.append(row)
    with OUT.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
