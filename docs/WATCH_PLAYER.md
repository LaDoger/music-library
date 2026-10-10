# Watch player (`?watch=<id>`)

A YouTube-style "score video": the engraved score fills the stage, a cursor and a highlighted
measure box follow the music, and the stage scrolls system by system (current + next system
visible, animated turn). Audio is rendered live in the browser from the score's own notes (the
MIDI for MIDI-only rows), so sound and cursor share one clock. No audio or video file is added to the repo.

- Route: `?watch=<id>` (shareable; `?id=` detail and composer-first browsing are unchanged). "▶ Watch" appears on every card and in the detail drawer for rows with a playable MIDI.
- Code: `assets/watch.js` + `assets/watch.css`, lazy-loaded by `assets/app.js` on first use.
- Loads only the selected `data/items/<id>.json` and its MusicXML/MXL; the MIDI only when there is no usable score (the slim index already in memory feeds the up-next list).
- Views: Score (default when a `.mxl/.musicxml/.xml` exists), Piano roll (canvas; the only view for MIDI-only rows), Both. Dark paper / Light paper (cream, black ink). Composer, work title and catalogue number are a static heading in the bar above the stage; nothing is drawn over the score, so the music starts with the score visible. Tempo 50–150 %, seek bar, fullscreen (F), Space = play/pause, Esc = close.
- Up next: remaining movements of the same work (same composer + title prefix before ":"/catalogue), then more by the same composer (editable scores and featured first). When a movement ends, the next one in the set autoplays.

## Layout and scrolling
The watch route is a normal page: the library content is hidden with `display:none` (not `visibility`), `.watch` is in normal flow, and the page scrolls. Only browser fullscreen (F) locks to the viewport. The stage is `max(260px, 100dvh - header bar - controls)` (JS sets `--w-bars` from the measured bar + controls heights), so bar + stage + controls fit on screen at scroll 0. "Up next" sits beside the stage on wide screens (sticky) and below it on ≤860px. The score is laid out to the stage width minus 16 px side padding; nothing overflows horizontally. Zoom −/+/Fit (50–250 %, 10 % steps) rescales the engraving while keeping it fit to width; it is kept in the URL as `&zoom=1.3` (omitted at 100 %). Controls wrap on mobile.

## Sync
Audio and cursor run on one clock built from the score itself (`assets/watch.js`, "score timeline"):

