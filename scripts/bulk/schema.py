"""Shared columns, composer identity, licence classes, and source rank.

Source rank (lower is better), from briefs/SOURCES_POLICY.md:
  1 OpenScore CC0 engraving
  2 Mutopia public domain
  3 Mutopia CC BY
  4 PDMX no_license_conflict with a high rating
  5 other clean PDMX
  8 CC BY-SA (kept in the candidate list, not downloaded as clean)
  9 composition-term flagged (death 1930–1955)
  10 excluded or unverified
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path

SCHEMA_COLUMNS = [
    "id", "composer", "death_year", "title", "catalog", "movement",
    "mood_tags", "tempo_energy", "notable_excerpt", "video_use_ideas",
    "editable_source_url", "editable_format", "editable_license",
    "musescore_url", "recording_source_url", "recording_performer",
    "recording_license", "recording_quality", "legal_notes",
    "local_score_path", "local_audio_path", "preview_path",
    "verified", "added_by",
]

# After the schema columns so a SCHEMA-only reader can still parse the prefix.
EXTRA_COLUMNS = [
    "source_rank", "source_name", "licence_class", "instrumentation",
    "popularity", "genre", "era", "dedup_key", "download_url",
    "repo_path", "external_id", "canon", "quality_penalty",
    "licence_scope", "publication_year", "licence_scope_reason",
]

CANDIDATE_COLUMNS = SCHEMA_COLUMNS + EXTRA_COLUMNS

# edition licence class, least to most restrictive for merge decisions
CLASS_ORDER = ["clean", "attribution", "flagged", "sharealike", "unverified", "excluded"]

# Named exclusions from the batch briefs. Death year also excludes life+70 failures.
EXCLUDED_CANONS = {
    "igor stravinsky",
    "sergei prokofiev",
    "dmitri shostakovich",
    "carl orff",
    "nikolai medtner",
    "kaikhosru shapurji sorabji",
    "kaikhosru sorabji",
}

# canon -> (display, death, id prefix, tier, extra substrings)
# tier 1 is the brief's first priority, 2 the next wave, 3 niche, 4 depth.
_RAW = [
    ("johann sebastian bach", "Johann Sebastian Bach", 1750, "bach", 1, ["j s bach", "js bach", "bachjs"]),
    ("carl philipp emanuel bach", "Carl Philipp Emanuel Bach", 1788, "cpebach", 3, ["cpe bach", "c p e bach", "emanuel bach"]),
    ("johann christian bach", "Johann Christian Bach", 1782, "jcbach", 4, ["johann christian bach", "christian bach"]),
    ("wilhelm friedemann bach", "Wilhelm Friedemann Bach", 1784, "wfbach", 4, ["friedemann"]),
    ("richard wagner", "Richard Wagner", 1883, "wagner", 1, ["richard wagner", "wagner"]),
    ("gustav mahler", "Gustav Mahler", 1911, "mahler", 1, ["gustav mahler", "mahler"]),
    ("anton bruckner", "Anton Bruckner", 1896, "bruckner", 1, ["anton bruckner", "bruckner"]),
    ("ludwig van beethoven", "Ludwig van Beethoven", 1827, "beethoven", 2, ["ludwig van beethoven", "beethoven", "ludvig van beethoven"]),
    ("wolfgang amadeus mozart", "Wolfgang Amadeus Mozart", 1791, "mozart", 2, ["wolfgang amadeus mozart", "w a mozart", "wa mozart", "mozart"]),
    ("frederic chopin", "Frédéric Chopin", 1849, "chopin", 2, ["frederic chopin", "chopin"]),
    ("claude debussy", "Claude Debussy", 1918, "debussy", 2, ["claude debussy", "debussy"]),
    ("franz schubert", "Franz Schubert", 1828, "schubert", 4, ["franz schubert", "schubert"]),
    ("robert schumann", "Robert Schumann", 1856, "schumann", 4, ["robert schumann"]),
    ("clara schumann", "Clara Schumann", 1896, "cschumann", 3, ["clara schumann"]),
    ("johannes brahms", "Johannes Brahms", 1897, "brahms", 4, ["johannes brahms", "brahms"]),
    ("joseph haydn", "Joseph Haydn", 1809, "haydn", 4, ["joseph haydn", "franz joseph haydn", "haydn"]),
    ("johann michael haydn", "Johann Michael Haydn", 1806, "mhaydn", 4, ["michael haydn"]),
    ("hugo wolf", "Hugo Wolf", 1903, "wolf", 4, ["hugo wolf"]),
    ("felix mendelssohn", "Felix Mendelssohn", 1847, "mendelssohn", 4, ["felix mendelssohn", "mendelssohn"]),
    ("fanny hensel", "Fanny Hensel", 1847, "hensel", 3, ["fanny hensel", "fanny mendelssohn"]),
    ("antonin dvorak", "Antonín Dvořák", 1904, "dvorak", 4, ["antonin dvorak", "dvorak"]),
    ("gabriel faure", "Gabriel Fauré", 1924, "faure", 3, ["gabriel faure", "faure"]),
    ("cesar franck", "César Franck", 1890, "franck", 3, ["cesar franck", "franck"]),
    ("alexander scriabin", "Alexander Scriabin", 1915, "scriabin", 3, ["scriabin", "skryabin", "scriabine"]),
    ("francois couperin", "François Couperin", 1733, "couperin", 3, ["francois couperin", "couperin"]),
    ("charles valentin alkan", "Charles-Valentin Alkan", 1888, "alkan", 3, ["alkan"]),
    ("jean philippe rameau", "Jean-Philippe Rameau", 1764, "rameau", 3, ["rameau"]),
    ("dieterich buxtehude", "Dieterich Buxtehude", 1707, "buxtehude", 3, ["buxtehude"]),
    ("girolamo frescobaldi", "Girolamo Frescobaldi", 1643, "frescobaldi", 3, ["frescobaldi"]),
    ("william byrd", "William Byrd", 1623, "byrd", 3, ["william byrd"]),
    ("carlo gesualdo", "Carlo Gesualdo", 1613, "gesualdo", 3, ["gesualdo"]),
    ("feruccio busoni", "Ferruccio Busoni", 1924, "busoni", 3, ["busoni"]),
    ("franz liszt", "Franz Liszt", 1886, "liszt", 3, ["franz liszt", "liszt"]),
    ("max reger", "Max Reger", 1916, "reger", 3, ["max reger", "reger"]),
    ("sergei lyapunov", "Sergei Lyapunov", 1924, "lyapunov", 3, ["lyapunov", "liapunov", "liapounov"]),
    ("mily balakirev", "Mily Balakirev", 1910, "balakirev", 3, ["balakirev"]),
    ("leopold godowsky", "Leopold Godowsky", 1938, "godowsky", 3, ["godowsky"]),
    ("george frideric handel", "George Frideric Handel", 1759, "handel", 4, ["handel", "haendel"]),
    ("antonio vivaldi", "Antonio Vivaldi", 1741, "vivaldi", 4, ["vivaldi"]),
    ("pyotr ilyich tchaikovsky", "Pyotr Ilyich Tchaikovsky", 1893, "tchaikovsky", 4, ["tchaikovsky", "tschaikowsky", "tchaikowsky"]),
    ("johann pachelbel", "Johann Pachelbel", 1706, "pachelbel", 4, ["pachelbel"]),
    ("domenico scarlatti", "Domenico Scarlatti", 1757, "scarlatti", 4, ["domenico scarlatti", "scarlatti"]),
    ("alessandro scarlatti", "Alessandro Scarlatti", 1725, "ascarlatti", 4, ["alessandro scarlatti"]),
    ("georg philipp telemann", "Georg Philipp Telemann", 1767, "telemann", 4, ["telemann"]),
    ("henry purcell", "Henry Purcell", 1695, "purcell", 4, ["henry purcell", "purcell"]),
    ("arcangelo corelli", "Arcangelo Corelli", 1713, "corelli", 4, ["corelli"]),
    ("erik satie", "Erik Satie", 1925, "satie", 4, ["erik satie", "satie"]),
    ("camille saint saens", "Camille Saint-Saëns", 1921, "saintsaens", 4, ["saint saens", "saint-saens"]),
    ("giuseppe verdi", "Giuseppe Verdi", 1901, "verdi", 4, ["giuseppe verdi", "verdi"]),
    ("georges bizet", "Georges Bizet", 1875, "bizet", 4, ["georges bizet", "bizet"]),
    ("edvard grieg", "Edvard Grieg", 1907, "grieg", 4, ["edvard grieg", "grieg"]),
    ("modest mussorgsky", "Modest Mussorgsky", 1881, "mussorgsky", 4, ["mussorgsky", "moussorgsky"]),
    ("nikolai rimsky korsakov", "Nikolai Rimsky-Korsakov", 1908, "rimskykorsakov", 4, ["rimsky", "korsakov"]),
    ("alexander borodin", "Alexander Borodin", 1887, "borodin", 4, ["borodin"]),
    ("richard strauss", "Richard Strauss", 1949, "rstrauss", 4, ["richard strauss"]),
    ("johann strauss ii", "Johann Strauss II", 1899, "strauss2", 4, ["johann strauss ii", "johann strauss"]),
    ("gustav holst", "Gustav Holst", 1934, "holst", 4, ["gustav holst", "holst"]),
    ("edward elgar", "Edward Elgar", 1934, "elgar", 4, ["edward elgar", "elgar"]),
    ("sergei rachmaninoff", "Sergei Rachmaninoff", 1943, "rachmaninoff", 4, ["rachmaninoff", "rachmaninov", "rakhmaninov"]),
    ("maurice ravel", "Maurice Ravel", 1937, "ravel", 4, ["maurice ravel", "ravel"]),
    ("bela bartok", "Béla Bartók", 1945, "bartok", 4, ["bartok", "bela bartok"]),
    ("george gershwin", "George Gershwin", 1937, "gershwin", 4, ["gershwin"]),
    ("scott joplin", "Scott Joplin", 1917, "joplin", 4, ["scott joplin", "joplin"]),
    ("igor stravinsky", "Igor Stravinsky", 1971, "stravinsky", 9, ["stravinsky"]),
    ("sergei prokofiev", "Sergei Prokofiev", 1953, "prokofiev", 9, ["prokofiev"]),
    ("dmitri shostakovich", "Dmitri Shostakovich", 1975, "shostakovich", 9, ["shostakovich"]),
    ("carl orff", "Carl Orff", 1982, "orff", 9, ["carl orff"]),
    ("nikolai medtner", "Nikolai Medtner", 1951, "medtner", 9, ["medtner"]),
    ("john dowland", "John Dowland", 1626, "dowland", 4, ["dowland"]),
    ("orlando gibbons", "Orlando Gibbons", 1625, "gibbons", 4, ["gibbons"]),
    ("thomas tallis", "Thomas Tallis", 1585, "tallis", 4, ["tallis"]),
    ("claudio monteverdi", "Claudio Monteverdi", 1643, "monteverdi", 4, ["monteverdi"]),
    ("jean baptiste lully", "Jean-Baptiste Lully", 1687, "lully", 4, ["lully"]),
    ("giovanni battista pergolesi", "Giovanni Battista Pergolesi", 1736, "pergolesi", 4, ["pergolesi"]),
    ("niccolo paganini", "Niccolò Paganini", 1840, "paganini", 4, ["paganini"]),
    ("gioachino rossini", "Gioachino Rossini", 1868, "rossini", 4, ["rossini"]),
    ("gaetano donizetti", "Gaetano Donizetti", 1848, "donizetti", 4, ["donizetti"]),
    ("charles gounod", "Charles Gounod", 1893, "gounod", 4, ["gounod"]),
    ("engelbert humperdinck", "Engelbert Humperdinck", 1921, "humperdinck", 4, ["humperdinck"]),
    ("paul dukas", "Paul Dukas", 1935, "dukas", 4, ["dukas"]),
    ("emmanuel chabrier", "Emmanuel Chabrier", 1894, "chabrier", 4, ["chabrier"]),
    ("louis moreau gottschalk", "Louis Moreau Gottschalk", 1869, "gottschalk", 4, ["gottschalk"]),
    ("john field", "John Field", 1837, "field", 4, ["john field"]),
    ("muzio clementi", "Muzio Clementi", 1832, "clementi", 4, ["clementi"]),
    ("stephen foster", "Stephen Foster", 1864, "foster", 4, ["stephen foster"]),
    ("fernando sor", "Fernando Sor", 1839, "sor", 5, ["fernando sor"]),
    ("francisco tarrega", "Francisco Tárrega", 1909, "tarrega", 5, ["tarrega"]),
    ("mauro giuliani", "Mauro Giuliani", 1829, "giuliani", 5, ["giuliani"]),
    ("johann jakob froberger", "Johann Jakob Froberger", 1667, "froberger", 4, ["froberger"]),
    ("marc antoine charpentier", "Marc-Antoine Charpentier", 1704, "charpentier", 4, ["charpentier"]),
    # Scale run 2 (2026-10-09): more PD composers (death <= 1929). Common surnames are
    # matched only by the full needles (see _STRICT_LAST).
    ("giacomo puccini", "Giacomo Puccini", 1924, "puccini", 4, ["puccini"]),
    ("jules massenet", "Jules Massenet", 1912, "massenet", 4, ["massenet"]),
    ("jacques offenbach", "Jacques Offenbach", 1880, "offenbach", 4, ["offenbach"]),
    ("isaac albeniz", "Isaac Albéniz", 1909, "albeniz", 4, ["albeniz"]),
    ("enrique granados", "Enrique Granados", 1916, "granados", 4, ["granados"]),
    ("edward macdowell", "Edward MacDowell", 1908, "macdowell", 4, ["macdowell", "mac dowell"]),
    ("anton arensky", "Anton Arensky", 1906, "arensky", 4, ["arensky"]),
    ("anatoly lyadov", "Anatoly Lyadov", 1914, "lyadov", 4, ["lyadov", "liadov"]),
    ("moritz moszkowski", "Moritz Moszkowski", 1925, "moszkowski", 4, ["moszkowski"]),
    ("carl czerny", "Carl Czerny", 1857, "czerny", 4, ["czerny"]),
    ("friedrich burgmuller", "Friedrich Burgmüller", 1874, "burgmuller", 4, ["burgmuller", "burgmueller"]),
    ("luigi boccherini", "Luigi Boccherini", 1805, "boccherini", 4, ["boccherini"]),
    ("giuseppe tartini", "Giuseppe Tartini", 1770, "tartini", 4, ["tartini"]),
    ("giacomo meyerbeer", "Giacomo Meyerbeer", 1864, "meyerbeer", 4, ["meyerbeer"]),
    ("bedrich smetana", "Bedřich Smetana", 1884, "smetana", 4, ["smetana"]),
    ("zdenek fibich", "Zdeněk Fibich", 1900, "fibich", 4, ["fibich"]),
    ("ernest chausson", "Ernest Chausson", 1899, "chausson", 4, ["chausson"]),
    ("mikhail glinka", "Mikhail Glinka", 1857, "glinka", 4, ["glinka"]),
    ("henri vieuxtemps", "Henri Vieuxtemps", 1881, "vieuxtemps", 4, ["vieuxtemps"]),
    ("pablo de sarasate", "Pablo de Sarasate", 1908, "sarasate", 4, ["sarasate"]),
    ("giovanni pierluigi da palestrina", "Giovanni Pierluigi da Palestrina", 1594, "palestrina", 4, ["palestrina"]),
    ("josquin des prez", "Josquin des Prez", 1521, "josquin", 4, ["josquin"]),
    ("orlande de lassus", "Orlande de Lassus", 1594, "lassus", 4, ["lassus", "orlando di lasso", "orlando lasso"]),
    ("jan pieterszoon sweelinck", "Jan Pieterszoon Sweelinck", 1621, "sweelinck", 4, ["sweelinck"]),
    ("johann kuhnau", "Johann Kuhnau", 1722, "kuhnau", 4, ["kuhnau"]),
    ("francesco geminiani", "Francesco Geminiani", 1762, "geminiani", 4, ["geminiani"]),
    ("antonio salieri", "Antonio Salieri", 1825, "salieri", 4, ["salieri"]),
    ("anton diabelli", "Anton Diabelli", 1858, "diabelli", 4, ["diabelli"]),
    ("friedrich kuhlau", "Friedrich Kuhlau", 1832, "kuhlau", 4, ["kuhlau"]),
    ("emile waldteufel", "Émile Waldteufel", 1915, "waldteufel", 4, ["waldteufel"]),
    ("franz von suppe", "Franz von Suppé", 1895, "suppe", 4, ["von suppe", "franz suppe"]),
    ("julius fucik", "Julius Fučík", 1916, "fucik", 4, ["julius fucik"]),
    ("alexandre guilmant", "Alexandre Guilmant", 1911, "guilmant", 4, ["guilmant"]),
    ("leon boellmann", "Léon Boëllmann", 1897, "boellmann", 4, ["boellmann", "boelmann"]),
    ("carl maria von weber", "Carl Maria von Weber", 1826, "weber", 4, ["von weber", "c m von weber", "carl maria weber"]),
    ("johann nepomuk hummel", "Johann Nepomuk Hummel", 1837, "hummel", 4, ["johann nepomuk hummel", "j n hummel"]),
    ("christoph willibald gluck", "Christoph Willibald Gluck", 1787, "gluck", 4, ["christoph willibald gluck", "c w gluck", "christoph gluck", "willibald gluck"]),
    ("vincenzo bellini", "Vincenzo Bellini", 1835, "bellini", 4, ["vincenzo bellini"]),
    ("arthur sullivan", "Arthur Sullivan", 1900, "sullivan", 4, ["arthur sullivan", "sir arthur sullivan"]),
    ("max bruch", "Max Bruch", 1920, "bruch", 4, ["max bruch"]),
    ("heinrich schutz", "Heinrich Schütz", 1672, "schutz", 4, ["heinrich schutz", "heinrich schuetz"]),
    ("michael praetorius", "Michael Praetorius", 1621, "praetorius", 4, ["michael praetorius"]),
    ("leo delibes", "Léo Delibes", 1891, "delibes", 4, ["delibes"]),
    ("benjamin godard", "Benjamin Godard", 1895, "godard", 4, ["benjamin godard"]),
    ("amilcare ponchielli", "Amilcare Ponchielli", 1886, "ponchielli", 4, ["ponchielli"]),
    ("ruggero leoncavallo", "Ruggero Leoncavallo", 1919, "leoncavallo", 4, ["leoncavallo"]),
    ("henryk wieniawski", "Henryk Wieniawski", 1880, "wieniawski", 4, ["wieniawski"]),
    ("leos janacek", "Leoš Janáček", 1928, "janacek", 4, ["janacek"]),
    ("samuel coleridge taylor", "Samuel Coleridge-Taylor", 1912, "coleridgetaylor", 4, ["coleridge taylor"]),
    ("traditional", "Traditional", None, "traditional", 5, []),
    ("anonymous", "Anonymous", None, "anonymous", 5, []),
]

# Scale run 3: more PDMX composers with Wikidata life dates, generated by
# gen_pdmx_composers.py. Matched on the full name only (see GENERATED_CANONS).
GENERATED_FILE = Path(__file__).resolve().parent / "pdmx_composers_wikidata.json"
GENERATED_CANONS = set()
if GENERATED_FILE.exists() and not os.environ.get("MUSICLIB_NO_GENERATED_COMPOSERS"):
    _hand = {item[0] for item in _RAW}
    for _entry in json.loads(GENERATED_FILE.read_text(encoding="utf-8"))["composers"]:
        if _entry["canon"] in _hand or _entry.get("death") is None:
            continue
        _RAW.append((_entry["canon"], _entry["name"], _entry["death"], _entry["prefix"], 6, _entry["aliases"]))
        GENERATED_CANONS.add(_entry["canon"])

# Scale run 4: hand-disambiguated names the generator skipped (see the json's notes).
MANUAL_FILE = Path(__file__).resolve().parent / "pdmx_composers_manual.json"
if MANUAL_FILE.exists() and not os.environ.get("MUSICLIB_NO_GENERATED_COMPOSERS"):
    _known = {item[0] for item in _RAW}
    for _entry in json.loads(MANUAL_FILE.read_text(encoding="utf-8"))["composers"]:
        if _entry["canon"] in _known or _entry.get("death") is None or _entry["death"] > 1929:
            continue
        _RAW.append((_entry["canon"], _entry["name"], _entry["death"], _entry["prefix"], 6, _entry["aliases"]))
        GENERATED_CANONS.add(_entry["canon"])

# LaDoger-approved US-PD-only composers (death 1930–1955). Full-name match only.
# Works need a verified publication year ≤ 1930 and licence_scope=US-PD-only.
US_PD_ONLY_CANONS = set()
US_PD_ONLY_FILE = MANUAL_FILE
if US_PD_ONLY_FILE.exists() and not os.environ.get("MUSICLIB_NO_GENERATED_COMPOSERS"):
    _known = {item[0] for item in _RAW}
    for _entry in json.loads(US_PD_ONLY_FILE.read_text(encoding="utf-8")).get("approved_us_pd_only", []):
        if _entry["canon"] in _known or _entry.get("death") is None:
            continue
        if not (1930 <= int(_entry["death"]) <= 1955):
            continue
        _RAW.append((_entry["canon"], _entry["name"], _entry["death"], _entry["prefix"], 6, _entry.get("aliases") or []))
        GENERATED_CANONS.add(_entry["canon"])
        US_PD_ONLY_CANONS.add(_entry["canon"])

COMPOSERS = {}
for canon, display, death, prefix, tier, _aliases in _RAW:
    COMPOSERS[canon] = {
        "name": display,
        "death": death,
        "prefix": prefix,
        "tier": tier,
    }

# Longer / more specific needles first. Bare last names are listed after family members.
_MATCH_RULES = []
for canon, _display, _death, _prefix, _tier, aliases in _RAW:
    needles = [canon] + list(aliases)
    _MATCH_RULES.append((canon, needles))
# Specific Bach-family and Haydn-family rules must beat the bare last name.
_SPECIFIC_FIRST = [
    "carl philipp emanuel bach",
    "johann christian bach",
    "wilhelm friedemann bach",
    "johann michael haydn",
    "clara schumann",
    "fanny hensel",
    "richard strauss",
    "johann strauss ii",
    "alessandro scarlatti",
    "domenico scarlatti",
    "robert schumann",
]
_MATCH_RULES.sort(key=lambda item: (0 if item[0] in _SPECIFIC_FIRST else 1, -len(item[0])))

GUITAR_ORIGINALS = {
    "fernando sor", "francisco tarrega", "mauro giuliani", "john dowland",
}

KIND_WORDS = [
    "prelude", "praeludium", "preludium", "fugue", "fuga", "toccata", "fantasia",
    "fantasy", "allemande", "courante", "sarabande", "gigue", "bourree", "minuet",
    "menuet", "scherzo", "aria", "chorale", "passacaglia", "chaconne", "invention",
    "sinfonia", "overture", "vorspiel", "liebestod", "adagio", "allegro", "andante",
    "largo", "lento", "presto", "vivace", "grave", "march", "marche", "waltz",
    "valse", "nocturne", "etude", "ballade", "polonaise", "mazurka", "rondo",
    "variation", "canon", "ricercar", "contrapunctus", "romance", "intermezzo",
    "bagatelle", "impromptu", "berceuse", "barcarolle", "humoreske", "ecossaise",
    "landler", "siciliano", "sicilienne", "air", "chaconne",
]

TOKEN_STOP = {
    "major", "minor", "string", "quartet", "piano", "sonata", "symphony",
    "movement", "allegro", "andante", "adagio", "largo", "presto", "vivace",
    "moderato", "opus", "prelude", "fugue", "menuet", "minuet", "gigue",
    "courante", "allemande", "sarabande", "bourree", "toccata", "fantasia",
    "fantasy", "partita", "suite", "chorale", "variation", "variations",
    "canon", "invention", "sinfonia", "concerto", "overture", "romance",
    "nocturne", "etude", "waltz", "polonaise", "mazurka", "ballade", "scherzo",
    "rondo", "american", "grande", "gross", "grosse", "klein", "kleine",
    "number", "no", "the", "and", "for", "with", "from", "piece", "pieces",
    "book", "volume", "part", "complete", "score", "voice", "violin", "cello",
}

SPAM_RE = re.compile(
    r"tutorial|synthesia|piano tiles|easy piano|beginner|karaoke|ringtone|"
    r"baby shark|despacito|shape of you|game of thrones|star wars|harry potter|"
    r"let it go|taylor swift|\bbts\b|bad guy|believer|christmas medley",
    re.I,
)

_ROMAN = {
    "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
    "vi": "6", "vii": "7", "viii": "8", "ix": "9",
}


def fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("ß", "ss").replace("æ", "ae").replace("ø", "o")
    text = text.lower().replace("_", " ")
    text = text.replace("–", "-").replace("—", "-")
    return text


def slugify(value: str, limit: int = 40) -> str:
    text = fold(value)
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    text = re.sub(r"_+", "_", text)
    return text[:limit].strip("_")


def _edit_distance(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                prev[j] + 1,
                cur[-1] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def _last_token_hit(text: str, last: str) -> bool:
    for token in text.split():
        if token == last:
            return True
        if len(token) >= 5 and len(last) >= 5 and _edit_distance(token, last) <= 1:
            return True
        if len(last) >= 6 and token.startswith(last[:6]) and abs(len(token) - len(last)) <= 2:
            return True
    return False


_STRICT_LAST = {
    "weber", "hummel", "gluck", "bellini", "sullivan", "bruch", "schutz",
    "praetorius", "godard", "prez", "suppe", "fucik", "taylor",
}


def match_composer(name: str) -> str:
    """Map a messy credit line to a canon key, or '' if it is not a known composer."""
    text = fold(name)
    text = re.sub(r"(?<=[a-z])(?=\d)", " ", text)  # "William Byrd1540 - 1623"
    text = re.sub(r"\b(1[4-9]\d{2}|20\d{2})\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    padded = f" {text} "
    # Family members before bare Bach / Haydn / Schumann / Strauss.
    if any(n in padded for n in (" cpe ", " c p e ", " emanuel bach ")):
        return "carl philipp emanuel bach"
    if "friedemann" in padded:
        return "wilhelm friedemann bach"
    if "johann christian" in padded or " j c bach " in padded:
        return "johann christian bach"
    if "michael haydn" in padded:
        return "johann michael haydn"
    if "clara schumann" in padded or "clara wieck" in padded:
        return "clara schumann"
    if "fanny hensel" in padded or "fanny mendelssohn" in padded:
        return "fanny hensel"
    if "richard strauss" in padded:
        return "richard strauss"
    if "johann strauss" in padded:
        return "johann strauss ii"
    if "alessandro scarlatti" in padded:
        return "alessandro scarlatti"
    if "schumann" in padded and "clara" not in padded:
        return "robert schumann"
    hits = []
    for canon, needles in _MATCH_RULES:
        if canon in {
            "carl philipp emanuel bach", "johann christian bach",
            "wilhelm friedemann bach", "johann michael haydn",
            "clara schumann", "fanny hensel", "richard strauss",
            "johann strauss ii", "alessandro scarlatti",
        }:
            continue
        for needle in needles:
            if f" {needle} " in padded or padded.strip() == needle:
                hits.append(canon)
                break
            last = canon.split()[-1]
            if canon in GENERATED_CANONS:
                continue  # full name only, never a bare or fuzzy surname
            if last in {"bach", "haydn", "strauss", "schumann", "scarlatti"} | _STRICT_LAST:
                continue
            if _last_token_hit(padded, last) and (
                canon.split()[0] in padded or len(needles) == 1 or last in padded
            ):
                # last-name hit; require the last name itself, not only a first name
                if _last_token_hit(padded, last):
                    hits.append(canon)
                    break
    # de-duplicate while preserving order
    seen = []
    for hit in hits:
        if hit not in seen:
            seen.append(hit)
    if not seen and _last_token_hit(padded, "bach") and "emanuel" not in padded:
        return "johann sebastian bach"
    if len(seen) == 1:
        return seen[0]
    if len(seen) > 1:
        # Prefer the earliest named person when the string is "Arr from X by Y"
        # and both are known. Ambiguous dual credits are left unmatched.
        return ""
    return ""


def composer_record(canon: str, display: str = "", death=None) -> dict:
    rec = COMPOSERS.get(canon)
    if rec:
        return rec
    prefix = slugify((display or canon).split()[-1] if (display or canon) else "piece", 18)
    return {
        "name": display or canon,
        "death": death,
        "prefix": prefix or "piece",
        "tier": 5,
    }


def parse_year(value) -> int | None:
    if value is None:
        return None
    match = re.search(r"(1[0-9]{3}|20[0-9]{2})", str(value))
    return int(match.group(1)) if match else None


def composition_status(canon: str, death: int | None, publication_year: int | None = None) -> tuple[str, str]:
    """Return (status, note) for the composition's term, separate from the edition licence."""
    if canon in EXCLUDED_CANONS or composer_record(canon)["tier"] >= 9:
        return "excluded", "Named exclusion in the source policy (not cleared for this library)."
    if canon in {"traditional", "anonymous"}:
        return "clean", "Source credits Traditional/Anonymous. The edition licence still has to be PD or CC0/CC-BY."
    if death is None:
        return "unverified", "Death year unknown; composition term not confirmed."
    if death > 1955:
        return "excluded", f"Composer died {death}; not public domain under life+70 as of 2026."
    if death > 1929:
        # LaDoger may approve individual composers for pre-1931 US-PD works only.
        if canon in US_PD_ONLY_CANONS and publication_year is not None and publication_year <= 1930:
            return (
                "flagged",
                f"US public domain only: composer died {death}; work published {publication_year} "
                "(before 1931). May be copyrighted elsewhere, including EU/Poland. "
                "LaDoger approved this composer with licence_scope=US-PD-only.",
            )
        return (
            "flagged",
            f"FLAG composer term: composer died {death}. Public domain in life+70 countries. "
            "Not a blanket PD-US claim, because works published from 1930 may remain protected. "
            "Do not import unless LaDoger approves the composer for US-PD-only with a verified "
            "pre-1931 publication year.",
        )
    return (
        "clean",
        f"Composer died {death}. Public domain in life+70 countries and, for this generation, "
        "normally PD-US as a historic published work.",
    )


