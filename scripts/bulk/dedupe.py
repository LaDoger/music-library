#!/usr/bin/env python3
"""Collapse duplicate pieces across library.csv and the bulk batches.

Called from build_bulk_layer.py, so every import goes through it. Also runs
standalone (``python3 scripts/bulk/dedupe.py``) to print the report only.

Two match keys:
  A  composer + normalised catalogue no. + normalised title (accents, punctuation,
     composer name, "arr.", "for piano", "by X" removed). Catalogue alone links
     rows when the movement signatures are compatible; title alone links rows
     only when neither side has a catalogue number.
  B  MIDI content fingerprint: melody line (top note per onset) as a
     transposition-invariant interval sequence. Exact hash of the first 64
     intervals, or interval 4-gram Jaccard >= SIM_MIN. B merges only within one
     composer, and never across two different catalogue numbers or movements,
     so movements sharing an opening theme stay apart.

Canonical per group: curated (library.csv) > OpenScore > Mutopia > best PDMX
(more tracks, longer, higher rating, cleaner title). Curated rows are never
dropped. The others become ``other_editions`` on the kept item.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema import fold, match_composer, movement_sig, normalize_catalog  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "parts" / ".dedupe_fingerprints.json"
MANIFEST = ROOT / "parts" / "DEDUPE_MANIFEST.csv"
REPORT = ROOT / "parts" / "DEDUPE_REPORT.md"
N_INTERVALS = 64
SIM_MIN = 0.85
MIN_NOTES = 24  # shorter melodies are too generic to fingerprint
GENERIC_COMPOSERS = {"traditional", "anonymous", "anon", "unknown", "various"}

TITLE_NOISE = [
    r"\barr(?:anged|\.|angement)?\b(?: (?:for|by) [^,;()\-]+)?",
    r"\bfor (?:solo |easy |simple |beginner )?(?:piano|guitar|organ|violin|flute|cello|harp|keyboard)(?: solo)?\b",
    r"\bpiano solo\b", r"\beasy\b", r"\bsimplified\b", r"\bversion\b", r"\btranscription\b",
    r"\bby [a-z .'-]+$",
]
CATALOG_IN_TITLE = re.compile(
    r"\b(?:bwv|hwv|wab|kv|k|op|opus|woo|d|rv|hob|l|s|no|nr|n)\.?\s*[ivx]*[:.]?\s*\d+[a-z]?\b", re.I)


# --------------------------------------------------------------------------- names / titles

def canon_composer(name: str) -> str:
    hit = match_composer(name or "")
    if hit:
        return hit
    text = re.sub(r"\([^)]*\)|\b1[4-9]\d\d\b", " ", fold(name))
    return re.sub(r"[^a-z]+", " ", text).strip()


def composer_variants(name: str) -> list[str]:
    """Spellings of the composer to strip from titles, longest first."""
    folded = re.sub(r"\([^)]*\)", " ", name or "").strip()
    parts = [p for p in re.split(r"\s+", folded) if p]
    out = {folded}
    if len(parts) >= 2:
        out.add(parts[-1])
        out.add(" ".join(parts[-2:]))
        out.add(parts[0][0] + ". " + parts[-1])
        if parts[-1].lower() in {"bach", "strauss", "scarlatti", "couperin", "schumann"}:
            out.discard(parts[-1])  # "Bach" alone is ambiguous in titles like "Bach Air"; keep the full name only
            out.add(parts[-1])     # ...but repeated "Bach - X" is still noise for this composer
    return sorted((v for v in out if len(v) >= 3), key=len, reverse=True)


def _name_pattern(variant: str) -> str:
    """Accent-insensitive regex for a name ("Albéniz" matches "Albeniz")."""
    out = []
    for ch in variant:
        base = fold(ch)
        if base.isalpha() and base != ch.lower():
            out.append(f"(?:{re.escape(ch)}|{re.escape(base)})")
        elif ch == " ":
            out.append(r"[\s.]+")
        else:
            out.append(re.escape(ch))
    return "".join(out)


def clean_title(title: str, composer: str) -> str:
    """Remove a repeated composer name and tidy separators; keep catalogue numbers."""
    text = (title or "").strip()
    if not text:
        return text
    original = text
    for variant in composer_variants(composer):
        pat = _name_pattern(variant)
        text = re.sub(rf"\s*[-–—:|/,]?\s*\(?\b(?:by|von|de|di)\s+{pat}\b'?s?\)?\s*$", "", text, flags=re.I)
        text = re.sub(rf"^\s*{pat}(?:'s)?\s*[-–—:|/,]+\s*", "", text, flags=re.I)
        text = re.sub(rf"\s*[-–—:|/,]+\s*\(?{pat}\)?\s*$", "", text, flags=re.I)
        text = re.sub(rf"\s*\({pat}\)\s*", " ", text, flags=re.I)
        text = re.sub(rf"^\s*{pat}(?:'s)?\s+(?=[A-Z0-9])", "", text)
    text = re.sub(r"\s*[-–—]\s*[-–—]\s*", " - ", text)
    text = re.sub(r"\s+([,.;:!?)])", r"\1", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" -–—:|/,_")
    if len(re.sub(r"[^A-Za-z]", "", text)) < 3:
        return original.strip()
    letters = re.sub(r"[^A-Za-z]", "", text)
    if letters.isupper() and len(letters) > 4 or letters.islower():
        text = _title_case(text)
    return text[:1].upper() + text[1:]


def _title_case(text: str) -> str:
    small = {"a", "an", "and", "the", "of", "in", "on", "for", "to", "de", "la", "le", "des", "du", "von", "der", "die", "das", "und", "op", "no"}
    words = text.lower().split(" ")
    out = []
    for i, word in enumerate(words):
        if CATALOG_IN_TITLE.fullmatch(word) or re.fullmatch(r"[ivxlc]+\.?", word):
            out.append(word.upper() if re.fullmatch(r"(?:bwv|hwv|wab|kv|rv)\d*[a-z]?|[ivxlc]+\.?", word) else word.capitalize())
        elif i and word in small:
            out.append(word)
        else:
            out.append(word[:1].upper() + word[1:])
    return " ".join(out)


def title_key(title: str, composer: str) -> str:
    text = fold(clean_title(title, composer))
    for variant in composer_variants(composer):
        text = re.sub(rf"\b{re.escape(fold(variant))}('s)?\b", " ", text)
    for pat in TITLE_NOISE:
        text = re.sub(pat, " ", text)
    text = re.sub(r"\b(?:no|nr|n|num|number)\.?\s*(?=\d)", " ", text)  # keep the number itself
    head = re.sub(r"\s+from\s+[a-z' ]+$", "", text)  # "... from 'Peer Gynt'"
    if len(re.sub(r"[^a-z0-9]", "", head)) >= 8:
        text = head
    text = re.sub(r"\b(in [a-g](?: (?:flat|sharp|b|#))?(?: (?:major|minor|maj|min|dur|moll))?)\b", " ", text)
    text = re.sub(r"\b(major|minor|the|a|an|no|num|number)\b", " ", text)
    return re.sub(r"[^a-z0-9]", "", text)


def catalog_key(row: dict) -> str:
    cat = normalize_catalog(row.get("catalog") or "")
    return cat if re.search(r"\d", cat) else ""


def movement_key(row: dict) -> str:
    number, kinds = movement_sig(row.get("movement") or "")
    return f"{number or ''}:{'-'.join(kinds)}"


# --------------------------------------------------------------------------- MIDI fingerprint

def melody_intervals(path: Path) -> list[int]:
    import mido  # only needed when a fingerprint is not cached

    mid = mido.MidiFile(str(path), clip=True)
    onsets: dict[int, int] = {}
    for track in mid.tracks:
        tick = 0
        for msg in track:
            tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0 and getattr(msg, "channel", 0) != 9:
                if msg.note > onsets.get(tick, -1):
                    onsets[tick] = msg.note
    pitches = [onsets[t] for t in sorted(onsets)][: N_INTERVALS * 3]
    steps = [b - a for a, b in zip(pitches, pitches[1:])]
    steps = [max(-12, min(12, s)) for s in steps if s != 0]  # repeated notes vary across editions
    return steps[: N_INTERVALS * 2]


def fingerprints(rows: list[dict]) -> dict[str, list[int]]:
    cache = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text())
        except ValueError:
            cache = {}
    out, dirty = {}, False
    for row in rows:
        rel = row.get("local_score_path") or ""
        path = ROOT / rel
        if not rel.lower().endswith((".mid", ".midi")) or not path.is_file():
            continue
        stamp = f"{rel}|{path.stat().st_size}"
        if stamp not in cache:
            try:
                cache[stamp] = melody_intervals(path)
            except Exception:  # noqa: BLE001 - a broken MIDI just gets no fingerprint
                cache[stamp] = []
            dirty = True
        out[row["id"]] = cache[stamp]
    if dirty:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, separators=(",", ":")))
    return out


def grams(steps: list[int]) -> set[tuple]:
    head = steps[:N_INTERVALS]
    return {tuple(head[i:i + 4]) for i in range(len(head) - 3)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


# --------------------------------------------------------------------------- grouping

class Groups:
    def __init__(self, ids):
        self.parent = {i: i for i in ids}

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def source_tier(row: dict) -> int:
    if row.get("_curated"):
        return 0
    name = (row.get("source_name") or "").lower()
    if name.startswith("openscore"):
        return 1
    if name.startswith("mutopia"):
        return 2
    if name.startswith("music21"):
        return 3
    return 4


def _midi_size(row: dict) -> int:
    path = ROOT / (row.get("local_score_path") or "")
    return path.stat().st_size if path.is_file() else 0


def quality(row: dict, fp: dict) -> tuple:
    pop = row.get("popularity") or ""
    rating = float((re.search(r"rating=([0-9.]+)", pop) or [0, 0])[1] or 0)
    ratings = float((re.search(r"ratings=([0-9.]+)", pop) or [0, 0])[1] or 0)
    title = row.get("title") or ""
    messy = int(bool(re.search(r"[_#*]|\b(?:wip|test|easy|simplified|arr)\b|^[a-z]", title, re.I)))
    return (source_tier(row), messy, -min(len(fp.get(row["id"], [])), 2 * N_INTERVALS) // 32,
            -_midi_size(row) // 4000, -(rating * min(ratings, 20)), len(title), row["id"])


def dedupe(curated: list[dict], bulk: list[dict]):
    """Return (kept bulk rows, {kept_id: [other_editions]}, manifest rows, stats)."""
    rows = [dict(r, _curated=True) for r in curated] + [dict(r) for r in bulk]
    by_id = {r["id"]: r for r in rows}
    fp = fingerprints(rows)
    groups = Groups(by_id)
    reason: dict[tuple, tuple] = {}

    meta = {}
    for r in rows:
        meta[r["id"]] = (canon_composer(r.get("composer")), catalog_key(r),
                         title_key(r.get("title"), r.get("composer") or ""), movement_key(r),
                         frozenset(re.findall(r"\d+", fold(r.get("title") or "") + " " + (r.get("movement") or ""))))

    # Key A
    buckets = defaultdict(list)
    for rid, (comp, cat, tkey, mov, _) in meta.items():
        if not comp:
            continue
        if cat:
            buckets[("cat", comp, cat, mov)].append(rid)
        elif len(tkey) >= 4:
            buckets[("title", comp, tkey, mov)].append(rid)
    # A whole-work row with no movement joins the catalogue's only movement row ("BWV 565" + "Toccata").
    movs = defaultdict(set)
    for kind, comp, key, mov in buckets:
        if kind == "cat":
            movs[(comp, key)].add(mov)
    for (comp, key), found in movs.items():
        named = found - {":"}
        if ":" in found and len(named) == 1:
            buckets[("cat", comp, key, named.pop())] += buckets.pop(("cat", comp, key, ":"))
    # A title-only row joins the one catalogued piece with the same title ("In the Hall of the Mountain King").
    titled = defaultdict(set)
    for rid, (comp, cat, tkey, mov, _) in meta.items():
        if comp and cat and len(tkey) >= 8:
            titled[(comp, tkey)].add(("cat", comp, cat, mov))
    for key in [k for k in buckets if k[0] == "title"]:
        hits = titled.get((key[1], key[2]), set())
        if len(hits) == 1:
            target = next(iter(hits))
            if target in buckets:
                buckets[target] += buckets.pop(key)
    for bucket in buckets.values():
        for i, a in enumerate(bucket):
            for b in bucket[i + 1:]:
                num_a, num_b = meta[a][4], meta[b][4]
                if num_a - num_b and num_b - num_a:  # BWV 1079 "Ricercar a 6" vs "Canon a 2"
                    continue
                if not titles_close(meta[a][2], meta[b][2]):  # Op. 46: "Morning Mood" vs "Mountain King"
                    continue
                groups.union(a, b)
                reason.setdefault((a, b), ("A", 1.0))

    # Key B, within one composer
    by_comp = defaultdict(list)
    for rid, steps in fp.items():
        if len(steps) >= MIN_NOTES and meta[rid][0] and meta[rid][0] not in GENERIC_COMPOSERS:
            by_comp[meta[rid][0]].append(rid)
    for comp, ids in by_comp.items():
        exact = defaultdict(list)
        for rid in ids:
            exact[hashlib.sha1(json.dumps(fp[rid][:N_INTERVALS]).encode()).hexdigest()].append(rid)
        g = {rid: grams(fp[rid]) for rid in ids}
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if groups.find(a) == groups.find(b) or not _b_compatible(meta[a], meta[b]):
                    continue
                same = fp[a][:N_INTERVALS] == fp[b][:N_INTERVALS] and len(fp[a]) >= N_INTERVALS
                sim = 1.0 if same else jaccard(g[a], g[b])
                if sim >= SIM_MIN:
                    groups.union(a, b)
                    reason[(a, b)] = ("B", round(sim, 3))

    members = defaultdict(list)
    for rid in by_id:
        members[groups.find(rid)].append(rid)

    kept, editions, manifest = [], defaultdict(list), []
    dropped = set()
    for ids in members.values():
        if len(ids) == 1:
            continue
        ranked = sorted(ids, key=lambda i: quality(by_id[i], fp))
        head = ranked[0]
        for rid in ranked[1:]:
            row = by_id[rid]
            if row.get("_curated"):
                continue  # two curated rows never drop each other; report only
            dropped.add(rid)
            why, sim = _why(reason, head, rid, ranked)
            manifest.append({"kept_id": head, "dropped_id": rid, "reason": why, "similarity": sim,
                             "kept_source": _src(by_id[head]), "dropped_source": _src(row),
                             "kept_title": by_id[head].get("title", ""), "dropped_title": row.get("title", "")})
            editions[head].append({
                "id": rid, "source": _src(row), "title": clean_title(row.get("title"), row.get("composer") or ""),
                "url": row.get("editable_source_url") or "",
                "licence": row.get("editable_license") or "",
            })
    for r in bulk:
        if r["id"] not in dropped:
            kept.append(r)
    return kept, dict(editions), manifest, _stats(rows, dropped)


def titles_close(a: str, b: str) -> bool:
    if not a or not b or a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.6


def _b_compatible(a: tuple, b: tuple) -> bool:
    _, cat_a, _, mov_a, num_a = a
    _, cat_b, _, mov_b, num_b = b
    if cat_a and cat_b and cat_a != cat_b:
        return False
    if num_a - num_b and num_b - num_a:  # "Psalm 22 part 1" vs "part 4": each title has a number the other lacks
        return False
    if mov_a != ":" and mov_b != ":" and mov_a != mov_b:
        return False
    return True


def _why(reason, head, rid, ranked):
    for pair in ((head, rid), (rid, head)):
        if pair in reason:
            return reason[pair]
    hits = [v for (x, y), v in reason.items() if rid in (x, y) and (x in ranked and y in ranked)]
    if hits:
        return max(hits, key=lambda v: v[1]) if all(h[0] == "B" for h in hits) else ("A", 1.0)
    return ("A", 1.0)


def _src(row: dict) -> str:
    return "curated" if row.get("_curated") else (row.get("source_name") or "")


def _stats(rows, dropped):
    before, after = Counter(), Counter()
    for r in rows:
        before[_src(r)] += 1
        if r["id"] not in dropped:
            after[_src(r)] += 1
    return {"before": dict(before), "after": dict(after), "dropped": len(dropped)}


def write_outputs(manifest: list[dict], stats: dict, extra: str = "") -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    fields = ["kept_id", "dropped_id", "reason", "similarity", "kept_source", "dropped_source", "kept_title", "dropped_title"]
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for m in sorted(manifest, key=lambda m: (m["kept_id"], m["dropped_id"])):
            writer.writerow({**m, "reason": m["reason"][0], "similarity": m["reason"][1]} if isinstance(m["reason"], tuple)
                            else m)
    reasons = Counter(m["reason"][0] if isinstance(m["reason"], tuple) else m["reason"] for m in manifest)
    lines = ["# Dedupe report", "", f"Rows dropped as duplicates: **{stats['dropped']}** "
             f"(key A {reasons.get('A', 0)}, key B {reasons.get('B', 0)}).", "",
             "| source | before | after | removed |", "|---|---:|---:|---:|"]
    for src in sorted(stats["before"]):
        b, a = stats["before"][src], stats["after"].get(src, 0)
        lines.append(f"| {src} | {b} | {a} | {b - a} |")
    tb, ta = sum(stats["before"].values()), sum(stats["after"].values())
    lines += [f"| **total** | {tb} | {ta} | {tb - ta} |", "",
              "Before = rows that passed the licence gate (curated + bulk). Curated rows are never dropped.",
              "Manifest: parts/DEDUPE_MANIFEST.csv. Alternates are kept as `other_editions` on the kept item "
              "(library_other_editions.json).", extra]
    REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_bulk_layer  # noqa: E402

    sys.exit(build_bulk_layer.main(["--check"]))
