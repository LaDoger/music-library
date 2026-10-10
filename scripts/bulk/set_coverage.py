#!/usr/bin/env python3
"""Per-set completeness of the top piano sets in the live catalog (data/catalog.json). Prints markdown rows.
Matcher + set list: scripts/bulk/piano_set_defs.py (handles titles without numbers, D/Op. aliases, nicknames).
  python3 scripts/bulk/set_coverage.py [--json out.json] [--catalog path]"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from piano_set_defs import SETS, match_set  # noqa: E402

def load(p):
    d = json.load(open(p)); return d["items"] if isinstance(d, dict) else d

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json"); ap.add_argument("--catalog", default=str(ROOT / "data/catalog.json")); a = ap.parse_args()
    items = load(a.catalog); out = {}
    print("| Set | Scope | Present | Missing |\n|-----|-------|---------|---------|")
    for s in SETS:
        have, miss, _ = match_set(items, s); out[s[0]] = {"have": have, "missing": miss, "n": len(s[4])}
        print(f"| {s[0]} | {s[3]} | {'COMPLETE' if not miss else f'{len(have)}/{len(s[4])}'} | {', '.join(miss) or '-'} |")
    if a.json: json.dump(out, open(a.json, "w"), indent=1)

if __name__ == "__main__":
    main()
