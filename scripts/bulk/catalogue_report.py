#!/usr/bin/env python3
"""Write docs/catalogues/<composer>.csv coverage checklists (depth run 1).

Maps live items (library.csv + library_bulk.csv, i.e. what the site shows) of each
checklist composer onto scripts/bulk/catalogue_data.py rows by title regex, then
reports coverage = in-scope entries with at least one live item / in-scope entries.

  python3 scripts/bulk/catalogue_report.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogue_data import COMPOSERS, IN  # noqa: E402
from import_depth_us_pd import Checklist, norm  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "catalogues"


def items_for(chk: Checklist):
    for name in ("library.csv", "library_bulk.csv"):
        path = ROOT / name
        if not path.is_file():
            continue
        for row in csv.DictReader(path.open(newline="", encoding="utf-8")):
            if chk.owns(row.get("composer") or ""):
                yield name, row


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for key, info in COMPOSERS.items():
        chk = Checklist(key)
        hits: dict[str, list[dict]] = {}
        unmatched = []
        for src, row in items_for(chk):
            hay = norm(f"{row.get('title','')} {row.get('movement','')} {row.get('catalog','')}")
            hit = chk.match(hay)
            if hit and hit[3] == IN:
                hits.setdefault(hit[0], []).append(row)
            elif not hit:
                unmatched.append(row)
        rows_out = []
        for cat, title, year, status, rx, note in info["rows"]:
            got = hits.get(cat, []) if status == IN else []
            rows_out.append({
                "cat_no": cat, "title": title, "publication_year": year or "", "status": status,
                "in_library": "yes" if got else ("" if status == IN else "n/a"),
                "n_items": len(got), "library_ids": " ".join(r["id"] for r in got[:6]),
                "sources": ",".join(sorted({r.get("source_name") or "curated" for r in got})),
                "note": note,
            })
        in_scope = [r for r in rows_out if r["status"] == IN]
        covered = [r for r in in_scope if r["in_library"] == "yes"]
        with (OUT_DIR / f"{key}.csv").open("w", newline="", encoding="utf-8") as handle:
            w = csv.DictWriter(handle, fieldnames=list(rows_out[0]))
            w.writeheader()
            w.writerows(rows_out)
        summary[key] = {
            "name": info["name"], "entries": len(rows_out), "in_scope": len(in_scope), "covered": len(covered),
            "coverage_pct": round(100 * len(covered) / max(1, len(in_scope)), 1),
            "live_items": sum(len(v) for v in hits.values()),
            "gaps": [r["cat_no"] + " " + r["title"] for r in in_scope if r["in_library"] != "yes"],
            "unmatched_live_items": [r["id"] for r in unmatched][:40],
        }
        print(f"{info['name']:22} in-scope entries {len(in_scope):3}  covered {len(covered):3}  "
              f"coverage {summary[key]['coverage_pct']:5.1f}%  live items {summary[key]['live_items']}  "
              f"other live items {len(unmatched)}")
    (ROOT / ".tmp" / "depth1").mkdir(parents=True, exist_ok=True)
    (ROOT / ".tmp" / "depth1" / "catalogue_coverage.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
