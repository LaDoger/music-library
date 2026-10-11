# Frédéric Chopin: Prelude: Op. 28, No. 20

Source: `files/scores/chopin_op28_funeral_march.mid`, absolute quarters [0, 52.0]; 4/4, c, opening ♩≈42.0. MIDI is referenced, not copied.

C minor throughout. Thirteen bars of block chords, one per beat. Phrase 1 (1–4) states the march: i–iv7–V7–i, a one-bar visit to Ab (VI, with Db), then C7→Fm and V/V→V, ending on a half cadence. Phrase 2 (5–8) moves the melody up an octave over a chromatic bass (C down to Eb) that passes a French sixth, then cadences: V65→i (bar 7) and the Neapolitan Db→V7→i PAC (bar 8). Bars 9–12 repeat 5–8 exactly; bar 13 is a held tonic chord.

## Story and key journey

- Bars 1–4: **A (march)**. Full chords with octave bass; i–iv7–V7–i, Ab tonicized in bar 2, HC on G in bar 4. Mood: solemn, grave, heavy.
- Bars 5–8: **B (lament)**. Higher melody over a semitone-by-semitone falling bass; French sixth (bar 6), IAC (bar 7), Neapolitan → PAC (bar 8). Mood: mournful, tender.
- Bars 9–12: **B′ (echo)**. Exact repeat of bars 5–8 (printed pp; dynamics not in the MIDI). Mood: mournful, hushed.
- Bars 13–13: **Coda**. Held C-minor chord. Mood: final, still.

## Tricks checked against the notes

- Every beat is a new full chord: the harmony changes four times per bar at quarter = 42, so the progression itself carries the melody.
- Bar 2: a whole bar in Ab (VI) with Db (bII), the same chords that later set up the final cadence in bar 8.
- Bars 5–7: the bass falls chromatically C–B–Bb–A–Ab–G, then F–Eb, under a nearly stepwise melody (lament bass).
- Bar 6: French sixth Ab–C–D–F# opens out onto the G octave.
- Beat-3 dotted rhythm with an appoggiatura (Eb→D, G→F, B→A) adds a sigh to most bars.
- Bars 9–12 repeat 5–8 exactly; the contrast in editions is dynamic only.

## Loops, hooks and K-pop uses

- Loop bars 5–8: Self-contained phrase ending on a PAC to C minor; bar 5 restarts on Cm, so the seam is a tonic-to-tonic join.
- Loop bars 1–4: Ends on V (G), which leads back to the Cm of bar 1.
- Hook bars 1–2: The recognisable opening chord march: i–iv7–V7–i, then Ab–Db–Eb7–Ab.
- Hook bars 5–6: High Eb5–D5–C5 line over the chromatic bass and the French sixth.
- Hook bars 7–8: Double cadence: V65→i, then Neapolitan → V7 → i.
- **verse**: Bars 5–8 as a slow piano bed: one chord per beat, chromatic falling bass, and the melody moves little, leaving space for a vocal.
- **chorus**: Bars 1–4 as a heavy ballad chorus progression (i–iv7–V7–i, VI–bII–V7/VI–VI) at half time with drums; ends on V for a turnaround.
- **bridge**: Bars 6–8: French sixth and Neapolitan before V7–i give a dark pre-resolution moment.

## Verification and limits

45/45 asserted chord spans pass (100.0%); 4 spans are explicitly `?`. All original MIDI tracks and CC64 sustain releases are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

Mutopia MIDI (PD edition, piece 472): 13 bars of 4/4, no pickup, quarter range 0–52, quarter = 42 throughout. Bars 9–12 are written out (the printed repeat of bars 5–8); not doubled. Beat 3 of most bars is a dotted-eighth + sixteenth figure. Constant MIDI velocity: printed ff / p / pp and the crescendo in bar 12 are not in the source and are not inferred. Ab/Db/Gb sound as G#/C#/F# spellings in the MIDI-derived score. MIDI-derived score, not an Urtext.

- Review bar 1: Draft read bar 1 as one Cm chord and missed the per-beat harmony; every bar was relabelled per quarter.
- Review bar 2: Ab is tonicized for one bar (I–IV–V7–I in Ab), not modulated; kept key c with a modulation event marking the brief Ab region and Roman numerals relative to C minor.
- Review bar 5: Beat 3 (B–D–Ab + F# sixteenth) left as ?: incomplete viio7 without F. Same in bar 9.
- Review bar 6: Beat 1 (A–C–G) left as ?: passing sonority on the chromatic bass, no complete triad. Same in bar 10.
- Review bar 6: Beat 2 labelled A-7b5 as the enharmonic spelling of the French sixth Ab–C–D–F#.
- Review bar 7: Draft IAC in bar 7 kept (V65 → i, melody Eb); the draft had no PAC in bar 8, added (G7 root position → Cm, top voice C).
- Review bar 9: Dynamics (ff, p, pp, crescendo) are printed in editions but absent from the constant-velocity MIDI; only the B′ section description mentions them.
- Unresolved chord spans in bars 5, 6, 9, 10. Exact beats and note-support reasons are in the bundle JSON verification.
