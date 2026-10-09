#!/usr/bin/env python3
"""Normalize composer / catalogue / movement and pick the best source.

Dedup key = canon(composer) + normalized catalogue + movement signature.
When the catalogue is missing, the key uses a title slug so two songs by the
same composer do not collapse. An existing library row blocks a candidate when
the catalogue matches and the movement labels are compatible (Prelude vs
Prelude 1 of the same BWV), or when a long distinctive title token matches.

Merge preference (lower source_rank, then lower quality_penalty, then higher
popularity): OpenScore, Mutopia PD, Mutopia CC BY, high-rated PDMX, other PDMX.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema import (  # noqa: E402
    CLASS_ORDER,
    composer_record,
    distinctive_tokens,
    fold,
    match_composer,
    movements_compatible,
    normalize_catalog,
    parse_year,
    slugify,
)


def canon_name(composer: str) -> str:
    hit = match_composer(composer)
    if hit:
        return hit
    text = fold(composer)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\b(1[4-9]\d{2}|20\d{2})\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def movement_label(movement: str) -> str:
    number, kinds = _sig(movement)
    if kinds and number:
        return number + "-" + "-".join(kinds)
    if kinds:
        return "-".join(kinds)
    if number:
        return "no" + number
    return re.sub(r"[^a-z0-9]", "", fold(movement))[:32]


def _sig(movement: str):
    from schema import movement_sig
    return movement_sig(movement)


def dedup_key(composer: str, catalog: str, title: str, movement: str) -> str:
    canon = canon_name(composer)
    cat = normalize_catalog(catalog)
    mov = movement_label(movement)
    if not cat:
        cat = "t" + slugify(title, 60).replace("_", "")
    return f"{canon}|{cat}|{mov}"


def popularity_value(text: str) -> float:
    if not text:
        return 0.0
    match = re.search(r"rating=([0-9.]+)", text)
    rating = float(match.group(1)) if match else 0.0
    fav = re.search(r"favorites=([0-9.]+)", text)
    favorites = float(fav.group(1)) if fav else 0.0
    return rating * 10 + min(favorites, 50)


def better(left: dict, right: dict) -> dict:
    """Return the preferred candidate. Lower rank, then lower penalty, then popularity."""
    def key(row):
        try:
            rank = int(row.get("source_rank") or 99)
        except ValueError:
            rank = 99
        try:
            penalty = int(row.get("quality_penalty") or 0)
        except ValueError:
            penalty = 0
        klass = row.get("licence_class") or "unverified"
        class_rank = CLASS_ORDER.index(klass) if klass in CLASS_ORDER else 9
        return (rank, penalty, class_rank, -popularity_value(row.get("popularity") or ""))

    return left if key(left) <= key(right) else right


class ExistingIndex:
    def __init__(self):
        self.ids = set()
        self.strict = set()
        self.by_catalog = {}  # (canon, catalog) -> list of movement strings
        self.tokens = {}  # canon -> set of tokens
        self.stems = set()

    def add_row(self, row: dict):
        ident = (row.get("id") or "").strip()
        if ident:
            self.ids.add(ident)
            self.stems.add(ident)
        composer = row.get("composer") or ""
        canon = canon_name(composer)
        catalog = row.get("catalog") or ""
        title = row.get("title") or ""
        movement = row.get("movement") or ""
        self.strict.add(dedup_key(composer, catalog, title, movement))
        cat = normalize_catalog(catalog)
        if cat:
            self.by_catalog.setdefault((canon, cat), []).append(movement)
        self.tokens.setdefault(canon, set()).update(distinctive_tokens(title, movement))
        for path in (row.get("local_score_path") or "", row.get("preview_path") or ""):
            if path:
                self.stems.add(Path(path).stem)

    def add_stem(self, stem: str):
        if stem:
            self.stems.add(stem)


def load_csv_rows(paths) -> list[dict]:
    rows = []
    for path in paths:
        path = Path(path)
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(list(csv.DictReader(handle)))
    return rows


def existing_from_paths(paths) -> ExistingIndex:
    index = ExistingIndex()
    for row in load_csv_rows(paths):
        index.add_row(row)
    return index


def is_duplicate(row: dict, index: ExistingIndex) -> str:
    """Return a short reason if this candidate is already in the library, else ''."""
    ident = (row.get("id") or "").strip()
    if ident and ident in index.ids:
        return "id"
    composer = row.get("composer") or ""
    canon = row.get("canon") or canon_name(composer)
    catalog = row.get("catalog") or ""
    title = row.get("title") or ""
    movement = row.get("movement") or ""
    if dedup_key(composer, catalog, title, movement) in index.strict:
        return "key"
    cat = normalize_catalog(catalog)
    if cat and (canon, cat) in index.by_catalog:
        for existing_movement in index.by_catalog[(canon, cat)]:
            if movements_compatible(movement, existing_movement):
                return "catalog+movement"
    tokens = distinctive_tokens(title, movement)
    long_tokens = {token for token in tokens if len(token) >= 8}
    overlap = long_tokens & index.tokens.get(canon, set())
    if overlap and (not cat or (canon, cat) in index.by_catalog or not normalize_catalog(catalog)):
        # Same work title, and catalogues do not contradict.
        if not cat or (canon, cat) in index.by_catalog:
            # Require the overlap to be a title token, not only a shared genre word.
            if any(len(token) >= 8 for token in overlap):
                # Do not treat a whole cycle as one work: the token must be
                # almost the entire folded title or movement, so "erlkonig"
                # matches and "winterreise" on a different song does not
                # unless that song's own slug is already present.
                folded_title = re.sub(r"[^a-z0-9]", "", fold(title))
                folded_mov = re.sub(r"[^a-z0-9]", "", fold(movement))
                for token in overlap:
                    if token in {folded_title, folded_mov} or folded_title.endswith(token) or folded_mov.endswith(token):
                        if not cat or (canon, cat) in index.by_catalog:
                            return "title"
    return ""


def id_taken(ident: str, index: ExistingIndex, used: set[str]) -> bool:
    if not ident or ident in used or ident in index.ids:
        return True
    for stem in index.stems | used:
        if ident == stem or ident.startswith(stem + "_") or stem.startswith(ident + "_"):
            return True
    return False


def allocate_id(base: str, index: ExistingIndex, used: set[str]) -> str:
    base = slugify(base, 72)
    if not base:
        base = "piece"
    candidate = base
    n = 2
    while id_taken(candidate, index, used):
        candidate = f"{base}b{n}"
        n += 1
        if n > 50:
            candidate = f"{base}b{n}"
            break
    used.add(candidate)
    return candidate


def merge_rows(rows: list[dict], index: ExistingIndex | None = None) -> tuple[list[dict], dict]:
    """Collapse to the best row per dedup key. Drop rows already in `index`."""
    index = index or ExistingIndex()
    best: dict[str, dict] = {}
    by_cat: dict[tuple[str, str], list[str]] = {}
    stats = {
        "in": len(rows),
        "existing": 0,
        "collapsed": 0,
        "excluded": 0,
        "kept": 0,
    }
    for row in rows:
        klass = row.get("licence_class") or ""
        if klass == "excluded":
            stats["excluded"] += 1
            continue
        if is_duplicate(row, index):
            stats["existing"] += 1
            continue
        key = row.get("dedup_key") or dedup_key(
            row.get("composer", ""), row.get("catalog", ""),
            row.get("title", ""), row.get("movement", ""),
        )
        row["dedup_key"] = key
        canon = row.get("canon") or canon_name(row.get("composer", ""))
        catalog_norm = normalize_catalog(row.get("catalog") or "")
        match_key = ""
        if catalog_norm:
            for existing_key in by_cat.get((canon, catalog_norm), []):
                existing = best[existing_key]
                if movements_compatible(row.get("movement") or "", existing.get("movement") or ""):
                    match_key = existing_key
                    break
        if match_key:
            stats["collapsed"] += 1
            best[match_key] = better(best[match_key], row)
        else:
            best[key] = row
            if catalog_norm:
                by_cat.setdefault((canon, catalog_norm), []).append(key)
    used = set()
    kept = []
    for row in best.values():
        if not row.get("id") or id_taken(row["id"], index, used):
            rec = composer_record(row.get("canon") or canon_name(row.get("composer", "")))
            prefix = rec["prefix"]
            cat = normalize_catalog(row.get("catalog") or "")[:22]
            mov = slugify(row.get("movement") or row.get("title") or "", 28)
            base = "_".join(part for part in (prefix, cat, mov) if part)
            row["id"] = allocate_id(base, index, used)
        else:
            used.add(row["id"])
        kept.append(row)
    kept.sort(key=lambda row: (
        int(row.get("source_rank") or 99),
        int(row.get("quality_penalty") or 0),
        row.get("composer") or "",
        row.get("catalog") or "",
        row.get("title") or "",
    ))
    stats["kept"] = len(kept)
    return kept, stats


def _self_test():
    from schema import classify_license, source_rank as rank_of

    assert classify_license("Public Domain") == ("PD", "clean")
    assert classify_license("Creative Commons Attribution-ShareAlike 4.0")[1] == "sharealike"
    assert classify_license("Creative Commons Attribution 4.0") == ("CC-BY", "attribution")
    assert classify_license("CC BY-NC-SA 4.0")[1] == "excluded"
    assert classify_license("cc-zero")[0] == "CC0"
    assert match_composer("J. S. Bach") == "johann sebastian bach"
    assert match_composer("C.P.E. Bach") == "carl philipp emanuel bach"
    assert match_composer("Joahnn Sebastian Bach") == "johann sebastian bach"
    assert match_composer("Craude.A.Debussy") == "claude debussy"
    assert match_composer("Arr from Franz Schubert by W.W. Gilchrist 1895") == "franz schubert"
    assert movements_compatible("Prelude", "Prelude 1")
    assert movements_compatible("Bourrée I", "Bourree 1")
    assert not movements_compatible("Bourrée I", "Bourrée II")
    assert not movements_compatible("Prelude", "Fugue")
    assert not movements_compatible("", "I. Allegro")
    left = dedup_key("Johann Sebastian Bach", "BWV 846", "WTC", "Prelude")
    right = dedup_key("BachJS", "BWV846", "Prelude", "Prelude")
    assert left == right, (left, right)
    numbered = dedup_key("BachJS", "BWV 846", "WTC", "Prelude 1")
    assert numbered != left
    assert movements_compatible("Prelude", "Prelude 1")
    assert rank_of("openscore-lieder", "clean") < rank_of("mutopia", "clean")
    assert rank_of("mutopia", "clean") < rank_of("pdmx", "clean", 4.8, 5)
    assert rank_of("pdmx", "clean", 4.8, 5) < rank_of("pdmx", "clean", 0, 0)
    a = {"source_rank": "1", "quality_penalty": "0", "licence_class": "clean", "popularity": "", "id": "a"}
    b = {"source_rank": "2", "quality_penalty": "0", "licence_class": "clean", "popularity": "rating=5", "id": "b"}
    assert better(a, b)["id"] == "a"
    index = ExistingIndex()
    index.add_row({
        "id": "bach_bwv846_prelude",
        "composer": "Johann Sebastian Bach",
        "catalog": "BWV 846",
        "title": "Well-Tempered Clavier: Prelude in C major",
        "movement": "Prelude",
        "local_score_path": "files/scores/bach_bwv846_prelude.mid",
    })
    candidate = {
        "composer": "Johann Sebastian Bach",
        "canon": "johann sebastian bach",
        "catalog": "BWV 846",
        "title": "Das Wohltemperierte Clavier I",
        "movement": "Prelude 1",
        "licence_class": "clean",
        "source_rank": "2",
        "quality_penalty": "0",
        "id": "bach_bwv846_prelude",
    }
    assert is_duplicate(candidate, index) in {"id", "key", "catalog+movement"}
    fugue = dict(candidate, movement="Fugue", id="bach_bwv846_fugue_new", title="Fugue 1")
    # id is new, catalogue matches, movement is not compatible with Prelude
    assert is_duplicate(fugue, index) == ""
    print("dedup self-test ok")


def main():
    parser = argparse.ArgumentParser(description="Dedup helpers and self-test")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--key", nargs=4, metavar=("COMPOSER", "CATALOG", "TITLE", "MOVEMENT"))
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if args.key:
        print(dedup_key(*args.key))
        return
    parser.print_help()


if __name__ == "__main__":
    main()
