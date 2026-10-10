# Watch player (`?watch=<id>`)

A YouTube-style "score video": the engraved score fills the stage, a cursor and a highlighted
measure box follow the music, and the stage scrolls system by system (current + next system
visible, animated turn). Audio is rendered live in the browser from the score MIDI. No audio or
video file is added to the repo.

- Route: `?watch=<id>` (shareable; `?id=` detail and composer-first browsing are unchanged). "▶ Watch" appears on every card and in the detail drawer for rows with a playable MIDI.
- Code: `assets/watch.js` + `assets/watch.css`, lazy-loaded by `assets/app.js` on first use.
- Loads only the selected `data/items/<id>.json`, its MIDI and its MusicXML/MXL (the slim index already in memory feeds the up-next list).
- Views: Score (default when a `.mxl/.musicxml/.xml` exists), Piano roll (canvas; the only view for MIDI-only rows), Both. Dark paper / Light paper (cream, black ink). Title card ~3 s at start. Tempo 50–150 %, seek bar, fullscreen (F), Space = play/pause, Esc = close.
- Up next: remaining movements of the same work (same composer + title prefix before ":"/catalogue), then more by the same composer (editable scores and featured first). When a movement ends, the next one in the set autoplays.

## Sync
OSMD cursor steps are recorded once (quarter-note timestamp + measure index). The MIDI tempo map converts playback seconds to quarter notes; the nearest step drives the cursor, measure box and system scroll. If the MIDI length differs from the score by >3 % (e.g. repeats expanded in the MIDI) the score time is scaled linearly. v1 limit: no repeat/jump tracking.

## Audio engines
- Piano-led pieces (≤3 instruments, ≥65 % GM piano programs, including piano + sung line): Tone.js `Sampler` with Salamander Grand Piano.
- Everything else: the Magenta `SoundFontPlayer` with SGM+ (same as the detail-page synth); also the fallback if piano samples fail.

## Third-party licences
| Component | Licence | Loaded from |
|---|---|---|
| OpenSheetMusicDisplay 1.9.0 | BSD-3-Clause | jsDelivr, watch page only |
| Tone.js 14.7.58, @magenta/music 1.23.1 (MIDI parsing, soundfont player) | MIT / Apache-2.0 | `assets/vendor/midi-player.bundle.js` (see `assets/vendor/README.md`) |
| Salamander Grand Piano samples (Alexander Holm) | CC BY 3.0 | `https://tonejs.github.io/audio/salamander/` at runtime; credited on the watch page |
| SGM+ soundfont | see Magenta | `storage.googleapis.com/magentadata` at runtime |

Deviation from the brief: MIDI is parsed with Magenta's `midiToSequenceProto` (already vendored) instead of adding `@tonejs/midi`. MusicXML without a MIDI is not played (every current MusicXML row has a MIDI).

## Tests
`NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_watch.cjs` (network needed). Covers piano MusicXML, MIDI-only, orchestral-style MusicXML, set autoplay; asserts the audio context runs, time advances, measure highlight and system turns, axe, mobile screenshot.
