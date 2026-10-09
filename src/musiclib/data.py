"""Catalogue access: local repo checkout first, GitHub Pages otherwise.

Lookup order for the data root:
  1. $MUSICLIB_ROOT (a checkout of LaDoger/music-library)
  2. the repo this package lives in, or any parent of the current directory
     that contains data/catalog.json
  3. $MUSICLIB_BASE or https://ladoger.github.io/music-library/ (downloads are
     cached under $MUSICLIB_CACHE or ~/.cache/musiclib)
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.request
from pathlib import Path

from musiclib import PAGES_BASE

USER_AGENT = "musiclib/0.1 (+https://github.com/LaDoger/music-library)"


def _find_root() -> Path | None:
    env = os.environ.get("MUSICLIB_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    for start in (Path(__file__).resolve(), Path.cwd().resolve()):
        for d in [start, *start.parents]:
            if (d / "data" / "catalog.json").is_file():
                return d
    return None


def fold(text: str) -> str:
    """Lowercase, strip accents: 'Dvořák' -> 'dvorak'."""
    t = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def squash(text: str) -> str:
    """'BWV 565' / 'Op. 27' -> 'bwv565' / 'op27' for catalogue-number matching."""
    return re.sub(r"[\s.,:'-]+", "", fold(text))



def pick_rank(item):
    """Editor's pick rank (1 = best, 0 = not a pick). Older catalogues used top_pick_rank."""
    return item.get("editors_pick_rank", item.get("top_pick_rank", 0)) or 0

class Library:
    def __init__(self):
        self.root = _find_root()
        self.base = os.environ.get("MUSICLIB_BASE", PAGES_BASE).rstrip("/") + "/"
        self.cache = Path(os.environ.get("MUSICLIB_CACHE", "~/.cache/musiclib")).expanduser()
        self._catalog = None

    @property
    def source(self) -> str:
        return str(self.root) if self.root else self.base

    # ---- fetching -------------------------------------------------------
    def fetch(self, url: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        tmp = dest.with_name(dest.name + ".part")
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 16):
                f.write(chunk)
        tmp.replace(dest)
        return dest

    def _json(self, rel: str):
        if self.root:
            return json.loads((self.root / rel).read_text(encoding="utf-8"))
        req = urllib.request.Request(self.base + rel, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))

    def local_file(self, rel: str) -> Path:
        """Repo-relative path (files/scores/..., previews/...) -> local file, downloading if needed."""
        if self.root and (self.root / rel).is_file():
            return self.root / rel
        dest = self.cache / rel
        if not dest.is_file():
            self.fetch(self.base + rel, dest)
        return dest

    # ---- catalogue ------------------------------------------------------
    def catalog(self) -> dict:
        if self._catalog is None:
            self._catalog = self._json("data/catalog.json")
        return self._catalog

    def items(self) -> list[dict]:
        return self.catalog()["items"]

    def get(self, item_id: str) -> dict:
        ids = {i["id"] for i in self.items()}
        if item_id not in ids:
            close = [i for i in sorted(ids) if item_id.lower() in i]
            hint = f" Did you mean: {', '.join(close[:5])}?" if close else " Try: musiclib search <words>"
            raise KeyError(f"unknown id {item_id!r}.{hint}")
        return self._json(f"data/items/{item_id}.json")

    def search(self, query: str = "", *, genre=None, composer=None, mood=None, energy=None,
               licence=None, has_score=False, has_recording=False, renderable=False,
               verified=False, top=False) -> list[dict]:
        tokens = fold(query).split()
        out = []
        for it in self.items():
            if genre and it["genre"] != genre:
                continue
            if composer and fold(composer) not in fold(it["composer"]):
                continue
            if mood and fold(mood) not in [fold(m) for m in it["mood"]]:
                continue
            if energy and it["energy"] != energy:
                continue
            if licence and it["licence_status"] not in licence:
                continue
            if has_score and not it["has_editable_score"]:
                continue
            if has_recording and not it["has_recording"]:
                continue
            if renderable and not it["renderable_midi"]:
                continue
            if verified and it["verified"] != "yes":
                continue
            if top and not pick_rank(it):
                continue
            blob = fold(" ".join([it["id"].replace("_", " "), it["title"], it["composer"], it["catalog"],
                                  it["movement"], it["genre"], it["era"], " ".join(it["mood"])]))
            flat = squash(blob)
            if all(t in blob or squash(t) in flat for t in tokens):
                out.append(it)
        if top:
            out.sort(key=pick_rank)
        return out
