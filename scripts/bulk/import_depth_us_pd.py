#!/usr/bin/env python3
"""Catalogue-driven import for LaDoger-approved US-PD-only composers (depth run 1).

Composers + work checklists live in scripts/bulk/catalogue_data.py. A source row
is imported only when (a) the composer is in approved_us_pd_only, (b) its title
matches a checklist row with status ``in-scope`` (verified published <= 1930)
and no excluded / unverified row claims it first, (c) the file's own licence is
PD / CC0 (PDMX subset no_license_conflict, Mutopia PD, OpenScore CC0).
Third-party arrangements (brass, woodwind, jazz, "arr.") are skipped.

Sources: PDMX (MIDI from mid.tar.gz), Mutopia and OpenScore rows in
parts/bulk_raw/{mutopia,openscore}.csv (downloaded through download_slice.process).

Usage:
  python3 scripts/bulk/import_depth_us_pd.py --dry-run [--composer ravel]
  python3 scripts/bulk/import_depth_us_pd.py [--composer ravel ...]
Writes parts/BULK_batchP7_rows.csv (re-runnable: ids already in the file are kept).
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogue_data import COMPOSERS, IN  # noqa: E402
from dedup import allocate_id, existing_from_paths  # noqa: E402
from schema import CANDIDATE_COLUMNS, fold, mood_tags, slugify, tempo_energy, US_PD_ONLY_CANONS  # noqa: E402
import download_slice  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZENODO = "https://zenodo.org/records/15571083"
PDMX_CSV = ROOT / ".tmp" / "pdmx" / "PDMX.csv"
MID_TAR = ROOT / ".tmp" / "pdmx" / "mid.tar.gz"
MID_ROOT = ROOT / ".tmp" / "pdmx" / "mid"
OUT = ROOT / "parts" / "BULK_batchP7_rows.csv"
FAIL = ROOT / "parts" / "bulk_raw" / "download_failures_P7.csv"
RAW = {"mutopia": ROOT / "parts" / "bulk_raw" / "mutopia.csv",
       "openscore": ROOT / "parts" / "bulk_raw" / "openscore.csv"}

NAME_RX = {
    "ravel": r"\bravel\b",
    "strauss_r": r"richard strauss|strauss,? richard|\br\.? ?strauss\b|^strauss$",
    "elgar": r"(?<!m)\belgar\b",
    "holst": r"\bholst\b",
    "rachmaninoff": r"rachmanin|rakhmanin|rachmanov",
}
NOT_NAME = re.compile(r"belue|after ravel|johann|julio melgar|strauss i\b")
ARRANGED = re.compile(
    r"\barr\b|arr\.|arranged|arrangement|transcri|for (woodwind|brass|tuba|trombone|viola|clarinet|guitar|"
    r"band|wind|flute|saxophone|choir|organ|jazz)|woodwind|\bbrass|\btuba|mellophone|\bjazz|\bswing\b|"
    r"\beasy\b|simplified|saattbb|\bsatb\b|choral fi|\bwip\b|\bdraft\b|unpublished|ensemble|"
    r"\borch\b|orch\.|quartert|\bjam\b|\bclarinet\b|\bviola\b|concert band|wind ensemble|\bchorale\b|o god beyond|i vow to thee my county",
    re.I,
)
# Ravel's own orchestration of Mussorgsky is catalogued (M.A24); PDMX credits it as "arr. Maurice Ravel".
RAVEL_ORCH = re.compile(r"(arr\.?|orchestration de\.?) *maurice ravel", re.I)
SCOPE = "US-PD-only"
SCOPE_REASON = (
    "US public domain only (composer died {death}; work published {year}, before 1931). "
    "May still be copyrighted elsewhere, including life+70 / life+100 territories "
    "(EU/Poland and others). LaDoger approved 2026-10-10 with this flag."
)
BATCH_COLUMNS = download_slice.BATCH_COLUMNS + [
    "licence_scope", "publication_year", "licence_scope_reason",
]


def midi_seconds(b: bytes) -> float:
    """Length of a Standard MIDI File in seconds (tempo map honoured); -1 if unparseable."""
    import struct
    try:
        _fmt, n, div = struct.unpack(">HHH", b[8:14])
        pos, end, tempos = 14, 0, [(0, 500000)]
        for _ in range(n):
            ln = struct.unpack(">I", b[pos + 4:pos + 8])[0]
            tr, pos = b[pos + 8:pos + 8 + ln], pos + 8 + ln
            i = t = run = 0
            while i < len(tr):
                v = 0
                while True:
                    c = tr[i]; i += 1; v = (v << 7) | (c & 127)
                    if not c & 128:
                        break
                t += v; s = tr[i]
                if s == 0xFF:
                    ty, ln2 = tr[i + 1], tr[i + 2]; i += 3
                    if ty == 0x51 and ln2 == 3:
                        tempos.append((t, int.from_bytes(tr[i:i + 3], "big")))
                    i += ln2
                elif s in (0xF0, 0xF7):
                    i += 2 + tr[i + 1]
                else:
                    if s & 128:
                        run = s; i += 1
                    else:
                        s = run
                    i += 1 if (s >> 4) in (0xC, 0xD) else 2
            end = max(end, t)
        sec, last, tp = 0.0, 0, 500000
        for tt, tpo in sorted(tempos):
            if tt > end:
                break
            sec += (tt - last) * tp / div / 1e6; last, tp = tt, tpo
        return sec + (end - last) * tp / div / 1e6
    except Exception:  # noqa: BLE001
        return -1.0


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def _bool(v) -> bool:
    return str(v).strip().lower() == "true"


class Checklist:
    def __init__(self, key: str):
        self.key = key
        self.info = COMPOSERS[key]
        self.rows = [(c, t, y, s, re.compile(rx) if rx else None, n) for c, t, y, s, rx, n in self.info["rows"]]
        self.name_rx = re.compile(NAME_RX[key], re.I)

    def owns(self, composer: str) -> bool:
        c = norm(composer)
        return bool(self.name_rx.search(c)) and not NOT_NAME.search(c)

    def match(self, hay: str):
        """First checklist row hit; exclusion/unverified rows are checked before in-scope ones."""
        for status_in in (False, True):
            for cat, title, year, status, rx, _note in self.rows:
                if rx is None or (status == IN) != status_in:
                    continue
                if rx.search(hay):
                    return cat, title, year, status
        return None


# Checklist entries that stand for a set of separate pieces: keep each file's own title (movement) there.
SETS = {"M.A24", "M.60", "M.69", "M.A4-11", "M.A17", "Op.3", "Op.10 / TrV 141", "Op.16", "Op.23", "Op.27 / TrV 170",
        "Op.30", "Op.31", "Op.34 No.14", "Op.36", "Op.37", "Op.39", "Op.42", "Op.60", "Op.32 / H.125", "Op.24 / H.90"}


_NAMES = r"(?:Maurice Ravel|M\.\s?Ravel|Ravel|Edward Elgar|Elgar|Richard Strauss|R\. ?Strauss|Gustav Holst|Holst|Sergei Rachmaninoff|S\.\s?Rachmaninoff?|Rachmaninoff|Rachmaninov)"


def tidy_title(title: str) -> str:
    """Drop composer names from PDMX titles ('Tout gai! Maurice Ravel', 'Elegie (S.Rachmaninoff. Op.3.No.1)')."""
    t = re.sub(r"\s*\([^)]*" + _NAMES + r"[^)]*\)", "", title, flags=re.I)
    t = re.sub(r"^\s*" + _NAMES + r"\b\.?\s*[-–:]?\s*", "", t, flags=re.I)
    t = re.sub(r"\s*[-–:]?\s*\b" + _NAMES + r"\b\.?\s*$", "", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip(" -–:") or title


def multi(entry_regex: str, cat: str = "") -> bool:
    return cat in SETS


def cat_label(cat: str) -> str:
    first = cat.split(" / ")[0]
    return re.sub(r"^(M|Op|H|TrV)\.(?=\d)", lambda m: m.group(1) + ". ", first)


def make_row(chk: Checklist, base: dict, cat, ctitle, year, title, source) -> dict:
    info = chk.info
    row = {c: "" for c in CANDIDATE_COLUMNS}
    row.update(base)
    reason = SCOPE_REASON.format(death=info["death"], year=year)
    row.update({
        "composer": info["name"], "death_year": str(info["death"]), "title": title,
        "catalog": cat_label(cat),
        "mood_tags": mood_tags(title, "", info["genre"]), "tempo_energy": tempo_energy(title, ""),
        "notable_excerpt": "Opening (00:00); play the score MIDI in the browser to audition.",
        "video_use_ideas": "Underscore a short scene with the opening bars.",
        "verified": "yes", "added_by": "bulk", "licence_class": "flagged",
        "genre": info["genre"], "era": info["era"], "canon": info["canon"], "quality_penalty": "0",
        "licence_scope": SCOPE, "publication_year": str(year), "licence_scope_reason": reason,
        "legal_notes": reason + " " + base.get("legal_notes", ""),
    })
    return row


def harvest(chks: list[Checklist], per_entry_cap: int = 4, per_multi_cap: int = 14):
    cands: list[dict] = []
    skipped = {"arranged": 0, "unmatched": 0, "excluded-or-unverified": 0}
    # --- PDMX
    with PDMX_CSV.open(newline="", encoding="utf-8", errors="replace") as handle:
        for raw in csv.DictReader(handle):
            if not _bool(raw.get("subset:no_license_conflict")) or _bool(raw.get("license_conflict")):
                continue
            lic = (raw.get("license") or "").lower().replace("_", "-")
            if lic not in {"publicdomain", "cc-zero", "cc0"}:
                continue
            comp = raw.get("composer_name") or ""
            chk = next((c for c in chks if c.owns(comp)), None)
            if not chk:
                continue
            blob = f"{raw.get('title') or ''} {raw.get('song_name') or ''}"
            orch = chk.key == "ravel" and RAVEL_ORCH.search(comp) and re.search(r"pictures|tableaux", blob, re.I)
            if not orch and ARRANGED.search(f"{blob} {comp}"):
                skipped["arranged"] += 1
                continue
            hit = chk.match(norm(blob))
            if not hit:
                skipped["unmatched"] += 1
                continue
            cat, ctitle, year, status = hit
            if status != IN:
                skipped["excluded-or-unverified"] += 1
                continue
            mid = (raw.get("mid") or "").strip()
            if not mid:
                continue
            rating = float(raw.get("rating") or 0)
            favs = int(float(raw.get("n_favorites") or 0))
            views = int(float(raw.get("n_views") or 0))
            ntr = int(float(raw.get("n_tracks") or 0))
            label = "PD" if "public" in lic else "CC0"
            base = {
                "editable_source_url": ZENODO, "editable_format": "MIDI; MusicXML (inside PDMX archives)",
                "editable_license": label, "source_rank": "9", "source_name": "pdmx",
                "instrumentation": f"{ntr or '?'} tracks",
                "popularity": f"rating={rating:.2f};ratings={int(float(raw.get('n_ratings') or 0))};favorites={favs};views={views}",
                "download_url": mid, "repo_path": mid, "external_id": Path(mid).stem,
                "legal_notes": (
                    f"PDMX Zenodo 10.5281/zenodo.15571083. subset:no_license_conflict; file licence "
                    f"{raw.get('license')} ({raw.get('license_url')}). Zenodo compilation is CC BY 4.0; this "
                    "file's own label is public domain or CC0. User-uploaded MuseScore transcription, not a "
                    f"critical edition. MIDI member: {mid}."),
            }
            title = (raw.get("title") or raw.get("song_name") or ctitle).strip()
            if not multi("", cat) or title.lower() in {"na", ""}:
                title = ctitle
            row = make_row(chk, base, cat, ctitle, year, tidy_title(title), "pdmx")
            row["_score"] = (100 if _bool(raw.get("is_best_unique_arrangement")) else 0) + rating + min(favs, 30) \
                + min(views, 5000) / 2000.0 + min(ntr, 40) / 10.0
            row["_cat"] = (chk.key, cat)
            cands.append(row)
    # --- Mutopia / OpenScore raw candidates
    for src, path in RAW.items():
        if not path.is_file():
            continue
        for raw in csv.DictReader(path.open(newline="", encoding="utf-8")):
            comp = raw.get("composer") or ""
            chk = next((c for c in chks if c.owns(comp)), None)
            if not chk:
                continue
            lic = (raw.get("editable_license") or "").lower()
            if lic not in {"pd", "cc0", "public domain", "cc-zero", "publicdomain"} and "cc0" not in lic and lic != "pd":
                continue
            blob = f"{raw.get('title') or ''} {raw.get('movement') or ''} {raw.get('catalog') or ''}"
            hit = chk.match(norm(blob))
            if not hit or hit[3] != IN:
                skipped["unmatched" if not hit else "excluded-or-unverified"] += 1
                continue
            cat, ctitle, year, _ = hit
            base = {k: raw.get(k, "") for k in CANDIDATE_COLUMNS if k in raw}
            base["legal_notes"] = (raw.get("legal_notes") or "").split("Composer died")[0].strip()
            title = (raw.get("title") or ctitle).strip()
            row = make_row(chk, base, cat, ctitle, year, title, src)
            for k in ("download_url", "repo_path", "external_id", "source_name", "source_rank", "editable_source_url",
                      "editable_format", "editable_license", "instrumentation", "popularity"):
                row[k] = raw.get(k, row.get(k, ""))
            row["_score"] = 200 - float(raw.get("source_rank") or 9)
            row["_cat"] = (chk.key, cat)
            cands.append(row)
    # cap per checklist entry
    cands.sort(key=lambda r: (-r["_score"], r["title"]))
    kept, count = [], {}
    for r in cands:
        key = r["_cat"]
        entry = next(e for e in COMPOSERS[key[0]]["rows"] if e[0] == key[1] and e[3] == IN)
        cap = per_multi_cap if multi(entry[4], entry[0]) else per_entry_cap
        if count.get(key, 0) >= cap:
            continue
        count[key] = count.get(key, 0) + 1
        kept.append(r)
    print(f"harvested {len(cands)} matching rows, kept {len(kept)}; skipped {skipped}")
    return kept


def extract(rows):
    members = []
    for row in rows:
        if row["source_name"] != "pdmx":
            continue
        member = row["download_url"].lstrip("./")
        if member.startswith("mid/") and not (MID_ROOT / member).is_file():
            members.append(member)
    if not members:
        return
    MID_ROOT.mkdir(parents=True, exist_ok=True)
    lst = MID_ROOT / "_members_p7.txt"
    lst.write_text("\n".join(members) + "\n", encoding="utf-8")
    print(f"extracting {len(members)} PDMX members")
    subprocess.check_call(["tar", "-xzf", str(MID_TAR), "-C", str(MID_ROOT), "-T", str(lst)])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--composer", nargs="*", default=None, help="checklist keys (default: all approved)")
    args = ap.parse_args()
    keys = args.composer or list(COMPOSERS)
    chks = []
    for k in keys:
        if COMPOSERS[k]["canon"] not in US_PD_ONLY_CANONS:
            print(f"SKIP {k}: not in approved_us_pd_only")
            continue
        chks.append(Checklist(k))
    rows = harvest(chks)
    by = {}
    for r in rows:
        by.setdefault((r["composer"], r["catalog"]), []).append(r["source_name"])
    for (c, cat), srcs in sorted(by.items()):
        print(f"  {c:22} {cat:14} x{len(srcs)} {sorted(set(srcs))}")
    if args.dry_run:
        return 0
    extract(rows)
    index = existing_from_paths([ROOT / "library.csv", *sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))])
    for path in (ROOT / "files" / "scores").iterdir():
        if path.is_file():
            index.add_stem(path.stem)
    used: set[str] = set()
    done, failures = [], []
    for row in rows:
        prefix = COMPOSERS[row["_cat"][0]]["prefix"]
        ident = allocate_id(f"{prefix}_{slugify(row['catalog'] + ' ' + row['title'], 48)}", index, used)
        row["id"] = ident
        try:
            if row["source_name"] == "pdmx":
                src = MID_ROOT / row["download_url"].lstrip("./")
                data = src.read_bytes()
                if data[:4] != b"MThd":
                    raise RuntimeError("not MIDI")
                if midi_seconds(data) < 20:  # truncated excerpts (e.g. a 14 s Rachmaninoff Prelude Op. 23/5) are not pieces
                    raise RuntimeError("shorter than 20 s")
                dest = ROOT / "files" / "scores" / f"{ident}.mid"
                if dest.exists():
                    raise RuntimeError("target exists")
                dest.write_bytes(data)
                out = {c: row.get(c, "") for c in BATCH_COLUMNS}
                out.update(local_score_path=f"files/scores/{ident}.mid", local_audio_path="", preview_path="")
            else:
                out = download_slice.process({k: v for k, v in row.items() if not k.startswith("_")}, None)
                for k in ("licence_scope", "publication_year", "licence_scope_reason"):
                    out[k] = row[k]
            out["id"] = ident
            done.append(out)
            index.add_stem(ident)
            print(f"OK {ident} pub={row['publication_year']} {row['source_name']}")
        except Exception as exc:  # noqa: BLE001
            failures.append({"id": ident, "source": row["source_name"], "error": str(exc)[:200]})
            print(f"FAIL {ident}: {exc}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=BATCH_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(done)
    if failures:
        with FAIL.open("w", newline="", encoding="utf-8") as handle:
            w = csv.DictWriter(handle, fieldnames=["id", "source", "error"])
            w.writeheader()
            w.writerows(failures)
    print(f"wrote {len(done)} rows -> {OUT}; failures {len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
