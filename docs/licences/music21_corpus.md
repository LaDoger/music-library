# music21 corpus: licence check (2026-10-09)

Source: https://github.com/cuthbertLab/music21/tree/master/music21/corpus (read over HTTPS; music21 10.5.0 installed in a temp venv only to convert MusicXML to MIDI).

## Blanket terms

- https://github.com/cuthbertLab/music21/blob/master/LICENSE: BSD 3-Clause. This covers the **software**, not the corpus.
- https://github.com/cuthbertLab/music21/blob/master/music21/corpus/license.txt: "Some encodings included in the corpus may not be used for commercial uses or have other restrictions: please see the licenses embedded in individual compositions or directories for more details." and "there may be restrictions on commercial use."
- https://github.com/cuthbertLab/music21/blob/master/music21/corpus/essenFolksong/license.txt: "The legal status of the Essen folksong database is unclear ... permission for non-commercial distribution and use of these files in music21."

So the corpus as a whole is **not** commercial-safe. A file passes only if its own embedded `<rights>` says PD, CC0 or CC BY, and the composer died in 1929 or earlier.

## Per-collection verdicts

| collection | embedded rights (quoted) | verdict |
|---|---|---|
| lusitano/allor_che_ignuda.mxl | "Copyright 2022 Michael Scott Asato Cuthbert: released as CC0/Public Domain" | **include** (CC0, clean) |
| weber/concertino_clarinet.mxl | "Released to Public Domain in 1998" (arranger Oliver Seely) | **include** (PD, clean) |
| corelli/opus3no1/1grave.xml | "© 2014, Creative Commons License (CC-BY)" | **include** (CC BY, attribution: credit Michael Scott Cuthbert / music21 corpus) |
| liliuokalani/aloha_oe.mxl | "Copyright 1884 by LILIUOKALANI (Now, Public Domain; Encoding by MSAC, CC0)" | eligible, but `uokalani_aloha_oe` already in library_bulk.csv; skipped |
| johnson_j_r/lift_every_voice.mxl | "Public Domain (Encoding by MSAC: CC0)" | exclude: J. Rosamond Johnson died 1954 (> 1929 rule) |
| leadSheet/fosterBrownHair.mxl | "Public Domain"; source wikifonia.org | exclude: Wikifonia user encoding, so the rights line probably covers the song and not the encoding. Unclear. |
| leadSheet/berlinAlexandersRagtime.mxl | "All Rights Reserved" | exclude |
| beach/prayer_of_a_tired_child.musicxml | "Engraving Copyright 2017 Michael Scott Cuthbert, most uses allowed for ..." | exclude: not an explicit PD/CC0/CC BY, and Beach died 1944 |
| ciconia, luca (trecento) | "freely distributed under a CC-BY-SA 3.0 license" | exclude (SA) |
| webern | "The edition CC-BY-SA Michael Scott Cuthbert"; Webern died 1945 | exclude |
| schoenberg | no rights; died 1951 | exclude |
| schubert/Lindenbaum.xml, schumann_clara/opus17 | "Copyright ©" (empty) | exclude |
| bach (433, Finale/Dolet), beethoven, haydn, mozart, joplin (MuseScore.com source), handel, verdi, cpebach, schumann_robert, schumann_clara polonaises, monteverdi | no `<rights>` element in sampled or all files | exclude (no licence stated) |
| palestrina (*.krn), chopin (*.krn) | KernScores headers: "Copyright 2000, John Miller ... Rights to all derivative electronic formats reserved." / ENC Craig Stuart Sapp | exclude |
| essenFolksong | non-commercial permission only | exclude (NC) |
| ryansMammoth, oneills1850, airdsAirs, nottingham-dataset, miscFolk (ABC) | transcriber notes only (e.g. "Contributed by Ray Davies", "Transcribed by Norbert Paap"); no licence | exclude (unclear) |
| trecento (103), josquin, demos, theoryExercises | trecento/josquin not individually cleared; demos and exercises are test files | exclude |

## Output

`scripts/bulk/harvest_music21.py` re-downloads each allow-listed file, checks that its `<rights>` still matches, converts it to `files/scores/<id>.mid` with music21, and writes `parts/BULK_batchK_rows.csv` (3 rows: `lusitano_allor_che_ignuda`, `weber_j109_clarinet_concertino`, `corelli_op3no1_grave`).
