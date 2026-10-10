#!/usr/bin/env python3
"""Tier list + catalogue coverage for the major composers (depth run 1).

Source of truth for scripts/featured_composers.json (featured rank used by the site)
and docs/catalogues/TIER_LIST.md.

  python3 scripts/bulk/tier_list.py

Coverage = distinct catalogue numbers found in live items (library.csv + library_bulk.csv)
divided by the size of the standard catalogue. Catalogue sizes are rounded published
figures; opus-number catalogues collapse "Op. 28 No. 7" to Op. 28, so those percentages
undercount sub-works and overcount sets. The figure is a rough guide, not an audit.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dedup import canon_name  # noqa: E402
from import_depth_us_pd import norm  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# rank 1 = top cinematic group (LaDoger 2026-10-10 09:21/09:22), 2 = next cinematic tier, 3 = tier A/B rest, 4 = other majors
# (name, rank, tier, catalogue label, catalogue size, [(prefix, regex with number group)], note)
OP = r"\bop(?:us)?\.? ?(\d+)"
T = [
    # --- rank 1: cinematic top group
    ("Maurice Ravel", 1, "A", "Marnat M.", 86, [("M", r"\bM\.? ?(\d+)")], "d.1937 US-PD-only (pub ≤1930). Boléro, Left Hand, G concerto, Don Quichotte excluded. Checklist: ravel.csv"),
    ("Claude Debussy", 1, "A", "Lesure L.", 145, [("L", r"\bL\.? ?(\d+)")], "d.1918, fully PD."),
    ("Erik Satie", 1, "A", "no standard catalogue", None, [], "d.1925, fully PD. ~160 works; Gymnopédies/Gnossiennes/Sarabandes core."),
    ("Gustav Mahler", 1, "A", "no standard (GMW ~ 60 works)", 60, [], "d.1911, fully PD. Few clean encodings; IMSLP Mahler 4 CC0 (manual download)."),
    ("Anton Bruckner", 1, "A", "WAB", 149, [("WAB", r"\bWAB ?(\d+)")], "d.1896, fully PD. Most IMSLP files NC/SA."),
    ("Richard Wagner", 1, "A", "WWV", 113, [("WWV", r"\bWWV ?(\d+)")], "d.1883, fully PD."),
    ("Richard Strauss", 1, "A", "Op. / TrV", 90, [("Op", OP)], "d.1949 US-PD-only (pub ≤1930). Checklist: strauss_r.csv"),
    ("Edward Elgar", 1, "A", "Op.", 91, [("Op", OP)], "d.1934 US-PD-only (pub ≤1930). Checklist: elgar.csv"),
    ("Gustav Holst", 1, "B", "Op. / H.", 60, [("Op", OP)], "d.1934 US-PD-only (pub ≤1930). Checklist: holst.csv"),
    ("Sergei Rachmaninoff", 1, "A", "Op.", 45, [("Op", OP)], "d.1943 US-PD-only (pub ≤1930). Op.42-45 etc. published later: excluded. Checklist: rachmaninoff.csv"),
    ("Alexander Scriabin", 1, "A", "Op.", 74, [("Op", OP)], "d.1915, fully PD."),
    # --- rank 2: next cinematic tier, fully PD
    ("Pyotr Ilyich Tchaikovsky", 2, "A", "Op. (TH Poznansky ~ 300)", 125, [("Op", OP)], ""),
    ("Antonín Dvořák", 2, "A", "B. Burghauser / Op.", 200, [("B", r"\bB\.? ?(\d+)"), ("Op", OP)], ""),
    ("Modest Mussorgsky", 2, "A", "no standard (~ 70 works)", 70, [], ""),
    ("Nikolai Rimsky-Korsakov", 2, "A", "Op.", 70, [("Op", OP)], ""),
    ("Hector Berlioz", 2, "A", "H. Holoman / Op.", 150, [("H", r"\bH\.? ?(\d+)"), ("Op", OP)], ""),
    ("Edvard Grieg", 2, "A", "Op. (EG)", 74, [("Op", OP)], ""),
    ("Camille Saint-Saëns", 2, "A", "Op.", 169, [("Op", OP)], ""),
    ("Giuseppe Verdi", 2, "A", "no standard (28 operas + ~ 80 other)", 110, [], ""),
    ("Gabriel Fauré", 2, "A", "Op.", 121, [("Op", OP)], ""),
    ("Franz Liszt", 2, "A", "S. Searle / Raabe", 800, [("S", r"\bS\.? ?(\d+)")], "Searle numbers run to ~ 800+; catalog-less items not counted."),
    # --- rank 3: tier A/B rest
    ("Johann Sebastian Bach", 3, "A", "BWV", 1128, [("BWV", r"\bBWV ?(\d+)")], ""),
    ("George Frideric Handel", 3, "A", "HWV", 610, [("HWV", r"\bHWV ?(\d+)")], ""),
    ("Antonio Vivaldi", 3, "A", "RV", 800, [("RV", r"\bRV ?(\d+)")], ""),
    ("Georg Philipp Telemann", 3, "B", "TWV", 3000, [("TWV", r"\bTWV ?[\d:]*?(\d+)")], "TWV runs to ~ 3,000+; coverage figure is a floor."),
    ("Domenico Scarlatti", 3, "A", "K. Kirkpatrick", 555, [("K", r"\bK\.? ?(\d+)"), ("L", r"\bL\.? ?(\d+)")], ""),
    ("Joseph Haydn", 3, "A", "Hob.", 750, [("Hob", r"\bHob\.? ?[IVXL]+[:\s]*(\d+)")], ""),
    ("Wolfgang Amadeus Mozart", 3, "A", "K. Köchel", 626, [("K", r"\bK\.? ?(\d+)")], ""),
    ("Ludwig van Beethoven", 3, "A", "Op. 1-138 + WoO 1-205", 343, [("Op", OP), ("WoO", r"\bWoO ?(\d+)")], ""),
    ("Franz Schubert", 3, "A", "D. Deutsch", 998, [("D", r"\bD\.? ?(\d+)")], ""),
    ("Robert Schumann", 3, "A", "Op.", 148, [("Op", OP)], ""),
    ("Felix Mendelssohn", 3, "A", "Op. (MWV)", 121, [("Op", OP)], ""),
    ("Frédéric Chopin", 3, "A", "Op. 1-74 + posth.", 112, [("Op", OP)], ""),
    ("Johannes Brahms", 3, "A", "Op. 1-122 + WoO", 160, [("Op", OP), ("WoO", r"\bWoO ?(\d+)")], ""),
    ("César Franck", 3, "B", "FWV", 100, [("FWV", r"\bFWV ?(\d+)")], ""),
    ("Charles-Valentin Alkan", 3, "B", "Op.", 76, [("Op", OP)], ""),
    ("Scott Joplin", 3, "A", "no catalogue (~ 53 works)", 53, [], "d.1917, fully PD."),
    ("Leopold Godowsky", 3, "B", "no catalogue (~ 400 works)", 400, [], "d.1938: needs LaDoger approval (1930–55 rule); nothing imported."),
    # --- rank 4: other majors
    ("Henry Purcell", 4, "B", "Z. Zimmerman", 900, [("Z", r"\bZ\.? ?(\d+)")], ""),
    ("Claudio Monteverdi", 4, "B", "SV", 337, [("SV", r"\bSV ?(\d+)")], ""),
    ("Giovanni Pierluigi da Palestrina", 4, "B", "no catalogue (~ 105 masses + motets)", None, [], ""),
    ("Arcangelo Corelli", 4, "B", "Op. 1-6 (72 works)", 72, [("Op", OP)], ""),
    ("Johann Pachelbel", 4, "B", "P. / PWV", 500, [("P", r"\bP\.? ?(\d+)")], ""),
    ("Jean-Philippe Rameau", 4, "B", "RCT", 300, [("RCT", r"\bRCT ?(\d+)")], ""),
    ("François Couperin", 4, "B", "no standard (~ 27 ordres, 220 pieces)", 220, [], ""),
    ("Christoph Willibald Gluck", 4, "B", "Wq.", 120, [("Wq", r"\bWq\.? ?(\d+)")], ""),
    ("Niccolò Paganini", 4, "B", "MS / Op.", 100, [("Op", OP), ("MS", r"\bMS ?(\d+)")], ""),
    ("Gioachino Rossini", 4, "B", "no standard (39 operas + ~ 200)", None, [], ""),
    ("Georges Bizet", 4, "B", "WD / Op.", 100, [("Op", OP)], ""),
    ("Giacomo Puccini", 4, "B", "SC (operas)", 12, [], "d.1924, fully PD; 12 operas + ~ 60 small works."),
    ("Jean Sibelius", 4, "X", "Op.", 116, [("Op", OP)], "d.1957: EXCLUDED (life+70 not yet; outside the 1930–55 window). Do not import."),
    ("Leoš Janáček", 4, "B", "JW", 100, [], "d.1928, fully PD."),
    ("Bedřich Smetana", 4, "B", "JB", 80, [], "d.1884."),
    ("Alexander Borodin", 4, "B", "no catalogue (~ 40 works)", 40, [], ""),
    ("Isaac Albéniz", 4, "B", "Op. / K.", 100, [("Op", OP)], "d.1909."),
    ("Enrique Granados", 4, "B", "Op.", 60, [("Op", OP)], "d.1916."),
    ("Carl Maria von Weber", 4, "B", "J. Jähns", 300, [("J", r"\bJ\.? ?(\d+)")], ""),
    ("Jacques Offenbach", 4, "B", "no standard (~ 100 stage works)", 100, [], ""),
    ("Johann Strauss II", 4, "B", "Op. 1-479", 479, [("Op", OP)], ""),
    ("John Field", 4, "B", "H. Hopkinson", 80, [("H", r"\bH\.? ?(\d+)")], ""),
    ("Muzio Clementi", 4, "B", "Op. / WO", 100, [("Op", OP)], ""),
    ("Carl Czerny", 4, "C", "Op. 1-861", 861, [("Op", OP)], "Mostly études; keep to signature sets."),
    ("Ferruccio Busoni", 4, "B", "BV", 300, [("BV", r"\bBV ?(\d+)")], "d.1924."),
    ("Max Reger", 4, "B", "Op. 1-147", 147, [("Op", OP)], "d.1916."),
]

# signature works for the rank 1-2 composers: (label, regex over normalised title+movement+catalog)
SIG = {
    "Maurice Ravel": [],
    "Claude Debussy": [("Clair de lune", r"clair de lune"), ("Arabesque", r"arabesque"), ("La mer", r"\bla mer\b"), ("Prélude à l'après-midi d'un faune", r"faune?\b|afternoon of a faun"),
        ("Nocturnes", r"nocturnes"), ("Rêverie", r"reverie"), ("Golliwogg's Cakewalk", r"golliwogg"), ("Suite bergamasque", r"bergamasque|passepied|menuet"),
        ("Estampes (Pagodes, Jardins sous la pluie)", r"pagodes|jardins sous la pluie|soiree dans grenade"), ("La cathédrale engloutie", r"cathedrale engloutie"),
        ("La fille aux cheveux de lin", r"cheveux de lin"), ("Des pas sur la neige", r"pas sur la neige"), ("String Quartet", r"string quartet"),
        ("Syrinx", r"syrinx"), ("Images (Reflets dans l'eau)", r"reflets dans l eau"), ("Pelléas et Mélisande", r"pelleas"), ("Danse sacrée et danse profane", r"danse sacree|danses sacree"),
        ("Children's Corner", r"children s corner|doctor gradus|jimbo")],
    "Erik Satie": [("Gymnopédie 1", r"gymnopedie.*(1|i\b)|gymnopedie no 1"), ("Gymnopédie 2", r"gymnopedie.*(2|ii\b)"), ("Gymnopédie 3", r"gymnopedie.*(3|iii)"),
        ("Gnossiennes", r"gnossienne"), ("Je te veux", r"je te veux"), ("Sarabandes", r"sarabande"), ("Parade", r"\bparade\b"), ("Vexations", r"vexations"),
        ("Embryons desséchés", r"embryons"), ("Trois morceaux en forme de poire", r"forme de poire"), ("Le Piccadilly", r"piccadilly"), ("Socrate", r"socrate"),
        ("Sports et divertissements", r"sports et divertissements"), ("Véritables préludes flasques", r"preludes flasques"), ("Messe des pauvres", r"messe des pauvres"),
        ("Avant-dernières pensées", r"avant dernieres pensees"), ("Danses gothiques", r"danses gothiques"), ("Ogives", r"ogives"), ("Descriptions automatiques", r"descriptions automatiques")],
    "Gustav Mahler": [("Symphony 1", r"symphony (no )?1\b|titan"), ("Symphony 2 Resurrection", r"symphony (no )?2\b|resurrection"), ("Symphony 3", r"symphony (no )?3\b"),
        ("Symphony 4", r"symphony (no )?4\b"), ("Symphony 5 / Adagietto", r"symphony (no )?5\b|adagietto"), ("Symphony 6", r"symphony (no )?6\b"), ("Symphony 7", r"symphony (no )?7\b"),
        ("Symphony 8", r"symphony (no )?8\b"), ("Symphony 9", r"symphony (no )?9\b"), ("Symphony 10 Adagio", r"symphony (no )?10\b"), ("Das Lied von der Erde", r"lied von der erde"),
        ("Kindertotenlieder", r"kindertotenlieder"), ("Rückert-Lieder", r"ruckert|ich bin der welt|um mitternacht"), ("Lieder eines fahrenden Gesellen", r"fahrenden gesellen"),
        ("Des Knaben Wunderhorn", r"wunderhorn|rheinlegendchen|urlicht"), ("Piano Quartet", r"piano quartet")],
    "Anton Bruckner": [("Symphony 4 Romantic", r"symphony (no )?4\b|romantic"), ("Symphony 7", r"symphony (no )?7\b"), ("Symphony 8", r"symphony (no )?8\b"), ("Symphony 9", r"symphony (no )?9\b"),
        ("Symphony 3", r"symphony (no )?3\b"), ("Symphony 5", r"symphony (no )?5\b"), ("Te Deum", r"te deum"), ("Ave Maria", r"ave maria"), ("Locus iste", r"locus iste"),
        ("Os justi", r"os justi"), ("Christus factus est", r"christus factus"), ("Mass in E minor", r"mass.*e minor|messe.*e moll"), ("Mass No. 3 in F minor", r"mass.*f minor"), ("Requiem", r"requiem"),
        ("String Quintet", r"string quintet"), ("Virga Jesse", r"virga jesse")],
    "Richard Wagner": [("Ride of the Valkyries", r"valkyrie|walkure"), ("Bridal Chorus (Lohengrin)", r"bridal chorus|treulich gefuhrt|lohengrin"), ("Tristan Prelude / Liebestod", r"tristan|liebestod"),
        ("Tannhäuser Overture / Pilgrims' Chorus", r"tannhauser|pilgrim"), ("Flying Dutchman", r"flying dutchman|fliegende hollander"), ("Parsifal", r"parsifal"),
        ("Meistersinger Prelude", r"meistersinger"), ("Das Rheingold", r"rheingold"), ("Siegfried's Funeral March / Götterdämmerung", r"gotterdammerung|funeral march|siegfried"),
        ("Siegfried Idyll", r"siegfried idyll"), ("Wesendonck Lieder", r"wesendonck"), ("Rienzi Overture", r"rienzi")],
    "Richard Strauss": [], "Edward Elgar": [], "Gustav Holst": [], "Sergei Rachmaninoff": [],
    "Alexander Scriabin": [("Etude Op. 2 No. 1", r"etude.*op 2\b|op 2 no 1"), ("Etudes Op. 8", r"etude.*op 8\b|op 8 no"), ("Etude Op. 42", r"op 42"), ("Poème de l'extase", r"extase|poeme of ecstasy"),
        ("Prometheus", r"prometheus|promethee"), ("Piano Sonata 4", r"sonata (no )?4"), ("Sonata 5", r"sonata (no )?5"), ("Sonata 9 Black Mass", r"black mass|sonata (no )?9"),
        ("Vers la flamme", r"vers la flamme"), ("Poème satanique", r"satanique"), ("Preludes Op. 11", r"op 11"), ("Piano Concerto", r"piano concerto"), ("Symphony 3 Divine Poem", r"divine poem|symphony (no )?3"),
        ("Poème-Nocturne / Poèmes Op. 32", r"op 32"), ("Fantasy Op. 28", r"op 28")],
    "Pyotr Ilyich Tchaikovsky": [("Swan Lake", r"swan lake|lac des cygnes"), ("Nutcracker", r"nutcracker|dance of the sugar|waltz of the flowers|casse noisette"), ("Sleeping Beauty", r"sleeping beauty"),
        ("1812 Overture", r"1812"), ("Romeo and Juliet", r"romeo"), ("Symphony 4", r"symphony (no )?4\b"), ("Symphony 5", r"symphony (no )?5\b"), ("Symphony 6 Pathétique", r"symphony (no )?6\b|pathetique"),
        ("Piano Concerto 1", r"piano concerto (no )?1\b"), ("Violin Concerto", r"violin concerto"), ("Marche slave", r"marche slave"), ("Capriccio italien", r"capriccio italien"),
        ("Eugene Onegin", r"onegin|eugene"), ("The Seasons", r"the seasons|barcarolle|troika"), ("Souvenir de Florence", r"souvenir de florence"), ("Serenade for Strings", r"serenade for strings"),
        ("Variations on a Rococo Theme", r"rococo")],
    "Antonín Dvořák": [("Symphony 9 From the New World", r"new world|symphony (no )?9\b"), ("Slavonic Dances", r"slavonic dance"), ("Song to the Moon (Rusalka)", r"rusalka|song to the moon"),
        ("String Quartet 12 American", r"american|quartet (no )?12"), ("Humoresque", r"humoresque|humoreske"), ("Cello Concerto", r"cello concerto"), ("Carnival Overture", r"carnival"),
        ("Symphony 8", r"symphony (no )?8\b"), ("Symphony 7", r"symphony (no )?7\b"), ("Serenade for Strings", r"serenade.*strings"), ("Dumky Trio", r"dumky"), ("Stabat Mater / Requiem", r"stabat mater|requiem"),
        ("Legends", r"legends"), ("Piano Quintet in A", r"piano quintet")],
    "Modest Mussorgsky": [("Pictures at an Exhibition", r"pictures at an exhibition|tableaux d une exposition|bydlo|great gate"), ("Night on Bald Mountain", r"bald mountain|night on"),
        ("Boris Godunov", r"boris"), ("Songs and Dances of Death", r"songs and dances of death|death"), ("Khovanshchina Dawn", r"khovansh|dawn"), ("Sunless", r"sunless"),
        ("The Nursery", r"nursery"), ("Sorochintsy Fair", r"sorochin")],
    "Nikolai Rimsky-Korsakov": [("Scheherazade", r"scheherazade|sheherazade"), ("Flight of the Bumblebee", r"bumble"), ("Capriccio espagnol", r"capriccio espagnol"), ("Russian Easter Festival Overture", r"russian easter|easter"),
        ("Sadko", r"sadko"), ("The Golden Cockerel (Hymn to the Sun)", r"golden cockerel|hymn to the sun|coq d or"), ("Snow Maiden", r"snow maiden|snegurochka"), ("Tsar Saltan", r"saltan"),
        ("Antar", r"antar"), ("Dance of the Tumblers", r"tumblers"), ("Spanish Capriccio", r"spanish")],
    "Hector Berlioz": [("Symphonie fantastique", r"fantastique|march to the scaffold"), ("Roman Carnival", r"roman carnival|carnaval romain"), ("Harold in Italy", r"harold"), ("Rákóczy March / Damnation of Faust", r"damnation|rakoczy|minuet of the will"),
        ("Requiem (Grande Messe)", r"requiem|messe des morts"), ("Les Troyens", r"troyens|royal hunt"), ("Le Corsaire", r"corsaire"), ("Béatrice et Bénédict", r"benedict"), ("Les nuits d'été", r"nuits d ete"), ("Benvenuto Cellini", r"cellini")],
    "Edvard Grieg": [("Peer Gynt: Morning Mood", r"morning mood|morgenstimmung|peer gynt"), ("Hall of the Mountain King", r"mountain king"), ("Piano Concerto", r"piano concerto"), ("Holberg Suite", r"holberg"),
        ("Lyric Pieces", r"lyric piece|wedding day at troldhaugen|to the spring|butterfly|notturno"), ("Sigurd Jorsalfar", r"sigurd"), ("Norwegian Dances", r"norwegian dance"), ("Solveig's Song", r"solveig"),
        ("Ase's Death", r"ase s death|aases tod"), ("Anitra's Dance", r"anitra"), ("Violin Sonatas", r"violin sonata"), ("String Quartet", r"string quartet")],
    "Camille Saint-Saëns": [("Danse macabre", r"danse macabre"), ("Carnival of the Animals (The Swan)", r"carnival of the animals|carnaval des animaux|the swan|le cygne"), ("Organ Symphony", r"organ symphony|symphony (no )?3"),
        ("Samson et Dalila (Mon coeur)", r"samson|dalila|dalilah"), ("Havanaise", r"havanaise"), ("Introduction and Rondo capriccioso", r"rondo capriccioso"), ("Piano Concerto 2", r"piano concerto (no )?2"),
        ("Piano Concerto 5 Egyptian", r"piano concerto (no )?5"), ("Cello Concerto 1", r"cello concerto"), ("Violin Concerto 3", r"violin concerto"), ("Africa", r"\bafrica\b"), ("Bacchanale", r"bacchanale"),
        ("Le Rouet d'Omphale", r"omphale")],
    "Giuseppe Verdi": [("Requiem (Dies irae)", r"requiem|dies irae"), ("La traviata (Brindisi)", r"traviata|brindisi"), ("Aida (Triumphal March)", r"\baida\b|triumphal"), ("Rigoletto (La donna è mobile)", r"rigoletto|donna e mobile"),
        ("Nabucco (Va pensiero)", r"nabucco|va pensiero"), ("Il trovatore (Anvil Chorus)", r"trovatore|anvil"), ("Otello", r"otello"), ("Falstaff", r"falstaff"), ("Macbeth", r"macbeth"),
        ("La forza del destino overture", r"forza del destino"), ("Don Carlos", r"don carlo"), ("Un ballo in maschera", r"ballo in maschera"), ("String Quartet", r"string quartet"), ("Ave Maria / Four Sacred Pieces", r"ave maria|pezzi sacri|te deum")],
    "Gabriel Fauré": [("Requiem (Pie Jesu, In paradisum)", r"requiem|pie jesu|in paradisum|libera me|sanctus|agnus dei|offertoire"), ("Pavane", r"pavane"), ("Sicilienne", r"sicilienne"), ("Après un rêve", r"apres un reve"),
        ("Élégie", r"elegie"), ("Cantique de Jean Racine", r"cantique de jean racine"), ("Clair de lune (op. 46)", r"clair de lune"), ("Dolly Suite (Berceuse)", r"dolly|berceuse"), ("Nocturnes", r"nocturne"),
        ("Barcarolles", r"barcarolle"), ("Pelléas et Mélisande suite", r"pelleas"), ("Piano Quartet 1", r"piano quartet"), ("Romances sans paroles", r"romances sans paroles"), ("Masques et bergamasques", r"masques"),
        ("Violin Sonata 1", r"violin sonata"), ("Les berceaux / Lydia / Notre amour (songs)", r"berceaux|lydia|notre amour|mandoline")],
    "Franz Liszt": [("Liebestraum 3", r"liebestraum"), ("La campanella", r"campanella"), ("Hungarian Rhapsody 2", r"hungarian rhapsody"), ("Les préludes", r"les preludes"), ("Mephisto Waltz", r"mephisto"),
        ("Totentanz", r"totentanz"), ("Consolation 3", r"consolation"), ("Piano Sonata in B minor", r"sonata in b minor|piano sonata"), ("Années de pèlerinage", r"annees de pelerinage|vallee d obermann|au bord d une source|les jeux d eaux"),
        ("Transcendental Etudes", r"transcendental|feux follets|mazeppa|paysage|wilde jagd"), ("Faust Symphony", r"faust symphony"), ("Piano Concerto 1", r"piano concerto (no )?1"), ("Un sospiro / Gnomenreigen", r"sospiro|gnomenreigen|waldesrauschen"),
        ("Orpheus / Tasso / Prometheus (tone poems)", r"orpheus|tasso|prometheus|hamlet"), ("Rhapsodie espagnole", r"rhapsodie espagnole"), ("Isolde's Liebestod (transcription)", r"liebestod")],
}


def load_items():
    out = []
    for name in ("library.csv", "library_bulk.csv"):
        for r in csv.DictReader((ROOT / name).open(newline="", encoding="utf-8")):
            out.append(r)
    return out


def main() -> int:
    items = load_items()
    by = {}
    for r in items:
        by.setdefault(canon_name(r["composer"]), []).append(r)
    rows, feat, report = [], {}, {}
    for name, rank, tier, cat_label, size, pats, note in T:
        canon = canon_name(name)
        its = by.get(canon, [])
        keys = set()
        no_cat = 0
        for r in its:
            hay = f"{r.get('catalog') or ''} {r.get('title') or ''}"
            hit = False
            for pref, rx in pats:
                m = re.search(rx, hay, re.I)
                if m:
                    keys.add(f"{pref}{int(m.group(1))}")
                    hit = True
                    break
            if not hit:
                no_cat += 1
        sig_missing = []
        sig_have = 0
        for label, rx in SIG.get(name, []):
            if any(re.search(rx, norm(f"{r['title']} {r.get('movement','')} {r.get('catalog','')}")) for r in its):
                sig_have += 1
            else:
                sig_missing.append(label)
        pct = None
        if size and pats:
            pct = round(100 * len(keys) / size, 1)
        rows.append((name, rank, tier, cat_label, size, len(its), len(keys), no_cat, pct, sig_have, sig_missing, note))
        feat[canon] = {"name": name, "featured_rank": rank, "tier": tier}
        report[name] = {"items": len(its), "catalogued_works": len(keys), "no_catalogue_items": no_cat, "coverage_pct": pct,
                        "signature_have": sig_have, "signature_total": len(SIG.get(name, [])), "signature_missing": sig_missing}
    (ROOT / "scripts" / "featured_composers.json").write_text(
        json.dumps({"_doc": "Featured composers for the site (depth run 1, LaDoger 2026-10-10). featured_rank 1 = top cinematic group, 2 = next cinematic tier, "
                            "3 = tier A/B, 4 = other major composers. Generated by scripts/bulk/tier_list.py; sibelius (d.1957) is excluded and carries rank 4 with no items.",
                    "composers": feat}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (ROOT / ".tmp" / "depth1").mkdir(parents=True, exist_ok=True)
    (ROOT / ".tmp" / "depth1" / "tier_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    # markdown
    groups = {1: "Rank 1: top cinematic group (priority override, LaDoger 2026-10-10)", 2: "Rank 2: next cinematic tier (fully PD)",
              3: "Rank 3: tier A/B core", 4: "Rank 4: other major composers"}
    md = ["# Tier list and catalogue coverage (depth run 1, 2026-10-10)", "",
          "Generated by `scripts/bulk/tier_list.py` from `library.csv` + `library_bulk.csv`. "
          "**Coverage = distinct catalogue numbers present in live items / size of the standard catalogue.** "
          "Catalogue sizes are rounded published figures. Opus-number catalogues collapse `Op. 28 No. 7` to `Op. 28`, "
          "and items without a parseable catalogue number are listed separately (`no-cat items`), so percentages are rough guides, "
          "not audits. For composers with no standard catalogue the figure is blank and the signature-work check is the measure. "
          "`Signature works` = a hand-picked list of the best-known pieces (title match); `missing` names the gaps to fill first.", "",
          "Obscurity cutoff: Godowsky and Scriabin fame level. Below that, no new composers. "
          "US-PD-only (approved by LaDoger): Ravel, R. Strauss, Elgar, Holst, Rachmaninoff (+ the four ragtime/song composers). "
          "Godowsky (d.1938) is **not** approved; Sibelius (d.1957) is excluded. 1930–55 deaths need LaDoger approval per composer.", ""]
    for g in (1, 2, 3, 4):
        md += [f"## {groups[g]}", "", "| composer | tier | catalogue | est. total | live items | catalogued works | no-cat items | coverage | signature works | notes / gaps |", "|---|---|---|---:|---:|---:|---:|---:|---|---|"]
        for (name, rank, tier, cat_label, size, n_items, n_keys, no_cat, pct, sig_have, sig_missing, note) in rows:
            if rank != g:
                continue
            sig_total = len(SIG.get(name, []))
            sig = f"{sig_have}/{sig_total}" if sig_total else "–"
            gaps = ("missing: " + ", ".join(sig_missing[:8]) + ("…" if len(sig_missing) > 8 else "")) if sig_missing else ""
            md.append(f"| {name} | {tier} | {cat_label} | {size or '?'} | {n_items} | {n_keys if pats_has(name) else '–'} | {no_cat} | "
                      f"{(str(pct) + '%') if pct is not None else '–'} | {sig} | {(note + ' ' + gaps).strip()} |")
        md.append("")
    md += ["## Reading the table", "",
           "* Rank 1 and 2 are featured first on the site (`featured_rank` in `data/composers.json`, composer filter/sort).",
           "* Per-work checklists for the US-PD-only composers: `docs/catalogues/{ravel,strauss_r,elgar,holst,rachmaninoff}.csv`.",
           "* Deep-source log and what is still blocked (IMSLP captcha, NC/SA files): `docs/catalogues/SOURCES_DEEP.md`.",
           "* Catalogue sizes: BWV ≈ 1,128; HWV ≈ 610; RV ≈ 800; K. Mozart 626; D. Schubert 998; Beethoven Op. 1-138 + WoO 1-205; Hob. ≈ 750; WWV ≈ 113; WAB 149; Lesure L. ≈ 145.", ""]
    (ROOT / "docs" / "catalogues").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "catalogues" / "TIER_LIST.md").write_text("\n".join(md), encoding="utf-8")
    for (name, rank, tier, cat_label, size, n_items, n_keys, no_cat, pct, sig_have, sig_missing, note) in rows:
        if rank <= 2:
            print(f"{name:26} items {n_items:4} cat {n_keys:4} nocat {no_cat:4} cov {pct} sig {sig_have}/{len(SIG.get(name, []))}")
    return 0


def pats_has(name: str) -> bool:
    return any(t[0] == name and t[5] for t in T)


if __name__ == "__main__":
    raise SystemExit(main())
