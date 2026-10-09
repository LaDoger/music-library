# UI: composer-first, full play, in-browser synth (2026-10-09)

Brief: `briefs/BRIEF_ui_composer_fullplay.md`. Owner files: `index.html`, `assets/*`, `data/composers.json`,
sync/catalog scripts, docs scrub. Batch-1 rows/files untouched apart from the generic `video_use_ideas` merge.

## Views and URL state
| URL | view |
|---|---|
| `/` (or `?view=composers`) | A–Z composer index: portrait or monogram, life dates, era, works / scores / recordings. Filters (genre, era, licence, score toggle…) narrow the index and its counts. Letter bar jumps. |
| `?composer=<full name>` | composer page: hero (portrait, dates, era, counts, portrait licence link) + that composer's works sorted by **catalogue number** (`Intl.Collator` numeric: BWV 208 < BWV 1007). Cards drop the repeated composer name and lead with the title. |
| `?view=works` | all works. Cards: composer (serif, primary) → title → catalogue (mono). Default sort composer → catalogue → title (`composer_sort` = "Bach, Johann Sebastian", "Strauss II, Johann"). |
| `?picks=1` | editor's picks in rank order (implies works view). |
| `?id=<id>` | detail drawer on top of any view. |
Other params as before: `q genre mood era energy licence rec verified score sort page`; `layout=list` (old `?view=list|grid` links are mapped). Typing a search switches to works.

## Player (one source at a time)
- Modes per piece: **Preview** (15 s), **Full recording**, **Synth render** (pre-rendered FluidSynth MP3), **Live MIDI synth**. Drawer "Listen" grid + sticky player segmented switch; badges `Preview · 15 s` / `Recording` / `Synth render · FluidSynth` / `Live MIDI synth`.
- Full: sources tried in order `stream_audio_url` → `release_audio_url`; on failure of both the player shows *Download / open recording*. Seek bar (click + arrow keys, 5 s steps), time / duration.
- One `Audio` element; the MIDI player is halted on every switch and the audio element is released while MIDI plays.
- Live MIDI: `assets/vendor/midi-player.bundle.js` (jsDelivr combine of Tone 14.7.58 + @magenta/music 1.23.1 core + html-midi-player 1.5.0; MIT / Apache-2.0 / BSD-2) is lazy-loaded on first use. Uses `core.SoundFontPlayer` with the Magenta SGM+ soundfont from storage.googleapis.com (loaded per instrument; not redistributed). Tempo 50–150 % rescales the NoteSequence and restarts at the same score position. Piano roll = `core.PianoRollSVGVisualizer` in the drawer. Position is tracked with `performance.now()` (start/stop with offset), not Tone transport.
- The sticky player sits above the drawer (z 60) and is part of the drawer's Tab cycle, so it stays operable; the dialog is therefore not `aria-modal`, but the background is `inert`.

## Data
- `scripts/video_ideas.py`: curated generic `video_use_ideas` (75 originals + niche batch rows), merge-by-id CSV rewrite (keeps CRLF, refuses to write if the CSV changed meanwhile); `sync_site_data.py` applies the same overrides and warns on niche wording.
- `scripts/fetch_composer_meta.py` → `data/cache/composer_meta.json`: Wikidata (name search, death year must match CSV) for birth/death, P18 portrait kept only if Commons extmetadata licence is Public domain / CC0 (42/47; Satie and Buxtehude portraits are CC BY-SA → monogram; Grieg's is "No restrictions" → monogram).
- `scripts/resolve_streams.py` → `data/cache/stream_audio.json`: Commons `videoinfo.derivatives` MP3 transcode (else original audio), archive.org `VBR MP3` derivative of the file matched by byte size. Must answer a ranged GET and match the local file's duration within 3 s (Elgar rejected: Commons file 5:46 vs local 8:02). 61/64 recordings.
- `scripts/build_midi_play.py` → `files/midi_play/<id>.mid` for zip-only (Dvořák 9, Pictures) and MusicXML-only rows (MuseScore 3, offscreen).
- `scripts/render_synth.py` → `release_staging/synth/<id>_synth.mp3` (FluidR3_GM, −16 LUFS, MP3 V2, capped at 5:00 + 3 s fade) for editor's picks with a playable MIDI (7), uploaded to Release **synth-v1** with per-file licence notes; `--record` writes `data/cache/synth_renders.json`.
- `data/composers.json` from `sync_site_data.py`. Field rename: `top_pick_*` → `editors_pick`, `editors_pick_rank`, `editors_pick_why` (catalog schema_version 2; CLI `--picks`, `--top` kept as alias).

## Look
Premium dark, champagne accent (#d8c49a), serif display face for composer names (system Palatino/Iowan/Georgia stack, no web fonts). "Credit required" badge moved from amber to blue so the accent never reads as a warning.

## Tests
- `scripts/check_pages_ui.cjs` (updated): composer index A–Z, composer page catalogue order, works default sort, search, facets + reload, picks, URL normalisation, modal focus/history, copy, tabs, single-audio playback/seek/keys, 320–1280 px overflow, 16× synthetic rows. PASS.
- `scripts/check_player.cjs` (new): listen modes + badges, full stream, seek, Release fallback, open-recording fallback, synth MP3, live MIDI + tempo + piano roll + pause, one source at a time, score-only row. PASS (live MIDI needs network; `SKIP_NET=1`).
- axe-core WCAG 2.1 A/AA: home, composer page, works grid/list, drawer with player: 0 violations.
- Real network: Commons stream, archive.org stream (Egmont), Release FLAC (`octet-stream`, Chopin Op. 9/2) and Release MP3 (Elgar) all play in Chrome.

## Known limits
- Safari: Commons/IA streams are MP3, fine; Release-only rows are OGG/FLAC/Opus files and may need the download link on older Safari.
- Live MIDI quality depends on the SGM+ soundfont and the MIDI's GM programs; long orchestral MIDIs take a few seconds to load samples.
- `composer=` uses the full composer name (as in the CSV); `data/composers.json` also has a `slug`.
