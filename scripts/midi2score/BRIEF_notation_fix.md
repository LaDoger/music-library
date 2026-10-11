# MusicBot: notation-fix pass for one MIDI-reconstructed score

Inputs: ID, MXL=files/scores/ID_reconstructed.mxl, MIDI (item's midi_play_url in data/items/ID.json).
Goal: make the score read like a sensible edition. Do NOT change which pitches sound or when.

1. Render: `xvfb-run -a mscore3 -o /tmp/musicbot_notation/ID.png -T 10 MXL` and LOOK at every page image.
2. List the obvious errors: staff crossings (notes on the wrong staff / ledger-line towers), stray or
   doubled rests, needless extra voices, wrong pickup/bar origin, bad enharmonic spelling, missing
   clef changes, bad ties/tuplets from quantisation, wrong time/key signature.
3. Fix them with a Python/music21 script (write it to /tmp/musicbot_notation/ID_fix.py), writing back to MXL.
   You may move notes between staves, merge/split voices, respell, add clef changes, re-bar a pickup,
   simplify tuplets that are clearly quantisation noise (keeping onsets within a 32nd).
4. Verify: `python3 scripts/midi2score/check_notes.py MIDI MXL` must exit 0. Re-render and look again.
5. Write /tmp/musicbot_notation/ID.notes.md: what was wrong, what you fixed, what remains (be concise).
Do not run git, do not touch any other file, no audio.
