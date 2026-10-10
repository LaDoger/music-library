#!/usr/bin/env python3
"""Per-set completeness of famous piano sets in the live catalog (data/catalog.json). Prints markdown rows."""
import json, re, sys, unicodedata
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def fold(s): return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
items = json.load(open(ROOT / "data/catalog.json"))
items = items["items"] if isinstance(items, dict) else items
def hay(it): return fold(" ".join(str(it.get(k) or "") for k in ("title", "movement", "catalog")))
# (set name, composer substring, set regex (on hay), scope, [(label, movement regex)])
SETS = [
 ("Debussy Children's Corner L.113", "debussy", r"children", "PD", [("1 Doctor Gradus", r"gradus"), ("2 Jimbo's Lullaby", r"jimbo"), ("3 Serenade for the Doll", r"doll|poupee"), ("4 The Snow Is Dancing", r"snow|neige"), ("5 The Little Shepherd", r"shepherd|berger"), ("6 Golliwogg's Cakewalk", r"golliwog")]),
 ("Ravel Le Tombeau de Couperin M.68", "ravel", r"tombeau", "US-PD-only", [("complete (6 mvts in one file)", r"tombeau")]),
 ("Ravel Valses nobles et sentimentales M.61", "ravel", r"valses nobles", "US-PD-only", [(f"Valse {i}", rf"valses nobles.*\b{i}\b") for i in range(1, 9)]),
 ("Scriabin 2 Poèmes Op.32", "scriabin", r"op\.? ?32", "PD", [("No. 1", r"op\.? ?32 no\.? ?1\b"), ("No. 2", r"op\.? ?32 no\.? ?2\b")]),
 ("Brahms 7 Fantasien Op.116", "brahms", r"op\.? ?116", "PD", [(f"No. {i}", rf"op\.? ?116.*no\.? ?{i}\b") for i in range(1, 8)]),
 ("Brahms 3 Intermezzi Op.117", "brahms", r"op\.? ?117", "PD", [(f"No. {i}", rf"op\.? ?117.*no\.? ?{i}\b") for i in range(1, 4)]),
 ("Brahms 6 Klavierstücke Op.118", "brahms", r"op\.? ?118", "PD", [(f"No. {i}", rf"op\.? ?118.*no\.? ?{i}\b") for i in range(1, 7)]),
 ("Brahms 4 Klavierstücke Op.119", "brahms", r"op\.? ?119", "PD", [(f"No. {i}", rf"op\.? ?119.*no\.? ?{i}\b") for i in range(1, 5)]),
 ("Debussy Suite bergamasque L.75", "debussy", r"bergamasque", "PD", [("Prélude", r"prelude"), ("Menuet", r"menuet"), ("Clair de lune", r"clair de lune"), ("Passepied", r"passepied")]),
 ("Debussy 2 Arabesques L.66", "debussy", r"arabesque", "PD", [("No. 1", r"arabesque.*\b1\b"), ("No. 2", r"arabesque.*\b2\b")]),
 ("Debussy Estampes L.100", "debussy", r"estampes|pagodes|grenade|jardins", "PD", [("Pagodes", r"pagodes"), ("La soirée dans Grenade", r"grenade"), ("Jardins sous la pluie", r"jardins")]),
 ("Debussy Pour le piano L.95", "debussy", r"pour le piano", "PD", [("Prélude", r"pour le piano.*prelude"), ("Sarabande", r"pour le piano.*sarabande"), ("Toccata", r"pour le piano.*toccata")]),
 ("Debussy Images I L.110", "debussy", r"images|reflets|hommage a rameau|mouvement", "PD", [("Reflets dans l'eau", r"reflets"), ("Hommage à Rameau", r"rameau"), ("Mouvement", r"images.*mouvement")]),
 ("Debussy Images II L.111", "debussy", r"images|cloches|poissons|lune descend", "PD", [("Cloches à travers les feuilles", r"cloches"), ("Et la lune descend", r"lune descend"), ("Poissons d'or", r"poissons")]),
 ("Debussy Préludes Book I L.117", "debussy", r"prelude", "PD", [(n, r) for n, r in [("Danseuses de Delphes", "delphes"), ("Voiles", r"voiles"), ("Le vent dans la plaine", "vent dans la plaine"), ("Les sons et les parfums", "parfums"), ("Les collines d'Anacapri", "anacapri"), ("Des pas sur la neige", "pas sur la neige"), ("Ce qu'a vu le vent d'ouest", "vent d.ouest"), ("La fille aux cheveux de lin", "cheveux de lin"), ("La sérénade interrompue", "serenade interrompue"), ("La cathédrale engloutie", "cathedrale"), ("La danse de Puck", "puck"), ("Minstrels", "minstrels")]]),
 ("Debussy Préludes Book II L.123", "debussy", r"prelude", "PD", [(n, r) for n, r in [("Brouillards", "brouillards"), ("Feuilles mortes", "feuilles mortes"), ("La puerta del Vino", "puerta"), ("Les fées sont d'exquises danseuses", "fees"), ("Bruyères", "bruyeres"), ("Général Lavine", "lavine"), ("La terrasse des audiences", "terrasse"), ("Ondine", "ondine"), ("Hommage à S. Pickwick", "pickwick"), ("Canope", "canope"), ("Les tierces alternées", "tierces"), ("Feux d'artifice", "feux d.artifice")]]),
 ("Ravel Miroirs M.43", "ravel", r"miroirs|noctuelles|oiseaux|barque|alborada|vallee", "US-PD-only", [("Noctuelles", "noctuelles"), ("Oiseaux tristes", "oiseaux"), ("Une barque sur l'océan", "barque"), ("Alborada del gracioso", "alborada"), ("La vallée des cloches", "vallee")]),
 ("Ravel Gaspard de la nuit M.55", "ravel", r"gaspard|ondine|gibet|scarbo", "US-PD-only", [("Ondine", "ondine"), ("Le gibet", "gibet"), ("Scarbo", "scarbo")]),
 ("Ravel Sonatine M.40", "ravel", r"sonatine", "US-PD-only", [("complete or mvts", "sonatine")]),
 ("Satie 3 Gymnopédies", "satie", r"gymnop", "PD", [(f"No. {i}", rf"gymnop.*\b{i}\b") for i in range(1, 4)]),
 ("Satie Gnossiennes 1-6", "satie", r"gnossienne", "PD", [(f"No. {i}", rf"gnossienne.*\b{i}\b") for i in range(1, 7)]),
 ("Satie 3 Sarabandes", "satie", r"sarabande", "PD", [(f"No. {i}", rf"sarabande.*\b{i}\b") for i in range(1, 4)]),
 ("Scriabin 12 Études Op.8", "scriabin", r"op\.? ?8\b", "PD", [(f"No. {i}", rf"op\.? ?8 no\.? ?{i}\b") for i in range(1, 13)]),
 ("Scriabin 8 Études Op.42", "scriabin", r"op\.? ?42", "PD", [(f"No. {i}", rf"op\.? ?42 no\.? ?{i}\b") for i in range(1, 9)]),
]
out = []
for name, comp, setre, scope, mvts in SETS:
    pool = [hay(it) for it in items if comp in fold(it.get("composer")) and re.search(setre, hay(it))]
    have = [l for l, r in mvts if any(re.search(r, h) for h in pool)]
    miss = [l for l, r in mvts if l not in have]
    st = "COMPLETE" if not miss else f"{len(have)}/{len(mvts)}"
    out.append((name, scope, st, have, miss))
    print(f"| {name} | {scope} | {st} | {', '.join(have) or '-'} | {', '.join(miss) or '-'} |")