def classify_license(text: str) -> tuple[str, str]:
    """Return (editable_license short label, class) from a licence phrase.

    Class is clean | attribution | sharealike | unverified | excluded.
    """
    raw = fold(text)
    raw = raw.replace("_", " ")
    if not raw.strip():
        return "", "unverified"
    if any(token in raw for token in (
        "by-nc", "by nc", "noncommercial", "non-commercial", "non commercial",
        "nc-sa", "nc-nd", "by-nd", "-nc",
    )):
        return "CC-BY-NC", "excluded"
    if any(token in raw for token in (
        "by-sa", "by sa", "sharealike", "share alike", "share-alike",
        "attribution-sharealike", "attribution sharealike", "cc-asa", "cc asa",
    )):
        return "CC-BY-SA", "sharealike"
    compact = raw.replace("-", "").replace(" ", "")
    if "cc0" in compact or "cczero" in compact or "creativecommonszero" in compact:
        return "CC0", "clean"
    if any(token in raw for token in ("public domain", "publicdomain", "public-domain")):
        return "PD", "clean"
    if any(token in raw for token in ("attribution", "cc by", "cc-by", "creative commons by")):
        return "CC-BY", "attribution"
    if "calcograf" in raw:
        return "other", "unverified"
    if "all rights" in raw or "copyright" in raw:
        return "other", "unverified"
    return "other", "unverified"


