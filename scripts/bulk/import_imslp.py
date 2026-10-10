#!/usr/bin/env python3
"""Import licence-checked IMSLP files fetched by hand/browser into ~/Downloads (MusicBot, imslp run 1).

Licences come from docs/catalogues/imslp_candidates.csv (usable=yes: CC0 1.0 / CC BY 3.0|4.0).
.mscz/.mxl are converted to MIDI with MuseScore 4 CLI (~/ms4/squashfs-root/AppRun); the original
engraving file is kept next to the MIDI in files/scores/. Writes parts/BULK_batchP10_rows.csv.
"""
from __future__ import annotations
import csv, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dedup import allocate_id, existing_from_paths  # noqa: E402
from import_depth_us_pd import BATCH_COLUMNS, SCOPE, SCOPE_REASON  # noqa: E402
from schema import CANDIDATE_COLUMNS, composer_record, mood_tags, slugify, tempo_energy  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DL = Path("/home/box/Downloads")
OUT = ROOT / "parts" / "BULK_batchP10_rows.csv"
MS = os.path.expanduser("~/ms4/squashfs-root/AppRun")
US = {"maurice ravel", "edward elgar", "gustav holst", "sergei rachmaninoff", "richard strauss"}
SKIP = {
    "PMLP80636-08_-_Daphnis_et_Chloé_Suite_No_2_-_Percussion.mscz": "percussion part only, not a complete score",
    "PMLP56075-Sonett_from_Capriccio.mid": "Capriccio is 1942: after the US-PD 1931 cutoff",
    "PMLP1312694-Serguéi_Rachmaninoff_-_Romance_in_A_Minor.mid": "published posthumously after 1930; no verified pre-1931 publication",
    "PMLP2397-Clair-de-Lune-in-C.mscz": "transposed to C; the original-key files are imported instead",
}
M = "Morrison"
# file -> (canon, title, catalog, movement, year, arranger, instrumentation)
T = {
 "PMLP7950-maniere_de_Borodine.mid": ("maurice ravel", "À la manière de Borodine", "M. 63/1", "", 1914, "", "piano"),
 "PMLP7506-Gnossienne-1-quintet.mscz": ("erik satie", "Gnossienne No. 1 (arr. for quintet)", "", "", 1893, "IMSLP contributor", "quintet arrangement"),
 "PMLP7506-Gnossienne-1-quartet.mscz": ("erik satie", "Gnossienne No. 1 (arr. for quartet)", "", "", 1893, "IMSLP contributor", "quartet arrangement"),
 "PMLP4215-Gymnopedie-1.mscz": ("erik satie", "Gymnopédie No. 1", "", "", 1888, "", "piano"),
 "PMLP19702-Je-te-veux.mscz": ("erik satie", "Je te veux", "", "", 1902, "", "piano"),
 "PMLP9667-Satie_Prière_pour_le_salut_de_mon_âme.mscz": ("erik satie", "Messe des pauvres: Prière pour le salut de mon âme", "", "No. 7", 1895, "", "organ"),
 "PMLP2383-Arabesque-1-Debussy.mscz": ("claude debussy", "Arabesque No. 1", "L. 66 No. 1", "", 1891, "", "piano"),
 "PMLP2383-arabesque_no2.mscz": ("claude debussy", "Arabesque No. 2", "L. 66 No. 2", "", 1891, "", "piano"),
 "PMLP2383-Arabesque-2-Debussy.mscz": ("claude debussy", "Arabesque No. 2", "L. 66 No. 2", "", 1891, "", "piano"),
 "PMLP9130-cahier_score.mid": ("claude debussy", "D'un cahier d'esquisses", "L. 99", "", 1904, "", "piano"),
 "PMLP2387-Golliwoggs-Cake-Walk.mscz": ("claude debussy", "Children's Corner: Golliwogg's Cakewalk", "L. 113", "No. 6 Golliwogg's Cakewalk", 1908, "", "piano"),
 "PMLP2394-Des_pas_sur_la_neige.mid": ("claude debussy", "Préludes Book 1: Des pas sur la neige", "L. 117 No. 6", "Des pas sur la neige", 1910, "", "piano"),
 "PMLP2394-cathedral.mid": ("claude debussy", "Préludes Book 1: La cathédrale engloutie", "L. 117 No. 10", "La cathédrale engloutie", 1910, "", "piano"),
 "PMLP2397-clair_de_lune.mscz": ("claude debussy", "Suite bergamasque: Clair de lune", "L. 75", "No. 3 Clair de lune", 1905, "", "piano"),
 "PMLP2397-Clair-de-Lune.mscz": ("claude debussy", "Suite bergamasque: Clair de lune", "L. 75", "No. 3 Clair de lune", 1905, "", "piano"),
 "PMLP15427-Symphony-1-2-Mahler.mscz": ("gustav mahler", "Symphony No. 1", "", "", 1899, "", "orchestra"),
 "PMLP58739-Mahler4FirstNormalTuning.mxl": ("gustav mahler", "Symphony No. 4", "", "", 1902, "", "orchestra"),
 "PMLP34545-Death_of_Siegfried.mscz": ("richard wagner", "Götterdämmerung: Siegfried's Death", "WWV 86D", "Siegfried's Death", 1876, "", "orchestra"),
 "PMLP21243-Tannhauser_Overture_Selections.mscz": ("richard wagner", "Tannhäuser: Overture (selections)", "WWV 70", "Overture (selections)", 1845, "", "orchestra"),
 "PMLP25663-Impromptu.mid": ("alexander scriabin", "Impromptu", "Op. 10", "", 1895, "", "piano"),
 "PMLP20227-Prelude.mid": ("alexander scriabin", "Prelude for the Left Hand", "Op. 9 No. 1", "", 1895, "", "piano"),
 "PMLP8451-Vers_la_flamme.mscz": ("alexander scriabin", "Vers la flamme", "Op. 72", "", 1914, "", "piano"),
 "PMLP8451-vers_la_flamme_orchestra.mscz": ("alexander scriabin", "Vers la flamme (arr. for orchestra)", "Op. 72", "", 1914, "IMSLP contributor", "orchestral arrangement"),
 "PMLP14674-Cello-Concerto-Elgar.mscz": ("edward elgar", "Cello Concerto in E minor", "Op. 85", "", 1921, "", "cello and orchestra"),
 "PMLP667730-Elgar_-_Ave_Verum_Corpus.mscz": ("edward elgar", "Ave verum corpus", "Op. 2 No. 1", "", 1902, "", "choir and organ"),
 "PMLP3415-Salut-d-amour.mscz": ("edward elgar", "Salut d'amour", "Op. 12", "", 1889, "", "violin and piano"),
 "PMLP7276-Elgar_Nimrod.mscz": ("edward elgar", "Enigma Variations: Nimrod", "Op. 36", "Var. IX Nimrod", 1899, "", "orchestra"),
 "PMLP913458-Edward_Elgar_-_Presto.mid": ("edward elgar", "Presto", "", "", 1889, "", "piano"),
 "PMLP1155587-Elgar_Offertoire_orch_arr_Morrison_sound.mid": ("edward elgar", "Offertoire (arr. for orchestra)", "", "", 1903, M, "orchestral arrangement"),
 "PMLP35136-Elgar_Music_Makers_Prelude_Band_sound.mid": ("edward elgar", "The Music Makers: Prelude (arr. for band)", "Op. 69", "Prelude", 1912, M, "band arrangement"),
 "PMLP1048949-Elgar_Polonia_pno_Morrison_sound.mid": ("edward elgar", "Polonia (arr. for piano)", "Op. 76", "", 1915, M, "piano arrangement"),
 "PMLP386967-Elgar_Coronation_March_band_arr_Morrison_sound.mid": ("edward elgar", "Coronation March (arr. for band)", "Op. 65", "", 1911, M, "band arrangement"),
 "PMLP900666-Elgar_Queen_Alex_band_arr_Morrison_sound.mid": ("edward elgar", "Queen Alexandra's Memorial Ode (arr. for band)", "", "", 1932, M, "band arrangement"),
 "PMLP900666-Elgar_Queen_Alex_orch.mid": ("edward elgar", "Queen Alexandra's Memorial Ode", "", "", 1932, "", "orchestra"),
 "PMLP367232-Psalm98Sco.mid": ("gustav holst", "I Vow to Thee, My Country", "H. 148", "", 1921, "", "choir/orchestra"),
 "PMLP406958-Holst_ave_maria.mid": ("gustav holst", "Ave Maria", "Op. 9b", "", 1900, "", "choir"),
 "PMLP48902-Saint-Pauls-Suite.mscz": ("gustav holst", "St Paul's Suite", "Op. 29 No. 2", "", 1922, "", "string orchestra"),
 "PMLP48902-Saint-Pauls-Suite-Quintet.mscz": ("gustav holst", "St Paul's Suite (arr. for string quintet)", "Op. 29 No. 2", "", 1922, "IMSLP contributor", "quintet arrangement"),
 "PMLP45655-Die_Toteninsel.mscz": ("sergei rachmaninoff", "Isle of the Dead", "Op. 29", "", 1909, "", "orchestra"),
 "PMLP5664-rachmaninoff_prelude_in_c_sharp_minor.mscz": ("sergei rachmaninoff", "Prelude in C-sharp minor", "Op. 3 No. 2", "", 1893, "", "piano"),
 "PMLP2017-Op._23,_No._10.mid": ("sergei rachmaninoff", "Prelude in G-flat major", "Op. 23 No. 10", "", 1903, "", "piano"),
 "PMLP2018-Op.32,_No.4.mid": ("sergei rachmaninoff", "Prelude in E minor", "Op. 32 No. 4", "", 1911, "", "piano"),
 "PMLP8797-III_Romance.mid": ("sergei rachmaninoff", "Suite No. 2: Romance", "Op. 17", "No. 3 Romance", 1901, "", "two pianos"),
 "PMLP266459-1-andante-op22.mid": ("edward elgar", "Very Easy Melodious Exercises: No. 1 Andante", "Op. 22 No. 1", "", 1892, "", "violin and piano"),
 "PMLP266459-2-allegretto-op22.mid": ("edward elgar", "Very Easy Melodious Exercises: No. 2 Allegretto", "Op. 22 No. 2", "", 1892, "", "violin and piano"),
 "PMLP266459-3-andante-op22.mid": ("edward elgar", "Very Easy Melodious Exercises: No. 3 Andante", "Op. 22 No. 3", "", 1892, "", "violin and piano"),
 "PMLP266459-4-andantino-op22.mid": ("edward elgar", "Very Easy Melodious Exercises: No. 4 Andantino", "Op. 22 No. 4", "", 1892, "", "violin and piano"),
 "PMLP266459-5-allegretto-op22.mid": ("edward elgar", "Very Easy Melodious Exercises: No. 5 Allegretto", "Op. 22 No. 5", "", 1892, "", "violin and piano"),
 "PMLP266459-6-allegro-op22.mid": ("edward elgar", "Very Easy Melodious Exercises: No. 6 Allegro", "Op. 22 No. 6", "", 1892, "", "violin and piano"),
}
# Elgar songs/partsongs on IMSLP (mostly orchestrations by Morrison): title from the CSV work field; year approx publication
ELGAR_YEARS = {"Always and Everywhere": 1901, "Arabian Serenade": 1914, "As I laye a-Thynkynge": 1888, "Big Steamers": 1918,
 "The Brook": 1914, "A Child Asleep": 1910, "A Christmas Greeting": 1907, "Come, Gentle Night!": 1901, "Credo": 1877,
 "Ecce Sacerdos Magnus": 1888, "Fear not, O land": 1914, "Fight for Right": 1916, "Follow the Colours": 1914, "Gloria": 1877,
 "Grete Malverne on a rocke": 1897, "Harmony Music No.6": 1879, "Harmony Music No.7": 1879, "In Moonlight": 1904,
 "Inside the Bar": 1917, "Is She Not Passing Fair?": 1908, "It Isnae Me": 1930, "The King's Way": 1909,
 "The Language of Flowers": 1872, "Like to the Damask Rose": 1893, "Memorial Chimes": 1923, "The Merry-go-round": 1914,
 "Now with the fast-departing light": 1903, "O Salutaris Hostia No.1 in E-flat major": 1880, "Organ Sonata": 1896,
 "Peckham March": 1881, "The Pipes of Pan": 1900, "Pleading": 1908, "Queen Mary's Song": 1889, "The Rapid Stream": 1932,
 "Reminiscences": 1877, "Roundel": 1920, "Salve Regina": 1876, "The Self Banished": 1895, "2 Songs": 1909, "3 Songs": 1913,
 "Speak, my Heart!": 1903, "They are at rest": 1910, "A War Song": 1884, "When Swallows Fly": 1932, "The Wind at Dawn": 1888,
 "The Woodland Stream": 1932}
