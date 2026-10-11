# Johannes Brahms: Waltz No. 10

Source: `files/scores/brahms_op39_waltz_no_10.mid`, absolute quarters [0, 96.0]; 3/4, G, opening ♩≈160.0. MIDI is referenced, not copied.

A 16-bar G-major waltz with both halves repeated (the MIDI unfolds it to 32 bars). A opens off-tonic: rocking, then rising, parallel thirds over a D pedal (V7). A G pedal then carries G7–C/G–Gm, darkening before a half cadence. B swerves from that D7 straight to B major (chromatic mediant), repeats the figure in B minor, and uses Bm as iii of G to return through IV–ii6–V7–I.

## Story and key journey

- Bars 1–8: **A**. 4 bars of V7 over a D pedal (rocking, rising thirds), then 4 bars over a G pedal (G7–C/G–Gm) closing on V7 (1st ending). Mood: graceful, lilting.
- Bars 9–16: **A (repeat)**. Literal repeat; the 2nd ending (bar 16) closes on V7 (HC). Mood: graceful, lilting.
- Bars 17–24: **B**. 2+2+4: B major, then B minor, then IV–ii6–V7–I in G (IAC on the 1st ending). Mood: surprised, bittersweet, resolved.
- Bars 25–32: **B (repeat)**. Literal repeat; the 2nd ending closes with a PAC on G. Mood: surprised, bittersweet, resolved.

## Tricks checked against the notes

- Bars 1–4: the waltz opens on V7 over a D pedal, not on the tonic; G appears only as passing G/D sonorities.
- Bars 1 and 3: the RH moves in parallel thirds, first rocking (C/E–D/F#), then climbing a scale in thirds.
- Bars 5–7: the tonic arrives as G7, then C/G, then G minor (Bb–B oscillation) over a G pedal, with an inner line falling F–E–D.
- Bars 16–17: the half-cadence D7 resolves to B major instead of G (chromatic mediant).
- Bars 17–20: the same two bars in B major, then B minor: parallel-mode shading.
- Bars 20–21: Bm is reinterpreted as iii of G and leads back by V7.
- Bars 21–24: IV–ii6–V7–I cadence with falling appoggiatura sixths over V7.

## Loops, hooks and K-pop uses

- Loop bars 1–8: Composer's own repeat: the 1st-ending D7 (bar 8) runs into the D7 of bar 1.
- Loop bars 1–4: Four bars of V7 over a D pedal: a hovering, unresolved loop.
- Loop bars 17–24: Composer's own repeat of B; the G-to-B seam is the mediant swerve.
- Hook bars 1–2: Rocking thirds over a D pedal, V7–I64–V7: the opening gesture.
- Hook bars 16–18: D7 to B major: the chromatic-mediant swerve.
- Hook bars 21–24: IV–ii6–V7–I cadential tag in G.
- **verse**: Bars 1–4: a dominant pedal with rocking thirds feels light and suspended; it suits a soft verse that has not landed yet.
- **pre-chorus**: Bars 5–8: G7–C/G–Gm over a tonic pedal darkens, then halts on V7 to set up an arrival.
- **bridge**: Bars 17–20: V7 sidestepping to B major, then B minor, gives a bridge a bright jolt and a shadow before IV–ii6–V7–I (bars 21–24) brings it home.

## Verification and limits

40/40 asserted chord spans pass (100.0%); 2 spans are explicitly `?`. All original MIDI tracks and CC64 sustain releases are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

Mutopia MIDI (LilyPond render, Public Domain, piece 2164): 32 bars of 3/4 from quarter 0 (no pickup), quarter = 160 BPM, no CC64 pedal. Both repeats are written out in the MIDI: A = bars 1–8 (1st ending bar 8) and 9–16 (2nd ending bar 16); B = 17–24 (1st ending) and 25–32 (2nd ending). Bar numbers follow the unfolded MIDI, not printed volta numbering. Home key G (MIDI key signature G; the draft's 'b' was a key-window artefact). Grace notes B–C–D before bars 23/31 (0.05 quarter) are omitted in notation. MIDI-derived score, not an Urtext.

- Review bar 1: The draft's key b was a window artefact; the piece is in G (MIDI key signature G). Bars 1–4 prolong D7 with passing G/D and Em7/D (= G6/D) sonorities; this is not a key change.
- Review bar 7: Gm is a colour reading: B natural (LH beat 3 and RH eighths) sounds almost as much as Bb, so a chromatic-neighbour oscillation over G is equally valid.
- Review bar 17: Bars 17–20 could be read as a tonicization of III/iii rather than established keys. B and b key signatures are shown because the passage is a self-contained 4-bar unit with no G-major chord.
- Review bar 24: IAC vs PAC depends on which RH line is heard as the melody. The D5 top voice makes the 1st ending imperfect; the 2nd ending (bar 32) has G4 on top.
- Unresolved chord spans in bars 8, 16. Exact beats and note-support reasons are in the bundle JSON verification.
