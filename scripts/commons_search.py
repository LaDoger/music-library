#!/usr/bin/env python3
"""Search Wikimedia Commons files and print license metadata from each file page.
Usage: commons_search.py "query" [limit]"""
import sys, json, urllib.request, urllib.parse, re
UA = {"User-Agent": "MusicLibraryResearch/1.0 (personal research; contact: none)"}
API = "https://commons.wikimedia.org/w/api.php"
def api(params):
    params.update(format="json")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))
def strip(s): return re.sub(r"<[^>]+>", "", s or "").strip()[:120]
q = sys.argv[1]; lim = sys.argv[2] if len(sys.argv) > 2 else "15"
r = api(dict(action="query", generator="search", gsrsearch=q, gsrnamespace=6, gsrlimit=lim,
             prop="imageinfo", iiprop="url|size|mime|extmetadata"))
for p in sorted(r.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
    ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
    g = lambda k: strip(m.get(k, {}).get("value"))
    if not ii["mime"].startswith(("audio", "application/ogg", "video/webm", "audio/midi")) and "midi" not in ii["mime"]:
        continue
    print(f'{p["title"]}\n   {ii["mime"]} {ii["size"]//1024}KB lic={g("LicenseShortName")} | artist={g("Artist")}\n   desc={g("ImageDescription")[:100]}\n   page={ii["descriptionurl"]}')
