#!/usr/bin/env python3
"""Independent post-build licence audit of library_bulk.csv (depth run 1). Exit 1 on any violation.

* death > 1929 only for US-PD-only rows of an approved composer with publication_year <= 1930
* no SA / NC / ND editable licence; verified=yes; score file exists
* excluded composers and explicitly excluded works (Ravel Boléro / G concerto / Left Hand / Don Quichotte) absent
"""
import csv, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import schema
from catalogue_data import COMPOSERS
from import_depth_us_pd import Checklist, norm

ROOT = Path(__file__).resolve().parents[2]
bad = []
n = 0
chk = {k: Checklist(k) for k in COMPOSERS}
for r in csv.DictReader((ROOT / "library_bulk.csv").open(newline="", encoding="utf-8")):
    n += 1
    rid = r["id"]
    death = r.get("death_year") or ""
    canon = schema.match_composer(r["composer"]) or ""
    scope = r.get("licence_scope") or ""
    if death.isdigit() and int(death) > 1929:
        pub = r.get("publication_year") or ""
        if not (scope == "US-PD-only" and canon in schema.US_PD_ONLY_CANONS and pub.isdigit() and int(pub) <= 1930 and int(death) <= 1955):
            bad.append((rid, "death>1929 without valid US-PD-only scope"))
    lic = (r.get("editable_license") or "").lower()
    if re.search(r"-sa|sharealike|-nc|-nd|noncommercial|noderiv", lic):
        bad.append((rid, "licence " + lic))
    if r.get("verified") != "yes":
        bad.append((rid, "unverified"))
    if not (ROOT / (r.get("local_score_path") or "x")).is_file():
        bad.append((rid, "score file missing"))
    if scope == "US-PD-only":
        for k, c in chk.items():
            if c.owns(r["composer"]):
                hit = c.match(norm(f"{r['title']} {r.get('movement','')} {r.get('catalog','')}"))
                if hit and hit[3] != "in-scope":
                    bad.append((rid, f"matches excluded/unverified checklist row {hit[0]} {hit[1]} ({hit[3]})"))
    if canon in {"igor stravinsky", "sergei prokofiev", "dmitri shostakovich", "carl orff"}:
        bad.append((rid, "excluded composer"))
    if canon == "maurice ravel" and re.search(r"\bbol[eé]ro\b", r["title"], re.I):
        bad.append((rid, "Boléro present"))
print(f"audited {n} bulk rows; violations: {len(bad)}")
for b in bad[:30]:
    print("  ", b)
sys.exit(1 if bad else 0)
