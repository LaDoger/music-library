# Frédéric Chopin: Mazurka: Op.33, No.1

Source: `files/scores/chopin_op33_mazurka_op_33_no_1.mid`, absolute quarters [0, 145.0]; 3/4, g#, opening ♩≈60.0. MIDI is referenced, not copied.

A short g# minor mazurka in ternary form. A (bars 1–12) is a sighing 12-bar theme over i, ii∅6/5, iv and V7 with two perfect cadences. A borrowed Em/G turns to B major, which is prepared by eight bars of dominant (F# pedal, then V7/V–V) before an 8-bar V7–I dance in B, played twice. D# links back to a literal return of A.

## Story and key journey

- Bars 0–0: **Pickup**. Lone D# upbeat. Mood: hesitant.
- Bars 1–12: **A**. g# minor, 4+4+4: opening phrase with an unaccompanied climb (3–4), then a ii∅6/5–i / iv–i / V7–i phrase stated twice, each ending with a PAC. Mood: melancholy, wistful.
- Bars 13–20: **B (dominant preparation)**. F# pedal under V7 and a common-tone dim7 (13–16), then V7/V–V four times (17–20): B major is promised but not yet stated. Mood: yearning, rising.
- Bars 21–36: **C (B-major dance)**. ii6–V7–I–V7–I–V7–I in B, 8 bars, repeated literally (29–36); octave-doubled melody from bar 25. Mood: bright, lilting.
- Bars 37–48: **A′**. Literal return of bars 1–12; ends on the second PAC with no coda. Mood: melancholy, resigned.

## Tricks checked against the notes

- Bars 0–2: a single upbeat and neighbour-note sigh before any harmony, then viio7/V–V7–i.
- Bars 3–4: the accompaniment drops out and the melody climbs alone.
- Bars 5–6: accompaniment on beats 2–3 only (iiø6/5–i, iv–i): the mazurka weight sits off the downbeat.
- Bar 12: a borrowed Em/G (minor iv of B) as the hinge into the relative major.
- Bars 13–20: eight bars of dominant (F# pedal, common-tone dim7, V7/V–V with 4–3 sighs) delay the B tonic until bar 24.
- Bars 21–28: two-chord V7–I dance with an added-sixth G#; octave doubling from bar 25 thickens the repeat.
- Bar 36→37: D# held from the B chord becomes the upbeat of the returning g# theme.

## Loops, hooks and K-pop uses

- Loop bars 5–8: iiø6/5–i, iv–i, viio7/V–V7, i: ends on the tonic and Chopin himself follows bar 8 with the same phrase (bars 9–12).
- Loop bars 21–28: B-major dance; the score repeats it literally (29–36), so the seam bar 28→21 is the composer's own.
- Loop bars 25–28: Octave-doubled V7–I–V7–I; four-bar loop in B.
- Hook bars 0–2: D# upbeat, E–D# sigh and viio7/V–V7–i: the opening gesture.
- Hook bars 17–20: V7/V–V swing with high/low register answers.
- Hook bars 23–24: V7–I with the leaping bass and added-sixth G#.
- **verse**: Bars 5–8 as a minor-key piano bed: four bars, chords on beats 2–3, ending on the tonic (loopable).
- **pre-chorus**: Bars 13–20: F# dominant pedal then V7/V–V; builds expectation for a B-major chorus.
- **chorus**: Bars 21–28: bright V7–I in B, the relative major of the verse; an 8-bar loop.
- **bridge**: Bars 0–4: sparse solo line with almost no harmony for a breakdown before returning to the minor verse.

## Verification and limits

62/62 asserted chord spans pass (100.0%); 17 spans are explicitly `?`. All original MIDI tracks and CC64 sustain releases are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

Mutopia MIDI (LilyPond 2.12.2 render, CC BY 3.0, Ryan Prince and the Mutopia Project): one-quarter D#4 pickup at quarter 0, bar 1 at quarter 1, 48 bars of 3/4 to quarter 145 (MIDI tempo 60 BPM). The A reprise (bars 37–48) and the repeat of the dance (29–36) are written out in the MIDI and are not doubled. Mordent (bar 11/47) and grace notes (bars 6, 10, 42, 46) sound as short notes before the beat. Sustain pedal (CC64) only in bars 17–36 and the last bar. MIDI-derived score, not an Urtext.

- Review bar 0: Pickup confirmed from the MIDI (D#4 alone at quarter 0; the viio7/V and V7 fall on beats 2–3 only with a one-quarter offset). The draft had no pickup, so every bar label was one beat early, and its tempo (100) did not match the MIDI (60).
- Review bar 1: Beat 2 of bars 1/7/11/37/43/47 is read as viio7/V (Cx–E#–G#–B) without E#; left as ? rather than asserting Cx°7 or the draft's misspelled G#dim/D.
- Review bar 6: Beat 1 of bars 6, 9, 10, 42, 45, 46 has only the melody; the tonic of the previous bar is implied but has stopped sounding, so these spans are ?.
- Review bar 13: B major is entered at bar 13 for the dominant preparation, but the B tonic first sounds in bar 24. Bars 13–20 could also be read as V of III inside g#; the modulation is confirmed by the 16 bars of B in 21–36.
- Review bar 15: F#o7 on beat 3 labelled as a common-tone diminished seventh (cto7) over the pedal; spelled F#–A–C–D# as in the MIDI.
- Review bar 18: C#7 is labelled from beat 1 although the left hand enters on beat 2; the beat-1 F# is read as a prepared 4–3 suspension over C#7 (also in bars 19–20).
- Review bar 15: Volume swell is taken from MIDI CC7 data, not from pitch changes; other dynamics are not inferred.
- Unresolved chord spans in bars 0, 1, 3, 4, 6, 7, 9, 10, 11, 37, 39, 40, 42, 43, 45, 46, 47. Exact beats and note-support reasons are in the bundle JSON verification.
