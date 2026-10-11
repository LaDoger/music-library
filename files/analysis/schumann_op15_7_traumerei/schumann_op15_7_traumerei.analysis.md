# Robert Schumann: Träumerei

Source: `files/scores/schumann_op15_7_traumerei.mid`, absolute quarters [0, 97.0]; 4/4, F, opening ♩≈60.0. MIDI is referenced, not copied.

An F-major rising theme in regular four-bar phrases. A (bars 1–8) ends with a half cadence, then cadences in C. B (9–16) restates the opening and sequences it into G minor and then D minor (tonicized, not established keys) before a Bbmaj7 turns back to a half cadence in F. A′ (17–24) repeats bars 1–4 and closes with a G9 peak and a perfect cadence.

## Story and key journey

- Bars 0–0: **Pickup**. Lone C4 upbeat. Mood: hushed.
- Bars 1–8: **A**. 4+4: I–IV rise, HC bar 4; second phrase via A7/C# and Fm to a PAC in tonicized C. Mood: tender, nostalgic.
- Bars 9–16: **B (sequence)**. Bars 9–12 tonicize G minor; 13–16 repeat it a fourth higher in D minor; Bbmaj7 → HC in F. Mood: yearning, wistful.
- Bars 17–24: **A′**. Bars 17–20 = 1–4; G9 peak in bar 22; PAC in bar 24. Mood: warm, settling.

## Tricks checked against the notes

- Bars 1–2: rising melody to a held top note over I–IV, with the accompaniment entering off the beat.
- Bars 3 and 19: V7 → V9 as the melody steps down, then a passing I6 before the half cadence.
- Bars 10 and 14: a suspended minor ninth (Eb5 over D, Bb5 over A) that resolves down by step.
- Bars 9–16: the same four-bar model up a fourth, G minor then D minor, without changing key.
- Bar 16: Dm/A → Bbmaj7 → C swerves away from D minor back to F.
- Bar 22: applied G9 with the melody on its ninth, then the cadence is delayed through ii6 and V/ii.

## Loops, hooks and K-pop uses

- Loop bars 1–4: I–IV–V7–I6–V–I–V ends on a half cadence that leads back into bar 1; needs the C pickup on the seam.
- Loop bars 9–16: Sequence ends on V of F, which resolves to bar 9 F.
- Hook bars 0–2: C–F leap and climb to the held F5 over IV: the famous opening.
- Hook bars 21–24: G9 climax and the closing cadence.
- **verse**: Bars 1–4 (pickup included) as a soft piano bed; four-bar phrases fit a vocal line.
- **pre-chorus**: Bars 13–16: rising sequence into D minor, ending on V of F to set up a chorus.
- **bridge**: Bars 9–12 move into G minor for a darker contrast with the same melody.
- **chorus**: Bars 21–24 (G9 peak, delayed cadence, PAC) as an emotional closing hook; no key change exists in the source.

## Verification and limits

62/63 asserted chord spans pass (98.41%); 4 spans are explicitly `?`. All original MIDI tracks and CC64 sustain releases are checked; non-chord tones remain in the ≥70% coverage denominator. This verifies pitch support, not harmonic function or the authority of the MIDI edition.

Mutopia MIDI (PD edition): one-quarter C4 pickup at quarter 0, bar 1 at quarter 1, 24 bars of 4/4 to quarter 97. No triplets; straight grid. The printed repeats (bars 1–8 and 9–24) are not unfolded in the MIDI and are not added. Spread bass grace notes (Bb2 bar 2/18, C#3 bar 6) sound 0.125 q before beat 2. MIDI-derived score, not an Urtext; bar 22 fermata appears only as a tempo drop.

- Review bar 0: Pickup confirmed from the LilyPond \partial 4 and the MIDI onset; the draft omitted it, so all its bar labels were one beat early.
- Review bar 8: Beat-3 C arrival has no G in the MIDI (root+third only); the label is retained and fails the mechanical check.
- Review bar 8: Cadence in C is read as a tonicized dominant inside F; a short modulation to V is also a defensible reading.
- Review bar 9: Draft F→D minor and D minor→F modulations removed: G minor (bars 10–12) and D minor (14–16) are tonicizations; no structural cadence in either.
- Review bar 12: G-minor dominant on beat 2.5 has no F#, and beat 4 has only G2–A2 under F4; both left as ? rather than forced.
- Review bar 16: Dm/A on beat 3 could be heard as an unresolved 6/4 rather than a tonic arrival; labelled vi64 either way.
- Review bar 22: Bar 22 tempo drop interpreted as the editions' fermata; dynamics are not inferred.
- Unresolved chord spans in bars 0, 8, 12. Exact beats and note-support reasons are in the bundle JSON verification.
