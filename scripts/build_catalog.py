#!/usr/bin/env python3
"""Build the agent-facing catalogue from data/library.json.

Outputs (all committed, served by GitHub Pages):
  data/catalog.json       compact index: one small record per piece + absolute URLs
  data/items/<id>.json    full record per piece (library.json row + URLs, render
                          hints and a ready-to-paste credit line)
  data/index/manifest.json + data/index/part-NNN.json
                          slim site index (columnar rows, relative URLs) in
                          chunks of <= SHARD_BYTES; the UI loads these, then
                          fetches data/items/<id>.json when a piece is opened
  (data/composers.json is written by sync_site_data.py; catalog.json links to it)

Run after scripts/sync_site_data.py (which calls this automatically). Idempotent:
output depends only on data/library.json and files in files/scores/.

Usage: python3 scripts/build_catalog.py [--check]   (--check: report only, no write)
"""
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_PATH = os.path.join(ROOT, "data", "library.json")
CATALOG_PATH = os.path.join(ROOT, "data", "catalog.json")
INDEX_DIR = os.path.join(ROOT, "data", "index")
SHARD_BYTES = 280_000
# Columns of the slim site index. Booleans are 0/1, moods ';'-joined, empty = "".
INDEX_FIELDS = [
    "id", "composer", "title", "catalog", "movement", "genre", "era", "mood_tags", "energy",
    "licence_status", "recording_status", "score_status", "verified", "has_editable_score",
    "has_recording", "editors_pick_rank", "death_year", "preview_url", "midi_play_url",
    "stream_audio_url", "release_audio_url", "video_use_ideas", "catalog_variants",
]
ITEMS_DIR = os.path.join(ROOT, "data", "items")

PAGES_BASE = "https://ladoger.github.io/music-library/"
REPO_URL = "https://github.com/LaDoger/music-library"
RELEASE_URL = REPO_URL + "/releases/tag/audio-v1"
SCHEMA_VERSION = 3  # 2: editors_pick_rank replaces top_pick_rank; composer + stream fields. 3: stream_synth_url removed (no synth audio)

LICENCE_MEANING = {
    "clean": "PD / CC0 / PDM / US-gov recording and score. Commercial use, no credit needed (courtesy credit still listed where the source asks).",
    "attribution": "CC BY somewhere in the row. Commercial use OK with the credit line in the post / video description.",
    "sharealike": "CC BY-SA or OAL somewhere in the row. Remixes may have to carry the same licence. Check recording_status vs score_status: often only one part is affected.",
    "flagged": "Known caveat (territorial term, arrangement, retired PD dedication). Read legal_notes before publishing.",
    "unverified": "Rights not confirmed from the source page. Do not publish without checking.",
}

# Rows whose only MIDI lives inside a shared zip: which member to render.
MIDI_MEMBERS = {
    "dvorak_new_world_largo": "Mvt2_Largo.mid",
    "dvorak_new_world_finale": "Mvt4_conFuoco.mid",
    "mussorgsky_pictures_promenade": "promenade-1.mid",
    "mussorgsky_pictures_baba_yaga": "baba.mid",
    "mussorgsky_pictures_great_gate_kiev": "great-gate.mid",
}


def url(rel):
    return PAGES_BASE + rel if rel else ""


def render_source(item, problems):
    """Pick the MIDI the CLI renders: a plain .mid, else a member of a *mid*.zip."""
    files = item.get("score_files") or []
    mids = [f for f in files if f.lower().endswith((".mid", ".midi"))]
    if mids:
        return {"file": mids[0], "url": url(mids[0]), "zip_member": ""}
    zips = [f for f in files if f.lower().endswith(".zip") and "mid" in os.path.basename(f).lower()]
    if not zips:
        return None
    member = MIDI_MEMBERS.get(item["id"], "")
    path = os.path.join(ROOT, zips[0])
    if os.path.exists(path):
        names = zipfile.ZipFile(path).namelist()
        if member and member not in names:
            problems.append(f"{item['id']}: zip member {member!r} not in {zips[0]}")
            member = ""
    if not member:
        problems.append(f"{item['id']}: MIDI only inside {zips[0]}; add it to MIDI_MEMBERS")
    return {"file": zips[0], "url": url(zips[0]), "zip_member": member}


def credit_text(item):
    """Plain-text credit for a video description. Lists every part that is used."""
    work = f"{item['composer']}: {item['title']}"
    if item.get("catalog"):
        work += f", {item['catalog']}"
    lines = [work + " (composition public domain)."]
    if item.get("has_recording"):
        perf = item.get("recording_performer") or "performer not named"
        lines.append(f"Recording: {perf}. Licence: {item.get('recording_license') or 'see source'}. "
                     f"Source: {item.get('recording_source_url') or item.get('release_audio_url')}")
    if item.get("has_editable_score"):
        lines.append(f"Score edition: {item.get('editable_source_url') or 'see repo'}. "
                     f"Licence: {item.get('editable_license') or 'see source'}.")
    return "\n".join(lines)


