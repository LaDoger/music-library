#!/usr/bin/env python3
"""Import PDMX no_license_conflict PD/CC0 rows that fill a *signature-work gap* of a featured composer.

Gaps come from scripts/bulk/tier_list.py (SIG regexes vs live items); only composers with
featured_rank 1-2 and death <= 1929 (fully PD) are considered; third-party arrangements are
skipped (same filter as import_depth_us_pd.ARRANGED). Writes parts/BULK_batchP9_rows.csv.

  python3 scripts/bulk/import_pdmx_signature_gaps.py [--dry-run]
"""
from __future__ import annotations

import argparse, csv, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tier_list as T  # noqa: E402
from dedup import allocate_id, canon_name, existing_from_paths  # noqa: E402
from import_depth_us_pd import ARRANGED, BATCH_COLUMNS, MID_ROOT, MID_TAR, PDMX_CSV, ZENODO, norm  # noqa: E402
from schema import CANDIDATE_COLUMNS, composer_record, mood_tags, slugify, tempo_energy  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "parts" / "BULK_batchP9_rows.csv"
csv.field_size_limit(10**9)


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); args = ap.parse_args()
    feat = json.loads((ROOT / "scripts" / "featured_composers.json").read_text(encoding="utf-8"))["composers"]
    ok_canons = {c for c, v in feat.items() if v["featured_rank"] <= 2 and composer_record(c)["death"] <= 1929}
    live = {}
    for name in ("library.csv", "library_bulk.csv"):
        for r in csv.DictReader((ROOT / name).open(newline="", encoding="utf-8")):
            live.setdefault(canon_name(r["composer"]), []).append(norm(f"{r['title']} {r.get('movement','')} {r.get('catalog','')}"))
    gaps = {}  # canon -> [(label, rx)]
    for name, sig in T.SIG.items():
        c = canon_name(name)
        if c in ok_canons:
            gaps[c] = [(l, rx) for l, rx in sig if not any(re.search(rx, h) for h in live.get(c, []))]
    picked = []
    for x in csv.DictReader(PDMX_CSV.open(newline="", encoding="utf-8", errors="replace")):
        if x["subset:no_license_conflict"] != "True" or x["license_conflict"] == "True" or x["license"] not in ("publicdomain", "cc-zero"):
            continue
        c = canon_name(x["composer_name"] or "")
        if c not in gaps or not gaps[c]:
            continue
        blob = f"{x['title']} {x['song_name']}"
        if re.search(r"phrygian|cadence", blob, re.I) or ARRANGED.search(f"{blob} {x['composer_name']}") or not (x["mid"] or "").strip():
            continue
        hit = next((l for l, rx in gaps[c] if re.search(rx, norm(blob))), None)
        if hit:
            picked.append((c, hit, x))
    print(f"{len(picked)} gap rows:", [(c[:8], h, x['title'][:30]) for c, h, x in picked])
    if args.dry_run or not picked:
        return 0
    members = [x["mid"].lstrip("./") for _, _, x in picked if not (MID_ROOT / x["mid"].lstrip("./")).is_file()]
    if members:
        lst = MID_ROOT / "_members_p9.txt"; lst.write_text("\n".join(members) + "\n")
        subprocess.check_call(["tar", "-xzf", str(MID_TAR), "-C", str(MID_ROOT), "-T", str(lst)])
    index = existing_from_paths([ROOT / "library.csv", *sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))])
    for p in (ROOT / "files" / "scores").iterdir():
        if p.is_file(): index.add_stem(p.stem)
    used, done = set(), []
    for c, label, x in picked:
        rec = composer_record(c)
        src = MID_ROOT / x["mid"].lstrip("./")
        data = src.read_bytes()
        if data[:4] != b"MThd": continue
        title = re.sub(r"\s*[-–]\s*" + re.escape(rec["name"].split()[-1]) + r".*$", "", x["title"]).strip() or label
        ident = allocate_id(f"{rec['prefix']}_{slugify(title, 48)}", index, used)
        dest = ROOT / "files" / "scores" / f"{ident}.mid"
        if dest.exists(): continue
        dest.write_bytes(data)
        lic = "PD" if x["license"] == "publicdomain" else "CC0"
        row = {k: "" for k in CANDIDATE_COLUMNS}
        row.update({"id": ident, "composer": rec["name"], "death_year": str(rec["death"]), "title": title,
                    "mood_tags": mood_tags(title, "", "classical"), "tempo_energy": tempo_energy(title, ""),
                    "notable_excerpt": "Opening (00:00); play the score MIDI in the browser to audition.",
                    "video_use_ideas": "Underscore a short scene with the opening bars.",
                    "editable_source_url": ZENODO, "editable_format": "MIDI; MusicXML (inside PDMX archives)", "editable_license": lic,
                    "legal_notes": (f"Composer died {rec['death']}. PDMX Zenodo 10.5281/zenodo.15571083. subset:no_license_conflict; file licence "
                                    f"{x['license']} ({x['license_url']}). Zenodo compilation is CC BY 4.0; this file's own label is public domain or CC0. "
                                    f"User-uploaded MuseScore transcription. MIDI member: {x['mid']}. Fills signature gap: {label}."),
                    "local_score_path": f"files/scores/{ident}.mid", "verified": "yes", "added_by": "bulk", "source_rank": "9",
                    "source_name": "pdmx", "licence_class": "clean", "instrumentation": f"{x['n_tracks']} tracks",
                    "popularity": f"rating={float(x['rating'] or 0):.2f};ratings=0;favorites=0;views=0", "genre": "classical", "era": ""})
        done.append({k: row.get(k, "") for k in BATCH_COLUMNS}); index.add_stem(ident); print("OK", ident)
    with OUT.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=BATCH_COLUMNS, extrasaction="ignore"); w.writeheader(); w.writerows(done)
    print(f"wrote {len(done)} rows -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
