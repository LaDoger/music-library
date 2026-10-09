# AGENTS.md — how an AI agent gets music out of this library

You are looking at **LaDoger's music library**: public-domain and openly licensed music for commercial and social video, organised by composer, with licence metadata and explicit caveats per item. Unverified rows are retained for research and are not cleared for publishing. Editable scores (MIDI / LilyPond) come first, so you can re-render or re-genre a piece. Recordings come second.

| what | where |
|---|---|
| Human site | https://ladoger.github.io/music-library/ (`?id=<id>` opens one piece) |
| Agent index (every piece, absolute URLs; a few MB at thousands of rows) | https://ladoger.github.io/music-library/data/catalog.json |
| Slim sharded index (what the site loads; columnar, relative URLs, parts ≤ 300 KB) | https://ladoger.github.io/music-library/data/index/manifest.json → `data/index/part-NNN.json` (`{fields, rows}`) |
| Full record per piece | https://ladoger.github.io/music-library/data/items/<id>.json |
| Full site data (all fields, relative paths) | https://ladoger.github.io/music-library/data/library.json |
| Composer index | https://ladoger.github.io/music-library/data/composers.json (site: `?composer=<name>`) |
| Short version of this file | https://ladoger.github.io/music-library/llms.txt |
| Full recordings | GitHub Release `audio-v1`: `https://github.com/LaDoger/music-library/releases/download/audio-v1/<file>` (each item's `release_audio_url`); direct streams in `stream_audio_url` |
| Synth renders | GitHub Release `synth-v1`: FluidSynth MP3s of editor's-pick scores (`stream_synth_url`; score licence applies) |
| Repo | https://github.com/LaDoger/music-library |
| CLI | `python -m musiclib ...` (see [CLI](#cli)) |

Relative paths in `library.json` (`previews/...`, `files/scores/...`) resolve against `pages_base` = `https://ladoger.github.io/music-library/`. All URL fields in `catalog.json` are absolute. Per-item JSON preserves the original relative `preview_url`, `score_url` and `score_files`; use `preview_url_abs`, `score_url_abs`, `score_files_abs` and `render_midi.url` for absolute URLs.

## Licence rules (read before you publish anything)

A PD composition does **not** make a recording PD. Each item has a `recording_status` and a `score_status`. `licence_status` is the most restrictive of the two.

| `licence_status` | meaning | what you may do |
|---|---|---|
| `clean` | PD / CC0 / PDM / US-government recording and score | Commercial use, no credit needed. Courtesy credit is still listed where the source asks for it. |
| `attribution` | CC BY somewhere in the row | Commercial use **with** the credit line (`credit_text`) in the post or video description |
| `sharealike` | CC BY-SA or OAL somewhere in the row | Remixes may have to carry the same licence. Often only the *score* is SA: if `recording_status` is `clean`, the recording alone is fine. Ask LaDoger before using an SA part. |
| `flagged` | Known caveat: Holst term in life+100 countries, band arrangement, retired CC PD dedication | Read `legal_notes` and `legal_flags`. Ask LaDoger if unsure. |
| `unverified` | Rights not confirmed from the source page | **Do not publish.** |

Rules that always hold:
- `legal_notes` is binding. `verified` must be `yes` for anything you publish.
- **Your own render of a score carries the score's licence (`score_status`), not the recording's.** A PD MIDI rendered by you is clean even when the row's recording is CC BY.
- US-government band recordings (Marine / Army / Navy / Air Force Band) are PD in the US. Other countries do not always agree; the row flags it.
- Never add music that is CC BY-NC, all-rights-reserved, or has a guessed licence. Never download from MuseScore.com (it needs a login). Excluded composers (not PD): Orff, Prokofiev, Shostakovich, Stravinsky. Ravel's Boléro is excluded (disputed).
- `musiclib credit <id>` prints the credit text and exits 0 only for `clean` / `attribution`.

**Quality bar:** no filler. Every row is a strong, recognisable piece with a stated video use (`video_use_ideas`) and a best excerpt (`notable_excerpt`). Previews are 15 s MP3s at about −16 LUFS. They are auditions only; use the full recording or your own render in the video.

## IDs and catalogue numbers

- `id` is stable, lowercase, and built from composer + catalogue number + short title: `bach_bwv565_toccata`, `beethoven_op67_symphony5`, `grieg_peer_gynt_mountain_king`. Files are named by id.
- `catalog` holds the standard catalogue number: `BWV 565`, `Op. 67`, `K. 525`, `HWV 56`, `WoO 59`, `L.75 No.3`. Search accepts any spacing: `bwv565`, `BWV 565`, `op 27`.
- One row per piece, or per movement when movements are used separately (`movement` field).
- `editors_pick_rank` 1–15 = editor's picks for video, the strongest general-purpose cues (0 = not a pick; `editors_pick` is the boolean).
- `composer_slug` / `composer_sort` link a work to its entry in `data/composers.json` (life dates, era, `piece_ids`, PD/CC0 portrait or null).

## Item fields you will use

From `catalog.json` → `items[]`: `id, composer, title, catalog, movement, genre, era, mood[], energy, licence_status, recording_status, score_status, verified, has_editable_score, has_recording, renderable_midi, editors_pick_rank, composer_slug, composer_sort, preview_url, score_url, release_audio_url, stream_audio_url, midi_play_url, stream_synth_url, item_json_url`.

The item JSON adds: `legal_notes, legal_flags, recording_license, recording_performer, recording_source_url, recording_quality, editable_license, editable_format, editable_source_url, notable_excerpt, video_use_ideas, score_files[] / score_files_abs[], render_midi {file, url, zip_member}, midi_play_url / midi_play_url_abs, stream_audio_url, stream_synth_url, birth_year, credit_text, licence_meaning, page_url`.

## Recipes

Assume you have a checkout (`git clone https://github.com/LaDoger/music-library && cd music-library`). Without one, every step also works over HTTPS (the URLs are in the JSON) and the CLI falls back to the Pages site.

### 1. Find a piece

```bash
python -m musiclib search --picks                     # editor's picks, ranked
python -m musiclib search dramatic --clean            # words match title/composer/catalogue/mood/genre
python -m musiclib search bwv 565
python -m musiclib search --mood epic --has-score     # filters: --genre --composer --mood --energy --licence --verified
python -m musiclib search --clean --renderable --json # machine output
```

Without the CLI, fetch `data/catalog.json` and filter `items` on `licence_status`, `mood`, `energy`, `has_editable_score`, `editors_pick_rank`, `composer_slug`.

### 2. Look at it and decide

```bash
python -m musiclib get grieg_peer_gynt_mountain_king          # URLs, local paths, licence, best excerpt, credit
python -m musiclib get grieg_peer_gynt_mountain_king --json   # = data/items/<id>.json
```

Play `preview_url` to audition. Bulk-imported rows (OpenScore, Mutopia, PDMX; `added_by` = `bulk`) have no pre-rendered preview: `preview_url` is empty, so audition `midi_play_url` (or `render` it, recipe 5). `notable_excerpt` gives the strongest timestamp.

### 3. Download the recording (Release URL)

```bash
python -m musiclib download tchaikovsky_1812_overture --what recording --out downloads/
# or: curl -L -o downloads/x.ogg "$(jq -r .release_audio_url data/items/tchaikovsky_1812_overture.json)"
```

Formats vary (FLAC / OGG / MP3 / M4A; see `recording_quality`). Only rows with `has_recording: true` have one. To listen without downloading, `stream_audio_url` (when set) is a direct Wikimedia Commons MP3 transcode or Internet Archive MP3 of the same recording (duration-checked against the Release file).

### 4. Fetch the score

```bash
python -m musiclib download beethoven_op67_symphony5 --what score --out downloads/
```

You get every file in `score_files` (MIDI, LilyPond `.ly`, PDF, Mutopia zips). Some rows share one zip for a whole cycle (Dvořák 9, Pictures at an Exhibition). `render_midi.zip_member` names the right MIDI inside it.

### 5. Render the MIDI (FluidSynth + FluidR3_GM)

```bash
python -m musiclib render grieg_peer_gynt_mountain_king --out renders/mk.wav
python -m musiclib render dvorak_new_world_largo --start 0:40 --duration 30 --out renders/largo.mp3
```

Defaults: soundfont `/usr/share/sounds/sf2/FluidR3_GM.sf2` (override with `--sf2` or `$MUSICLIB_SF2`), 44.1 kHz stereo, 0.3 s fade-in, 0.5 s fade-out, two-pass loudness normalisation to −16 LUFS (`--lufs`, `--no-normalize`). Output type comes from the extension (`.wav .mp3 .flac .m4a .ogg`).

The same thing by hand:

```bash
fluidsynth -ni -g 0.8 -r 44100 -F out.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 files/scores/<id>.mid
```

Install: `apt install fluidsynth fluid-soundfont-gm ffmpeg` (macOS: `brew install fluid-synth ffmpeg` plus any GM `.sf2`).

### 6. Re-genre / arrange the notes

Edit the MIDI (or the LilyPond source) yourself, e.g. with `mido`, `music21` or `pretty_midi`: change instruments (GM program numbers), tempo, drums, harmony. Then render your file:

```bash
python -m musiclib render --midi my_arrangement.mid --out renders/trap_toccata.mp3
```

`python -m musiclib arrange <id> --style <style>` is a **hook** for a future arranger. Set `MUSICLIB_ARRANGE_CMD` to a command template (placeholders `{midi} {style} {out} {id} {item_json}`). The command must write a MIDI file to `{out}`. Without the variable it prints the source MIDI and exits 2. An arrangement inherits the score's licence: a CC BY-SA score makes the arrangement share-alike.

### 7. Trim for video

```bash
python -m musiclib trim downloads/grieg_peer_gynt_mountain_king.flac --start 1:42 --duration 30 --out cut.mp3
# by hand: ffmpeg -ss 102 -t 30 -i in.flac -af "afade=t=in:d=0.3,afade=t=out:st=29.5:d=0.5,loudnorm=I=-16:TP=-1.5" cut.mp3
```

Use `notable_excerpt` for the start point. X / social video: −14 to −16 LUFS works well. Under a voice-over, mix music about 12–18 dB below the voice.

### 8. Write the attribution

```bash
python -m musiclib credit bach_bwv565_toccata
```

Paste `credit_text` into the post / video description when the status is `attribution`. Credit only the parts you used. If you rendered the score yourself, the recording credit is not needed; the score credit is, when `score_status` is `attribution`. For CC BY, add the licence link and say what you changed (excerpt, normalisation, fades); `legal_notes` names the exact credit. For `clean`, a courtesy credit is optional but nice.

## CLI

```bash
pip install -e .            # from the repo root; installs the `musiclib` command (stdlib only)
python -m musiclib -h       # or without installing: PYTHONPATH=src python -m musiclib -h
```

| command | does |
|---|---|
| `search [words] [filters]` | text + filter search; `--json` for machine output |
| `get <id> [--json]` | URLs, local paths, licence, excerpt, credit |
| `credit <id> [--json]` | licence check + credit text (exit 3 if not clean/attribution) |
| `download <id> --what recording\|score\|preview\|all` | fetch files to `--out` (default `downloads/`) |
| `render <id>` / `render --midi f.mid` | FluidSynth → wav/mp3/flac, with trim, fades and loudness |
| `trim <audio>` | cut, fade and normalise any audio file |
| `arrange <id> --style s` | re-genre hook (`$MUSICLIB_ARRANGE_CMD`) |
| `info` | where the data is coming from |

Data source: `$MUSICLIB_ROOT`, otherwise the checkout the package is in (or one above the current directory), otherwise `$MUSICLIB_BASE`, otherwise the Pages site (cached in `~/.cache/musiclib`). An MCP server is planned: [docs/MCP_PLAN.md](docs/MCP_PLAN.md).

## Changing the library (maintainers / agents with write access)

- `library.csv` is the hand-curated master. Bulk imports live in `library_bulk.csv` (built by `python3 scripts/bulk/build_bulk_layer.py` from `parts/BULK_batch*_rows.csv`; PD / CC0 / CC BY only, composer died ≤ 1929). A `library.csv` row wins on the same id. After editing either, run `python3 scripts/sync_site_data.py`. It rebuilds `data/library.json`, `data/catalog.json`, `data/index/*` and `data/items/*.json`. Never hand-edit the JSON.
- Licence policy and columns: `SCHEMA.md`. Progress and resume steps: `STATUS.md`.
- **Never commit `files/audio/`** (full recordings go to the Release with `scripts/upload_release.sh`). Never commit secrets or tokens.
- Verify every licence on the source page itself; set `verified=yes` only after you have seen the licence text.