def combine_status(edition_class: str, composition_class: str) -> str:
    if "excluded" in (edition_class, composition_class):
        return "excluded"
    if edition_class == "sharealike":
        return "sharealike"
    if composition_class == "flagged":
        return "flagged"
    if "unverified" in (edition_class, composition_class):
        return "unverified"
    if edition_class == "attribution":
        return "attribution"
    if edition_class == "clean" and composition_class == "clean":
        return "clean"
    return edition_class or "unverified"


def source_rank(source_name: str, licence_class: str, rating: float = 0.0, n_ratings: int = 0) -> int:
    if licence_class == "sharealike":
        return 8
    if licence_class == "flagged":
        return 9
    if licence_class in {"excluded", "unverified", ""}:
        return 10
    if source_name.startswith("openscore"):
        return 1
    if source_name == "mutopia" and licence_class == "clean":
        return 2
    if source_name == "mutopia" and licence_class == "attribution":
        return 3
    if source_name == "pdmx":
        if rating >= 4.5 and n_ratings >= 3:
            return 4
        return 5
    return 7


def era_for(composer: str, death_year) -> str:
    known = {
        "Johann Sebastian Bach": "Baroque",
        "George Frideric Handel": "Baroque",
        "Antonio Vivaldi": "Baroque",
        "Johann Pachelbel": "Baroque",
        "François Couperin": "Baroque",
        "Jean-Philippe Rameau": "Baroque",
        "Dieterich Buxtehude": "Baroque",
        "Henry Purcell": "Baroque",
        "Arcangelo Corelli": "Baroque",
        "Domenico Scarlatti": "Baroque",
        "Georg Philipp Telemann": "Baroque",
        "Wolfgang Amadeus Mozart": "Classical",
        "Joseph Haydn": "Classical",
        "Ludwig van Beethoven": "Classical / early Romantic",
        "Franz Schubert": "Romantic",
        "Frédéric Chopin": "Romantic",
        "Antonín Dvořák": "Romantic",
        "Giuseppe Verdi": "Romantic",
    }
    if composer in known:
        return known[composer]
    year = parse_year(death_year)
    if (composer or "").strip().lower() in {"traditional", "anonymous"}:
        return "Traditional"
    if year is None:
        return ""
    if year < 1630:
        return "Renaissance"
    if year <= 1760:
        return "Baroque"
    if year <= 1830:
        return "Classical"
    if year <= 1920:
        return "Romantic"
    return "20th century"


