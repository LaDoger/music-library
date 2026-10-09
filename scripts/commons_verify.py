#!/usr/bin/env python3
"""Fetch Commons file page wikitext + license metadata for each title (one per line on stdin).
Prints license templates, author/source/date fields, direct URL. Usage: commons_verify.py < titles.txt"""
import sys, json, urllib.request, urllib.parse, re
UA = {"User-Agent": "MusicLibraryResearch/1.0"}
API = "https://commons.wikimedia.org/w/api.php"
def get(params):
    params.update(format="json")
    return json.load(urllib.request.urlopen(urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA), timeout=30))
for t in [l.strip() for l in sys.stdin if l.strip()]:
    r = get(dict(action="query", titles=t, prop="revisions|imageinfo", rvprop="content", rvslots="main",
                 iiprop="url|size|mime|extmetadata"))
    p = next(iter(r["query"]["pages"].values()))
    if "missing" in p: print("MISSING", t); continue
    wt = p["revisions"][0]["slots"]["main"]["*"]; ii = p["imageinfo"][0]; m = ii["extmetadata"]
    tmpl = sorted(set(x.strip() for x in re.findall(r"\{\{\s*([^|}\n]+)", wt)))
    lic = [x for x in tmpl if re.search(r"(?i)pd|cc|public|gfdl|oal|license|self|musopen|usgov|military|air force|marine|navy|army|attrib|lic", x)]
    fields = {k: re.sub(r"\s+", " ", v)[:200] for k, v in re.findall(r"\|\s*(author|source|date|performer|description|permission)\s*=\s*([^\n]*)", wt, re.I)}
    print("=" * 100); print(t); print("  url:", ii["url"]); print("  page:", ii["descriptionurl"]); print("  mime/size:", ii["mime"], ii["size"])
    print("  LicenseShortName:", m.get("LicenseShortName", {}).get("value"), "| UsageTerms:", re.sub("<[^>]+>", "", m.get("UsageTerms", {}).get("value", ""))[:100])
    print("  license templates:", lic)
    for k, v in fields.items(): print(f"  {k}: {v}")