def build():
    rows = json.load(open(LIB_PATH, encoding="utf-8"))
    index, items, problems = [], {}, []
    for r in rows:
        rid = r["id"]
        render = render_source(r, problems) if r.get("has_editable_score") else None
        item_rel = f"data/items/{rid}.json"
        index.append({
            "id": rid,
            "composer": r["composer"],
            "composer_slug": r.get("composer_slug", ""),
            "composer_sort": r.get("composer_sort", ""),
            "title": r["title"],
            "catalog": r.get("catalog", ""),
            "movement": r.get("movement", ""),
            "genre": r.get("genre", ""),
            "era": r.get("era", ""),
            "mood": r.get("mood_tags_list", []),
            "energy": r.get("energy", ""),
            "licence_status": r["licence_status"],
            "recording_status": r.get("recording_status", ""),
            "score_status": r.get("score_status", ""),
            "verified": r.get("verified", ""),
            "has_editable_score": r["has_editable_score"],
            "has_recording": r["has_recording"],
            "renderable_midi": bool(render and (render["file"].endswith((".mid", ".midi")) or render["zip_member"])),
            "editors_pick_rank": r.get("editors_pick_rank", 0),
            "preview_url": url(r.get("preview_url", "")),
            "score_url": url(r.get("score_url", "")),
            "release_audio_url": r.get("release_audio_url", ""),
            "stream_audio_url": r.get("stream_audio_url", ""),
            "midi_play_url": url(r.get("midi_play_url", "")),
            "item_json_url": url(item_rel),
        })
        full = dict(r)
        full.pop("search_text", None)
        full.update({
            "schema_version": SCHEMA_VERSION,
            "pages_base": PAGES_BASE,
            "page_url": PAGES_BASE + "?id=" + rid,
            "item_json_url": url(item_rel),
            "preview_url_abs": url(r.get("preview_url", "")),
            "score_url_abs": url(r.get("score_url", "")),
            "score_files_abs": [url(f) for f in r.get("score_files", [])],
            "midi_play_url_abs": url(r.get("midi_play_url", "")),
            "render_midi": render,
            "licence_meaning": LICENCE_MEANING.get(r["licence_status"], ""),
            "credit_text": credit_text(r),
        })
        items[rid] = full
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "name": "LaDoger music library",
        "description": "Legally usable music (PD / CC0 / CC BY, flagged otherwise) for commercial and social video. "
                       "Relative paths resolve against pages_base; every *_url field here is already absolute.",
        "pages_base": PAGES_BASE,
        "repo": REPO_URL,
        "release": RELEASE_URL,
        "agents_md": REPO_URL + "/blob/main/AGENTS.md",
        "llms_txt": PAGES_BASE + "llms.txt",
        "full_data": PAGES_BASE + "data/library.json",
        "composers": PAGES_BASE + "data/composers.json",
        "licence_status_meaning": LICENCE_MEANING,
        "count": len(index),
        "items": index,
    }
    return catalog, items, problems


def slim_row(r):
    out = []
    for f in INDEX_FIELDS:
        if f == "mood_tags":
            v = ";".join(r.get("mood_tags_list", []))
        elif f == "catalog_variants":
            # search aliases: 'BWV 565' also matches 'bwv565'
            v = " ".join(w for w in r.get("search_text", "").split() if any(c.isdigit() for c in w))
        elif f == "verified":
            v = 1 if r.get("verified") == "yes" else 0
        else:
            v = r.get(f, "")
        if isinstance(v, bool):
            v = int(v)
        out.append(v)
    return out


def build_index(rows):
    """Split the slim index into parts of at most SHARD_BYTES (compact JSON)."""
    parts, cur, size = [], [], 0
    for r in rows:
        row = slim_row(r)
        n = len(json.dumps(row, ensure_ascii=False, separators=(",", ":"))) + 1
        if cur and size + n > SHARD_BYTES:
            parts.append(cur)
            cur, size = [], 0
        cur.append(row)
        size += n
    if cur:
        parts.append(cur)
    names = [f"part-{i:03d}.json" for i in range(len(parts))]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "count": len(rows),
        "fields": INDEX_FIELDS,
        "parts": [{"file": n, "count": len(p)} for n, p in zip(names, parts)],
        "item_json": "data/items/{id}.json",
    }
    return manifest, dict(zip(names, parts))


def dump(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def main():
    catalog, items, problems = build()
    if "--check" not in sys.argv:
        os.makedirs(ITEMS_DIR, exist_ok=True)
        dump(catalog, CATALOG_PATH)
        for rid, full in items.items():
            dump(full, os.path.join(ITEMS_DIR, rid + ".json"))
        for name in os.listdir(ITEMS_DIR):
            if name.endswith(".json") and name[:-5] not in items:
                os.remove(os.path.join(ITEMS_DIR, name))
        manifest, shards = build_index(json.load(open(LIB_PATH, encoding="utf-8")))
        os.makedirs(INDEX_DIR, exist_ok=True)
        for name in os.listdir(INDEX_DIR):
            if name.startswith("part-") and name not in shards:
                os.remove(os.path.join(INDEX_DIR, name))
        for name, rows in shards.items():
            with open(os.path.join(INDEX_DIR, name), "w", encoding="utf-8") as f:
                json.dump({"fields": INDEX_FIELDS, "rows": rows}, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")
        dump(manifest, os.path.join(INDEX_DIR, "manifest.json"))
        print(f"wrote data/catalog.json + {len(items)} data/items/*.json + {len(shards)} data/index parts")
    else:
        print(f"checked {len(items)} items")
    for p in problems:
        print("WARN", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