LIC = {"Creative Commons Zero 1.0": "CC0", "Creative Commons Attribution 4.0": "CC BY 4.0", "Creative Commons Attribution 3.0": "CC BY 3.0"}


def elgar_meta(c):
    work = re.sub(r" \(Elgar, Edward\)$", "", c["work"])
    m = re.match(r"(.*?)(?:, (Op\.\s?\d+))?$", work)
    base, op = m[1], (m[2] or "").replace("Op.", "Op. ")
    year = ELGAR_YEARS.get(base) or ELGAR_YEARS.get(base.split(",")[0])
    f = c["file"]
    title = base
    mv = re.search(r"mvt_(\d)", f)
    if base == "Organ Sonata":
        title = f"Organ Sonata No. 1: movement {mv[1]} (arr. for orchestra)"
    elif base.startswith(("2 Songs", "3 Songs")):
        song = re.sub(r"PMLP\d+-Elgar_|_(orch|orchestra).*$|_music.*$", "", f).replace("_", " ")
        title = song.title().replace("Oh ", "O ").replace("Was It Some Golden Star", "Was It Some Golden Star?").replace("Song D", "Song (in D)").replace("Song E", "Song (in E)").replace("Of ", "of ").replace("The ", "the ").replace("In the", "In the")
    arr = M if ("Morrison" in f or "_orch" in f or "orchestra" in f or "band" in f) and base not in {"Harmony Music No.6", "Harmony Music No.7", "Peckham March", "Reminiscences"} else ""
    if arr and "(arr." not in title:
        title += " (arr. for orchestra)" if "band" not in f else " (arr. for band)"
    if "_A_orch" in f or "_B_orch" in f:
        title += " [version %s]" % ("A" if "_A_orch" in f else "B")
    if "w_harp" in f: title += " [with harp]"
    if "no_harp" in f: title += " [without harp]"
    if "1pt" in f or "2pt" in f: title += " [%s-part]" % f.split("pt_")[0][-1]
    if "SATB_organ" in f: title += " [SATB and organ]"
    elif "SATB" in f: title += " [SATB]"
    if "Flowers.mid" in f and "orch" not in f: title = "The Language of Flowers"
    return ("edward elgar", title, op, "", year, arr, "orchestral arrangement" if arr else "ensemble")


