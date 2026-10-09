#!/usr/bin/env python3
"""Resolve a direct, browser-streamable URL for each recording -> data/cache/stream_audio.json.

Network step, run by hand after rows with recordings are added; sync_site_data.py only
reads the cache and sets `stream_audio_url` on matching rows.

  Wikimedia Commons  videoinfo.derivatives of the File: page. Prefer the MP3 transcode
                     (plays in every browser), else the original if it is audio/*.
  Internet Archive   /metadata/<item>: match the local file by byte size (or name), then
                     prefer its "VBR MP3" derivative.

A stream is accepted only when its duration is within 3 s of the local file (ffprobe), so
a stream never silently differs from the recording the row describes. Rows without a local
file are accepted on the source match alone. Each URL must answer a ranged GET.
Rejections are printed and not cached.

Usage: python3 scripts/resolve_streams.py [--refresh] [--only <id>]
"""
import csv
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "library.csv")
CACHE = os.path.join(ROOT, "data", "cache", "stream_audio.json")
UA = "LaDoger-music-library/1.0 (https://github.com/LaDoger/music-library)"
COMMONS = "https://commons.wikimedia.org/w/api.php"
TOLERANCE = 3.0


def fetch_json(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
                return json.load(r)
        except Exception:  # noqa: BLE001 - retry any network error
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def clean(u):
    return re.sub(r"\?utm_[^#]*$", "", u or "")


def reachable(url):
    """Ranged GET (follows redirects): the browser <audio> needs 200/206 and a body."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-1023"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status in (200, 206) and len(r.read(1024)) > 0
    except Exception:  # noqa: BLE001
        return False


def local_duration(path):
    if not path or not os.path.exists(path):
        return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return float(out)
    except (ValueError, subprocess.SubprocessError):
        return None


def commons(src):
    title = urllib.parse.unquote(src.split("/wiki/", 1)[1]).replace("_", " ")
    q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title,
                                "prop": "videoinfo", "viprop": "url|size|mime|derivatives"})
    page = next(iter(fetch_json(COMMONS + "?" + q)["query"]["pages"].values()))
    info = (page.get("videoinfo") or [None])[0]
    if not info:
        return None
    derivs = info.get("derivatives") or []
    mp3 = [d for d in derivs if d.get("type", "").startswith("audio/mpeg")]
    audio = [d for d in derivs if d.get("type", "").startswith("audio/")]
    orig_is_audio = info.get("mime", "").startswith("audio/") or (
        info.get("mime") == "application/ogg" and not info.get("width"))
    if mp3:
        url, mime = mp3[0]["src"], "audio/mpeg"
    elif orig_is_audio:
        url, mime = info["url"], info["mime"]
    elif audio:
        url, mime = audio[0]["src"], audio[0]["type"]
    else:
        return None
    return {"stream_audio_url": clean(url), "stream_audio_mime": mime.split(";")[0],
            "stream_audio_original": clean(info["url"]) if orig_is_audio else "",
            "duration": round(info.get("duration") or 0, 2), "via": "commons"}


IA_CACHE = {}


def seconds(v):
    """archive.org lengths are '512.3' or 'mm:ss' / 'h:mm:ss'."""
    total = 0.0
    for part in str(v or 0).split(":"):
        total = total * 60 + float(part)
    return total


def archive(src, local):
    item = src.rstrip("/").split("/details/", 1)[1].split("/")[0]
    if item not in IA_CACHE:
        IA_CACHE[item] = fetch_json(f"https://archive.org/metadata/{urllib.parse.quote(item)}")
    files = IA_CACHE[item].get("files", [])
    size = os.path.getsize(local) if local and os.path.exists(local) else None
    orig = [f for f in files if size and f.get("size") and int(f["size"]) == size]
    if not orig:
        return None
    name = orig[0]["name"]
    mp3 = [f for f in files if f.get("original") == name and f.get("format", "").endswith("MP3")]
    pick = mp3[0] if mp3 else orig[0]
    base = f"https://archive.org/download/{urllib.parse.quote(item)}/"
    return {"stream_audio_url": base + urllib.parse.quote(pick["name"]),
            "stream_audio_mime": "audio/mpeg" if mp3 else "audio/flac",
            "stream_audio_original": base + urllib.parse.quote(name),
            "duration": round(seconds(pick.get("length") or orig[0].get("length")), 2), "via": "archive.org"}


def main():
    refresh = "--refresh" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    for r in csv.DictReader(open(CSV_PATH, encoding="utf-8", newline="")):
        rid, src = r["id"].strip(), (r.get("recording_source_url") or "").strip()
        if (only and rid != only) or (rid in cache and not refresh) or not src:
            continue
        local = os.path.join(ROOT, r["local_audio_path"]) if r.get("local_audio_path") else ""
        try:
            if "commons.wikimedia.org/wiki/" in src:
                res = commons(src)
            elif "archive.org/details/" in src:
                res = archive(src, local)
            else:
                res = None
        except Exception as e:  # noqa: BLE001
            print(f"ERR  {rid}: {e}")
            continue
        if not res:
            print(f"--   {rid}: no streamable source")
            continue
        if not reachable(res["stream_audio_url"]):
            if res.get("stream_audio_original") and reachable(res["stream_audio_original"]):
                res["stream_audio_url"] = res["stream_audio_original"]
            else:
                print(f"DEAD {rid}: {res['stream_audio_url']}")
                continue
        ld = local_duration(local)
        if ld and res["duration"] and abs(ld - res["duration"]) > TOLERANCE:
            print(f"SKIP {rid}: duration {res['duration']}s vs local {ld:.1f}s")
            continue
        res["local_duration"] = round(ld, 2) if ld else None
        cache[rid] = res
        print(f"OK   {rid}: {res['via']} {res['stream_audio_mime']} {res['duration']}s")
        time.sleep(0.2)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(cache.items())), f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, CACHE)
    print(f"{len(cache)} streams in {os.path.relpath(CACHE, ROOT)}")


if __name__ == "__main__":
    main()
