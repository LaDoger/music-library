#!/usr/bin/env python3
"""Download Commons originals listed in a TSV (id<TAB>File:title) into files/audio/<id>.<ext>.
Writes a TSV of id, title, url, page, mime, local path to stdout."""
import sys, json, urllib.request, urllib.parse, os, time
UA = {"User-Agent": "MusicLibraryResearch/1.0"}
API = "https://commons.wikimedia.org/w/api.php"
root = sys.argv[2] if len(sys.argv) > 2 else "/workspace/music/library"
for line in open(sys.argv[1], encoding="utf-8"):
    if not line.strip(): continue
    rid, title = line.rstrip("\n").split("\t")
    q = urllib.parse.urlencode(dict(action="query", titles=title, prop="imageinfo", iiprop="url|mime", format="json"))
    p = next(iter(json.load(urllib.request.urlopen(urllib.request.Request(API + "?" + q, headers=UA), timeout=30))["query"]["pages"].values()))
    ii = p["imageinfo"][0]
    ext = os.path.splitext(urllib.parse.unquote(ii["url"].split("?")[0]))[1].lower()
    rel = f"files/audio/{rid}{ext}"; dst = os.path.join(root, rel)
    if not os.path.exists(dst) or os.path.getsize(dst) == 0:
        req = urllib.request.Request(ii["url"].split("?")[0], headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r, open(dst + ".part", "wb") as f:
            while chunk := r.read(1 << 20): f.write(chunk)
        os.replace(dst + ".part", dst); time.sleep(1)
    print("\t".join([rid, title, ii["url"].split("?")[0], ii["descriptionurl"], ii["mime"], rel]), flush=True)
