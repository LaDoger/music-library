# Library CSV schema

One row per piece (or per movement when movements are used separately).

Columns (exact header, comma-separated CSV, UTF-8):
id,composer,death_year,title,catalog,movement,mood_tags,tempo_energy,notable_excerpt,video_use_ideas,editable_source_url,editable_format,editable_license,musescore_url,recording_source_url,recording_performer,recording_license,recording_quality,legal_notes,local_score_path,local_audio_path,preview_path,verified,added_by

Field rules:
- id: lowercase slug, e.g. bach_bwv565_toccata, grieg_peer_gynt_mountain_king
- death_year: integer
- mood_tags: semicolon-separated, e.g. dramatic;epic;dark
- tempo_energy: short phrase, e.g. allegro / high drive
- notable_excerpt: bars or mm:ss of a strong clip if known, else blank
- video_use_ideas: one short sentence
- editable_*: leave blank if none found; license must be PD / CC0 / CC-BY / CC-BY-SA (flag SA) / other — never invent
- musescore_url: MuseScore.com page if useful later (do NOT download; login-gated)
- recording_*: same license discipline; quality like "FLAC 44.1/16" or "MP3 320" or "OGG"
- legal_notes: PD-EU? PD-US? caveats (Holst Planets, Ravel Boléro, Rachmaninoff US, etc.)
- local_*_path: relative to /workspace/music/library/ after download, else blank
- preview_path: relative path under previews/ for the ~15s audition MP3 (required for every row that has a usable score or recording)
- verified: yes | unverified | no (no = known problem; unverified = could not confirm from source page)
- added_by: codex | claude | grok

License policy (strict):
- Safe for commercial/social video without attribution: PD composition + PD/CC0 recording, or own render from PD/CC0 editable file.
- Safe with attribution: CC BY (note required credit in legal_notes).
- Flag only, do not treat as clean: CC BY-SA (share-alike may infect remixes), disputed works.
- Exclude: CC BY-NC, all-rights-reserved recordings, Orff, Prokofiev, Shostakovich, Stravinsky (not PD).
- A PD score ≠ a PD recording. Verify each recording's own page.

Preview policy (required):
- Every piece with a downloaded recording OR editable file gets a ~15s MP3 preview in previews/<id>_<composer>_<title>.mp3
- Prefer cutting the best excerpt from the PD/CC recording; else render MIDI/MusicXML via FluidSynth + good soundfont
- Spec: MP3 192k, loudness ~-16 LUFS integrated, short fades in/out (~0.3–0.5s), stereo
- Also build previews/index.html: simple player listing all pieces with mood tags and audio controls

## Multi-genre extension (2026-10-09)
Additional JSON fields (CSV may lag; sync script fills JSON):
- genre: classical | jazz | ragtime | blues | folk | world | marches | early_popular | film_silent | modern_cc | other
- era: free text browse bucket
- licence_status: clean | attribution | sharealike | flagged | unverified
- has_editable_score, has_recording: booleans
- release_audio_url: GitHub Release asset URL for full recording
Scope: any legally usable good music for commercial/social video. Quality bar: no filler. Verify every licence per file.

Site-only JSON fields (all derived by `scripts/sync_site_data.py`; do not hand-edit the JSON):
- recording_status, score_status: licence class of each part (blank when the part is absent)
- licence_status: most restrictive of the two (clean < attribution < flagged < sharealike < unverified); `flagged` comes from the FLAGGED list in the script; verified != yes forces unverified
- legal_flags: short caveat chips derived from legal_notes (informational, do not change the badge)
- energy: low | moderate | high | very_high (from tempo_energy)
- score_files: every file under files/scores/ belonging to the row
- editors_pick, editors_pick_rank, editors_pick_why: from the README "Editor's picks for video" table (false / 0 / blank otherwise)
- video_use_ideas: CSV text passed through `scripts/video_ideas.py` (generic edit uses only; niche, brand or market wording is rewritten and the sync warns)
- composer_slug, composer_short, composer_sort ("Bach, Johann Sebastian"), birth_year: composer identity; birth_year from data/cache/composer_meta.json (Wikidata)
- stream_audio_url, stream_audio_mime, duration_s: direct browser stream of the same recording (Commons MP3 transcode or archive.org MP3), from data/cache/stream_audio.json; accepted only when its duration matches the local file within 3 s
- midi_play_url: MIDI the in-browser synth plays (the row's .mid, or files/midi_play/<id>.mid extracted from a shared zip / converted from MusicXML by scripts/build_midi_play.py)
- stream_synth_url / release_synth_url, synth_duration_s: pre-rendered FluidSynth MP3 on Release synth-v1 (data/cache/synth_renders.json). Carries the score licence.
- `data/composers.json`: one entry per composer, A–Z by sort name: slug, name, short_name, sort_name, birth_year (nullable), death_year, era, genres[], piece_count, score_count, recording_count, piece_ids[], wikidata, portrait_url (nullable; only Commons files tagged Public domain / CC0), portrait_licence, portrait_source, portrait_note
- search_text: lowercase search blob incl. catalogue variants (BWV 565 / bwv565)
- Optional CSV columns `genre`, `era` override the derived values.

Agent files (generated by `scripts/build_catalog.py`, which `sync_site_data.py` runs; do not hand-edit):
- `data/catalog.json`: `{schema_version, pages_base, repo, release, licence_status_meaning, count, items[]}`. Each item has: id, composer, title, catalog, movement, genre, era, mood[], energy, licence_status, recording_status, score_status, verified, has_editable_score, has_recording, renderable_midi, editors_pick_rank, composer_slug, composer_sort, and the absolute URLs preview_url, score_url, release_audio_url, stream_audio_url, midi_play_url, stream_synth_url, item_json_url. schema_version 2 (editors_pick_rank replaced top_pick_rank).
- `data/items/<id>.json`: the library.json row (minus search_text), plus page_url, item_json_url, *_abs URLs, `render_midi {file, url, zip_member}` (the MIDI that `musiclib render` uses; zip members are set in MIDI_MEMBERS in the script), licence_meaning and credit_text.
