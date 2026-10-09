#!/usr/bin/env python3
"""Fetch composer life dates + an optional PD/CC0 portrait into data/cache/composer_meta.json.

Network step, run by hand when composers are added (sync_site_data.py only reads the
cache, so the site build stays offline and deterministic).

  Wikidata  wbsearchentities(name) -> candidate whose P570 death year equals the CSV
            death_year (and is a human, Q5). Takes P569 birth, P570 death, P18 image.
  Commons   imageinfo/extmetadata of the P18 file. The portrait is kept only when the
            file licence is Public domain or CC0 (LicenseShortName / License); anything
            else -> portrait_url null and the site shows a monogram.

Existing cache entries are kept unless --refresh is given.

Usage: python3 scripts/fetch_composer_meta.py [--refresh] [--only "Name"]
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "library.csv")
CACHE = os.path.join(ROOT, "data", "cache", "composer_meta.json")
UA = "LaDoger-music-library/1.0 (https://github.com/LaDoger/music-library)"
WD = "https://www.wikidata.org/w/api.php"
COMMONS = "https://commons.wikimedia.org/w/api.php"


def get(url, params):
    q = url + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(q, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - retry any network error
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def year(claims, prop):
    for c in claims.get(prop, []):
        v = c.get("mainsnak", {}).get("datavalue", {}).get("value", {})
        m = re.match(r"[+-](\d{4})", v.get("time", ""))
        if m:
            return int(m.group(1))
    return None


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def portrait(filename):
    data = get(COMMONS, {"action": "query", "format": "json", "titles": "File:" + filename,
                         "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 320})
    page = next(iter(data["query"]["pages"].values()))
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata", {})
    short = strip_html(meta.get("LicenseShortName", {}).get("value"))
    lic = strip_html(meta.get("License", {}).get("value")).lower()
    ok = short.lower() in ("public domain", "cc0") or lic in ("pd", "cc0")
    if meta.get("NonFree", {}).get("value") in ("true", True):
        ok = False
    return {
        "portrait_url": info.get("thumburl") if ok else None,
        "portrait_file_page": info.get("descriptionurl") or "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(filename.replace(" ", "_")),
        "portrait_licence": short or lic or "unknown",
        "portrait_ok": ok,
        "portrait_artist": strip_html(meta.get("Artist", {}).get("value"))[:160],
    }


def lookup(name, death_year):
    found = get(WD, {"action": "wbsearchentities", "format": "json", "language": "en",
                     "type": "item", "limit": 7, "search": name})
    ids = [s["id"] for s in found.get("search", [])]
    if not ids:
        return None
    ents = get(WD, {"action": "wbgetentities", "format": "json", "ids": "|".join(ids), "props": "claims"})["entities"]
    for qid in ids:
        claims = ents[qid].get("claims", {})
        humans = [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for c in claims.get("P31", [])]
        if "Q5" not in humans:
            continue
        d = year(claims, "P570")
        if death_year and d != death_year:
            continue
        img = None
        for c in claims.get("P18", []):
            img = c["mainsnak"].get("datavalue", {}).get("value")
            if img:
                break
        out = {"wikidata": qid, "birth_year": year(claims, "P569"), "death_year": d, "image": img}
        if img:
            out.update(portrait(img))
        return out
    return None


def main():
    refresh = "--refresh" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    composers = {}
    for r in csv.DictReader(open(CSV_PATH, encoding="utf-8", newline="")):
        name = (r.get("composer") or "").strip()
        if name:
            try:
                composers.setdefault(name, int(r.get("death_year") or 0) or None)
            except ValueError:
                composers.setdefault(name, None)
    for name, dy in sorted(composers.items()):
        if only and name != only:
            continue
        if name in cache and not refresh:
            continue
        # "Johann Strauss I" -> search without the regnal suffix as well
        res = lookup(name, dy) or lookup(re.sub(r"\s+(I|II|III|Jr\.?|Sr\.?)$", "", name), dy)
        cache[name] = res or {"wikidata": None, "birth_year": None, "death_year": dy, "image": None,
                              "portrait_url": None, "portrait_ok": False}
        r = cache[name]
        print(f"{name}: {r.get('wikidata')} {r.get('birth_year')}-{r.get('death_year')} "
              f"portrait={'yes' if r.get('portrait_url') else 'no'} ({r.get('portrait_licence', '-')})")
        time.sleep(0.3)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(cache.items())), f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, CACHE)
    print(f"{len(cache)} composers in {os.path.relpath(CACHE, ROOT)}")


if __name__ == "__main__":
    main()
