#!/usr/bin/env python3
"""Rebuild data/library.json (the Pages site data) from library.csv.

Safe to re-run after every batch expansion: output depends only on library.csv,
README.md (top picks), files on disk and, for a few hand-set fields, the previous
data/library.json.

Derived fields
  genre               CSV `genre` column > previous JSON > composer map > "classical"
  era                 CSV `era` column > composer map > death-year bucket
  has_editable_score  local_score_path exists on disk
  has_recording       local_audio_path set or release_audio_url set
  recording_status    licence class of recording_license (blank if no recording)
  score_status        licence class of editable_license (blank if no score)
  licence_status      worst of the above, + FLAGGED overrides, verified!=yes -> unverified
  legal_flags         short caveat chips (territorial term, arrangement, render, ...)
  energy              low | moderate | high | very_high, from tempo_energy
  score_files         every file in files/scores/ belonging to the row
  release_audio_*     GitHub Release asset for local_audio_path
  top_pick_rank/why   from the "Top 15 picks" table in README.md
  search_text         lowercase blob the UI searches (catalogue variants included)

Also rebuilds data/catalog.json + data/items/*.json (scripts/build_catalog.py).

Usage: python3 scripts/sync_site_data.py [--check]   (--check: report only, no write)
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "library.csv")
JSON_PATH = os.path.join(ROOT, "data", "library.json")
README_PATH = os.path.join(ROOT, "README.md")
SCORES_DIR = os.path.join(ROOT, "files", "scores")
RELEASE_BASE = "https://github.com/LaDoger/music-library/releases/download/audio-v1/"

GENRES = ["classical", "jazz", "ragtime", "blues", "folk", "world", "marches",
          "early_popular", "film_silent", "modern_cc", "other"]

# Licence classes, least to most restrictive. The site never shows a better
# badge than the worst part of the row.
SEVERITY = ["clean", "attribution", "flagged", "sharealike", "unverified"]

# Composer -> era where the death-year bucket would be wrong (e.g. Handel d.1759
# is Baroque, not Classical). Extend as batches add composers.
COMPOSER_ERA = {
    "Johann Sebastian Bach": "Baroque",
    "George Frideric Handel": "Baroque",
    "Antonio Vivaldi": "Baroque",
    "Johann Pachelbel": "Baroque",
    "Jean-Philippe Rameau": "Baroque",  # d.1764 would otherwise fall in the Classical bucket
    "Carlo Gesualdo": "Renaissance",
    "William Byrd": "Renaissance",
    "Mily Balakirev": "Romantic",
    "Wolfgang Amadeus Mozart": "Classical",
    "Joseph Haydn": "Classical",
    "Ludwig van Beethoven": "Classical / early Romantic",
    "Franz Schubert": "Romantic",
    "Antonín Dvořák": "Romantic",
    "Giuseppe Verdi": "Romantic",
}

# Rows that must not show "Clean" even though their licence strings are PD/CC0.
# Mirrors README "License rules" section 3. Keep reasons short; legal_notes has detail.
FLAGGED = {
    "holst_planets_mars": "Holst d.1934: not PD in life+100 territories",
    "holst_planets_jupiter": "Holst d.1934: not PD in life+100 territories",
    "liszt_hungarian_rhapsody_2": "Band arrangement by non-government arranger",
    "tchaikovsky_nutcracker_waltz_of_flowers": "Band arrangement; arranger status not stated",
    "offenbach_orpheus_cancan": "Retired CC PD dedication; may not hold outside US",
    "mahler_adagietto": "Retired CC PD dedication (archive item)",
}

FLAG_RULES = [
    # (chip label, regex on legal_notes + licence strings)
    ("Composer-term caveat", r"FLAG (HOLST|RACHMANINOFF|composer term|death year)"),
    ("US-gov PD (territorial)", r"PD-USGov|US Marine Band|USGov|U\.S\. federal government"),
    ("Arrangement risk", r"arrangement (copyright not confirmed|not stated)|residual risk on arrangement|arranger .* not stated|status of arrangement not stated"),
    ("Retired PD dedication", r"retired (Creative Commons|CC) (Public Domain|public-domain|PD)|licenses/publicdomain/"),
    ("Own MIDI render", r"own (FluidSynth|MIDI|synthesized)[^.]*render|virtual-piano render|not a human"),
    ("Lo-fi source", r"lo-fi|low bitrate|Acoustic 78|Acoustic, mono|Mono \(1ch\)"),
    ("Courtesy credit", r"courtesy (credit|attribution)|conservatively credit"),
]


def classify(lic):
    """Licence string -> class, or '' when there is nothing licensed."""
    s = (lic or "").strip()
    if not s:
        return ""
    low = s.lower()
    if "unverified" in low or low.startswith("other"):
        return "unverified"
    if "by-sa" in low or "by sa" in low or "share" in low or "open audio" in low or "oal" in low:
        return "sharealike"
    if "-nc" in low or " nc" in low or "all rights" in low:
        return "unverified"  # should never be in the library; surface it loudly
    if re.search(r"cc[- ]?by|attribution", low):
        return "attribution"
    if re.search(r"\bpd\b|pd-|cc0|public domain|pdm|cc-pd", low):
        return "clean"
    return "unverified"


def worst(*classes):
    present = [c for c in classes if c]
    return max(present, key=SEVERITY.index) if present else "unverified"


def era_for(composer, death_year):
    if composer in COMPOSER_ERA:
        return COMPOSER_ERA[composer]
    try:
        d = int(death_year)
    except (TypeError, ValueError):
        return "Unknown"
    if d <= 1760:
        return "Baroque"
    if d <= 1830:
        return "Classical"
    if d <= 1900:
        return "Romantic"
    if d <= 1950:
        return "Late Romantic / early 20th"
    return "Modern"


def energy_for(tempo):
    t = (tempo or "").lower()
    part = t.split("/", 1)[1] if "/" in t else t
    if re.search(r"very high|maximum|explosive|frenzied", part):
        return "very_high"
    if re.search(r"very low|\blow\b|low energy|floating|suspended|restrained|low pulse", part) and "low-mid" not in part:
        return "low"
    if re.search(r"mid-high|\bmid\b|moderate|low-mid|swelling|lilting|singing|flowing|continuous|poised|measured|buoyant|processional|rolling|gradual", part):
        return "moderate"
    if re.search(r"high|drive|relentless|brisk|bright|march|rising|building", part):
        return "high"
    return "moderate"


def catalog_variants(catalog):
    """'BWV 565' -> 'bwv 565 bwv565'; 'Op. 27 No. 2' -> '... op27 op 27 no2'."""
    c = (catalog or "").lower()
    if not c:
        return ""
    squashed = re.sub(r"[\s.]+", "", c)
    spaced = re.sub(r"([a-z])\.?\s*(\d)", r"\1 \2", c.replace(".", ". "))
    spaced = re.sub(r"\s+", " ", spaced.replace(". ", " "))
    return " ".join(sorted({c, squashed, spaced}))


def score_files_for(row):
    path = row.get("local_score_path", "")
    if not path:
        return []
    stem = os.path.splitext(os.path.basename(path))[0]
    stem = re.sub(r"-(lys|mids)$", "", stem)
    prefixes = {stem, row["id"]}
    try:
        names = sorted(os.listdir(SCORES_DIR))
    except FileNotFoundError:
        return []
    out = []
    for n in names:
        base = os.path.splitext(n)[0]
        if any(base == p or base.startswith(p + "_") or base.startswith(p + "-") for p in prefixes):
            out.append("files/scores/" + n)
    if path not in out and os.path.exists(os.path.join(ROOT, path)):
        out.insert(0, path)
    return out


def parse_top_picks():
    picks = {}
    try:
        text = open(README_PATH, encoding="utf-8").read()
    except FileNotFoundError:
        return picks
    m = re.search(r"## Top 15 picks.*?\n(\|.*?)(\n\n|\Z)", text, re.S)
    if not m:
        return picks
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].isdigit():
            picks[cells[1].strip("`")] = (int(cells[0]), cells[2])
    return picks


def load_previous():
    try:
        return {r["id"]: r for r in json.load(open(JSON_PATH, encoding="utf-8"))}
    except (FileNotFoundError, ValueError):
        return {}


def build():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8", newline="")))
    prev = load_previous()
    picks = parse_top_picks()
    out, problems = [], []

    for r in rows:
        rid = r["id"].strip()
        p = prev.get(rid, {})
        item = {k: (v or "").strip() for k, v in r.items() if k}

        genre = item.get("genre") or p.get("genre") or "classical"
        if genre not in GENRES:
            problems.append(f"{rid}: unknown genre {genre!r}")
        item["genre"] = genre
        item["era"] = item.get("era") or era_for(item["composer"], item.get("death_year"))

        score_files = score_files_for(item)
        has_score = bool(item.get("local_score_path")) and os.path.exists(os.path.join(ROOT, item["local_score_path"]))
        audio = item.get("local_audio_path", "")
        audio_abs = os.path.join(ROOT, audio) if audio else ""
        if audio:
            name = os.path.basename(audio)
            item["release_audio_name"] = name
            item["release_audio_url"] = RELEASE_BASE + name
            item["release_audio_bytes"] = os.path.getsize(audio_abs) if os.path.exists(audio_abs) else p.get("release_audio_bytes", 0)
        else:
            item["release_audio_name"] = item["release_audio_url"] = ""
            item["release_audio_bytes"] = 0
        has_rec = bool(audio or item["release_audio_url"])

        rec_status = classify(item.get("recording_license")) if has_rec else ""
        score_status = classify(item.get("editable_license")) if has_score else ""
        status = worst(rec_status, score_status)
        if rid in FLAGGED:
            status = worst(status, "flagged")
        if item.get("verified") != "yes":
            status = "unverified"

        blob = " ".join([item.get("legal_notes", ""), item.get("recording_license", ""), item.get("editable_license", "")])
        flags = [label for label, rx in FLAG_RULES if re.search(rx, blob, re.I)]
        if score_status == "sharealike" and rec_status != "sharealike":
            flags.append("ShareAlike score only")
        if rid in FLAGGED:
            flags.insert(0, FLAGGED[rid])

        preview = item.get("preview_path", "")
        if preview and not os.path.exists(os.path.join(ROOT, preview)):
            problems.append(f"{rid}: preview missing {preview}")
        if item.get("local_score_path") and not has_score:
            problems.append(f"{rid}: score missing {item['local_score_path']}")

        moods = [m.strip() for m in item.get("mood_tags", "").split(";") if m.strip()]
        rank, why = picks.get(rid, (0, ""))

        item.update({
            "preview_url": preview,
            "score_url": item.get("local_score_path", "") if has_score else "",
            "score_files": score_files if has_score else [],
            "mood_tags_list": moods,
            "has_editable_score": has_score,
            "has_recording": has_rec,
            "recording_status": rec_status,
            "score_status": score_status,
            "licence_status": status,
            "legal_flags": flags,
            "energy": energy_for(item.get("tempo_energy")),
            "top_pick_rank": rank,
            "top_pick_why": why,
        })
        item["search_text"] = " ".join([
            item["title"], item["composer"], item.get("catalog", ""), catalog_variants(item.get("catalog")),
            item.get("movement", ""), rid.replace("_", " "), " ".join(moods), genre, item["era"],
            item.get("recording_performer", ""),
        ]).lower()
        out.append(item)

    missing_picks = sorted(set(picks) - {o["id"] for o in out})
    if missing_picks:
        problems.append(f"top picks not in CSV: {missing_picks}")
    return out, problems


def main():
    out, problems = build()
    check = "--check" in sys.argv
    if not check:
        tmp = JSON_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, JSON_PATH)
    from collections import Counter
    print(f"{'checked' if check else 'wrote'} {len(out)} rows -> {os.path.relpath(JSON_PATH, ROOT)}")
    print("licence_status:", dict(Counter(o["licence_status"] for o in out)))
    print("genre:", dict(Counter(o["genre"] for o in out)), "era:", dict(Counter(o["era"] for o in out)))
    print("energy:", dict(Counter(o["energy"] for o in out)))
    print("scores:", sum(o["has_editable_score"] for o in out), "recordings:", sum(o["has_recording"] for o in out),
          "top picks:", sum(1 for o in out if o["top_pick_rank"]))
    for p in problems:
        print("WARN", p)
    if not check:
        # agent-facing data/catalog.json + data/items/*.json derive from library.json
        import build_catalog
        if build_catalog.main():
            problems.append("build_catalog warnings")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
