# Batch 1 — Codex Wagner + Mahler score expansion

23 new verified, clean, score-only classical rows: **13 Wagner + 10 Mahler**. Every row has a WWV/GMW catalogue number, a stated video use and a 15-second MIDI audition. No full recordings were added. Existing recording licences and caveats are unchanged.

## Included

- Wagner: Tannhäuser overture (WWV 70); Meistersinger Act I prelude (WWV 96); Parsifal Act I prelude and Good Friday Magic (WWV 111); Elsa’s Procession (WWV 75); Siegfried’s Funeral March and Götterdämmerung Act III prelude (WWV 86D); Tristan Liebestod (WWV 90); all five Wesendonck songs (WWV 91).
- Mahler: all five Kindertotenlieder (GMW 45-K); all four Lieder eines fahrenden Gesellen (GMW 10-K); Rheinlegendchen (GMW 29-K).
- Files: 23 MIDI, 23 compressed MusicXML, 14 native MuseScore files; 23 MP3 auditions. Native scores are preserved byte-for-byte. MIDI exports preserve the native scores’ hidden tempo events; Rheinlegendchen uses the repository MusicXML with explicit playback tempos. Voice-and-piano songs audition the vocal line on GM oboe, not a sung recording. The opera excerpts are piano reductions, not orchestral performances.

## Licence evidence

- [OpenScore Lieder](https://github.com/OpenScore/Lieder) expressly releases its scores under CC0. Used commit `38c5db510224d9facdc4b08d741fc788cfb58ea8`; each song’s README and score path are recorded in the manifest. The repository licence and README are preserved in `docs/licences/batch1_codex/`.
- Eight Wagner piano scores were downloaded directly from [Artform’s Wagner collection](https://app.jamescartersound.com/sheet-music/wagner/), which explicitly labels each listed score public domain. Each selected score additionally matches a per-file CC0 entry with `license_conflict=False` in [PDMX release 15571083](https://zenodo.org/records/15571083); the MXL files carry no conflicting rights statement. Collection labels alone were insufficient: Entrance of the Gods into Walhalla was excluded because its archived metadata reports a licence conflict.
- The original MuseScore pages returned HTTP 403. No files were downloaded from MuseScore.com. The Artform licence statement is the checked source-page evidence for its eight files; archived metadata is supporting evidence, not a substitute source-page verification for other candidates. PDMX’s dataset-level CC BY 4.0 metadata notice is acknowledged in the legal notes; this batch redistributes Artform’s independently labelled PD score files, not PDMX archive files.
- Parsifal prelude’s metadata and visible credits disagree on the historic arranger (Heintz vs Kleinmichel). Both are out of life+70 copyright; the discrepancy is disclosed in `legal_notes` rather than silently resolved.
- Per-file origins, licensing evidence, SHA256 hashes, MIDI note counts and preview offsets: `docs/licences/batch1_codex/manifest.json`.

## Quality and validation

23/23 entries checked: unique IDs; nonempty catalogue, excerpt and video-use fields; classical genre; `verified=yes`; `score_status=clean`; `licence_status=clean`; existing editable files; correct per-item MIDI render hints. Preview checks: approximately 15.05 seconds, 44.1 kHz stereo MP3 at 192 kbps, fades, measured integrated loudness −16.5 to −16.0 LUFS. File hashes match the manifest. Authored files pass the whitespace check; upstream README and native MSCX whitespace is preserved with the original bytes. Results are in `docs/licences/batch1_codex/validation.json`.

Ran `scripts/sync_site_data.py`, `scripts/build_catalog.py --check`, preview-index generation and CLI search/get smoke checks. All ten new Mahler scores appear in clean/renderable searches. Sampled cross-audit of Claude’s Bach slice: all 170 rows passed structural checks; ten source-page licence checks (including both CC BY rows) matched. See `parts/BATCH1_codex_CROSS_AUDIT.md`.

Strong starting auditions: Tannhäuser’s Pilgrims theme, Meistersinger’s opening, Ich hab’ ein glühend Messer, In diesem Wetter, Im Treibhaus and Träume. These are slice recommendations; the site’s existing ranked picks were not changed by this work.

## Gaps and resume

Mahler symphony candidates remain **research only**: original source pages were blocked, and archived file-level CC0 labels do not resolve all arrangement/archive licensing questions. The hmscomp Adagietto excerpt is CC0 on Free-scores, but that source offers no editable file. It was not attached to the existing flagged recording row. IMSLP symphonies 1–9 exposed no editable Source Files. Incomplete/WIP Wagner overtures and modern Mahler 10 completions were excluded. Kunstderfuge forbids redistribution without permission; the free Mahler MIDI download site supplies no explicit commercial-use licence.

Specific candidate IDs, blockers and next steps are in `parts/BATCH1_codex_RESEARCH.md`. Resume by opening an original per-file licensing page or an authorised, explicitly licensed editable mirror; confirm arrangement provenance; only then import the score and render its audition. Temporary research is under `.tmp/batch1_codex/` and is not published.

Concurrent Bach and UI/research changes were preserved. The commit is scoped to this expansion’s rows, score/preview assets, derived data and reports. Never commit `files/audio/` or temporary research.

## Checkpoints

- CP-WM1: briefs/schema/protocol read; quota 45%, continue.
- CP-WM2: 15 OpenScore song scores and CC0 evidence acquired; quota 46%, continue.
- CP-WM3: 23 curated rows / 60 score files prepared; native tempos preserved; quota 47%, continue.
- CP-WM4: previews, licence/data checks and Bach cross-audit passed; generated site/agent data; commit/push next.
- CP-WM5: commit and live-deployment result recorded in STATUS.md.
