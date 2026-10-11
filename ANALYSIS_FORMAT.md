# Annotated-score bundles, version 1

One directory per piece: `files/analysis/<id>/`. An agent opens
`<id>.analysis.json` for music, source provenance, form, harmony, story and
use suggestions; `<id>.annotated.musicxml` carries playable notes and the
same analysis; `<id>.analysis.md` is the human summary. The XML also embeds
the complete compact analysis JSON in the standard identification
`miscellaneous-field` named `analysis-json`, so one XML file gives an
agent both the actual notes and all analysis/use metadata. MIDI is referenced
by `meta.midi_play_url`, never duplicated. No synth audio is stored.

## Coordinates and source fidelity

`meta` contains `id`, `parent_item_id`, composer, title, `source_file`,
`quarter_range: [start, end]` (absolute source quarters, end exclusive), key
(music21 notation: `b` = B minor, `B` = B major), time signature, tempo,
`bar_quarters`, optional `pickup_quarters` and explicit `bar_layout` for
meter changes. `tempo` is the first source quarter-note BPM;
`suggested_arrangement_tempo` is editorial, when supplied. Tempo changes
inside the excerpt are carried by MusicXML, not silently replaced.

`bars[]` is in score order. `bar` is the printed bar number (0 for pickup);
`start_quarter` is relative to the excerpt; `duration_quarters` handles
short pickups and meter changes. `chords[]` contains `{beat, symbol, rn,
function}` and optionally a reason. Beat 1 is the beginning of the bar;
beat increments are **quarters**, including compound meter. A symbol runs
to the next chord or the bar end. Label at each harmonic change; do not
manufacture new chords for melodic passing notes or repeat identical
symbols on every attack. `?` means no complete assertion is warranted.

MIDI pitches are sounding pitches. Piano staves follow the supplied MIDI;
Kalinnikov explicitly uses an oboe melody + harp/string piano reduction.
Quantisation uses straight sixteenths/eighths and triplet eighths/sixteenths;
Schumann uses an explicit straight grid (no triplets in the source movement);
`quantisation_divisors` can constrain the grid per spec. Long gated MIDI notes are extended by at most 0.22 quarter to an integer-duration
notated release. Grace notes below 0.10 quarter are omitted. The JSON
verification checks **original, unquantised, all-track MIDI**, including
ornaments; it does not use the reduction to make a label pass. No repeats
are added to already unfolded performances. These are MIDI-derived
editions, not verified critical editions.

## MusicXML carrier

At every labelled harmonic change, `<harmony>` gives the chord symbol.
Roman numerals appear under the bass staff as `<lyric number="rn"
name="rn">`, or as a below-staff `[rn]` words direction when no bass onset
exists at that position. `<key>` changes follow the reviewed key areas.
A local tonicization does not automatically require a new key signature.
Every event becomes a words direction at `beat` (default 1). Prefixes:

| JSON event type | MusicXML prefix |
|---|---|
| modulation | `[mod]` |
| counterpoint | `[cpt]` |
| voicing_orchestration | `[voi]` |
| tension_release | `[ten]` |
| rhythm_phrase | `[rhy]` |
| motif | `[mot]` |
| texture_dynamics | `[tex]` |
| bass_line | `[bass]` |
| colour_chord | `[col]` |
| cadence | `[cad]` |
| form | `[form]` |
| story | `[story]` |
| hook | `[hook]` |
| mood | `[mood]` |

Pedals use `tension_release:pedal_point_*` or `bass_line:pedal`; texture
uses `texture_dynamics`. This avoids a second set of synonymous event types.

## Analysis JSON

- `schema_version: 1`, `draft`, `reviewed_by`: drafts always have `true` /
  `null`; reviewed bundles have `false` and a named review/date.
- `sections[]`: `{name, start_bar, end_bar, mood[], description}`.
- `bars[]`: coordinates, key, chords and `events[]` of `{type, technique,
  text, beat?}`. Modulation adds `from_key` / `to_key`; a cadence can add
  `arrival_bar`. Events can describe a span in text. Only annotate techniques
  demonstrably present in the notes; do not fill all categories by quota.
