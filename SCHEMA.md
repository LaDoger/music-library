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
