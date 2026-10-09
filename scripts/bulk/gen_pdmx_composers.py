#!/usr/bin/env python3
"""Generate scripts/bulk/pdmx_composers_wikidata.json: extra PDMX composers with life dates.

Scale run 3 (2026-10-09). The hand list in schema.py (_RAW) covers the famous names.
This script finds the PDMX composer_name values that the hand list does not match,
among rows that already pass the PDMX licence + quality filter, and looks each one up
in Wikidata. Life dates come from Wikidata only (P569 / P570), never from a guess.

A name becomes an entry only when all of these hold:
  * it has at least --min-rows PDMX rows, and at least two words after cleaning
    (a bare surname such as "Marshall" or "Carolan" is too ambiguous);
  * exactly one Wikidata human (P31 Q5) whose occupation is a kind of musician
    (P106 / P279* Q639669 or Q36834) has that exact label or alias;
  * that person has a death date (unknown death = not imported);
  * any years written into the PDMX credit ("(1665-1747)", "1540 - 1623") agree with
    Wikidata within two years.

schema.py loads the JSON. Generated composers are matched on the full name only
(no surname or fuzzy match), so "Thomas Morley" never catches "Morley" or "Thomas".
Death <= 1929 is clean, 1930-1955 is flagged and not downloaded, > 1955 is excluded.

Usage: python3 scripts/bulk/gen_pdmx_composers.py [--min-rows 3] [--csv .tmp/pdmx/PDMX.csv]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

os.environ["MUSICLIB_NO_GENERATED_COMPOSERS"] = "1"  # match against the hand list only
sys.path.insert(0, str(Path(__file__).resolve().parent))

import harvest_pdmx_sample as pdmx  # noqa: E402
from schema import COMPOSERS, EXCLUDED_CANONS, catalog_from_text, fold, match_composer, slugify  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "pdmx_composers_wikidata.json"
SPARQL = "https://query.wikidata.org/sparql"
UA = "LaDoger-music-library/1.0 (https://github.com/LaDoger/music-library) gen_pdmx_composers"
LANGS = ("en", "de", "fr", "it", "es", "nl", "pt", "pl", "cs", "sv", "da", "nb", "hu", "la")

# Reviewed by hand after generation: Wikidata has one musician with the name, but the
# PDMX uploads are by someone else. Kept out (not imported) until identified properly.
DENY = {
    "John Mason": "Wikidata hit is the English hymn writer (1646-1694); PDMX credits are "
                  "19th-century Scottish fiddle tunes (Wild Rose of the Mountain).",
}

NOT_A_PERSON = re.compile(
    r"\b(trad|traditional|anon|anonymous|unknown|unattributed|unbekannt|composer|arr|arranged|"
    r"arrangement|transcribed|after|composed|realizations?|hand|band|bands|book|ms|manuscript|"
    r"collection|various|music|hymn|tune|playback|feat|ft|and|und|et|the|by|von der)\b",
    re.I,
)


def clean_name(raw: str) -> tuple[str, list[int]]:
    """'William Byrd1540 - 1623' -> ('William Byrd', [1540, 1623]); '' when not a plain name."""
    text = (raw or "").strip()
    years = [int(y) for y in re.findall(r"(1[0-9]{3})", text)]
    text = re.sub(r"[\[(][^\])]*[\])]", " ", text)          # (1665-1747), [1665-1738]
    text = re.sub(r"\bc\.\s*", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)           # Byrd1540
    text = re.sub(r"\d{3,4}", " ", text)
    text = re.sub(r"\s*[-–—/]\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" ,.;:")
    if not text or NOT_A_PERSON.search(text) or re.search(r"[^\w\s.'\-]", text, re.U):
        return "", years
    words = [w for w in text.split() if re.search(r"[A-Za-zÀ-ž]{2,}", w)]
    if len(words) < 2 or len(text) > 48 or text.islower():
        return "", years
    return text, years


def unmatched_names(csv_path: Path) -> tuple[Counter, dict]:
    counts: Counter = Counter()
    raw_forms: dict[str, Counter] = defaultdict(Counter)
    years: dict[str, list] = defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            ok, _label, _klass = pdmx._licence_ok(row)
            if not ok:
                continue
            title = row.get("title") or row.get("song_name") or ""
            if not pdmx._passes_quality(row, catalog_from_text(title)):
                continue
            raw = (row.get("composer_name") or "").strip()
            if not raw or raw.upper() == "NA" or match_composer(raw):
                continue
            name, ys = clean_name(raw)
            if not name:
                continue
            counts[name] += 1
            raw_forms[name][raw] += 1
            years[name].extend(ys)
    return counts, {"raw": raw_forms, "years": years}


def _sparql(query: str) -> dict:
    data = urllib.parse.urlencode({"query": query, "format": "json"}).encode()
    for attempt in range(5):
        request = urllib.request.Request(SPARQL, data=data, headers={
            "User-Agent": UA, "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except Exception as exc:  # noqa: BLE001 — retry with backoff (429 / 5xx / timeouts)
            wait = 5 * (attempt + 1)
            print(f"  sparql retry {attempt + 1} in {wait}s: {exc}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("Wikidata SPARQL failed 5 times")


def lookup(names: list[str]) -> dict[str, dict[str, dict]]:
    """name -> {qid: {label, birth, death}} for musician humans with that exact label/alias."""
    def lit(value: str) -> str:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    values = " ".join(f"({lit(n)} {lit(n)}@{lang})" for n in names for lang in LANGS)
    query = f"""
