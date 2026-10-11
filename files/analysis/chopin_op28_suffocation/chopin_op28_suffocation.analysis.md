# Frédéric Chopin: Prelude: Op. 28, No. 4 ('Suffocation')

Source: `files/scores/chopin_op28_suffocation.mid`, absolute quarters [0, 101.0]; 2/2, e, opening ♩≈56.0. MIDI is referenced, not copied.

E minor throughout, in two parallel halves (1–12, 13–25). Over a static B–C sigh in the melody, the LH repeated chords slide down one semitone at a time through dominant, half-diminished and diminished sevenths, reaching iv (A minor) by bar 9 and ending the first half on V7 (bar 12). The second half repeats the opening with a faster slide, breaks into the only climax (C6 over B7♭9, bar 17), dodges the cadence with V7 → VI (bars 20–21), and closes with an augmented sixth (bar 23) and V → i (bars 24–25). There are no real modulations; A minor is only tonicized.

## Story and key journey

- Bars 0–0: **Upbeat**. Lone B upbeat. Mood: hushed.
- Bars 1–12: **A (first half)**. Melody holds B–C for four bars, then A–B, while the LH descends chromatically from i6 to iv6 (bar 9). Bars 9–12: the melody starts moving; B7 ↔ iv6 alternation; HC on V7 in bar 12. Mood: desolate, numb, sighing.
- Bars 13–16: **A′ (second half)**. Restatement of bar 1 with a compressed chromatic slide (bars 14–15), then the melody breaks upward in bar 16. Mood: desolate, restless.
- Bars 17–20: **Climax and collapse**. C6 over B7(b9) in bar 17, falling back at once; suspended dominants (bars 18–20) end on B7. Mood: anguished, exhausted.
- Bars 21–25: **Coda**. Deceptive V7 → VI (bar 21), cadential 6/4 (bar 22), augmented sixth then silence (bar 23), V with 4–3 (bar 24), tonic close (bar 25). Mood: resigned, grave, still.

## Tricks checked against the notes

- Bars 1–8: the melody barely moves (B–C, then A–B); all the motion is in the LH chords, where one voice at a time slips down a semitone.
- Bars 2–8: the chromatic slide passes through V43, a French-sixth-sounding B7♭5, iiø7 and viio7 colours before landing on iv6 at bar 9.
- Bar 12: the LH drops out and the RH alone spells V7, ending the first half on the dominant.
- Bar 17: the only climax, C6 over B7♭9 with an octave B bass, gone within a bar.
- Bars 20–21: V7 → VI deceptive resolution delays the ending.
- Bar 23: augmented sixth with A# in the bass, followed by silence, before V (with 4–3) → i.

## Loops, hooks and K-pop uses

- Loop bars 1–8: Static B–C / A–B melody over a slowly descending chord bed; bar 8 G#o7 moves to A minor, so the seam back to bar 1 Em/G is audible.
- Loop bars 1–4: i6 → V43 → chromatic → E7 four-bar cell with a constant melody note; loops on a single held B.
- Hook bars 0–4: B upbeat, held B with C neighbour, LH chords sliding down: the recognisable opening.
- Hook bars 16–17: Melody leaps to A5 and peaks on C6 over B7♭9.
- Hook bars 20–25: Deceptive cadence, augmented sixth, silence and the final cadence.
- **verse**: Bars 1–8 as a sparse piano bed; the near-static melody leaves room for a vocal line, and the LH chord slide gives slow harmonic motion.
- **bridge**: Bars 16–17: the sudden upward break to C6 suits a short emotional peak before a drop-out.
- **pre-chorus**: Bars 9–12: moving melody over B7 ↔ iv6, ending on V7 to set up a chorus in E minor.
- **chorus**: Bars 20–25 as an outro: deceptive V7 → VI, a silent beat, then V → i. Slow (quarter = 56); no key change exists in the source.

## Verification and limits

54/56 asserted chord spans pass (96.43%); 2 spans are explicitly `?`. All original MIDI tracks and CC64 sustain releases are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

Mutopia MIDI (PD edition, piece 468): one-quarter pickup at quarter 0, bar 1 at quarter 1, 25 bars of 2/2 (4 quarters each) to quarter 101. No repeats. MIDI tempo 56 per quarter throughout. Pickup sounds B3 (dotted eighth) then B4 (sixteenth); printed editions show a B4 upbeat, so the B3 may be a source octave error. Bars 12 and 18 contain RH eighth-note triplets. Bar 23 has two quarters of sound then silence (the printed fermata rest). A# / D# are spelled Bb / Eb in the MIDI-derived score. The LH repeated chords and the final three chords are merged in places by the MIDI; the final bar is a single whole-bar chord. MIDI-derived score, not an Urtext.

- Review bar 0: Draft had no pickup, so all its bars were one quarter early and it showed 26 bars; corrected to a 1-quarter pickup + 25 bars (quarter range 0–101).
- Review bar 0: Pickup B3 dotted-eighth + B4 sixteenth in the MIDI; editions print a B4 upbeat. Not corrected (MIDI kept as source).
- Review bar 1: Draft key changes e → a (bar 1), a → E (bar 9), E → e (bar 17) removed: no cadence confirms either key. A minor is tonicized in bars 3–9; the piece stays in E minor.
- Review bar 3: Many LH sonorities in bars 2–8 and 14–16 are voice-leading products of the chromatic descent; the seventh-chord labels describe the sound, and the Roman numerals are approximate.
- Review bar 3: Beat 4 G#o7/F fails the check: B4 stops at beat 4 and the melody C5 is the recurring upper neighbour, so B is absent for one quarter (F–G#–D–C). Kept as G#o7; not relabelled Dø7.
- Review bar 16: Beat 3 left as ?: C#–E–Bb with A5 in the melody and no G; incomplete A7(b9)/C# or C#o7 with an appoggiatura.
- Review bar 17: Beat 3 (D#/F#/G/B for one eighth) is treated as the B7 resolving late; Em/G is labelled from beat 3.5.
- Review bar 18: Bsus4 in bars 18–20 has no D# until bar 20 beat 3; it could also be read as an Em/B 6/4 without G.
- Review bar 21: C7 on beat 3 has Bb moving down to A, so it is read as a chromatic VI7, not an augmented sixth; only bar 23 is labelled Ger+6.
- Review bar 21: Beat 1 C fails on coverage (66.7%): the MIDI pedal goes down on the same tick (q 81) as the bar-20 B7 chord releases, so the verifier holds B, D# and A into bar 21. The attacks are C3–G3–E4 only; C is kept.
- Review bar 22: Beat 1 B–E–A is read as Esus4/B (cadential 6/4 with suspended A), not B7sus4: no F# sounds.
- Review bar 22: G# on beat 2 is read as a passing major-mode colour in the A–G#–G inner line, not a real E-major arrival.
- Review bar 25: Printed editions have three separate final chords; the MIDI sounds one whole-bar chord. Dynamics (smorzando / pp) are not inferred.
- Unresolved chord spans in bars 0, 3, 16, 21. Exact beats and note-support reasons are in the bundle JSON verification.
