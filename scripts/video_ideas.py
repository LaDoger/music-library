#!/usr/bin/env python3
"""Generic video-edit uses for `video_use_ideas`, merged into library.csv by id.

The library is general-purpose: ideas describe the edit (opener, montage, reveal,
voice-over bed, transition), never a niche, brand or market. `IDEAS` holds the
curated text per id; `BANNED` catches niche/brand wording in any row (including rows
added later) so sync_site_data.py can warn and the site never shows it.

  python3 scripts/video_ideas.py          rewrite video_use_ideas in library.csv (merge by id)
  python3 scripts/video_ideas.py --check  report rows that still need a rewrite

The CSV write is atomic and re-reads the file right before writing, so rows appended by
other agents in the meantime are kept; only the video_use_ideas cell of known ids changes.
"""
import csv
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "library.csv")
NOTES_PATH = os.path.join(ROOT, "scripts", "video_notes.json")

# Niche, brand and market wording that does not belong in a general library. The first
# names are written with a character class so a repo-wide grep for them stays at zero.
BANNED = re.compile(
    r"s[a]ylor|str[a]tegy|\bms[t]r\b|bitc[o]in|cr[y]pto|\bbtc\b|fiat|hard money|number go up|\bATH\b|all-time high|"
    r"bear[- ]market|bull[- ]market|\bFUD\b|liquidation|short squeeze|\bsqueeze\b|trading|treasury|inflation|"
    r"\bmarket\b|market-|adoption|digital capital|\bhodl\b|\bsats\b|halving|price", re.I)

IDEAS = {
    # original 75
    "bach_bwv1007_prelude": "A single-line build under a step-by-step explanation.",
    "bach_bwv1068_air": "Calm, measured bed for a long-form voice-over or a thoughtful close.",
    "bach_bwv565_toccata": "Open a major announcement or a dramatic title card with the iconic organ flourish.",
    "bach_bwv846_prelude": "Underscore a clear explanation, a tutorial or a quiet data sequence.",
    "beethoven_op27_2_moonlight1": "Support a sober, reflective or late-night sequence.",
    "beethoven_op27_2_moonlight3": "Build momentum through a rapid, high-stakes montage.",
    "beethoven_op67_symphony5": "Open a bold statement with the iconic four-note motif.",
    "beethoven_op84_egmont": "Use the victorious coda for a decisive closing sequence.",
    "beethoven_woo59_fur_elise": "Use the recognisable piano opening for a warm, human moment.",
    "berlioz_fantastique_witches_sabbath": "Apocalyptic Dies irae and fugue for a dark, chaotic or Halloween sequence.",
    "bizet_carmen_toreador": "Swagger cue for a bold entrance or a confident walk-on.",
    "borodin_quartet2_nocturne": "A tender two-shot or a quiet founder story.",
    "borodin_steppes": "Open a wide landscape or a long journey.",
    "brahms_hungarian_dance_5": "Playful, fiery cue with tempo swings for comedic edits.",
    "chopin_op10_12_revolutionary": "Score a forceful response or a rapid action montage.",
    "chopin_op28_15_raindrop": "Pair the repeated-note motif with patience, rain or a slow passage of time.",
    "chopin_op9_2_nocturne": "Support a polished calm explanation or a reflective outro.",
    "debussy_arabesque_1": "Use the opening arpeggios under a light product or travel cut.",
    "debussy_clair_de_lune": "Hold under a quiet night shot or a reflective close.",
    "debussy_danse_sacree": "Score a slow ceremonial walk or a museum sequence.",
    "dvorak_new_world_finale": "Brass-led opener for a journey, a launch or a story of progress.",
    "dvorak_new_world_largo": "Reflective 'going home' moment or a long-horizon look back.",
    "elgar_pomp_circumstance_1": "Graduation, a milestone or a speaker walk-on.",
    "faure_apres_un_reve": "Carry a voice-over about a long-held goal or a personal story.",
    "faure_pavane": "Processional underscore for a formal entrance or a closing card.",
    "faure_sicilienne": "Light pastoral B-roll or a soft interlude between harder cuts.",
    "grieg_peer_gynt_morning_mood": "Sunrise or new-beginning opener before a reveal.",
    "grieg_peer_gynt_mountain_king": "Accelerating build-up for a countdown, a chase or a growth montage.",
    "handel_hwv349_hornpipe": "Introduce a confident achievement or a formal celebration.",
    "handel_hwv56_hallelujah": "Celebrate a milestone with the opening Hallelujah motif.",
    "holst_planets_jupiter": "Jubilant uplift; the broad hymn tune for an emotional peak.",
    "holst_planets_mars": "Ominous 5/4 build-up for a conflict, a showdown or a storm.",
    "liszt_hungarian_rhapsody_2": "The fast friska section for a high-energy montage or a comic chase.",
    "liszt_la_campanella": "Precision and virtuosity cue for craftsmanship, engineering or sport.",
    "liszt_liebestraum_3": "Nostalgic, tender interlude.",
    "mahler_adagietto": "A still memorial frame or a slow emotional peak.",
    "mendelssohn_op26_hebrides": "Open a seascape, a voyage or an expansive long-range story.",
    "mozart_k331_rondo_turca": "Add a nimble rhythm to quick explanatory cuts.",
    "mozart_k525_nachtmusik": "Introduce a crisp recurring chapter motif or an elegant opener.",
    "mozart_k550_symphony40": "Restless urgency under an analytical voice-over or a fast sequence of decisions.",
    "mussorgsky_night_on_bald_mountain": "Menacing storm, nightmare or villain sequence.",
    "mussorgsky_pictures_baba_yaga": "Hard-hitting chaos cut for a turbulent montage.",
    "mussorgsky_pictures_great_gate_kiev": "Monumental finale for a milestone, an unveiling or a grand reveal.",
    "mussorgsky_pictures_promenade": "Calm, confident walk-on for a keynote intro or a gallery tour.",
    "offenbach_orpheus_cancan": "Slapstick speed-up, a blooper reel or a comic smash cut.",
    "pachelbel_canon_d": "Accompany a wedding, a family montage or a steady story of growth.",
    "rachmaninoff_piano_concerto_2": "Sweeping romantic climax for a hero narrative.",
    "rachmaninoff_prelude_op3_no2": "Fateful bell-chord cue for a reckoning or a turning point.",
    "ravel_pavane": "A formal farewell or a black-tie still.",
    "rimskykorsakov_flight_of_the_bumblebee": "Frantic speed cue for a time-lapse, a rush or a chase.",
    "rimskykorsakov_scheherazade_sea": "Majestic, mysterious opener for a voyage or an odyssey.",
    "rstrauss_zarathustra_sunrise": "Open a launch, a reveal or a sense of scale.",
    "saintsaens_carnival_aquarium": "Mysterious underwater, night-sky or discovery mood bed.",
    "saintsaens_danse_macabre": "Spooky-playful skeleton dance for Halloween or a mischievous montage.",
    "saintsaens_samson_bacchanale": "Frenzied climax for a wild party or a chaotic finale.",
    "satie_gnossienne_1": "Underscore a puzzle, a night walk or an uneasy pause.",
    "satie_gymnopedie_1": "Bed a still portrait or a slow text card.",
    "schubert_d328_erlkonig": "Create tension with the galloping piano introduction.",
    "schumann_op15_7_traumerei": "Close a thoughtful message with a gentle, reflective piano phrase.",
    "smetana_vltava": "A widening landscape, a river journey or a story that gathers speed.",
    "strauss1_radetzky": "Punch in a crowd, a countdown or a victory beat.",
    "strauss2_blue_danube": "Glide through a city night montage, a dance or a celebration cut.",
    "suppe_light_cavalry": "Drive a fast montage, a race or a charge.",
    "tchaikovsky_1812_overture": "Victory finale with cannons and bells: the ultimate 'we did it' cue.",
    "tchaikovsky_nutcracker_waltz_of_flowers": "Elegant celebratory sweep for a gala or an award moment.",
    "tchaikovsky_piano_concerto_1": "Massive opening chords for a big announcement.",
    "tchaikovsky_romeo_and_juliet": "Sweeping love-theme climax for a romance or a reunion.",
    "tchaikovsky_swan_lake_act2_scene": "Haunting oboe theme for a downfall, a farewell or an elegy.",
    "verdi_aida_triumphal_march": "Fanfare for a triumphant reveal, an opening ceremony or a victory lap.",
    "verdi_requiem_dies_irae": "Doom cue for a disaster, a collapse or a dramatic reckoning.",
    "vivaldi_rv269_spring": "Reveal upbeat progress with the famous opening ritornello.",
    "vivaldi_rv315_summer_storm": "Drive a fast montage of turbulence, weather or decisive action.",
    "wagner_lohengrin_bridal_chorus": "Wedding cue, sincere or tongue-in-cheek for an unlikely pairing.",
    "wagner_tristan_prelude": "Slow-burn tension under a long-form narrative.",
    "wagner_walkure_ride_of_the_valkyries": "Charge or attack montage: the classic air-cavalry cue.",
    # batch 1 touch-ups (niche wording only; other batch rows are already generic)
    "bach_bwv230_lobet_den_herrn": "Bright, busy energy for a milestone or a growth montage.",
    "bach_bwv533_prelude_e_minor": "Brooding organ opener for a serious history segment.",
    "bach_bwv773_invention2": "Two voices chasing each other for a cat-and-mouse story.",
    "bach_bwv776_invention5": "Poised, orderly backdrop for a data or diagram walkthrough.",
    "bach_bwv851_prelude": "Driving triplets for a turbulent or fast-moving segment.",
    "bach_bwv542_fantasia_fugue": "Relentless fugue drive behind a big-argument montage.",
}


