#!/usr/bin/env python3
"""Fill missing movements of the top piano sets (piano_set_defs.SETS) from clean local candidate pools.

Pools: parts/BULK_candidates.csv (Mutopia PD/CC BY, OpenScore CC0, PDMX clean) and the full PDMX.csv
(subset:no_license_conflict, licence publicdomain/cc-zero, no licence conflict, <=2 tracks, no arrangements).
Fully-PD composers only (death <= 1929); US-PD-only sets are left to the IMSLP browser list.
Writes parts/BULK_batchPS_rows.csv (picked up by build_bulk_layer.py).
  python3 scripts/bulk/import_piano_sets.py [--dry-run]
"""
from __future__ import annotations
import argparse, csv, json, math, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import piano_set_defs as D  # noqa: E402
from dedup import allocate_id, canon_name, existing_from_paths  # noqa: E402
from import_depth_us_pd import ARRANGED, MID_ROOT, MID_TAR, PDMX_CSV, ZENODO  # noqa: E402
from schema import composer_record, mood_tags, slugify, tempo_energy  # noqa: E402
import download_slice as DS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "parts" / "BULK_batchPS_rows.csv"
csv.field_size_limit(10**9)
SRC_ORDER = {"mutopia": 0, "openscore-lieder": 1, "pdmx": 2}

def score(r):
    pop = r.get("popularity") or ""
    m = re.search(r"rating=([\d.]+);ratings=(\d+)", pop)
    rt, n = (float(m.group(1)), int(m.group(2))) if m else (0.0, 0)
    return (SRC_ORDER.get(r["source_name"], 9), -(rt * math.log(2 + n)))

def pdmx_rows(comps):
    out = []
    for x in csv.DictReader(PDMX_CSV.open(newline="", encoding="utf-8", errors="replace")):
        if x["subset:no_license_conflict"] != "True" or x["license_conflict"] == "True" or x["license"] not in ("publicdomain", "cc-zero"):
            continue
        c = canon_name(x["composer_name"] or "")
        if c not in comps or not (x["mid"] or "").strip():
            continue
        blob = f"{x['title']} {x['song_name']} {x.get('subtitle','')}"
        if ARRANGED.search(f"{blob} {x['composer_name']}") or int(float(x["n_tracks"] or 9)) > 2 or x.get("is_draft") == "True":
            continue
        rec = composer_record(c); lic = "PD" if x["license"] == "publicdomain" else "CC0"
        title = re.sub(r"\s*[-–]\s*" + re.escape(rec["name"].split()[-1]) + r".*$", "", x["title"]).strip() or x["song_name"]
        out.append({"composer": rec["name"], "death_year": str(rec["death"]), "title": title, "catalog": "", "movement": "",
            "subtitle": x.get("subtitle", ""), "mood_tags": mood_tags(title, "", "classical"), "tempo_energy": tempo_energy(title, ""),
            "notable_excerpt": "Opening (00:00); play the score MIDI in the browser to audition.",
            "video_use_ideas": "Underscore a short scene with the opening bars.", "editable_source_url": ZENODO,
            "editable_format": "MIDI; MusicXML (inside PDMX archives)", "editable_license": lic,
            "legal_notes": (f"Composer died {rec['death']}. PDMX Zenodo 10.5281/zenodo.15571083. subset:no_license_conflict; file licence "
                            f"{x['license']} ({x['license_url']}). Zenodo compilation is CC BY 4.0; this file's own label is public domain or CC0. "
                            f"User-uploaded MuseScore transcription, not a critical edition. MIDI member: {x['mid']}."),
            "verified": "yes", "source_rank": "9", "source_name": "pdmx", "licence_class": "clean",
            "instrumentation": f"{x['n_tracks']} tracks; piano", "popularity": f"rating={float(x['rating'] or 0):.2f};ratings={x['n_ratings'] or 0};favorites={x['n_favorites'] or 0};views={x['n_views'] or 0}",
            "genre": "classical", "era": "", "download_url": x["mid"], "repo_path": x["mid"], "canon": c})
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--plan", default=str(ROOT / ".tmp/psets/plan.json")); a = ap.parse_args()
    items = D.json.load(open(ROOT / "data/catalog.json")) if hasattr(D, "json") else json.load(open(ROOT / "data/catalog.json"))
    items = items["items"] if isinstance(items, dict) else items
    sets = [s for s in D.SETS if s[3] == "PD"]
    comps = {canon_name(s[1]) for s in sets}
    pool = []
    for r in csv.DictReader((ROOT / "parts/BULK_candidates.csv").open(newline="", encoding="utf-8")):
        if r.get("licence_class") in ("clean", "attribution") and r.get("canon") in comps and int(r.get("death_year") or 9999) <= 1929 \
                and not ARRANGED.search(f"{r['title']} {r.get('movement','')}") and r["source_name"] != "pdmx":
            pool.append(r)
    pool += pdmx_rows(comps)
    print("pool", len(pool))
    for i, r in enumerate(pool): r["_k"] = i
    picked, plan = {}, []
    for s in sets:
        have, miss, _ = D.match_set(items, s)
        if not miss: continue
        cands = [{"id": r["_k"], "composer": r["composer"], "title": r['title'], "movement": r.get("movement", ""), "catalog": r.get("catalog", "")} for r in pool if canon_name(s[1]) == r["canon"]]
        _, _, hits = D.match_set(cands, s)
        for lab in miss:
            ks = hits.get(lab, [])
            # prefer a file that hits only this movement (not a multi-number compilation)
            ks = sorted(ks, key=lambda k: (sum(k in v for v in hits.values()) > 1, score(pool[k])))
            if ks:
                k = ks[0]; picked.setdefault(k, []).append(f"{s[0]}: {lab}"); plan.append((s[0], lab, pool[k]["source_name"], pool[k]["title"]))
    json.dump(plan, open(a.plan, "w"), indent=0)
    print(f"{len(plan)} movements fillable via {len(picked)} files")
    for p in plan: print("  ", p)
    if a.dry_run: return 0
    members = [pool[k]["download_url"].lstrip("./") for k in picked if pool[k]["source_name"] == "pdmx" and not (MID_ROOT / pool[k]["download_url"].lstrip("./")).is_file()]
    if members:
        lst = ROOT / ".tmp/psets/members.txt"; lst.write_text("\n".join(members) + "\n")
        subprocess.check_call(["tar", "-xzf", str(MID_TAR), "-C", str(MID_ROOT), "-T", str(lst)])
    index = existing_from_paths([ROOT / "library.csv", *sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))])
    for p in (ROOT / "files/scores").iterdir():
        if p.is_file(): index.add_stem(p.stem)
    used, ok = set(), 0
    for k, labs in picked.items():
        r = dict(pool[k]); rec = composer_record(r["canon"])
        r["id"] = allocate_id(f"{rec['prefix']}_ps_{slugify(r['title'], 48)}", index, used)
        r["legal_notes"] = (r.get("legal_notes") or "") + " Fills complete-set gap: " + "; ".join(labs) + "."
        r["added_by"] = "bulk"
        try:
            done = DS.process(r, MID_ROOT, False)
        except Exception as e:  # noqa: BLE001
            print("FAIL", r["id"], str(e)[:200]); continue
        done["added_by"] = "bulk"
        DS._append(OUT, done); ok += 1; print("OK", done["id"], labs)
    print(f"wrote {ok} rows -> {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