SELECT ?name ?p ?pLabel ?birth ?death WHERE {{
  VALUES (?name ?l) {{ {values} }}
  ?p rdfs:label|skos:altLabel ?l .
  ?p wdt:P31 wd:Q5 .
  FILTER EXISTS {{ ?p wdt:P106/wdt:P279* ?occ . VALUES ?occ {{ wd:Q639669 wd:Q36834 }} }}
  OPTIONAL {{ ?p wdt:P569 ?birth }}
  OPTIONAL {{ ?p wdt:P570 ?death }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,de,fr,it,es,nl". }}
}}"""
    out: dict[str, dict[str, dict]] = defaultdict(dict)
    for b in _sparql(query)["results"]["bindings"]:
        name = b["name"]["value"]
        qid = b["p"]["value"].rsplit("/", 1)[-1]
        rec = out[name].setdefault(qid, {"label": b.get("pLabel", {}).get("value", name),
                                         "births": set(), "deaths": set()})
        for key, field in (("birth", "births"), ("death", "deaths")):
            match = re.match(r"-?(\d{3,4})", b.get(key, {}).get("value", "").lstrip("+"))
            if match:
                rec[field].add(int(match.group(1)))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--csv", type=Path, default=ROOT / ".tmp" / "pdmx" / "PDMX.csv")
    parser.add_argument("--min-rows", type=int, default=3)
    parser.add_argument("--batch", type=int, default=40)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    counts, extra = unmatched_names(args.csv)
    names = [n for n, c in counts.most_common() if c >= args.min_rows]
    print(f"{len(counts)} cleaned unmatched names; {len(names)} with >= {args.min_rows} rows")

    found: dict[str, dict] = {}
    for i in range(0, len(names), args.batch):
        found.update(lookup(names[i:i + args.batch]))
        print(f"  looked up {min(i + args.batch, len(names))}/{len(names)}; hits so far {len(found)}")
        time.sleep(1.0)

    hand_prefixes = {rec["prefix"] for rec in COMPOSERS.values()}
    entries, skipped = {}, Counter()
    skip_log = []
    for name in names:
        hits = found.get(name) or {}
        if name in DENY:
            skipped["denied"] += 1
            skip_log.append({"name": name, "why": DENY[name], "qids": sorted(hits)})
            continue
        if not hits:
            skipped["no-wikidata-musician"] += 1
            continue
        if len(hits) > 1:
            skipped["ambiguous"] += 1
            skip_log.append({"name": name, "why": "ambiguous", "qids": sorted(hits)})
            continue
        qid, rec = next(iter(hits.items()))
        if not rec["deaths"]:
            skipped["no-death-date"] += 1
            skip_log.append({"name": name, "why": "no death date", "qids": [qid]})
            continue
        death, birth = max(rec["deaths"]), (min(rec["births"]) if rec["births"] else None)
        written = extra["years"].get(name) or []
        if written and not any(abs(y - death) <= 2 or (birth and abs(y - birth) <= 2) for y in written):
            skipped["year-mismatch"] += 1
            skip_log.append({"name": name, "why": f"credit years {sorted(set(written))} vs {birth}-{death}", "qids": [qid]})
            continue
        canon = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", fold(rec["label"]))).strip()
        if canon in COMPOSERS or canon in EXCLUDED_CANONS or match_composer(rec["label"]):
            skipped["already-in-hand-list"] += 1
            continue
        alias = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", fold(name))).strip()
        if qid in {e["wikidata"] for e in entries.values()}:
            entry = next(e for e in entries.values() if e["wikidata"] == qid)
            if alias not in entry["aliases"] and alias != entry["canon"]:
                entry["aliases"].append(alias)
            entry["pdmx_rows"] += counts[name]
            continue
        last = slugify(canon.split()[-1], 18)
        prefix = last if last not in hand_prefixes else slugify(canon, 24).replace("_", "")
        while prefix in hand_prefixes:
            prefix += "x"
        hand_prefixes.add(prefix)
        entries[canon] = {
            "canon": canon,
            "name": rec["label"],
            "birth": birth,
            "death": death,
            "prefix": prefix,
            "wikidata": qid,
            "aliases": [alias] if alias != canon else [],
            "pdmx_rows": counts[name],
        }
    rows = sorted(entries.values(), key=lambda e: e["canon"])
    payload = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": "Wikidata SPARQL (P31 Q5, P106/P279* musician or composer, P569/P570); "
                  "names = PDMX composer_name values not matched by the schema.py hand list",
        "min_rows": args.min_rows,
        "composers": rows,
        "skipped": skip_log,
    }
    args.out.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    deaths = Counter("<=1929" if e["death"] <= 1929 else "1930-1955" if e["death"] <= 1955 else ">1955" for e in rows)
    print(f"entries {len(rows)} {dict(deaths)}; skipped {dict(skipped)}")
    print(f"wrote {args.out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