def _movement_number(head: str) -> str | None:
    token = r"(i{1,3}|iv|vi{0,3}|ix|\d{1,2})"
    for pattern in (
        rf"^(?:no\.?\s*)?{token}\b",
        rf"(?:^|\s)(?:no\.?\s*)?{token}\s*$",
    ):
        match = re.search(pattern, head)
        if not match:
            continue
        raw = match.group(1)
        if raw.isdigit():
            return str(int(raw))
        if raw in _ROMAN:
            return _ROMAN[raw]
    return None


def movement_sig(movement: str) -> tuple[str | None, tuple[str, ...]]:
    """(movement number or None, kind words) for dedup compatibility."""
    text = fold(movement)
    text = text.replace("praeludium", "prelude").replace("preludium", "prelude")
    text = text.replace("fuga", "fugue")
    head = text.strip()
    number = _movement_number(head)
    kinds = []
    for kind in KIND_WORDS:
        if kind in {"praeludium", "preludium", "fuga"}:
            continue
        if re.search(rf"\b{kind}\b", text) and kind not in kinds:
            kinds.append(kind)
    return number, tuple(kinds[:3])


def movements_compatible(left: str, right: str) -> bool:
    """True when two movement labels are the same musical movement."""
    if not (left or "").strip() and not (right or "").strip():
        return True
    n1, k1 = movement_sig(left)
    n2, k2 = movement_sig(right)
    if k1 and k2:
        if not set(k1) & set(k2):
            return False
        if n1 and n2 and n1 != n2:
            return False
        return True
    if k1 or k2:
        return False
    s1 = re.sub(r"[^a-z0-9]", "", fold(left))
    s2 = re.sub(r"[^a-z0-9]", "", fold(right))
    if not s1 or not s2:
        return s1 == s2
    return s1 == s2 or s1 in s2 or s2 in s1


