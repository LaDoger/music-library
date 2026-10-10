#!/usr/bin/env python3
"""Rewrite US-PD-only legal_notes / licence_scope_reason per composer (LaDoger 2026-10-11): composers who died <=1955
(except Stravinsky, Prokofiev) are PD in the EU too, so drop 'may still be copyrighted elsewhere'. usage: fix_scope_notes.py file.csv..."""
import csv, re, sys
RX = re.compile(r"(May (still )?be copyrighted elsewhere[^.]*\.|may still be copyrighted elsewhere[^.]*\.)( LaDoger approved [0-9-]+ with this flag\.)?", re.I)
for p in sys.argv[1:]:
    rows = list(csv.DictReader(open(p, newline=""))); f = list(rows[0].keys()); n = 0
    for r in rows:
        if r.get("licence_scope") != "US-PD-only": continue
        name = r.get("composer", "").lower()
        try: died = int(r.get("death_year") or 0)
        except ValueError: died = 0
        if "stravinsky" in name or "prokofiev" in name or not died or died > 1955: continue
        for k in ("legal_notes", "licence_scope_reason"):
            new = RX.sub(f"Also public domain in the EU / life+70 countries (composer died {died}); only this pre-1931 publication is US-PD, later works by the composer are not.", r.get(k, ""))
            if new != r.get(k, ""): r[k] = new; n += 1
    lt = "\r\n" if b"\r\n" in open(p, "rb").read(4096) else "\n"; w = csv.DictWriter(open(p, "w", newline=""), fieldnames=f, lineterminator=lt); w.writeheader(); w.writerows(rows); print(p, "fixed", n)
