# Music library

A composer-first library of **good music we can legally use** in commercial and social video: public-domain and openly licensed classical music today, with room for jazz, ragtime, blues, folk, world, marches, early popular, silent/film and quality modern CC0 / CC BY. No filler; every licence is checked per file.

**Editable scores come first.** The point is to take a work (Bach, Wagner, anything PD), get a clean MIDI / LilyPond / MusicXML file and re-genre or re-render it for video. Recordings are secondary.

- **Live site:** https://ladoger.github.io/music-library/
- **Repo:** https://github.com/LaDoger/music-library
- **Full recordings:** GitHub Release [`audio-v1`](https://github.com/LaDoger/music-library/releases/tag/audio-v1) (not in git, too large). Each row's `release_audio_url` points at its asset.
- **Synth renders:** GitHub Release [`synth-v1`](https://github.com/LaDoger/music-library/releases/tag/synth-v1): full-length FluidSynth MP3s of editor's-pick scores (`stream_synth_url`; they carry the score licence).

The library started with 75 classical pieces and grows in batches (Bach BWV first, then Wagner, Mahler, Bruckner and other PD composers). The site and `data/*.json` are regenerated from `library.csv`; the numbers below are a snapshot at the last sync.

| | count |
|---|---|
| Works (rows) | 334 |
| Composers | 47 (42 with a verified PD portrait) |
| Rows with a downloadable editable score | 289 |
| Rows with a full recording (Release `audio-v1`) | 64 (61 with a direct Commons / Internet Archive stream) |
| Pre-rendered synth MP3s (Release `synth-v1`) | 7 |
| Licence badge: Clean / Credit required / ShareAlike / Flagged / Unverified | 259 / 33 / 32 / 6 / 4 |

## For AI agents and the `musiclib` CLI

Agents start at **[AGENTS.md](AGENTS.md)** (licence rules and recipes: find → download → score → render → re-genre → trim → credit) or **[llms.txt](https://ladoger.github.io/music-library/llms.txt)**. Machine-readable data on Pages:

- [`data/catalog.json`](https://ladoger.github.io/music-library/data/catalog.json): compact index; every URL is absolute (`pages_base` = `https://ladoger.github.io/music-library/`)
- `data/items/<id>.json`: full record per piece, with `credit_text`, `render_midi` and `legal_notes`

The CLI is pure stdlib Python 3.9+:

```bash
pip install -e .                                   # repo root; or: PYTHONPATH=src python -m musiclib ...
musiclib search --picks                            # editor's picks, ranked; also: search bwv 565, search dramatic --clean --has-score
musiclib get grieg_peer_gynt_mountain_king         # URLs, local paths, licence, best excerpt, credit
musiclib download tchaikovsky_1812_overture --what recording   # from the Release; --what score|preview|all
musiclib render grieg_peer_gynt_mountain_king --start 0:30 --duration 30 --out clip.mp3
musiclib render --midi my_arrangement.mid --out arr.mp3        # render your own edited MIDI
musiclib trim downloads/x.flac --start 1:42 --duration 30      # cut + fades + -16 LUFS
musiclib credit bach_bwv565_toccata                # credit text; exit 3 unless clean/attribution
musiclib arrange <id> --style lofi                 # hook: runs $MUSICLIB_ARRANGE_CMD (not built in yet)
```

**Soundfont and tools:** `render` needs FluidSynth and ffmpeg, plus the General MIDI soundfont `/usr/share/sounds/sf2/FluidR3_GM.sf2`. Install them with `apt install fluidsynth fluid-soundfont-gm ffmpeg`; on macOS use `brew install fluid-synth ffmpeg` and download any GM `.sf2`. Point to a different soundfont with `--sf2 path` or `MUSICLIB_SF2`. Without a checkout, the CLI reads from the Pages site and caches files in `~/.cache/musiclib`. An MCP server is planned in [docs/MCP_PLAN.md](docs/MCP_PLAN.md).

## Using the site

- **Composers first.** The home page is an A–Z index of composers with life dates, era, a count of works / scores / recordings and a portrait (only Wikimedia Commons files tagged public domain or CC0, checked through the Commons API; everyone else gets a monogram). Click a composer for their page (`?composer=Johann%20Sebastian%20Bach`): all their works sorted by **catalogue number** (BWV, Op., K., WWV…), with every filter still available.
- **All works** (`?view=works`) lists every piece. Cards lead with the composer, then the title, then the catalogue number. Default order: composer, then catalogue number, then title; other sorts (title, best match, death year, energy, scores first) are in the Sort menu.
- **Search** by composer, title or **catalogue number**: `BWV 565`, `bwv565`, `Op. 27`, `K331`, `WWV 86`. Accents are optional (`dvorak`).
- **Filters:** composer, genre, era, mood, energy, licence status, has recording, verified, plus the **Has editable score** toggle. Every filter is in the URL, so a filtered view can be shared.
- **Editor's picks for video** row on the home page (the 15 below). **See all ranked** / the *Editor's picks* tab shows them in rank order (`?picks=1`).
- **Player** (one source at a time, `Space` play/pause, `Esc` stop, `/` search). Each piece offers whatever exists:
  - **Preview**: the 15 s audition clip.
  - **Full recording**: the whole performance, with seek bar and time / duration. It streams the Commons MP3 transcode or Internet Archive MP3 when one was resolved (`stream_audio_url`), else the GitHub Release file; if the browser cannot play either, the player offers *Download / open recording*.
  - **Synth render**: the score rendered by FluidSynth (FluidR3_GM), pre-rendered for editor's picks on Release `synth-v1` (`stream_synth_url`).
  - **Live MIDI synth**: any scored piece played in the browser (Magenta SoundFontPlayer, SGM+ soundfont, loaded on first use) with **tempo** control (50–150 %) and a piano roll.
  - Synth renders are made from the score, so they carry the **score** licence; the player and detail panel say so.
- **Detail panel** (click a title, or link `?id=<id>`): listen buttons, strong excerpt, video ideas, licence badge for the recording and the score, legal flags and notes, **Copy licence + credit**, and links to the preview, full recording, stream, synth render, score files and source pages.

Licence badges show the **most restrictive** part of the row and never overclaim:

| badge | meaning |
|---|---|
| Clean | PD / CC0 / PDM / US-gov recording and score; no credit needed (courtesy credits still listed) |
| Credit required | CC BY (or Commons attribution) somewhere in the row |
| ShareAlike | CC BY-SA or OAL somewhere in the row (often only the score; the card shows "rec … · score …") |
| Flagged | known caveat: Holst term in life+100 territories, band arrangements, retired CC PD dedication |
| Unverified | rights not confirmed from the source page |

Run locally:

```bash
cd /workspace/music/library
python3 -m http.server 8000      # then open http://localhost:8000/
```

### Updating the site data

`data/library.json`, `data/catalog.json` and `data/items/*.json` are generated. After editing `library.csv` (or merging a new batch) run:

```bash
python3 scripts/sync_site_data.py          # rebuild JSON (idempotent)
python3 scripts/sync_site_data.py --check  # summary + warnings only
```

It derives genre, era, energy, `licence_status` (+ separate `recording_status` / `score_status`), `legal_flags`, `has_editable_score`, `has_recording`, score file lists, `release_audio_url`, `editors_pick_rank` (from the table in this README), composer fields and `data/composers.json`, and merges the offline caches in `data/cache/` (`stream_audio_url`, `stream_synth_url`). `video_use_ideas` passes through `scripts/video_ideas.py`, which keeps the wording generic.

The network steps are separate and cached, so the sync itself stays offline:

```bash
python3 scripts/video_ideas.py          # rewrite niche video_use_ideas in library.csv (merge by id)
python3 scripts/fetch_composer_meta.py  # Wikidata life dates + PD/CC0-only Commons portraits -> data/cache/composer_meta.json
python3 scripts/resolve_streams.py      # Commons / archive.org direct streams (duration-checked) -> data/cache/stream_audio.json
python3 scripts/build_midi_play.py      # browser MIDI for zip-only / MusicXML-only scores -> files/midi_play/<id>.mid
python3 scripts/render_synth.py         # FluidSynth MP3s for editor's picks -> release_staging/synth/
gh release upload synth-v1 release_staging/synth/*_synth.mp3 --clobber && python3 scripts/render_synth.py --record
python3 scripts/sync_site_data.py       # then rebuild the JSON
``` New genres: add a `genre` column value to the CSV rows (`classical | jazz | ragtime | blues | folk | world | marches | early_popular | film_silent | modern_cc | other`). Architecture and scaling notes for 1000+ rows: `parts/UI_NOTES.md`.

### Deploying (GitHub Pages)

Pages serves the repo root of `main`: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/ (root)`**. `.nojekyll` makes Pages serve files as-is. `files/audio/` is git-ignored and never committed; full recordings are uploaded to the Release with `scripts/upload_release.sh`.

## Folder layout

```
index.html, assets/          the Pages site (vanilla JS, no build step)
data/library.json            site data, generated by scripts/sync_site_data.py
data/composers.json          composer index (life dates, era, counts, piece ids, portrait + licence)
data/cache/                  network lookups cached for the offline sync (composer meta, streams, synth renders)
assets/vendor/               html-midi-player bundle (Tone.js + Magenta core), loaded only for live MIDI
data/catalog.json, data/items/  agent index + per-item records (scripts/build_catalog.py, run by sync)
AGENTS.md, llms.txt          agent entry points; docs/MCP_PLAN.md
src/musiclib/, pyproject.toml  the musiclib CLI (search/get/download/render/trim/credit/arrange)
library.csv / library.xlsx   master list, one row per piece/movement
SCHEMA.md                    column definitions and license policy
README.md                    this file
STATUS.md / STATUS.txt       checkpoint log / build log
files/audio/<id>.<ext>       full recordings, local only (git-ignored; published on Release audio-v1)
files/midi_play/<id>.mid     browser-playable MIDI extracted from shared zips / converted from MusicXML
files/scores/<id>.<ext>      editable scores: MIDI, LilyPond (.ly), PDF, Mutopia zips
                             (<id>_lilypond.zip / <id>_midi.zip; shared sets like
                             mussorgsky_pictures_at_an_exhibition-*.zip, dvorak_new_world-*.zip)
previews/<id>.mp3            15 s audition clips
previews/index.html          audition page (all clips, mood tags, license line, filter box)
parts/                       per-agent source CSVs and summaries, MERGE_NOTES.md, UI_NOTES.md
logs/                        license evidence, source pages, download manifests, rename map
scripts/                     sync_site_data.py, make_preview.py, build_preview_index.py, merge_library.py,
                             upload_release.sh, Commons helpers
```

Files are named by `id`, which already contains the composer, catalogue number and short title (e.g. `beethoven_op67_symphony5.flac`).
A few codex entries also keep their LilyPond source (`.ly`) or the original ALAC file (`chopin_op9_2_nocturne.m4a`) next to the file the CSV points to.

## How to audition offline

The site above is the main way in. For a no-server fallback:

1. Open `previews/index.html` in a browser. Opening it straight from disk works; there are no external dependencies.
2. Type in the filter box to search by composer, title or mood (e.g. `epic`, `dark`, `calm`, `triumphant`).
3. Each card shows the mood tags, the tempo/energy, who added it, and the recording and score licenses. Rows that are not fully verified are labelled.
4. When you like a clip, find its `id` in `library.csv`. Check `legal_notes` and use the full file from the Release (or `files/audio/` locally). Use `notable_excerpt` to find the strongest part.

Every preview is 15 s, MP3 192 kbps, 44.1 kHz stereo, normalised to about -16 LUFS (measured -16.9 to -15.1), with 0.35 s / 0.45 s fades.
Previews are cut from the licensed recording where there is one. Otherwise they are our own FluidSynth renders of the licensed MIDI.
The MIDI renders are bach_bwv1007_prelude, bach_bwv1068_air, debussy_arabesque_1, debussy_clair_de_lune, faure_*, handel_hwv56_hallelujah, mozart_k525_nachtmusik, pachelbel_canon_d and satie_gnossienne_1.
They are not human performances.

## License rules

A public-domain composition does not mean a public-domain recording. Read **both** `recording_license` and `editable_license`, and treat `legal_notes` as binding.

**1. Safe: commercial or social use, no attribution needed.**
- The composition is PD, and the recording is PD, CC0, PDM or US-government.
- Or: your own render from a PD/CC0 score.
- Examples: Musopen PD/CC0 releases, and US Marine, Army, Navy or Air Force Band recordings.
- US-government recordings are PD in the US. Other countries do not always agree; the row notes say so.
- Courtesy credit is still recommended where the source asks for it: Beethoven 5 (Skidmore/Musopen), Moonlight I (Paul Pitman/Musopen), Moonlight III and Träumerei (Musopen).

**2. Safe with attribution (CC BY or Commons "attribution").** Put the credit in the post or video description.

| id | credit |
|---|---|
| bach_bwv565_toccata | Norbert Schenk (organ), CC BY 4.0 |
| rstrauss_zarathustra_sunrise | Kevin MacLeod (incompetech.com), CC BY 3.0 |
| schubert_d328_erlkonig | recording credited on source page, CC BY 3.0 |
| holst_planets_jupiter | Skidmore College Orchestra / Musopen (Commons attribution template) |
| pachelbel_canon_d | preview is a render of a CC BY 4.0 Mutopia edition (Michael Fischer v. Mollard / Mutopia) |
| mussorgsky_night_on_bald_mountain | **score only** CC BY 3.0. The recording itself is PD (site badge: Credit required, "rec Clean · score Credit required"). |

**3. Flag only: do not treat as clean.**
- *Share-alike recordings:*
  - mussorgsky_pictures_baba_yaga (CC BY-SA 2.0 DE)
  - saintsaens_carnival_aquarium (CC BY-SA 2.0)
  - wagner_tristan_prelude (EFF Open Audio License, which works like BY-SA)
  - verdi_requiem_dies_irae (CC BY-SA 4.0, and also `unverified`)
- *Share-alike scores:* the matching recordings are PD/CC0, so only score renders are affected.
  - bizet_carmen_toreador (Carmen Prelude score)
  - dvorak_new_world_largo and dvorak_new_world_finale
  - mussorgsky_pictures_* (promenade, great_gate_kiev, baba_yaga)
  - strauss2_blue_danube (Mutopia MIDI; the preview uses the PD Marine Band recording)
  - satie_gnossienne_1 and faure_pavane: here the **preview itself** is a render of the BY-SA edition.
- *Unverified* (could not confirm the recording's clearance): tchaikovsky_swan_lake_act2_scene, rimskykorsakov_scheherazade_sea, brahms_hungarian_dance_5, verdi_requiem_dies_irae.
- *Composer-term caveats:*
  - Holst (d. 1934, The Planets): PD in the US and in life+70/life+80 countries; not PD where terms run longer (e.g. life+100 in Mexico). The Mars file is only a 61 s excerpt.
  - Rachmaninoff (d. 1943): PD in life+70 countries. Both works were published before 1926, so both are PD in the US.
  - R. Strauss (d. 1949): Zarathustra (1896) is PD in the US and in life+70 countries since 2020.
  - Elgar (d. 1934): Pomp and Circumstance No. 1 (1901) is PD in the US and in life+70 countries.
- *Arrangements:* military-band arrangements with a non-government arranger carry low but non-zero risk. This covers liszt_hungarian_rhapsody_2 and tchaikovsky_nutcracker_waltz_of_flowers.
- *Other:*
  - offenbach_orpheus_cancan uses the retired CC PD dedication, which may not hold outside the US.
  - Vivaldi uses a PDM-owner declaration, not CC0.
  - ravel_pavane is a virtual-piano render.

**4. Excluded (not in the library):**
- Composers: Orff, Prokofiev, Shostakovich, Stravinsky.
- Ravel's Boléro (disputed).
- Anything CC BY-NC, all-rights-reserved, or with a guessed license.
- Recordings tagged PD-EU-audio only, which are still protected in the US (e.g. Barbirolli's 1947 Nimrod).

## Editor's picks for video

The 15 strongest, most recognisable cues for general video editing, ranked. All picks are `verified=yes`. Picks 1–11 and 14 have fully clean **recordings**. (The site badge also counts the score: picks 4 and 5 show ShareAlike and pick 14 Credit required because of their Mutopia scores.) Picks 12, 13 and 15 need a credit (Moonlight I is a courtesy credit). Picks 3 and 10 are PD in the US as government works. The sync script reads this table into `editors_pick_rank` / `editors_pick_why`.

| # | id | why |
|---|---|---|
| 1 | grieg_peer_gynt_mountain_king | Slow-to-frantic build: ideal for countdowns, chases and growth montages. PD recording and PD score. |
| 2 | beethoven_op67_symphony5 | The four-note motif, a thesis statement for bold announcements. PD (courtesy credit Skidmore/Musopen). |
| 3 | tchaikovsky_1812_overture | Cannons and bells finale for victory or record-breaking moments. US Army Band, PD-US. |
| 4 | mussorgsky_pictures_great_gate_kiev | Monumental, cathedral-like grandeur for unveilings and landmark visuals. PD. |
| 5 | dvorak_new_world_finale | Brass march of progress for journeys, launches and openers. PD recording. |
| 6 | beethoven_op84_egmont | Victorious coda in a 48/24 FLAC. Triumphant closer after a struggle. PD. |
| 7 | mozart_k550_symphony40 | Restless urgency under an analytical voice-over. PD FLAC. |
| 8 | chopin_op10_12_revolutionary | Defiant, stormy piano for a turning point or a call to action. PD, named performer. |
| 9 | vivaldi_rv315_summer_storm | Furious strings for storms, turbulence and action cuts. PDM-owner declaration. |
| 10 | verdi_aida_triumphal_march | Ceremonial trumpets for milestones, openings and award moments. US Marine Band, PD-US. |
| 11 | tchaikovsky_piano_concerto_1 | Huge opening chords for a grand, confident intro. CC0 (mono). |
| 12 | bach_bwv565_toccata | The most recognisable dramatic organ opening there is. CC BY 4.0, credit Norbert Schenk. |
| 13 | rstrauss_zarathustra_sunrise | "2001" sunrise awe for dawn-of-a-new-era reveals. CC BY 3.0, credit Kevin MacLeod. |
| 14 | mussorgsky_night_on_bald_mountain | Dark and chaotic, for storms, villains or crisis segments. PD recording. |
| 15 | beethoven_op27_2_moonlight1 | Calm, mysterious contrast for reflective passages. PD (courtesy credit Paul Pitman/Musopen). |

Honourable mentions:
- holst_planets_mars: relentless and martial, CC0, but carries the Holst territorial flag and is only 61 s.
- mendelssohn_op26_hebrides: mysterious, majestic; PD FLAC.
- handel_hwv349_hornpipe: regal; US Marine Band.
- elgar_pomp_circumstance_1: ceremonial; US Marine Band.
- chopin_op9_2_nocturne: calm and polished, CC0.

## How to re-render previews

```bash
cd /workspace/music/library
# from a recording (start as seconds or MM:SS)
python3 scripts/make_preview.py --audio files/audio/<id>.<ext> --start 1:42 --out previews/<id>.mp3
# from a MIDI score (FluidSynth + /usr/share/sounds/sf2/FluidR3_GM.sf2)
python3 scripts/make_preview.py --midi files/scores/<id>.mid --start 0 --out previews/<id>.mp3
# rebuild the audition page from library.csv
python3 scripts/build_preview_index.py
```

`make_preview.py` cuts 15 s and applies the fades. It then normalises in two passes (loudnorm measure, then linear apply at -16 LUFS / -1.5 dBTP) and checks the encoded MP3, correcting the gain if it misses by more than 0.5 LU.
If you change the clip, update `notable_excerpt` in `library.csv` too.

To rebuild `library.csv` / `library.xlsx` from the part files, run `python3 scripts/merge_library.py`.
This normalises filenames, re-renders any missing or off-loudness previews, and is safe to re-run.
It overwrites `library.csv`, so make manual CSV edits in `parts/*_rows.csv`, or don't re-run the merge after editing `library.csv`.

## MuseScore.com: left for later

MuseScore.com downloads need a login, so nothing was downloaded from there, and **no `musescore_url` values were filled in** (the column is empty in every row).
If you later log in and want editable files, these are the pieces with no local editable score. Look them up and record the page URL in `musescore_url` first:
- Holst Mars and Jupiter
- Mozart Symphony 40
- Beethoven Egmont and Moonlight I and III
- Mendelssohn Hebrides
- Vivaldi Spring and Summer
- Handel Water Music
- Tchaikovsky (all)
- Wagner (all)
- Rachmaninoff
- Saint-Saëns
- Liszt
- Smetana, Borodin and Mahler

Check each MuseScore score's own license. Many user uploads are all-rights-reserved or non-commercial, which this library excludes. Prefer the CC0 OpenScore editions.
