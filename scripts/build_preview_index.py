#!/usr/bin/env python3
"""Build previews/index.html from library.csv (falls back to parts/*_rows.csv
if library.csv is absent) plus any extra preview MP3s.

Paths in the page are relative to previews/index.html. Regenerate after
library.csv changes:

    python3 scripts/build_preview_index.py
"""
from __future__ import annotations

import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "parts"
LIBRARY = ROOT / "library.csv"
PREVIEWS = ROOT / "previews"
OUT = PREVIEWS / "index.html"

FIELDS = (
    "id",
    "composer",
    "title",
    "movement",
    "mood_tags",
    "tempo_energy",
    "preview_path",
    "added_by",
    "recording_license",
    "editable_license",
    "verified",
)


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def load_rows() -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    sources = [LIBRARY] if LIBRARY.is_file() else sorted(PARTS.glob("*_rows.csv"))
    for path in sources:
        with path.open(newline="", encoding="utf-8") as handle:
            for record in csv.DictReader(handle):
                key = (record.get("id") or "").strip() or (record.get("preview_path") or "")
                if not key or key in seen:
                    continue
                seen.add(key)
                rows.append(record)
    known_previews = set()
    for record in rows:
        preview = (record.get("preview_path") or "").strip()
        if preview:
            known_previews.add(Path(preview).name)
    if PREVIEWS.is_dir():
        for mp3 in sorted(PREVIEWS.glob("*.mp3")):
            if mp3.name in known_previews:
                continue
            stem = mp3.stem.replace("_", " ")
            rows.append(
                {
                    "id": mp3.stem,
                    "composer": "",
                    "title": stem,
                    "movement": "",
                    "mood_tags": "",
                    "tempo_energy": "",
                    "preview_path": f"previews/{mp3.name}",
                    "added_by": "",
                }
            )
    rows.sort(key=lambda r: (
        (r.get("composer") or "zzz").lower(),
        (r.get("title") or "").lower(),
        (r.get("id") or "").lower(),
    ))
    return rows


def audio_src(preview_path: str) -> str:
    name = Path(preview_path).name
    if name and (PREVIEWS / name).is_file():
        return name
    return ""


def render(rows: list[dict]) -> str:
    body = []
    for record in rows:
        moods = [m.strip() for m in (record.get("mood_tags") or "").split(";") if m.strip()]
        pills = "".join(f'<span class="tag">{esc(m)}</span>' for m in moods)
        movement = (record.get("movement") or "").strip()
        title = (record.get("title") or record.get("id") or "Untitled").strip()
        if movement:
            title = f"{title} — {movement}"
        composer = (record.get("composer") or "").strip()
        tempo = (record.get("tempo_energy") or "").strip()
        added = (record.get("added_by") or "").strip()
        src = audio_src(record.get("preview_path") or "")
        if src:
            player = f'<audio controls preload="none" src="{esc(src)}"></audio>'
        else:
            player = '<span class="missing">no preview file</span>'
        meta_bits = [b for b in (composer, tempo, added) if b]
        lic = []
        if (record.get("recording_license") or "").strip():
            lic.append("rec: " + record["recording_license"].strip())
        if (record.get("editable_license") or "").strip():
            lic.append("score: " + record["editable_license"].strip())
        if (record.get("verified") or "yes").strip() != "yes":
            lic.append("verified: " + record["verified"].strip())
        search = " ".join([
            record.get("id") or "",
            composer,
            record.get("title") or "",
            movement,
            record.get("mood_tags") or "",
            tempo,
            added,
        ]).lower()
        body.append(
            f'<article class="row" data-search="{esc(search)}">'
            f'<div class="meta"><h2>{esc(title)}</h2>'
            f'<p class="by">{esc(" · ".join(meta_bits))}</p>'
            f'<div class="tags">{pills}</div>'
            f'<p class="lic">{esc(" | ".join(lic))}</p></div>'
            f'<div class="play">{player}</div></article>'
        )
    count = len(rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Music library previews</title>
<style>
  :root {{
    color-scheme: dark;
    --bg: #12141c;
    --card: #1c2030;
    --line: #2c3348;
    --text: #ebe6dc;
    --muted: #a39b90;
    --gold: #d4b483;
    --tag: #2a3148;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 16px/1.45 Georgia, "Iowan Old Style", Palatino, serif;
  }}
  header {{
    padding: 2rem 1.25rem 1rem;
    max-width: 980px;
    margin: 0 auto;
  }}
  h1 {{
    font-weight: 500;
    font-size: 1.8rem;
    margin: 0 0 0.35rem;
    letter-spacing: 0.01em;
  }}
  header p {{ margin: 0; color: var(--muted); }}
  .tools {{
    max-width: 980px;
    margin: 0 auto;
    padding: 0.75rem 1.25rem 0.25rem;
  }}
  input[type="search"] {{
    width: 100%;
    background: var(--card);
    color: var(--text);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.65rem 0.8rem;
    font: inherit;
  }}
  main {{
    max-width: 980px;
    margin: 0 auto;
    padding: 0.5rem 1.25rem 3rem;
  }}
  article.row {{
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(220px, 340px);
    gap: 0.75rem 1.25rem;
    align-items: center;
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--line);
  }}
  h2 {{
    font-size: 1.05rem;
    font-weight: 500;
    margin: 0;
  }}
  .by {{ margin: 0.15rem 0 0.35rem; color: var(--muted); font-size: 0.92rem; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 0.35rem; }}
  .tag {{
    background: var(--tag);
    color: var(--gold);
    border-radius: 999px;
    padding: 0.1rem 0.55rem;
    font: 0.75rem/1.4 ui-sans-serif, system-ui, sans-serif;
    letter-spacing: 0.02em;
  }}
  audio {{ width: 100%; height: 36px; }}
  .lic {{ margin: 0.35rem 0 0; color: var(--muted); font: 0.75rem/1.35 ui-sans-serif, system-ui, sans-serif; }}
  .missing {{ color: var(--muted); font-size: 0.9rem; }}
  footer {{
    max-width: 980px;
    margin: 0 auto;
    padding: 0 1.25rem 2rem;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  @media (max-width: 700px) {{
    article.row {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Music library previews</h1>
  <p>{count} pieces. About 15 seconds each. Check the license line and README.md before publishing.</p>
</header>
<div class="tools">
  <input id="q" type="search" placeholder="Filter by composer, title, or mood" aria-label="Filter pieces">
</div>
<main id="list">
{"".join(body)}
</main>
<footer>Regenerate with <code>python3 scripts/build_preview_index.py</code>.</footer>
<script>
  const q = document.getElementById("q");
  const rows = Array.from(document.querySelectorAll("article.row"));
  q.addEventListener("input", () => {{
    const needle = q.value.trim().toLowerCase();
    for (const row of rows) {{
      row.hidden = needle && !row.dataset.search.includes(needle);
    }}
  }});
</script>
</body>
</html>
"""


def main() -> None:
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    OUT.write_text(render(rows), encoding="utf-8")
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
