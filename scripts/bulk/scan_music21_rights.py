#!/usr/bin/env python3
"""Scan every MusicXML file in the music21 corpus for its embedded <rights> line (depth run 1).

Writes .tmp/depth1/music21_rights.csv (path, composer_dir, rights). Read-only scan, polite
(4 workers). A file is only importable if its own rights line says PD / CC0 / CC BY.
  python3 scripts/bulk/scan_music21_rights.py
"""
import csv, json, re, sys, urllib.request, zipfile, io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".tmp" / "depth1" / "music21_rights.csv"
UA = {"User-Agent": "music-library-depth1/1.0"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def rights(path):
    try:
        data = get("https://raw.githubusercontent.com/cuthbertLab/music21/master/" + path)
    except Exception as exc:  # noqa: BLE001
        return f"ERR {exc}"
    try:
        if data[:2] == b"PK":
            z = zipfile.ZipFile(io.BytesIO(data))
            text = " ".join(z.read(m).decode("utf8", "replace") for m in z.namelist() if not m.startswith("META") and m.endswith((".xml", ".musicxml")))
        else:
            text = data.decode("utf8", "replace")
    except Exception as exc:  # noqa: BLE001
        return f"ERR {exc}"
    return " | ".join(x.strip() for x in re.findall(r"<rights[^>]*>([^<]*)", text))[:300]


def main():
    tree = json.loads(get("https://api.github.com/repos/cuthbertLab/music21/git/trees/master?recursive=1"))["tree"]
    files = [t["path"] for t in tree if t["path"].startswith("music21/corpus/") and t["path"].lower().endswith((".mxl", ".xml", ".musicxml"))]
    print(len(files), "corpus xml files", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(4) as ex, OUT.open("w", newline="", encoding="utf-8") as h:
        w = csv.writer(h)
        w.writerow(["path", "composer_dir", "rights"])
        for p, r in zip(files, ex.map(rights, files)):
            w.writerow([p, p.split("/")[2], r])
            h.flush()


main()
