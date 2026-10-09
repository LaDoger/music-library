#!/usr/bin/env python3
"""Merge harvest CSVs into parts/BULK_candidates.csv.

Reads parts/bulk_raw/*.csv, drops excluded rows and anything already present
in library.csv or parts/BATCH1_*.csv, and keeps the best source per dedup key.
The output is append-friendly candidate metadata. It does not rewrite
library.csv.
"""
from __future__ import annotations

import argparse
import csv
import sys
from glob import glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dedup import existing_from_paths, load_csv_rows, merge_rows  # noqa: E402
from schema import CANDIDATE_COLUMNS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def score_stems(scores: Path):
    stems = set()
    if not scores.is_dir():
        return stems
    for path in scores.iterdir():
        if path.is_file():
            stems.add(path.stem)
    return stems


def main():
    parser = argparse.ArgumentParser(description="Merge bulk candidates and dedup")
    parser.add_argument("--raw", type=Path, default=ROOT / "parts" / "bulk_raw")
    parser.add_argument("--out", type=Path, default=ROOT / "parts" / "BULK_candidates.csv")
    parser.add_argument("--library", type=Path, default=ROOT / "library.csv")
    parser.add_argument("--batch-glob", default=str(ROOT / "parts" / "BATCH1_*.csv"))
    args = parser.parse_args()
    raw_paths = sorted(args.raw.glob("*.csv")) if args.raw.is_dir() else []
    if not raw_paths:
        raise SystemExit(f"no harvest CSVs in {args.raw}")
    existing_paths = [args.library, *sorted(glob(args.batch_glob))]
    index = existing_from_paths(existing_paths)
    for stem in score_stems(ROOT / "files" / "scores"):
        index.add_stem(stem)
    rows = load_csv_rows(raw_paths)
    kept, stats = merge_rows(rows, index)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(kept)
    print(f"existing files: {[str(path) for path in existing_paths if Path(path).exists()]}")
    print(f"stats {stats}")
    print(f"wrote {len(kept)} -> {args.out}")


if __name__ == "__main__":
    main()