- `modulations[]`: derived from modulation events, with bar and technique.
- `mood[]`: `{start_bar, end_bar, labels[]}`; editorial section mood.
- `loop_candidates[]`, `hook_candidates[]`: `{start_bar, end_bar, why,
  quarter_range?, requires_audition?}`. Candidate ranges are inclusive bars;
  exact absolute quarter ranges override a pickup/seam cut. A candidate
  is not a guarantee of an audible seamless loop.
- `kpop_uses[]`: `{where, why}` for verse, pre-chorus, chorus, bridge or
  final-chorus lift when appropriate. Suggestions describe possibilities,
  not verified examples in existing pop songs.
- `tags[]`: sorted, deduplicated `type:technique` strings derived from events.
  Agents can search `analysis_tags` in the agent catalogue, then fetch the
  bundle for exact bars. For example `bass_line:chromatic`.
- `verification`: music21 version, method, matched/labelled/unknown/total
  span counts, `chord_note_match_pct`, `labelled_span_pct`, flagged bars with
  reasons, and per-span sounding pitch-class weights, required/missing PCs
  and coverage. `review_flags` holds interpretive concerns independently of
  mechanical pass/fail.

For each asserted span, root, third, fifth and seventh (if in the chord)
must all occur, and the chord's pitch classes must explain at least 70%
of the sum of note-duration weights. CC64 sustain releases are respected across tracks sharing a MIDI channel.
`meta.sustain_events` preserves relative-quarter controller events in the
self-contained carrier metadata. Doublings count as sounding note mass;
velocity does not. Non-chord tones remain in the denominator.
Extensions enter coverage but the root/third/fifth/seventh check remains
explicit. `?` spans are reported separately, never counted as matches;
100% asserted matches can coexist with substantial unresolved material.
A match says the notes support the chord, not that the Roman numeral,
modulation, cadence or source edition is correct. Review checks those.

## Player and sub-piece route

The sync script discovers complete **reviewed** bundle directories and
sets `analysis_url` and `annotated_score_url`. Drafts are never exposed.
The existing `?watch=<id>` route loads the annotated MusicXML instead of
the parent MIDI. Schumann No. 10 gets a generated item and index row under
`schumann_op15_schumann_kinderszenen_op_15__no10`. Its source MIDI and
score licence/provenance are inherited; parent recording, stream and
preview fields are cleared. Its audio is the excerpt's score notes,
not the complete Kinderszenen MIDI. Ordinary CLI MIDI download still
returns the parent file; use the explicit quarter range for excerpt work.

Analysis defaults on for a reviewed bundle. Button / A toggles it;
`&analysis=0/1` overrides `localStorage.watchAnalysis`. The toggle
re-engraves a filtered in-memory XML without changing the audio or
measure-time map. Harmony and RN disappear when off. Long prefixed event
words are always suppressed in the player engraving and shown in a
reserved header card above the stage; the download retains every word.
This prevents clipped text or annotations covering the current system.

Callouts and the form ribbon use the same unrolled measure/time entries
as cursor/audio; seeking, tempo changes and unfolded repeats share one
clock. A callout expires after its source position plus three measure
entries (up to four displayed bars including its onset); fade is visual.
The ribbon follows tempo-map seconds and its segments seek to sections.
Layout remains a scrolling page, width fit with 16px score padding. The
current watch score-audio engine uses notated key-release durations; it
does not replay CC64 pedal events. Source sustain contributes to chord
verification and is retained in metadata, but the browser rendition is
drier than the original MIDI performance.

## Build and review pipeline

Install optional analysis dependencies with
`pip install -r scripts/analysis/requirements.txt`. The stdlib CLI stays
independent of these dependencies.

```
python3 scripts/analysis/build_annotated.py --spec scripts/analysis/specs/ID.json
python3 scripts/analysis/verify_chords.py files/analysis/ID/ID.analysis.json
python3 scripts/analysis/auto_analyse.py ID --out-root /tmp/analysis-draft --spec-dir /tmp/analysis-draft/specs
```