def needs_rewrite(text):
    return bool(BANNED.search(text or ""))


def load_notes(path=NOTES_PATH):
    """Generated per-row notes from scripts/bulk/video_notes.py; niche wording is dropped."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {k: v for k, v in json.load(f).items() if isinstance(v, str) and not needs_rewrite(v)}


NOTES = load_notes()


def clean_idea(rid, text):
    """Text the site should show: curated override, else generated note, else the CSV text."""
    return IDEAS.get(rid) or NOTES.get(rid) or text or ""


def main():
    check = "--check" in sys.argv
    raw = open(CSV_PATH, encoding="utf-8", newline="").read()
    reader = csv.DictReader(io.StringIO(raw))
    fields = reader.fieldnames
    rows = list(reader)
    changed = 0
    for r in rows:
        new = clean_idea(r["id"].strip(), r.get("video_use_ideas", ""))
        if new != r.get("video_use_ideas", ""):
            changed += 1
            r["video_use_ideas"] = new
    left = [r["id"] for r in rows if needs_rewrite(r.get("video_use_ideas"))]
    print(f"{'would change' if check else 'changed'} {changed} of {len(rows)} rows")
    for rid in left:
        print("NEEDS REWRITE", rid)
    if check or not changed:
        return 1 if left else 0
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=fields, lineterminator="\r\n" if "\r\n" in raw else "\n")
    w.writeheader()
    w.writerows(rows)
    # Another agent may have appended rows while we worked: only write if unchanged.
    if open(CSV_PATH, encoding="utf-8", newline="").read() != raw:
        print("library.csv changed during rewrite; re-run")
        return 2
    tmp = CSV_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(out.getvalue())
    os.replace(tmp, CSV_PATH)
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