def to_midi(src: Path, dst: Path) -> None:
    for exe in (MS, "musescore3"):
        r = subprocess.run([exe, "-o", str(dst), str(src)], env=dict(os.environ, QT_QPA_PLATFORM="offscreen"),
                           capture_output=True, timeout=300)
        if dst.is_file():
            break
    if not dst.is_file() or dst.read_bytes()[:4] != b"MThd":
        raise RuntimeError("musescore conversion failed: " + r.stderr.decode()[-200:])


def main() -> int:
    dry = "--dry-run" in sys.argv
    cands = [c for c in csv.DictReader((ROOT / "docs/catalogues/imslp_candidates.csv").open(encoding="utf-8")) if c["usable"] == "yes"]
    index = existing_from_paths([ROOT / "library.csv", *sorted((ROOT / "parts").glob("BULK_batch*_rows.csv"))])
    for p in (ROOT / "files" / "scores").iterdir():
        index.add_stem(p.stem)
    used, done, skipped, seen = set(), [], [], set()
    for c in cands:
        f = c["file"]
        if f in seen:
            continue
        seen.add(f)
        if f in SKIP:
            skipped.append((f, SKIP[f])); continue
        meta = T.get(f) or (elgar_meta(c) if c["composer_category"].startswith("Elgar") else None)
        if not meta or not meta[4]:
            skipped.append((f, "no metadata/year")); continue
        canon, title, cat, mvt, year, arr, instr = meta
        if canon in US and year > 1930:
            skipped.append((f, f"published {year}: after the US-PD 1931 cutoff")); continue
        rec = composer_record(canon)
        lic = LIC[c["copyright"]]
        src = DL / f
        if dry:
            print(rec["prefix"], "|", title, "|", lic, "|", arr); done.append(1); continue
        ident = allocate_id(f"{rec['prefix']}_{slugify(('imslp ' + cat + ' ' + title).strip(), 48)}", index, used)
        ext = src.suffix.lower()
        dst = ROOT / "files" / "scores" / f"{ident}.mid"
        if ext == ".mid":
            shutil.copy2(src, dst)
        else:
            shutil.copy2(src, ROOT / "files" / "scores" / f"{ident}{ext}")
            try:
                to_midi(src, dst)
            except Exception as exc:  # noqa: BLE001
                for q in (dst, ROOT / "files" / "scores" / f"{ident}{ext}"):
                    q.unlink(missing_ok=True)
                skipped.append((f, f"conversion failed: {str(exc)[:80]}")); continue
        index.add_stem(ident)
        who = arr if arr and arr != "IMSLP contributor" else ""
        credit = (f"Arrangement by {who} (IMSLP). " if who else ("Arrangement by an IMSLP contributor. " if arr else ""))
        attrib = "" if lic == "CC0" else (f"{lic}: credit \"{f}\" by "
                  + (f"{who}" if who else "its IMSLP uploader") + f", via IMSLP ({c['page_url']}). ")
        notes = (f"Source: IMSLP file {f} ({c['desc'] or 'file'}), licence {lic} per the IMSLP file tag. {credit}{attrib}"
                 + ("Converted .mscz/.mxl to MIDI with MuseScore 4 CLI; original engraving file kept. " if ext != ".mid" else "")
                 + "No third-party recording; the site plays the MIDI in-browser.")
        row = {k: "" for k in CANDIDATE_COLUMNS}
        row.update({
            "id": ident, "composer": rec["name"], "death_year": str(rec["death"]), "title": title, "catalog": cat, "movement": mvt,
            "mood_tags": mood_tags(title, "", "classical"), "tempo_energy": tempo_energy(title, ""),
            "notable_excerpt": "Opening (00:00); play the score MIDI in the browser to audition.",
            "video_use_ideas": "Underscore a short scene with the opening bars.",
            "editable_source_url": c["page_url"], "editable_format": {".mid": "MIDI", ".mscz": "MuseScore + MIDI", ".mxl": "MusicXML + MIDI"}[ext],
            "editable_license": lic, "legal_notes": notes, "local_score_path": f"files/scores/{ident}.mid",
            "verified": "yes", "added_by": "bulk", "source_rank": "9", "source_name": "imslp",
            "licence_class": "clean", "instrumentation": instr, "genre": "classical", "era": "",
        })
        if canon in US:
            reason = SCOPE_REASON.format(death=rec["death"], year=year)
            row.update({"licence_scope": SCOPE, "publication_year": str(year), "licence_scope_reason": reason,
                        "licence_class": "flagged", "legal_notes": reason + " " + notes})
        done.append({k: row.get(k, "") for k in BATCH_COLUMNS})
        print("OK", ident)
    print(f"{len(done)} rows; skipped {len(skipped)}:"); [print("  SKIP", s) for s in skipped]
    if not dry:
        with OUT.open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=BATCH_COLUMNS); w.writeheader(); w.writerows(done)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
