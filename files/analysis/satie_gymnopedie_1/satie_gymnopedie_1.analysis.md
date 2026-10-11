# Erik Satie: Gymnopédie No. 1

Source: `files/scores/satie_gymnopedie_1.mid`, absolute quarters [0, 141.0]; 3/4, D, opening ♩≈60.0. MIDI is referenced, not copied.

D major, 3/4, slow (quarter = 60). Every bar is bass on beat 1 and a chord on beats 2–3, one harmony per bar. A four-bar Gmaj7–Dmaj7 sway (IVmaj7–Imaj7, F#4 common in both) carries the theme (bars 5–12, restated 13–21). The bass then steps out (iii–vi–ii) to a borrowed D minor (bar 21). A second melody (22–31) sits over a nine-bar D pedal that alternates Em7, Am (minor v), D7 and Dm7. The first ending (32–39) closes with Mixolydian v7 → I. In this MIDI the repeat is not unfolded: the second ending (40–47) follows straight away and turns to D minor over an E pedal, ending v7 → i.

## Story and key journey

- Bars 1–4: **Intro**. Gmaj7–Dmaj7 sway alone. Mood: still, hypnotic.
- Bars 5–12: **A: theme**. Melody F#–A–G–F#–C#–B–C#–D–A over the sway, held A4 to bar 12; plagal close at bar 8. Mood: wistful, gentle.
- Bars 13–21: **A': theme and continuation**. Bars 13–16 repeat the theme; bass moves F#–B–E–E–D (iii–vi–ii–ii7–borrowed i). Nine-bar phrase ending on held E4 over Dm(add9). Mood: wistful, searching.
- Bars 22–31: **B: second melody over D pedal**. Two five-bar phrases (22–26, 27–31) over a tonic pedal from bar 23; Em7/D, Am/D, D7 and Dm7 mix major and minor tonic colour. Mood: melancholy, floating.
- Bars 32–39: **Close (first ending)**. Bass E–F#–B–E pedal, melody rises to E5, ii9 → v7 → I in D major. Mood: lifting, resolved.
- Bars 40–47: **Close (second ending)**. Same start as bar 32, then F natural, E pedal under Dm/E, Fmaj7/E, Am/E; Em7(b9) → Am7 → Dm. Mood: darkening, resigned.

## Tricks checked against the notes

- Bars 1–16: only two chords, Gmaj7 and Dmaj7, one per bar. They share F#4, so the right-hand chord barely changes while the bass swings G2–D2.
- Bass on beat 1, chord on beats 2–3: the whole piece uses this slow waltz texture with about two octaves of empty space between bass and chord.
- Bar 6: melody C#5 over Dmaj7 puts the major seventh on top, the piece's signature colour.
- No leading note at the cadences: minor v (Am, Am7) replaces V in bars 22, 25, 28, 30, 38 and 46.
- Bars 21 and 27: D minor appears right next to D major (borrowed i, i7), so the mode keeps shifting under the same bass.
- Bars 23–31: nine bars of tonic pedal D2 under Em7, Am, D7 and Dm7.
- Bars 40–47: the second ending replays the first-ending shape with F natural over an E pedal and closes in D minor.

## Loops, hooks and K-pop uses

- Loop bars 1–4: Gmaj7–Dmaj7 ×2 with no melody; bar 4 Dmaj7 returns to bar 1 Gmaj7 exactly as in the piece.
- Loop bars 5–12: Full theme over the sway; bar 12 Dmaj7 → bar 5 Gmaj7 is the written return (bars 12 → 13).
- Loop bars 23–26: Em7/D–Em7/D–Am/D–D7 over the D pedal; D7 back to Em7/D keeps the pedal, but the melody seam needs listening.
- Hook bars 5–8: The famous opening melody F#–A | G–F#–C# | B–C#–D | A over IVmaj7–Imaj7.
- Hook bars 1–2: Gmaj7 → Dmaj7 bass-and-chord cell; recognisable without the melody.
- Hook bars 38–39: Am7 → D modal cadence (first ending close).
- **verse**: Bars 1–4 / 5–12: the Gmaj7–Dmaj7 sway at quarter = 60 (or double-time feel at 120) gives a soft bed with a lot of room for a vocal.
- **pre-chorus**: Bars 17–21: bass steps F#m–Bm–Em–Em7 to borrowed Dm(add9) under one held note; the shift to minor builds tension before a chorus.
- **bridge**: Bars 22–31: D pedal with Em7, Am, D7 and Dm7 mixing major and minor; suits a hazy, floating bridge.
- **chorus**: Bars 32–39 as an outro or final line: rising melody and Am7 → D close without a leading note. Bars 40–47 give a darker minor ending. There is no key lift in the source.

## Verification and limits

47/47 asserted chord spans pass (100.0%); 0 spans are explicitly `?`. All original MIDI tracks and CC64 sustain releases are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

Mutopia MIDI (PD edition, piece 37): 47 bars of 3/4 from quarter 0, no pickup, MIDI tempo 60 per quarter, key signature 2 sharps. The MIDI does NOT unfold the repeat: bars 1–39 are the first half with its first ending (bars 32–39, closing on D major), and bars 40–47 follow directly as the second ending (printed bars 71–78 in a written-out edition, closing on D minor). The repeated bars 1–31 are not played a second time. Bars 9–12 carry an F#4 quarter on beat 1 in the treble track (doubling the chord's F#4); not checked against a printed edition. Texture throughout: bass dotted half on beat 1, chord on beats 2–3, melody above. MIDI-derived score, not an Urtext.

- Review bar 1: Draft split each bar into a "?" bass beat and a beats-2–3 chord. The bass dotted half sounds under the chord, so one chord per bar from beat 1 is used.
- Review bar 1: Tempo set to the MIDI value (quarter = 60); the draft said 100.
- Review bar 33: Draft key change D → A at bar 33 removed: no G# and no E–A cadence; A/E (bar 35) moves to iii42, not I. Read as D major through bar 39.
- Review bar 40: The MIDI does not unfold the repeat: bars 40–47 (second ending) follow bar 39 directly, and the repeat of bars 1–31 is missing. Bar numbers 40–47 here = printed 71–78 in a written-out edition.
- Review bar 40: D → d treated as a modulation for the second ending, since the piece ends in D minor. Bar 40 itself has no F; the F natural arrives at bar 41. A modal-mixture reading (D Dorian/Aeolian close) is also possible.
- Review bar 25: Am/D (bars 25, 28, 30) could also be named D7sus2 (D–E–A–C); music21 has no 7sus2 symbol, so it is labelled as minor v over the tonic pedal.
- Review bar 9: Bars 9–12: treble F#4 quarter on beat 1 doubles the chord F#4; source detail not checked against print.
- Review bar 39: Cadences in bars 39 and 47 are v7 → I/i with no leading note, so they are labelled tonic_close, not PAC/IAC. Draft IAC/HC candidates in bars 26, 28, 31, 38, 40 and 46 removed (no V present).
