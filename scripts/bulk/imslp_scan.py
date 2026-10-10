#!/usr/bin/env python3
"""Polite IMSLP scan: list MIDI / MusicXML files whose own Copyright field is PD / CC0 / CC BY.

Read-only: uses the public MediaWiki API (categorymembers + parse wikitext) at ~1 request/s and
never requests a file URL (downloads sit behind a captcha bot check, which this does NOT bypass).
Output is a manual-download candidate list, one CSV per run.

  python3 scripts/bulk/imslp_scan.py "Ravel, Maurice" "Debussy, Claude" ... [--max-pages 400]
Cache: .tmp/depth1/imslp/<page>.json (resumable).
"""
import argparse, csv, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".tmp" / "depth1" / "imslp2"
UA = {"User-Agent": "music-library-depth1/1.0 (LaDoger/music-library; polite scan, 1 req/s)"}
EXT = re.compile(r"\.(mid|midi|mxl|xml|musicxml|mscz)$", re.I)
OK = re.compile(r"^(Public Domain|Creative Commons Zero.*|Creative Commons Attribution(?: [\d.]+)?)$", re.I)


def api(**p):
    p["format"] = "json"
    url = "https://imslp.org/api.php?" + urllib.parse.urlencode(p)
    for k in range(4):
        try:
            time.sleep(1.0)
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception:  # noqa: BLE001
            time.sleep(4 * (k + 1))
    return None  # failure: callers must not cache it


def category(name, cap):
    titles, cont = [], {}
    while len(titles) < cap:
        d = api(action="query", list="categorymembers", cmtitle="Category:" + name, cmlimit=500, cmnamespace=0, **cont) or {}
        titles += [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
        if "continue" not in d:
            break
        cont = d["continue"]
    return titles[:cap]


def files(title):
    safe = re.sub(r"[^\w.-]+", "_", title)[:120]
    f = CACHE / (safe + ".json")
    if f.is_file():
        return json.loads(f.read_text(encoding="utf-8"))
    d = api(action="parse", page=title, prop="wikitext")
    if d is None:
        return []
    text = d.get("parse", {}).get("wikitext", {}).get("*", "")
    out = []
    for block in re.split(r"\{\{#fte:imslp(?:file|audio)", text)[1:]:
        block = block.split("}}")[0] if "|Copyright=" not in block else block
        cp = re.search(r"\|Copyright=([^\n|]*)", block)
        names = re.findall(r"\|File Name \d+=([^\n|]*)", block)
        descs = re.findall(r"\|File Description \d+=([^\n|]*)", block)
        for i, n in enumerate(names):
            if EXT.search(n.strip()):
                out.append({"file": n.strip(), "desc": (descs[i] if i < len(descs) else "").strip(), "copyright": (cp.group(1).strip() if cp else "")})
    CACHE.mkdir(parents=True, exist_ok=True)  # only successful parses are cached
    f.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("categories", nargs="+")
    ap.add_argument("--max-pages", type=int, default=400)
    ap.add_argument("--out", default=str(ROOT / ".tmp" / "depth1" / "imslp_candidates.csv"))
    args = ap.parse_args()
    rows = []
    for cat in args.categories:
        titles = category(cat, args.max_pages)
        print(cat, len(titles), "works", flush=True)
        for t in titles:
            for fl in files(t):
                usable = "yes" if OK.match(fl["copyright"]) and "NonCommercial" not in fl["copyright"] else "no"
                rows.append({"composer_category": cat, "work": t, **fl, "usable": usable,
                             "page_url": "https://imslp.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"))})
        with open(args.out, "w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=["composer_category", "work", "file", "desc", "copyright", "usable", "page_url"])
            w.writeheader(); w.writerows(rows)
    print(len(rows), "midi/xml files;", sum(r["usable"] == "yes" for r in rows), "usable-licence")


main()