1. The MusicXML is read directly (`.mxl` is unzipped in the browser with `DecompressionStream`; the same text is handed to OSMD).
2. Measures are unrolled into playback order: repeat barlines (`times=`), voltas (`<ending>` spans, including invisible ones), D.C. / D.S. / Fine / To Coda / Coda from `<sound>` attributes (or the usual words when a file has none). As in MuseScore, repeats are not replayed after a D.C./D.S. jump and the last volta is taken. Jumps are scoped per movement (measure numbering restarting at 1, or 0 for a pickup, starts a movement): D.C./segno/coda targets stay inside it and Fine ends only that movement. A volta without a stop closes at its backward repeat; a backward repeat without `times=` inside a volta group plays as many passes as the highest ending number ("1, 3" / "2, 4" = four verses).
3. Tempo comes from `<sound tempo>` (or `<metronome>`) at its exact position; after a jump the tempo in force at the target measure (score order) applies. 120 qpm before the first mark (as MuseScore). A score with no tempo mark at all borrows the MIDI's tempo map (by quarter-note position) when the MIDI has the same length in quarters (±3 %).
4. The notes of the unrolled score (ties merged, transposing parts sounded, `<midi-program>` per part, dynamics from `<sound dynamics>` / dynamic marks, grace and cue notes skipped) become the NoteSequence the Salamander / sampler / SGM+ engines play. Seek, tempo (50–150 %), sound picker and autoplay work on that sequence.
5. Playback seconds → unrolled quarter position → unrolled measure → score measure + offset. The cursor moves at note level (every onset step of OSMD's iterator in that measure), the measure box and system scroll follow the score measure, so a repeat or D.S. sends the cursor back to the right place. Jumps use an iterator clone per measure, so no replay from the start.

Fallbacks: MIDI-only rows play the MIDI (piano roll only). If the score cannot be turned into notes (unzip unsupported, parse error, measure count differs from OSMD) or with `&audio=midi` (debug/compat), the MIDI plays and is aligned to the unrolled score by a banded DTW on onset pitch sets (cost 1 − Jaccard), giving a piecewise-linear MIDI-time → score-position map; only if that also fails does the old linear tempo-map scaling apply.

Batch check (all 1,267 MusicXML rows, 2026-10-10): no parse failures, measure count equals OSMD's on every row. 107 rows differ from their MIDI's length by >10 %: 13 were tempo reading (fixed: 120 qpm before the first mark; MIDI tempo map for scores without marks), the rest are mostly string-quartet MIDIs from another source (different structure) and MuseScore export quirks (e.g. a later movement's D.C. replaying the whole file). The score's own repeat signs win.

Not modelled: fermata holds, ornaments/trills, tremolo expansion, grace notes, swing, `<offset>` on notes; `after-jump` repeat attributes. Expression text (rit., accel.) without a tempo mark does not change the tempo.

### Drift test
`scripts/watch_drift.cjs` (also run inside `check_watch.cjs`) measures cursor drift against an independent ground truth: `scripts/watch_truth.py` unrolls the MusicXML in Python and cross-checks every unrolled measure against the MIDI's note onsets; the notes the audio engine actually triggers are aligned to those score onsets (subsequence DTW), and the true position is the window from the last sounded onset to "now". The cursor's measure + offset is placed on the unrolled timeline and the error is reported in quarter-note beats over 8 samples per piece (start + 7 seeks). Requirement: < 1 beat.

| piece | why | before (max / mean beats) | after (max / mean beats) |
|---|---|---|---|
| `duchambge_ronde_des_pauvres` (voice + piano, 33 bars → 49 played) | repeat, volta 1 (invisible) / 2, D.S. al Fine | 22.18 / 14.31 | 0.00 / 0.00 |
| `wagner_wwv75_elsa_procession` (piano, 113 bars) | 18 different tempo marks (32–80 qpm) | 0.00 / 0.00 (7 of 8 samples usable) | 0.00 / 0.00 |
| `wagner_wwv86d_siegfried_funeral_march` (piano, 82 bars) | plain | 5.25 / 0.67 | 0.08 / 0.01 |

Also after: Duchambge at 150 % tempo 0.50 / 0.06; Duchambge with `&audio=midi` (MIDI audio, DTW-aligned) 0.00 / 0.00. Before = commit c0833add (linear scaling, no repeats) with only a cursor-readout hook added.

## Audio engines
- Piano-led pieces (≤3 instruments, ≥65 % GM piano programs, including piano + sung line): Tone.js `Sampler` with Salamander Grand Piano.
- Everything else: the Magenta `SoundFontPlayer` with SGM+ (same as the detail-page synth); also the fallback if piano samples fail.

## Sound picker
A "Sound" select in the player lazy-loads only the chosen set; the choice is kept in `localStorage` (`watchSound`) and the URL (`&sound=<id>`, which wins). `auto` = Salamander for piano-led pieces, SGM+ otherwise. Switching mid-play keeps position and resumes. A sampler sound plays every pitched part of the piece with that one instrument; use "Orchestral set" for multi-instrument pieces. If a set fails to load, the player keeps the current sound.

| id | Sound | Source | Licence |
|---|---|---|---|
| `salamander` | Grand piano | https://tonejs.github.io/audio/salamander/ | CC BY 3.0 (Alexander Holm) |
| `harpsichord`, `rhodes` (GM Electric Piano 1), `celesta`, `musicbox`, `organ` (Church Organ) | FluidR3_GM, pre-rendered per instrument | https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/ (README: https://github.com/gleitz/midi-js-soundfonts) | CC BY 3.0 (per that README) |
| `gm` | SGM+ orchestral set | https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus | existing engine |

Skipped: a soft/felt or upright piano. The only candidates found were MusyngKite/FatBoy (CC BY-SA 3.0, share-alike) and tonejs-instruments (mixed sources incl. Freesound/Karoryfer; its README claims CC BY 3.0 but per-sample provenance is unclear and it is not on a CDN path that resolves), so none was added. Nothing is stored in the repo. The credits line in the player names the active set.

## Third-party licences
| Component | Licence | Loaded from |
|---|---|---|
| OpenSheetMusicDisplay 1.9.0 | BSD-3-Clause | jsDelivr, watch page only |
| Tone.js 14.7.58, @magenta/music 1.23.1 (MIDI parsing, soundfont player) | MIT / Apache-2.0 | `assets/vendor/midi-player.bundle.js` (see `assets/vendor/README.md`) |
| Salamander Grand Piano samples (Alexander Holm) | CC BY 3.0 | `https://tonejs.github.io/audio/salamander/` at runtime; credited on the watch page |
| SGM+ soundfont | see Magenta | `storage.googleapis.com/magentadata` at runtime |

Deviation from the brief: MIDI is parsed with Magenta's `midiToSequenceProto` (already vendored) instead of adding `@tonejs/midi`. Rows with MusicXML play from the score; the Watch button still requires `midi_play_url` (every current MusicXML row has one), which is the fallback audio.

## Tests
`NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_watch.cjs` (network needed). Covers piano MusicXML, MIDI-only, orchestral-style MusicXML, set autoplay; also a layout matrix (1280x800, 1440x900, 1920x1080, 1366x768, 390x844, 820x1180 in chromium; webkit/firefox when installed): library and watch pages scroll, no horizontal overflow, stage + controls fit the viewport, zoom; screenshots to `.tmp/watch/shots_fix/`. Asserts the audio context runs, time advances, measure highlight and system turns, axe, mobile screenshot, a static composer / title / catalogue heading above the stage with no overlay on the score, and sync drift < 1 beat on the three drift pieces (plus one at 150 % tempo and one with `&audio=midi`, DTW-aligned). The drift test needs `python3`; `mido` is optional (MIDI cross-check of the ground truth).
