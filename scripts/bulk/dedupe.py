#!/usr/bin/env python3
"""Collapse duplicate pieces across library.csv and the bulk batches.

Called from build_bulk_layer.py, so every import goes through it. Also runs
standalone (``python3 scripts/bulk/dedupe.py``) to print the report only.

Two match keys:
  A  composer + normalised catalogue no. + movement identity (No., month name,
     key, sub-title) + normalised title. Rows whose movement identifiers conflict
     never merge. Catalogue alone links rows when movement identities match or
     one side has none; title alone links rows only when neither side has a
     catalogue number.
  B  MIDI content fingerprint: melody line (top note per onset) as a
     transposition-invariant interval sequence. Exact hash of the first 64
     intervals, or interval 4-gram Jaccard >= SIM_MIN. B merges only within one
     composer, never across different catalogue numbers, and only when movement
     identifiers (No. / month / key / sub-title) match or are both absent.

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
    if folded.lower() == "traditional":
        out.add("Traditional music")  # PDMX folk uploads: "Traditional music - Glencoe March"
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


# Month names (EN/DE/FR/IT) -> stable code. Used for sets like Tchaikovsky's Seasons.
_MONTHS = {
    "january": "jan", "janvier": "jan", "januar": "jan", "gennaio": "jan",
    "february": "feb", "fevrier": "feb", "februar": "feb", "febbraio": "feb",
    "march": "mar", "mars": "mar", "marz": "mar", "maerz": "mar", "marzo": "mar",
    "april": "apr", "avril": "apr", "aprile": "apr",
    "may": "may", "mai": "may", "maggio": "may",
    "june": "jun", "juin": "jun", "juni": "jun", "giugno": "jun",
    "july": "jul", "juillet": "jul", "juli": "jul", "luglio": "jul",
    "august": "aug", "aout": "aug", "agosto": "aug",
    "september": "sep", "septembre": "sep", "settembre": "sep",
    "october": "oct", "octobre": "oct", "oktober": "oct", "ottobre": "oct",
    "november": "nov", "novembre": "nov",
    "december": "dec", "decembre": "dec", "dezember": "dec", "dicembre": "dec",
}
_NO_RE = re.compile(
    r"\b(?:no|nr|n|num|number|movement|mov\.?|mtv|teil|part)\.?\s*(\d{1,2})\b", re.I)
_ROMAN_NO_RE = re.compile(
    r"(?:^|[\s:.\-–—])(?:no\.?\s*)?(i{1,3}|iv|vi{0,3}|ix|x|xi|xii)\b(?!\w)", re.I)
_KEY_RE = re.compile(
    r"\bin\s+([a-g])(?:[\s\-]*(flat|sharp|b|#|es|is))?(?:\s*(major|minor|maj|min|dur|moll))?\b",
    re.I)
_OP_NO_RE = re.compile(r"\bop(?:us)?\.?\s*\d+\s*(?:no|nr|n)\.?\s*(\d{1,2})\b", re.I)
# Kind / form words that are not distinctive movement subtitles on their own.
_SUB_STOP = {
    "prelude", "praeludium", "preludium", "fugue", "fuga", "toccata", "fantasia",
    "fantasy", "allemande", "courante", "sarabande", "gigue", "bourree", "minuet",
    "menuet", "scherzo", "aria", "chorale", "passacaglia", "chaconne", "invention",
    "sinfonia", "overture", "adagio", "allegro", "andante", "largo", "lento",
    "presto", "vivace", "grave", "march", "waltz", "valse", "nocturne", "etude",
    "ballade", "polonaise", "mazurka", "rondo", "variation", "variations", "canon",
    "romance", "intermezzo", "bagatelle", "impromptu", "berceuse", "barcarolle",
    "sonata", "symphony", "concerto", "suite", "partita", "quartet", "trio",
    "piece", "pieces", "movement", "book", "volume", "major", "minor", "piano",
    "the", "and", "from", "with", "for", "op", "opus", "no", "number", "kinderscenen",
    "kinderszenen", "seasons", "preludes", "etudes", "songs", "lyric",
}


def _norm_key_token(letter: str, accidental: str | None, mode: str | None) -> str:
    letter = letter.lower()
    acc = (accidental or "").lower()
    if acc in {"flat", "b", "es"}:
        letter += "b"
    elif acc in {"sharp", "#", "is"}:
        letter += "s"
    mode_l = (mode or "").lower()
    if mode_l in {"minor", "min", "moll"}:
        return f"{letter}minor"
    if mode_l in {"major", "maj", "dur"}:
        return f"{letter}major"
    return letter


def _roman_to_int(raw: str) -> str | None:
    raw = raw.lower()
    table = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
             "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12}
    return str(table[raw]) if raw in table else None


def _subtitle_slug(text: str) -> str:
    """Distinctive free-text movement/sub-title, or '' if only generic form words."""
    folded = fold(text or "")
    folded = _NO_RE.sub(" ", folded)
    folded = _KEY_RE.sub(" ", folded)
    folded = re.sub(r"\b(?:op(?:us)?\.?\s*\d+)\b", " ", folded)
    for month in _MONTHS:
        folded = re.sub(rf"\b{month}\b", " ", folded)
    tokens = re.findall(r"[a-z0-9]+", folded)
    keep = [t for t in tokens if t not in _SUB_STOP and not t.isdigit() and len(t) >= 3]
    if not keep:
        return ""
    return "".join(keep)[:40]


def movement_parts(row: dict) -> dict[str, str]:
    """Typed movement identifiers for a row: no / month / key / sub.

    Drawn from title, movement and catalogue so set members (Kinderszenen
    pieces, Seasons months, Op. 28 preludes, numbered movements) stay apart
    even when they share one Op. number.
    """
    title = row.get("title") or ""
    movement = row.get("movement") or ""
    catalog = row.get("catalog") or ""
    blob = fold(f"{title} {movement} {catalog}")
    parts: dict[str, str] = {}

    nums = _NO_RE.findall(blob)
    if not nums:
        op_no = _OP_NO_RE.search(blob)
        if op_no:
            nums = [op_no.group(1)]
    if not nums:
        # Trailing / separated roman: "Préludes - Book I - XII", "I. Prelude"
        for match in _ROMAN_NO_RE.finditer(blob):
            converted = _roman_to_int(match.group(1))
            if converted:
                nums.append(converted)
    if nums:
        # Prefer the last number (usually the piece no. after Op. / suite no.)
        parts["no"] = str(int(nums[-1]))

    for name, code in _MONTHS.items():
        if re.search(rf"\b{name}\b", blob):
            parts["month"] = code
            break

    key_match = _KEY_RE.search(blob)
    if key_match:
        parts["key"] = _norm_key_token(key_match.group(1), key_match.group(2), key_match.group(3))

    # Subtitle: prefer the movement field; else the segment after ":" / " - " in the title.
    sub = _subtitle_slug(movement)
    if not sub:
        seg = title
        for sep in (" - ", " – ", " — ", ": ", "; "):
            if sep in title:
                seg = title.split(sep)[-1]
                break
        sub = _subtitle_slug(seg)
    # Avoid re-stating a lone month/key as subtitle.
    if sub and sub not in {parts.get("month", ""), parts.get("key", "")}:
        parts["sub"] = sub

    # Fall back to kind+number from movement_sig when nothing else landed.
    if not parts:
        number, kinds = movement_sig(movement or title)
        if number:
            parts["no"] = number
        if kinds:
            parts["kind"] = "-".join(kinds)
    return parts


def movement_key(row: dict) -> str:
    """Stable movement identity for dedupe buckets, or ':' when none found."""
    parts = movement_parts(row)
    if not parts:
        return ":"
    return "|".join(f"{k}:{parts[k]}" for k in sorted(parts))


def _parse_identity(value: str) -> dict[str, str]:
    if not value or value == ":":
        return {}
    return dict(p.split(":", 1) for p in value.split("|") if ":" in p)


def identities_conflict(a: str, b: str) -> bool:
    """True when movement identifiers disagree (not equal / not a refinement).

    A refinement is OK for key A: ``sub:haschemann`` may merge with
    ``no:3|sub:haschemann``. Parallel but non-overlapping ids like
    ``key:gminor`` vs ``no:6`` conflict, as do different months or Nos.
    """
    if not a or a == ":" or not b or b == ":":
        return False
    if a == b:
        return False
    da, db = _parse_identity(a), _parse_identity(b)
    for dim in set(da) & set(db):
        if da[dim] != db[dim]:
            return True
    ka, kb = set(da), set(db)
    # Neither identity is a subset of the other → distinct pieces of the set.
    if not (ka <= kb or kb <= ka):
        return True
    return False


def identities_match_or_absent(a: str, b: str) -> bool:
    """Fingerprint merges only when identities are equal, or both absent."""
    empty_a = not a or a == ":"
    empty_b = not b or b == ":"
    if empty_a and empty_b:
        return True
    if empty_a or empty_b:
        return False
    return a == b


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
    if name in ("commons", "imslp"):  # hand-vetted gap fillers never displace an id that is already live
        return 5
    return 4


def _midi_size(row: dict) -> int:
    path = ROOT / (row.get("local_score_path") or "")
    return path.stat().st_size if path.is_file() else 0


def quality(row: dict, fp: dict) -> tuple:
    pop = row.get("popularity") or ""
    rating = float((re.search(r"rating=([0-9.]+)", pop) or [0, 0])[1] or 0)
    ratings = float((re.search(r"ratings=([0-9.]+)", pop) or [0, 0])[1] or 0)
    title = row.get("title") or ""
    messy = int(bool(re.search(r"[_#*]|\b(?:wip|test|easy|simplified|arr)\b|^[a-z]", title, re.I)
                     or re.search(r"Ã|Â|(?<=[a-z])Ì|[\x80-\x9f]|[åäèæç]{3}", title)))  # mojibake: "SolfeÌge", "ååèäº"
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

    # Key A. Bucket by composer + catalogue (or title when no catalogue). Movement
    # identity is not part of the bucket key so "Op. 15" / "Op. 15 No. 3" editions of
    # the same piece can still meet; identities_conflict blocks distinct movements.
    buckets = defaultdict(list)
    for rid, (comp, cat, tkey, mov, _) in meta.items():
        if not comp:
            continue
        if cat:
            # Strip a trailing noN from opXXnoY so Op.15 and Op.15 No.3 share a bucket;
            # the piece number lives in the movement identity instead.
            cat_stem = re.sub(r"(op\d+)no\d+[a-z]?$", r"\1", cat)
            buckets[("cat", comp, cat_stem)].append(rid)
        elif len(tkey) >= 4:
            buckets[("title", comp, tkey)].append(rid)
    # A title-only row joins the one catalogued piece with the same title ("In the Hall of the Mountain King").
    titled = defaultdict(set)
    for rid, (comp, cat, tkey, mov, _) in meta.items():
        if comp and cat and len(tkey) >= 8:
            cat_stem = re.sub(r"(op\d+)no\d+[a-z]?$", r"\1", cat)
            titled[(comp, tkey)].add(("cat", comp, cat_stem))
    for key in [k for k in buckets if k[0] == "title"]:
        hits = titled.get((key[1], key[2]), set())
        if len(hits) == 1:
            target = next(iter(hits))
            if target in buckets:
                buckets[target] += buckets.pop(key)
    for bucket in buckets.values():
        for i, a in enumerate(bucket):
            for b in bucket[i + 1:]:
                if identities_conflict(meta[a][3], meta[b][3]):
                    continue  # Kinderszenen No.2 vs No.3, Seasons August vs January, …
                # Whole-work (no identity) must not absorb a multi-movement catalogue.
                mov_a, mov_b = meta[a][3], meta[b][3]
                if (mov_a == ":") != (mov_b == ":"):
                    # Allow only when the named side is the sole identity in this bucket
                    # with a titles_close match (handled below); otherwise skip.
                    named = {meta[x][3] for x in bucket if meta[x][3] != ":"}
                    if len(named) != 1:
                        continue
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
    if not a or not b:
        return True
    if a == b:
        return True
    # "prelude" in "preludeop236" is not evidence they are the same piece.
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if shorter in longer and len(shorter) >= 10:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.6


def _b_compatible(a: tuple, b: tuple) -> bool:
    _, cat_a, _, mov_a, num_a = a
    _, cat_b, _, mov_b, num_b = b
    if cat_a and cat_b and cat_a != cat_b:
        return False
    if num_a - num_b and num_b - num_a:  # "Psalm 22 part 1" vs "part 4": each title has a number the other lacks
        return False
    if identities_conflict(mov_a, mov_b):
        return False
    # Fingerprint merges only when movement ids match, or both are absent.
    if not identities_match_or_absent(mov_a, mov_b):
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