def normalize_catalog(value: str) -> str:
    text = fold(value)
    text = text.replace("opus", "op")
    replacements = [
        (r"\bwoo\s*", "woo"),
        (r"\bno\.?\s*", "no"),
        (r"\bnr\.?\s*", "no"),
        (r"\bop\.?\s*", "op"),
        (r"\bbwv\s*", "bwv"),
        (r"\bwwv\s*", "wwv"),
        (r"\bwab\s*", "wab"),
        (r"\bhwv\s*", "hwv"),
        (r"\brv\s*", "rv"),
        (r"\banh\.?\s*", "anh"),
        (r"\bhob(?:oken)?\.?\s*", "hob"),
        (r"\bkv\.?\s*", "k"),
        (r"\bk\.?\s*", "k"),
        (r"\bd\.?\s*", "d"),
        (r"\bl\.?\s*", "l"),
        (r"\bb\.?\s*", "b"),
        (r"\bsz\.?\s*", "sz"),
        (r"\bgmw\s*", "gmw"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return re.sub(r"[^a-z0-9]", "", text)


def catalog_from_text(*parts: str) -> str:
    blob = " ".join(p for p in parts if p)
    patterns = [
        r"BWV\s*Anh\.?\s*\d+[a-z]?",
        r"BWV\s*\d+[a-z]?",
        r"WWV\s*\d+[a-zA-Z]?",
        r"WAB\s*\d+[a-z]?",
        r"HWV\s*\d+[a-z]?",
        r"RV\s*\d+[a-z]?",
        r"WoO\s*\d+[a-z]?",
        r"Hob(?:oken)?\.?\s*[IVX]+[:.\s]*\d+",
        r"Op\.?\s*\d+\s*(?:No\.?\s*\d+)?",
        r"K\.?\s*\d+[a-z]?",
        r"KV\s*\d+[a-z]?",
        r"D\.?\s*\d{2,4}",
        r"L\.?\s*\d+[a-z]?",
        r"S\.?\s*\d+[a-z]?",
        r"B\.?\s*\d{2,4}",
        r"Sz\.?\s*\d+",
    ]
    for pattern in patterns:
        match = re.search(pattern, blob, flags=re.I)
        if match:
            found = re.sub(r"\s+", " ", match.group(0)).strip()
            return found
    return ""


def distinctive_tokens(*parts: str) -> set[str]:
    out = set()
    for part in parts:
        if not part:
            continue
        folded = fold(part)
        for word in re.findall(r"[a-z0-9]{6,}", folded):
            if word not in TOKEN_STOP and not word.isdigit():
                out.add(word)
        slug = re.sub(r"[^a-z0-9]", "", folded)
        if len(slug) >= 8 and slug not in TOKEN_STOP:
            out.add(slug)
    return out


def mood_tags(title: str, movement: str, style: str = "") -> str:
    text = fold(f"{title} {movement} {style}")
    tags: list[str] = []
    rules = [
        (r"adagio|largo|lent\b|grave|sarabande|traurig|tod\b|death|requiem|lament", ["slow", "somber"]),
        (r"allegro|presto|vivace|gigue|scherzo", ["fast", "bright"]),
        (r"andante|moderato|minuet|menuet", ["moderate", "elegant"]),
        (r"nocturne|berceuse|reverie|traum|dream|nacht|clair", ["nocturnal", "gentle"]),
        (r"march|marcia|fest|triumph", ["march", "ceremonial"]),
        (r"fugue|ricercar|contrapunctus|canon", ["contrapuntal"]),
        (r"prelude|praeludium|air\b", ["intimate"]),
        (r"rondo|humor|joke|scherz", ["playful"]),
        (r"romance|liebes|amour|love", ["lyrical", "tender"]),
        (r"storm|sturm|tempest|quake", ["dramatic"]),
    ]
    for pattern, words in rules:
        if re.search(pattern, text):
            tags.extend(words)
    if not tags:
        tags = ["classical", "lyrical"]
    deduped = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return ";".join(deduped[:5])


def tempo_energy(title: str, movement: str) -> str:
    text = fold(f"{movement} {title}")
    if re.search(r"presto|vivace", text):
        return "presto / high drive"
    if re.search(r"allegro", text):
        return "allegro / high drive"
    if re.search(r"adagio|largo|grave|lent", text):
        return "adagio / low energy"
    if re.search(r"andante|andantino", text):
        return "andante / moderate"
    if re.search(r"moderato|minuet|menuet|andante", text):
        return "moderato / moderate"
    return "moderate / opening"


def video_use(tags: str) -> str:
    if "somber" in tags or "dramatic" in tags:
        return "Hold under a serious scene or a slow reveal."
    if "fast" in tags or "bright" in tags:
        return "Drive a short montage or a brisk transition."
    if "nocturnal" in tags or "gentle" in tags or "tender" in tags:
        return "Bed a quiet scene or a soft voiceover."
    if "playful" in tags:
        return "Lighten a playful cut."
    if "ceremonial" in tags or "march" in tags:
        return "Mark an entrance or a title card."
    if "contrapuntal" in tags:
        return "Underscore a focused explanation with the opening bars."
    return "Underscore a short scene with the opening bars."


def quality_penalty(canon: str, title: str, movement: str, instrumentation: str) -> int:
    title_l = fold(f"{title} {movement}")
    inst = fold(instrumentation)
    penalty = 0
    if "guitar" in inst and canon not in GUITAR_ORIGINALS:
        penalty += 4
    study = bool(re.search(r"\b(exercise|lesson|study|etude|finger)\b", title_l))
    if study and canon not in {"frederic chopin", "franz liszt", "claude debussy", "alexander scriabin", "charles valentin alkan"}:
        penalty += 5
    if re.search(r"arrang|transcri", title_l):
        penalty += 2
    if SPAM_RE.search(title_l):
        penalty += 20
    return penalty


def blank_candidate() -> dict:
    row = {column: "" for column in CANDIDATE_COLUMNS}
    row["added_by"] = "grok"
    row["genre"] = "classical"
    row["verified"] = "yes"
    row["source_rank"] = "10"
    row["quality_penalty"] = "0"
    return row