The auto draft accepts verified clean/attribution piano MIDI with <=64
bars and constant meter, chordifies per half-bar, estimates keys with
8-bar Krumhansl windows and emits conservative cadence/pedal/key-change
candidates. It does not auto-review or auto-publish. MusicXML-only scores
need a playable MIDI from the existing `build_midi_play.py` conversion
first. Changing meter and excerpt work require a hand spec.

`data/analysis_queue.txt` is a candidate queue, not an approval list.
`run_queue.sh N` requires a configured `MUSICLIB_ANALYSIS_REVIEW_CMD`
(see `scripts/analysis/BRIEF_analyse.md`), reviews/builds/verifies each
item, then commits it and fetches/rebases/rebuilds/pushes sequentially,
with up to three push attempts. `--no-push` commits locally;
`--draft-only` processes N items into a temporary directory and never
commits or pushes. The local one-item test uses this last mode.

## Technique vocabulary

`MODULATIONS.md` and `COUNTERPOINT.md` were absent when this format was
written. Existing `ideas/modulations/` candidate/job descriptions were
read; no canonical technique ids were defined there. The fallback below
is authoritative for these bundles; future idea documents should reuse
these ids. `direct/phrase_modulation` is normalised to the JSON-safe
`direct_phrase_modulation`; spacing/register and suspension subtypes have
explicit ids. `scripts/analysis/vocabulary.json` is the machine-readable
copy, validated by the builder.


### modulation

| Technique id | Definition |
|---|---|
| `pivot_chord` | A chord is reinterpreted in the destination key. |
| `common_tone` | A sustained common pitch connects distinct key areas. |
| `chromatic_slide` | Semitone voice-leading connects adjacent harmonic regions. |
| `direct_phrase_modulation` | A new key begins directly at a phrase boundary. |
| `chromatic_mediant` | Key centres a third apart are connected chromatically. |
| `enharmonic_dim7` | A diminished seventh is respelled to target another tonic. |
| `enharmonic_aug6` | An augmented-sixth sonority is enharmonically reinterpreted. |
| `sequence` | A repeated harmonic/melodic model moves the tonal centre. |
| `dominant_pedal_lift` | A dominant pedal prepares arrival in a new key. |
| `truck_driver` | A direct upward step raises a repeated refrain. |

### counterpoint

| Technique id | Definition |
|---|---|
| `imitation` | A voice restates another voice's idea. |
| `canon` | Strict imitation continues at a fixed delay. |
| `contrary_motion` | Two independent voices move in opposite directions. |
| `parallel_3rds_6ths` | Voices move together in thirds or sixths. |
| `oblique_motion` | One voice holds while another moves. |
| `voice_exchange` | Two voices exchange their pitches or roles. |
| `countermelody` | A distinct second melody accompanies the main line. |
| `invertible` | Counterpoint remains valid when the voices exchange registers. |
| `stretto` | Imitative entries overlap before the preceding idea finishes. |
| `suspension_chain` | Successive prepared dissonances resolve in a chain. |

### voicing_orchestration

| Technique id | Definition |
|---|---|
| `open_spacing` | Chord tones are spread across a wide register. |
| `close_spacing` | Chord tones sit close together. |
| `doubling` | A note or line is reinforced in unison or octaves. |
| `parallel_chords` | A chord shape moves in parallel (planing). |
| `register_high_shift` | Material moves into a higher register. |
| `register_low_shift` | Material moves into a lower register. |
| `cross_voicing` | Voice registers cross or interlock. |

### tension_release

| Technique id | Definition |
|---|---|
| `suspension_4_3` | A prepared fourth resolves down to a third. |
| `suspension_9_8` | A prepared ninth resolves down to an octave. |
| `suspension_7_6` | A prepared seventh resolves down to a sixth. |
| `appoggiatura` | An accented dissonance resolves by step. |
| `pedal_point_tonic` | A tonic pitch persists under changing harmony. |
| `pedal_point_dominant` | A dominant pitch persists under changing harmony. |
| `pedal_point_inner` | An inner voice persists under changing harmony. |
| `delayed_resolution` | Expected harmonic release is postponed. |
| `deceptive_resolution` | A dominant resolves to an unexpected substitute. |

### rhythm_phrase

