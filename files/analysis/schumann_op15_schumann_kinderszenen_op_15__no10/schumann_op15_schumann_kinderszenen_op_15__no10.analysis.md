# Robert Schumann: Kinderszenen Op. 15 No. 10 'Fast zu ernst' (annotated)

Source: `files/scores/schumann_op15_schumann_kinderszenen_op_15.mid`, absolute quarters [867.75, 928]; 2/4, g#, opening ♩≈48.0. MIDI is referenced, not copied.

A displaced sixteenth-note song whose 13-bar span is part of the tension. The tune moves through B major and D# minor without losing the gravity of G# minor. The repeat is already written out in this MIDI; the final open fifth is a tonic ending but cannot pass a full triad check.

## Story and key journey

- Bars 0–0: **Pickup / start**. A lone D#4 pickup, not a complete chord. Mood: hesitant.
- Bars 1–13: **Theme 1**. Thirteen bars, with melody and bass displaced and relative-major/dominant-minor detours. Mood: grave, unsettled.
- Bars 14–26: **Theme 1 restated**. The supplied MIDI repeats the same 13-bar structure. Mood: insistent, reflective.
- Bars 27–29: **Coda / arrival**. G# minor settles, then ends on an open tonic fifth in a 4/4 bar. Mood: quiet, resolved.

## Tricks checked against the notes

- The melody begins at beat 1.25 while the low bass attacks on beat 1: preserve this built-in hesitation.
- The 13-bar phrase closes through the relative major and a D# dominant; a conventional 12-bar crop loses its own restart.
- Low bass, broken inner notes and upper tune form distinct layers; the source MIDI is insufficient to claim canon or invertible counterpoint.

## Loops, hooks and K-pop uses

- Loop bars 0–13: D# pickup plus 13-bar loop, per note recurrence; end at 893.75, moving the returning pickup to the seam.
- Hook bars 1–2: Delayed upper G#–B–A# against G# and Fx bass motion.
- Hook bars 7–11: A#7 → D#m, then D#7 → G#m creates the dark turn and return.
- **verse**: The displaced melody and broad bass leave a restrained narrative groove.
- **pre-chorus**: A#7 → D# minor detour can build tension before a return to G# minor.
- **bridge**: Use the full asymmetric phrase as an instrumental bridge; keep its 13-bar length.
- **chorus**: Revoice the closing G# minor arrival as a sustained refrain; no literal final-chorus step-up occurs.

## Verification and limits

50/50 asserted chord spans pass (100.0%); 2 spans are explicitly `?`. All original MIDI tracks are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

D#4 pickup checked at absolute quarter 867.75; bar 1 at 868. No. 11 starts at 928, in G. The supplied performance unfolds the 13-bar phrase twice (second statement starts at 894), followed by bars 27–28 and a 4/4 closing bar at 924. The MIDI key signature B is interpreted as G# minor, with E# and Fx spelled correctly. No score repeats are added. The empty end of the final 4/4 bar is retained.

- Review bar 10: Bar 10 diminished colour retains D-natural; interpretation above the D# pedal is uncertain. Check against a critical edition.
- Review bar 13: Loop seam uses abs 893.75 (26 quarters), not full downbeat 894; move the pickup deliberately when arranging.
- Unresolved chord spans in bars 0, 29. Exact beats and note-support reasons are in the bundle JSON verification.
