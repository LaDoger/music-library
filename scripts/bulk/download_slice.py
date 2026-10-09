#!/usr/bin/env python3
"""Download a licence-clean first slice and render 15 second previews.

Reads parts/BULK_candidates.csv. Selects at most --limit new pieces
(default 220, hard cap 300) across OpenScore quartets, OpenScore Lieder,
Mutopia PD/CC-BY, and PDMX only when the MIDI member is already on disk.
Writes scores under files/scores/, previews under previews/, and appends
parts/BULK_batchA_rows.csv. Never rewrites library.csv or BATCH1 files.

Safe to re-run: ids already in the batch CSV, or whose score file already
exists, are skipped.
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dedup import (  # noqa: E402
    canon_name,
    dedup_key,
    existing_from_paths,
    is_duplicate,
    load_csv_rows,
    popularity_value,
)
from midi_clip import clip_midi  # noqa: E402
from schema import (  # noqa: E402
    CANDIDATE_COLUMNS,
    SCHEMA_COLUMNS,
    composer_record,
    normalize_catalog,
)

ROOT = Path(__file__).resolve().parents[2]
BATCH_COLUMNS = SCHEMA_COLUMNS + [
    "source_rank", "source_name", "licence_class", "instrumentation",
    "popularity", "genre", "era",
]
SOURCE_CAPS = {
    "openscore-lieder": 120,
    "openscore-quartets": 36,
    "mutopia": 60,
    "pdmx": 24,
}
# --bulk (scale run): per-source caps sized for thousands, composer caps off.
BULK_SOURCE_CAPS = {
    "openscore-lieder": 2000,
    "openscore-quartets": 600,
    "mutopia": 1500,
    "pdmx": 2500,
}
BULK = False
MAX_LIMIT = 3000
COMPOSER_CAPS = {
    "franz schubert": 26,
    "robert schumann": 16,
    "johannes brahms": 12,
    "hugo wolf": 10,
    "ludwig van beethoven": 16,
    "wolfgang amadeus mozart": 12,
    "joseph haydn": 8,
    "frederic chopin": 10,
    "claude debussy": 8,
    "felix mendelssohn": 6,
    "gabriel faure": 4,
    "johann sebastian bach": 8,
    "richard wagner": 6,
    "gustav mahler": 6,
    "anton bruckner": 8,
    "fanny hensel": 6,
    "clara schumann": 4,
    "antonin dvorak": 4,
}
TIER_CAPS = {1: 8, 2: 10, 3: 6, 4: 4, 5: 3}
MAX_DOWNLOAD = 8_000_000


def composer_cap(canon: str) -> int:
    if BULK:
        return 10_000
    if canon in COMPOSER_CAPS:
        return COMPOSER_CAPS[canon]
    return TIER_CAPS.get(composer_record(canon)["tier"], 6)


def _row_sort_key(row: dict):
    source_order = {
        "openscore-quartets": 0,
        "openscore-lieder": 1,
        "mutopia": 2,
        "pdmx": 3,
    }
    return (
        source_order.get(row.get("source_name") or "", 9),
        int(row.get("source_rank") or 99),
        int(row.get("quality_penalty") or 0),
        -popularity_value(row.get("popularity") or ""),
        row.get("catalog") or "",
        row.get("title") or "",
    )


def _take(groups: dict[str, list], order: list[str], limit: int, picked, by_source, by_composer):
    """Round-robin one piece per composer. Stop at exactly `limit` new rows.

    The cap is checked inside the composer loop. Checking it only at the
    start of a round would append every composer in that round and overshoot.
    """
    cursors = {canon: 0 for canon in order}
    while len(picked) < limit:
        progressed = False
        for canon in order:
            if len(picked) >= limit:
                return
            if by_composer[canon] >= composer_cap(canon):
                continue
            rows = groups.get(canon) or []
            while cursors[canon] < len(rows):
                row = rows[cursors[canon]]
                cursors[canon] += 1
                source = row.get("source_name") or ""
                caps = BULK_SOURCE_CAPS if BULK else SOURCE_CAPS
                if by_source[source] >= caps.get(source, 20):
                    continue
                picked.append(row)
                by_source[source] += 1
                by_composer[canon] += 1
                progressed = True
                break
        if not progressed:
            break


def select(
    rows: list[dict],
    limit: int,
    pdmx_root: Path | None,
    prior_source: Counter | None = None,
    prior_composer: Counter | None = None,
) -> list[dict]:
    eligible = [
        row for row in rows
        if row.get("licence_class") in {"clean", "attribution"}
        and int(row.get("quality_penalty") or 0) < 20
    ]
    wholes = set()
    for row in eligible:
        catalog = normalize_catalog(row.get("catalog") or "")
        if (
            catalog
            and not (row.get("movement") or "").strip()
            and row.get("source_name") == "openscore-quartets"
        ):
            wholes.add((row.get("canon") or "", catalog))
    filtered = []
    for row in eligible:
        catalog = normalize_catalog(row.get("catalog") or "")
        movement = (row.get("movement") or "").strip()
        if movement and catalog and (row.get("canon") or "", catalog) in wholes:
            if row.get("source_name") != "openscore-quartets":
                continue
        if row.get("source_name") == "pdmx":
            if not _pdmx_file(row, pdmx_root):
                continue
        filtered.append(row)
    groups: dict[str, list] = {}
    for row in filtered:
        groups.setdefault(row.get("canon") or "", []).append(row)
    for canon in groups:
        groups[canon].sort(key=_row_sort_key)
    named = [canon for canon in groups if canon in COMPOSER_CAPS]
    named.sort(key=lambda canon: (composer_record(canon)["tier"], canon))
    rest = [canon for canon in groups if canon not in COMPOSER_CAPS]
    rest.sort(key=lambda canon: (composer_record(canon)["tier"], canon))
    picked = []
    by_source = Counter(prior_source or {})
    by_composer = Counter(prior_composer or {})
    _take(groups, named, limit, picked, by_source, by_composer)
    _take(groups, rest, limit, picked, by_source, by_composer)
    print("selected", len(picked), dict(Counter(row.get("source_name") or "" for row in picked)))
    return picked


def _prior_counts(path: Path) -> tuple[Counter, Counter]:
    """Counts already appended to the batch CSV, so a resume keeps the caps."""
    sources: Counter = Counter()
    composers: Counter = Counter()
    if not path.exists() or path.stat().st_size == 0:
        return sources, composers
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            sources[row.get("source_name") or ""] += 1
            composers[canon_name(row.get("composer") or "")] += 1
    return sources, composers


def _pdmx_file(row: dict, root: Path | None) -> Path | None:
    if root is None:
        return None
    member = (row.get("download_url") or "").lstrip("./")
    path = root / member if member else None
    if path and path.is_file() and path.stat().st_size > 64:
        return path
    return None


def _mutopia_alt(url: str) -> str:
    """Retry one directory up when the LilyPond file is nested under itself.

    ftp/.../BWV1013/bwv1013/bwv1013.mid follows the .ly path. The rendered MIDI
    is often ftp/.../BWV1013/bwv1013.mid. A normal ftp/.../Piece/Piece.mid URL
    is left alone; this alternate is only fetched after that URL 404s.
    """
    parts = urllib.parse.urlsplit(url)
    segs = [segment for segment in parts.path.split("/") if segment]
    if len(segs) < 4 or not segs[-1].lower().endswith(".mid"):
        return ""
    stem = segs[-1][:-4].lower()
    if stem != segs[-2].lower() or stem != segs[-3].lower():
        return ""
    segs = segs[:-2] + [segs[-1]]
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, "/" + "/".join(segs), "", ""))


def _fetch(url: str, dest: Path) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "music-library-bulk/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read(MAX_DOWNLOAD + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} {url}") from exc
    if len(data) < 64 or len(data) > MAX_DOWNLOAD:
        raise RuntimeError(f"unexpected size {len(data)} for {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return data


def _export_midi(mxl: Path, mid: Path, work: Path):
    runtime = work / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = str(work)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["XDG_RUNTIME_DIR"] = str(runtime)
    result = subprocess.run(
        ["mscore3", "-o", str(mid), str(mxl)],
        check=False, env=env, timeout=180,
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not mid.exists() or mid.stat().st_size < 50:
        tail = (result.stderr or result.stdout or "")[-400:]
        raise RuntimeError(f"mscore3 failed ({result.returncode}): {tail}")
    if mid.read_bytes()[:4] != b"MThd":
        raise RuntimeError("mscore3 did not write a MIDI file")


def _preview(midi: Path, out: Path):
    script = ROOT / "scripts" / "make_preview.py"
    result = subprocess.run(
        ["python3", str(script), "--midi", str(midi), "--start", "0", "--out", str(out)],
        check=False, cwd=str(ROOT), timeout=180,
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not out.exists() or out.stat().st_size < 8000:
        tail = (result.stderr or result.stdout or "")[-500:]
        raise RuntimeError(f"preview failed: {tail}")
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(out)],
        check=True, capture_output=True, text=True,
    )
    duration = float(probe.stdout.strip() or "0")
    if not 12.0 <= duration <= 16.5:
        raise RuntimeError(f"preview duration {duration:.2f}s")


def _github_mxl(row: dict) -> str:
    repo = "OpenScore/Lieder" if row.get("source_name") == "openscore-lieder" else "OpenScore/StringQuartets"
    folder = row.get("repo_path") or ""
    if not folder.startswith("scores/"):
        return ""
    quoted = urllib.parse.quote(folder)
    url = f"https://api.github.com/repos/{repo}/contents/{quoted}?ref=main"
    request = urllib.request.Request(url, headers={"User-Agent": "music-library-bulk/1.0", "Accept": "application/vnd.github+json"})
    try:
        response_cm = urllib.request.urlopen(request, timeout=60)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} {url}") from exc
    with response_cm as response:
        import json
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        return ""
    for item in payload:
        name = item.get("name") or ""
        if name.endswith(".mxl") and item.get("download_url"):
            return item["download_url"]
    return ""


def process(row: dict, pdmx_root: Path | None, preview: bool = True) -> dict:
    ident = row["id"]
    work = ROOT / ".tmp" / "bulk" / "work" / ident
    if work.exists():
        subprocess.run(["rm", "-rf", str(work)], check=False)
    work.mkdir(parents=True)
    source = row.get("source_name") or ""
    final_mid = ROOT / "files" / "scores" / f"{ident}.mid"
    final_preview = ROOT / "previews" / f"{ident}.mp3"
    final_mxl = ROOT / "files" / "scores" / f"{ident}.mxl"
    if final_mid.exists() or final_mxl.exists() or final_preview.exists():
        raise RuntimeError("target file already exists; refusing to clobber")
    try:
        if source == "mutopia":
            raw = work / "source.mid"
            try:
                data = _fetch(row["download_url"], raw)
            except RuntimeError:
                alt = _mutopia_alt(row.get("download_url") or "")
                if not alt:
                    raise
                data = _fetch(alt, raw)
                row["download_url"] = alt
            if data[:4] != b"MThd":
                raise RuntimeError("FTP URL did not return MIDI")
            score_mid = raw
        elif source == "pdmx":
            local = _pdmx_file(row, pdmx_root)
            if local is None:
                raise RuntimeError("PDMX MIDI is not extracted")
            score_mid = local
            if score_mid.read_bytes()[:4] != b"MThd":
                raise RuntimeError("PDMX member is not MIDI")
        elif source.startswith("openscore"):
            mxl = work / "source.mxl"
            try:
                data = _fetch(row["download_url"], mxl)
            except RuntimeError:
                alt = _github_mxl(row)
                if not alt:
                    raise
                data = _fetch(alt, mxl)
                row["download_url"] = alt
            if data[:2] != b"PK":
                raise RuntimeError("OpenScore URL did not return a zip/mxl")
            exported = work / "exported.mid"
            _export_midi(mxl, exported, work)
            score_mid = exported
            final_mxl.write_bytes(mxl.read_bytes())
        else:
            raise RuntimeError(f"unknown source {source}")
        if preview:
            clipped = work / "clip.mid"
            clip_midi(score_mid, clipped, 20.0)
            _preview(clipped, work / "preview.mp3")
        final_mid.write_bytes(Path(score_mid).read_bytes())
        if preview:
            final_preview.write_bytes((work / "preview.mp3").read_bytes())
    finally:
        subprocess.run(["rm", "-rf", str(work)], check=False)
    done = {column: row.get(column, "") for column in BATCH_COLUMNS}
    done["id"] = ident
    done["local_score_path"] = f"files/scores/{ident}.mid"
    done["local_audio_path"] = ""
    # Bulk rows have no pre-rendered preview; the site synthesises the MIDI on demand.
    done["preview_path"] = f"previews/{ident}.mp3" if preview else ""
    done["added_by"] = "grok" if preview else "bulk"
    done["recording_source_url"] = ""
    done["recording_performer"] = ""
    done["recording_license"] = ""
    done["recording_quality"] = ""
    if not done.get("notable_excerpt"):
        done["notable_excerpt"] = "Own MIDI render 00:00-00:15 (opening)"
    return done


def _append(path: Path, row: dict):
    new_file = not path.exists() or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=BATCH_COLUMNS, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        writer.writerow(row)
        handle.flush()


def _done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["id"] for row in csv.DictReader(handle) if row.get("id")}


def main():
    parser = argparse.ArgumentParser(description="Download the first bulk slice and render previews")
    parser.add_argument("--candidates", type=Path, default=ROOT / "parts" / "BULK_candidates.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "parts" / "BULK_batchA_rows.csv")
    parser.add_argument("--limit", type=int, default=220)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--pdmx-root", type=Path, default=ROOT / ".tmp" / "pdmx" / "mid")
    parser.add_argument("--failures", type=Path, default=ROOT / "parts" / "bulk_raw" / "download_failures.csv")
    parser.add_argument(
        "--sources", default="",
        help="Comma-separated source_name filter (openscore-lieder, openscore-quartets, mutopia, pdmx)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--bulk", action="store_true",
                        help="Scale run: thousands-sized source caps, no composer caps")
    parser.add_argument("--no-preview", action="store_true",
                        help="Skip the 15 s MP3 preview (bulk rows play via the in-browser MIDI synth)")
    args = parser.parse_args()
    global BULK
    BULK = args.bulk
    if args.limit > MAX_LIMIT:
        raise SystemExit(f"refusing a slice above {MAX_LIMIT} pieces")
    library_paths = [ROOT / "library.csv", *sorted((ROOT / "parts").glob("BATCH1_*.csv"))]
    index = existing_from_paths(library_paths)
    for folder in (ROOT / "files" / "scores", ROOT / "previews"):
        if folder.is_dir():
            for path in folder.iterdir():
                if path.is_file():
                    index.add_stem(path.stem)
    already = _done_ids(args.out)
    rows = load_csv_rows([args.candidates])
    fresh = []
    for row in rows:
        if row.get("id") in already:
            continue
        if is_duplicate(row, index):
            continue
        # Recompute the key so a stale candidate cannot sneak past a new library row.
        row["dedup_key"] = row.get("dedup_key") or dedup_key(
            row.get("composer", ""), row.get("catalog", ""),
            row.get("title", ""), row.get("movement", ""),
        )
        fresh.append(row)
    if args.sources.strip():
        allowed = {part.strip() for part in args.sources.split(",") if part.strip()}
        fresh = [row for row in fresh if (row.get("source_name") or "") in allowed]
    prior_source, prior_composer = _prior_counts(args.out)
    picked = select(
        fresh, args.limit,
        args.pdmx_root if args.pdmx_root.exists() else None,
        prior_source, prior_composer,
    )
    print(f"queue {len(picked)} after dedup ({len(already)} already in {args.out.name})")
    if args.dry_run:
        by_comp = Counter((row.get("composer"), row.get("source_name")) for row in picked)
        for key, count in sorted(by_comp.items(), key=lambda item: (-item[1], item[0][0] or "")):
            print(f"  {count:3} {key[1]:22} {key[0]}")
        return
    failures = []
    ok = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(process, row, args.pdmx_root, not args.no_preview): row for row in picked}
        for future in as_completed(futures):
            row = futures[future]
            try:
                done = future.result()
            except Exception as exc:  # noqa: BLE001 — record and continue the slice
                failures.append({"id": row.get("id", ""), "source": row.get("source_name", ""), "error": str(exc)[:500]})
                print(f"FAIL {row.get('id')} {exc}")
                continue
            _append(args.out, done)
            ok += 1
            print(f"OK {ok} {done['id']}")
    if failures:
        args.failures.parent.mkdir(parents=True, exist_ok=True)
        with args.failures.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "source", "error"])
            writer.writeheader()
            writer.writerows(failures)
        print(f"failures {len(failures)} -> {args.failures}")
    print(f"wrote {ok} rows -> {args.out}")


if __name__ == "__main__":
    main()