| Technique id | Definition |
|---|---|
| `phrase_length` | A notable phrase length, including asymmetry, shapes the music. |
| `hemiola` | A temporary regrouping swaps two and three accents. |
| `syncopation` | An accent or entrance displaces the expected strong beat. |
| `anticipation` | A voice anticipates the supporting arrival. |
| `elision` | A phrase end doubles as the next phrase's beginning. |
| `extension` | Additional material lengthens an expected phrase. |

### motif

| Technique id | Definition |
|---|---|
| `inversion` | A motif reverses interval directions. |
| `augmentation` | A motif returns with longer durations. |
| `diminution` | A motif returns with shorter durations. |
| `fragmentation` | A small part of a motif is isolated. |
| `sequence` | A motif repeats at another pitch level. |
| `retrograde` | A motif reverses note order. |
| `liquidation` | A motif progressively loses its identifying details. |
| `repetition` | A motif returns without structural transformation. |

### texture_dynamics

| Technique id | Definition |
|---|---|
| `thinning` | The number or activity of voices decreases. |
| `thickening` | The number or activity of voices increases. |
| `build_to_climax` | Register or texture grows toward a peak. |
| `climax` | A local high point of intensity or register. |
| `subito` | A sudden marked contrast changes the texture or dynamics. |
| `fade` | A marked or audible gradual reduction closes the texture. |

### bass_line

| Technique id | Definition |
|---|---|
| `walking` | A regularly moving bass links chord changes. |
| `stepwise_descent` | A bass falls mainly by step (including lament patterns). |
| `pedal` | A repeated or held bass pitch anchors changing harmony. |
| `contrary` | Bass moves opposite another identified voice. |
| `arpeggiated` | Bass figuration outlines chord tones. |
| `chromatic` | Semitone movement is structurally prominent in the bass. |

### colour_chord

| Technique id | Definition |
|---|---|
| `borrowed` | Modal mixture imports a chord from another mode. |
| `neapolitan` | The flattened second-degree major chord colours the approach to a dominant. |
| `aug6_italian` | Italian augmented sixth contains flat 6, tonic and sharp 4. |
| `aug6_french` | French augmented sixth adds scale degree 2. |
| `aug6_german` | German augmented sixth adds flat 3. |
| `added_note` | An added or extended chord tone supplies colour; text names it. |
| `half_dim` | A minor-third/diminished-fifth/minor-seventh sonority supplies colour. |
| `dim7_colour` | A fully diminished seventh supplies colour or ambiguous function. |
| `chromatic_mediant` | Chromatic third-related chords supply colour without established modulation. |

### cadence

| Technique id | Definition |
|---|---|
| `PAC` | Root-position dominant to tonic, melody ending on tonic. |
| `IAC` | Authentic cadence with inversion or non-tonic melodic ending. |
| `HC` | Phrase ends on the dominant. |
| `DC` | Dominant cadence resolves deceptively. |
| `plagal` | Subdominant to tonic phrase close. |
| `tonic_close` | Tonic ending without an immediately asserted authentic cadence. |
| `open_phrase` | Melodic phrase boundary leaves harmony open. |

### form

| Technique id | Definition |
|---|---|
| `intro` | Preparatory opening material. |
| `theme_1` | Main thematic statement or return. |
| `theme_2` | Contrasting or related second thematic region. |
| `bridge` | Connecting or contrasting passage. |
| `theme_tail` | Closing continuation of the theme. |
| `coda` | Closing material after the principal thematic span. |

### story

| Technique id | Definition |
|---|---|
| `start` | Opening situation or emotional premise (起). |
| `continuation` | Development of the opening situation (承). |
| `turn` | A change redirects the emotional or musical journey (转). |
| `arrival` | A resulting state or return completes the local story (合). |

### hook

| Technique id | Definition |
|---|---|
| `melodic_cell` | A compact identifiable melodic figure. |
| `harmonic_cell` | A compact identifiable progression. |
| `rhythmic_cell` | A compact identifiable rhythmic figure. |

### mood

| Technique id | Definition |
|---|---|
| `section_mood` | Editorial mood labels for a named section. |
