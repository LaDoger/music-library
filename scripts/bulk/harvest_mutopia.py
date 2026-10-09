#!/usr/bin/env python3
"""Harvest Mutopia LilyPond headers into a candidate CSV.

Clones https://github.com/MutopiaProject/MutopiaProject (about 25 MB; sources
only, no MIDI) unless --repo points at an existing checkout. MIDI, when the
website has rendered it, lives at the same relative path under
https://www.mutopiaproject.org/ftp/ with a .mid suffix. The candidate stores
that URL. Download happens later and skips anything that is not actually there.

Each piece keeps the copyright / license string from its own header. Public
domain and CC BY are licence-clean. CC BY-SA is kept and marked sharealike.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from schema import (  # noqa: E402
    CANDIDATE_COLUMNS,
    blank_candidate,
    catalog_from_text,
    classify_license,
    combine_status,
    composer_record,
    composition_status,
    era_for,
    match_composer,
    mood_tags,
    parse_year,
    quality_penalty,
    source_rank,
    tempo_energy,
    video_use,
)

ROOT = Path(__file__).resolve().parents[2]
REPO_URL = "https://github.com/MutopiaProject/MutopiaProject.git"
FTP = "https://www.mutopiaproject.org/ftp"
MUTOPIA_CODES = {
    "BachJS": "johann sebastian bach",
    "BachCPE": "carl philipp emanuel bach",
    "BeethovenLv": "ludwig van beethoven",
    "MozartWA": "wolfgang amadeus mozart",
    "ChopinFF": "frederic chopin",
    "DebussyC": "claude debussy",
    "BrucknerA": "anton bruckner",
    "WagnerR": "richard wagner",
    "MahlerG": "gustav mahler",
    "SchubertF": "franz schubert",
    "BrahmsJ": "johannes brahms",
    "SchumannR": "robert schumann",
    "HaydnFJ": "joseph haydn",
    "HaydnJM": "johann michael haydn",
    "HandelGF": "george frideric handel",
    "VivaldiA": "antonio vivaldi",
    "LisztF": "franz liszt",
    "TchaikovskyPI": "pyotr ilyich tchaikovsky",
    "DvorakA": "antonin dvorak",
    "FaureG": "gabriel faure",
    "FranckC": "cesar franck",
    "SatieE": "erik satie",
    "RavelM": "maurice ravel",
    "ScriabinA": "alexander scriabin",
    "CouperinF": "francois couperin",
    "RameauJP": "jean philippe rameau",
    "BuxtehudeD": "dieterich buxtehude",
    "AlkanCV": "charles valentin alkan",
    "GesualdoC": "carlo gesualdo",
    "ByrdW": "william byrd",
    "FrescobaldiG": "girolamo frescobaldi",
    "RegerM": "max reger",
    "PurcellH": "henry purcell",
    "ScarlattiD": "domenico scarlatti",
    "TelemannGP": "georg philipp telemann",
    "Mendelssohn-BartholdyF": "felix mendelssohn",
    "GriegE": "edvard grieg",
    "Saint-SaensC": "camille saint saens",
    "BizetG": "georges bizet",
    "VerdiG": "giuseppe verdi",
    "PachelbelJ": "johann pachelbel",
    "CorelliA": "arcangelo corelli",
    "MussorgskyM": "modest mussorgsky",
    "Rimsky-KorsakovN": "nikolai rimsky korsakov",
    "BorodinA": "alexander borodin",
    "HolstGT": "gustav holst",
    "ElgarE": "edward elgar",
    "RachmaninoffS": "sergei rachmaninoff",
    "BartokB": "bela bartok",
    "GershwinG": "george gershwin",
    "JoplinS": "scott joplin",
    "StraussR": "richard strauss",
    "StraussJJ": "johann strauss ii",
    "DukasP": "paul dukas",
    "RossiniG": "gioachino rossini",
    "DonizettiG": "gaetano donizetti",
    "GounodC": "charles gounod",
    "HumperdinckE": "engelbert humperdinck",
    "GottschalkLM": "louis moreau gottschalk",
    "FieldJ": "john field",
    "ClementiM": "muzio clementi",
    "FosterSC": "stephen foster",
    "DowlandJ": "john dowland",
    "MonteverdiC": "claudio monteverdi",
    "LullyJB": "jean baptiste lully",
    "PergolesiGB": "giovanni battista pergolesi",
    "PaganiniN": "niccolo paganini",
    "SorF": "fernando sor",
    "TarregaF": "francisco tarrega",
    "GiulianiM": "mauro giuliani",
    "FrobergerJJ": "johann jakob froberger",
    "CharpentierMA": "marc antoine charpentier",
    "ChabrierEA": "emmanuel chabrier",
    "SousaJP": "john philip sousa",
    "Traditional": "traditional",
    "Anonymous": "anonymous",
}


def _strip_comments(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_string:
            out.append(ch)
            if ch == "\\" and nxt:
                out.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "%" and nxt == "{":
            end = text.find("%}", i + 2)
            i = n if end < 0 else end + 2
            out.append(" ")
            continue
        if ch == "%":
            end = text.find("\n", i)
            i = n if end < 0 else end
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _header_block(text: str) -> str:
    cleaned = _strip_comments(text)
    match = re.search(r"\\header\b", cleaned)
    if not match:
        return cleaned[:4000]
    i = cleaned.find("{", match.end())
    if i < 0:
        return cleaned[:4000]
    depth = 0
    for j in range(i, len(cleaned)):
        if cleaned[j] == "{":
            depth += 1
        elif cleaned[j] == "}":
            depth -= 1
            if depth == 0:
                return cleaned[i:j + 1]
    return cleaned[i:i + 8000]


def _assign(header: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*=\s*\"([^\"]*)\"", header)
    return match.group(1).strip() if match else ""


def _piece_id(header: str) -> str:
    match = re.search(r"Mutopia-\d{4}/\d{2}/\d{2}-(\d+)", header)
    return match.group(1) if match else ""


def _licence_text(header: str) -> str:
    parts = [
        _assign(header, "copyright"),
        _assign(header, "license"),
        _assign(header, "licence"),
    ]
    blob = " ".join(part for part in parts if part)
    if blob.strip():
        return blob
    # Markup copyright: keep a short slice that still contains the licence words.
    for phrase in (
        "Attribution-ShareAlike", "Attribution", "Public Domain", "ShareAlike",
        "public domain", "CC-BY", "BY-SA",
    ):
        if phrase.lower() in header.lower():
            return header
    return blob


def _should_skip(path: Path) -> bool:
    name = path.name.lower()
    if "header" in name or name.startswith("part-") or name.startswith("common"):
        return True
    parts = {part.lower() for part in path.parts}
    if "common" in parts:
        return True
    return False


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _borrow_header(path: Path, header: str) -> str:
    if _licence_text(header).strip() and _assign(header, "mutopiatitle"):
        return header
    extra = []
    for folder in [path.parent, *path.parents]:
        if folder.name == "ftp":
            break
        for sibling in sorted(folder.glob("*header*.ly"))[:4]:
            extra.append(_header_block(_read(sibling)[:20000]))
        if extra and _licence_text(header + "\n" + "\n".join(extra)).strip():
            break
        if folder.parent.name == "ftp":
            break
    return header + "\n" + "\n".join(extra)


def ensure_repo(dest: Path) -> Path:
    if (dest / "ftp").is_dir():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        ["git", "clone", "--depth", "1", REPO_URL, str(dest)],
    )
    return dest


def harvest(repo: Path) -> list[dict]:
    ftp = repo / "ftp"
    rows = []
    for path in sorted(ftp.rglob("*.ly")):
        if _should_skip(path):
            continue
        text = _read(path)
        if "mutopiatitle" not in text and "mutopiaopus" not in text:
            continue
        header = _borrow_header(path, _header_block(text[:30000]))
        title = _assign(header, "mutopiatitle") or _assign(header, "title")
        if not title:
            continue
        code = _assign(header, "mutopiacomposer")
        human = _assign(header, "composer")
        years = re.search(r"(\d{4})\s*[-–]\s*(\d{4})", human)
        death = int(years.group(2)) if years else None
        canon = MUTOPIA_CODES.get(code) or match_composer(human) or ""
        if not canon and code:
            canon = match_composer(code)
        if not canon:
            canon = match_composer(human) or "unknown"
        from schema import COMPOSERS
        rec = composer_record(canon, re.sub(r"\s*\(.*?\)", "", human).strip() if human else code, death)
        if death is None:
            death = rec["death"]
        if canon in COMPOSERS:
            display = COMPOSERS[canon]["name"]
        else:
            display = re.sub(r"\s*\(.*?\)", "", human).strip() or rec["name"] or code or "Unknown"
        opus = _assign(header, "mutopiaopus") or _assign(header, "opus")
        subtitle = _assign(header, "subtitle")
        instrument = _assign(header, "mutopiainstrument")
        style = _assign(header, "style")
        maintainer = _assign(header, "maintainer")
        piece_id = _piece_id(header)
        licence_blob = _licence_text(header)
        short, edition_class = classify_license(licence_blob)
        comp_class, comp_note = composition_status(canon, death)
        # Traditional / Anonymous only stay clean when the edition itself is PD or CC0.
        if canon in {"traditional", "anonymous"} and edition_class != "clean":
            comp_class = edition_class
        licence_class = combine_status(edition_class, comp_class)
        rel = path.relative_to(ftp).with_suffix(".mid").as_posix()
        movement = subtitle
        if not movement:
            # The mutopia title often already names the movement ("Praeludium I").
            movement = ""
            if re.search(r"prelude|fugue|praeludium|allegro|adagio|bourree|gigue|sarabande", title, re.I):
                movement = title
        catalog = catalog_from_text(opus, title, path.parent.name) or opus
        row = blank_candidate()
        row.update({
            "composer": display,
            "death_year": "" if death is None else str(death),
            "title": title,
            "catalog": catalog,
            "movement": movement,
            "mood_tags": mood_tags(title, movement, style),
            "tempo_energy": tempo_energy(title, movement),
            "notable_excerpt": "Own MIDI render 00:00-00:15 (opening)",
            "editable_source_url": (
                f"https://www.mutopiaproject.org/cgibin/piece-info.cgi?id={piece_id}"
                if piece_id else f"{FTP}/{path.relative_to(ftp).parent.as_posix()}/"
            ),
            "editable_format": "MIDI; LilyPond",
            "editable_license": short,
            "legal_notes": (
                f"{comp_note} Mutopia header licence: {licence_blob[:240]}. "
                f"Piece id {piece_id or 'unknown'}. "
                + (f"CC BY credit: {maintainer} and the Mutopia Project. " if short == "CC-BY" and maintainer else "")
                + "MIDI, when present, is the Mutopia FTP render of this LilyPond file, not a performance. "
                "Preview is an own FluidSynth (FluidR3_GM) render, 15 seconds, fades, loudness-normalised. "
                f"source_rank pending. Instrumentation: {instrument or 'unspecified'}."
            ),
            "source_name": "mutopia",
            "licence_class": licence_class,
            "instrumentation": instrument,
            "popularity": "",
            "genre": "classical",
            "era": era_for(display, death),
            "download_url": f"{FTP}/{rel}",
            "repo_path": path.relative_to(repo).as_posix(),
            "external_id": piece_id,
            "canon": canon,
        })
        penalty = quality_penalty(canon, title, movement, instrument)
        row["quality_penalty"] = str(penalty)
        try:
            rating = 0.0
            n_ratings = 0
        except ValueError:
            rating, n_ratings = 0.0, 0
        row["source_rank"] = str(source_rank("mutopia", licence_class, rating, n_ratings))
        row["video_use_ideas"] = video_use(row["mood_tags"])
        row["verified"] = "yes" if licence_class in {"clean", "attribution", "sharealike"} else "unverified"
        if piece_id:
            row["id"] = ""  # merge allocates a non-colliding id
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Harvest Mutopia piece headers")
    parser.add_argument("--repo", type=Path, default=ROOT / ".tmp" / "bulk" / "MutopiaProject")
    parser.add_argument("--out", type=Path, default=ROOT / "parts" / "bulk_raw" / "mutopia.csv")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    repo = ensure_repo(args.repo)
    sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    rows = harvest(repo)
    if args.limit:
        rows = rows[:args.limit]
    for row in rows:
        row["legal_notes"] += f" Mutopia git {sha[:12]}."
    write_csv(args.out, rows)
    from collections import Counter
    counts = Counter(row["licence_class"] for row in rows)
    print(f"mutopia rows {len(rows)} -> {args.out}")
    print("classes", dict(counts))
    print("commit", sha)


if __name__ == "__main__":
    main()
