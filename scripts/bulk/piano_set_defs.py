"""Complete-set definitions for the top piano repertoire + a tolerant movement matcher.

Each set: (name, composer substring, [catalogue regexes], scope, [(label, number, [alias regexes])]).
A movement matches an item (hay = folded "title | movement | catalog") when the composer matches and either
  * one of the set catalogue regexes matches and the movement number follows it ("Op. 90 No. 2", "op90no2",
    "D.899/2", "D 899 Nr. 2"), or a set alias word (e.g. "impromptu") plus the number appears with a catalogue hit; or
  * an alias regex for the movement matches (titles without numbers: "Träumerei", "Impromptu in c-moll",
    "Moments musicaux no. 3", month names, Debussy prelude titles).
Alternate catalogue systems are aliases of the same set (Schubert D.899 = Op.90, D.935 = Op.142, D.780 = Op.94).
"""
from __future__ import annotations
import re, unicodedata

def fold(s): return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
def hay(it): return fold(" | ".join(str(it.get(k) or "") for k in ("title", "movement", "catalog")))

def op(n): return rf"\bop(?:us)?\.? ?{n}(?![0-9])"
def cat(prefix, n): return rf"\b{prefix}\.? ?{n}(?![0-9])"
NUMW = {1: "one|first|i", 2: "two|second|ii", 3: "three|third|iii"}
SCH = "robert schumann"

def num_rx(cats, n):
    c = "(?:" + "|".join(cats) + ")"
    # catalogue then number: "op. 10 no. 3", "op10no03", "op.10/3", "op 10, nr 3", "op. 10 - 3"
    return rf"{c}[^|]{{0,25}}?(?:\bno?s?\.? ?0?{n}\b|\bnr\.? ?0?{n}\b|n\.? ?o?\.? ?0?{n}\b|/ ?0?{n}\b|[,\- ] ?0?{n}\b(?![.,]\d))|\bno\.? ?0?{n}\b[^|]{{0,30}}?{c}"

def mv(labels_aliases, start=1, numbered=True):
    return [(lab, i if numbered else 0, al) for i, (lab, al) in enumerate(labels_aliases, start)]

def numbered(n, aliases=None, label="No. {i}"):
    aliases = aliases or {}
    return [(label.format(i=i), i, aliases.get(i, [])) for i in range(1, n + 1)]

SETS = [
 # ---- Chopin
 ("Chopin Études Op.10", "chopin", [op(10)], "PD", numbered(12, {3: [r"tristesse"], 5: [r"black key"], 12: [r"revolution"]})),
 ("Chopin Études Op.25", "chopin", [op(25)], "PD", numbered(12, {1: [r"aeolian harp"], 9: [r"butterfl"], 11: [r"winter wind"], 12: [r"ocean"]})),
 ("Chopin Préludes Op.28", "chopin", [op(28)], "PD", numbered(24, {15: [r"raindrop"]})),
 ("Chopin 4 Ballades", "chopin", [r"ballad"], "PD", [("No. 1 Op.23", 1, [op(23)]), ("No. 2 Op.38", 2, [op(38)]), ("No. 3 Op.47", 3, [op(47)]), ("No. 4 Op.52", 4, [op(52)])]),
 ("Chopin 4 Scherzi", "chopin", [r"scherz"], "PD", [("No. 1 Op.20", 1, [op(20)]), ("No. 2 Op.31", 2, [op(31)]), ("No. 3 Op.39", 3, [op(39)]), ("No. 4 Op.54", 4, [op(54)])]),
 ("Chopin Nocturnes Op.9", "chopin", [op(9)], "PD", numbered(3)),
 ("Chopin Nocturnes Op.15", "chopin", [op(15)], "PD", numbered(3)),
 ("Chopin Nocturnes Op.27", "chopin", [op(27)], "PD", numbered(2)),
 ("Chopin Nocturnes Op.32", "chopin", [op(32)], "PD", numbered(2)),
 ("Chopin Nocturnes Op.48", "chopin", [op(48)], "PD", numbered(2)),
 ("Chopin Nocturnes Op.55", "chopin", [op(55)], "PD", numbered(2)),
 ("Chopin Nocturnes Op.62", "chopin", [op(62)], "PD", numbered(2)),
 ("Chopin Nocturne C# minor (posth.) B.49", "chopin", [r"\bb\.? ?49\b|kk\.? ?iva ?/? ?16|lento con gran"], "PD", [("Lento con gran espressione", 0, [r"\bb\.? ?49\b|lento con gran|nocturne[^|]*(?:c ?(?:#|sharp)|cis)[^|]*(?:minor|moll)[^|]*posth|nocturne no\.? ?20"])]),
 ("Chopin Waltzes Op.18", "chopin", [op(18)], "PD", [("Grande valse brillante", 1, [r"grande valse brillante[^|]*(e.flat|es|op\.? ?18)"])]),
 ("Chopin Waltzes Op.34", "chopin", [op(34)], "PD", numbered(3)),
 ("Chopin Waltzes Op.42", "chopin", [op(42)], "PD", [("Waltz in A-flat", 1, [op(42)])]),
 ("Chopin Waltzes Op.64", "chopin", [op(64)], "PD", numbered(3, {1: [r"minute waltz|valse du petit chien"]})),
 ("Chopin Waltzes Op.69", "chopin", [op(69)], "PD", numbered(2, {1: [r"farewell waltz|l'adieu|valse de l.adieu"]})),
 ("Chopin Waltzes Op.70", "chopin", [op(70)], "PD", numbered(3)),
 # ---- Schubert (D and Op. aliases; key aliases for D.899)
 ("Schubert Impromptus D.899 (Op.90)", "schubert", [cat("d", 899), op(90)], "PD", numbered(4, {
     1: [r"impromptu[^|]*\bc[ -]?(minor|moll)"], 2: [r"impromptu[^|]*\be[ -]?(flat|b|s)[ -]?(major|dur)|impromptu[^|]*\bes[ -]dur"],
     3: [r"impromptu[^|]*\bg[ -]?(flat|b)[ -]?(major|dur)|impromptu[^|]*\bges[ -]dur"], 4: [r"impromptu[^|]*\ba[ -]?(flat|b)[ -]?(minor|major|dur)|impromptu[^|]*\bas[ -]dur"]})),
 ("Schubert Impromptus D.935 (Op.142)", "schubert", [cat("d", 935), op(142)], "PD", numbered(4, {3: [r"rosamunde[^|]*impromptu|impromptu[^|]*b[ -]?(flat|b)[ -]?(major|dur)"]})),
 ("Schubert Moments musicaux D.780 (Op.94)", "schubert", [cat("d", 780), op(94), r"moments? musica"], "PD", numbered(6)),
 # ---- Mendelssohn
 ("Mendelssohn Songs without Words Op.19b", "mendelssohn", [op(19)], "PD", numbered(6, {1: [r"sweet remembrance|suss(e|er) erinnerung"]})),
 ("Mendelssohn Songs without Words Op.30", "mendelssohn", [op(30)], "PD", numbered(6)),
 ("Mendelssohn Songs without Words Op.62", "mendelssohn", [op(62)], "PD", numbered(6, {6: [r"spring song|fruhlingslied[^|]*(62|lied ohne|songs without)"]})),
 ("Mendelssohn Songs without Words Op.67", "mendelssohn", [op(67)], "PD", numbered(6, {4: [r"spinn(ing|erlied)"]})),
 ("Mendelssohn Songs without Words Op.38", "mendelssohn", [op(38)], "PD", numbered(6)),
 ("Mendelssohn Songs without Words Op.53", "mendelssohn", [op(53), r"\bs\.? ?53(?![0-9])"], "PD", numbered(6)),
 ("Mendelssohn Songs without Words Op.85", "mendelssohn", [op(85)], "PD", numbered(6)),
 ("Mendelssohn Songs without Words Op.102", "mendelssohn", [op(102), r"\bs\.? ?102(?![0-9])"], "PD", numbered(3)),
 ("Mendelssohn String Quartets Op.12-80", "mendelssohn", [op(12), op(13), op(44), op(80)], "PD", [
     ("Quartet No. 1 Op.12", 0, [op(12)]), ("Quartet No. 2 Op.13", 0, [op(13)]),
     ("Quartet No. 3 Op.44/1", 0, [r"\bop\.? ?44[^|]{0,8}?(?:no\.? ?)?1(?![0-9])"]),
     ("Quartet No. 4 Op.44/2", 0, [r"\bop\.? ?44[^|]{0,8}?(?:no\.? ?)?2(?![0-9])"]),
     ("Quartet No. 5 Op.44/3", 0, [r"\bop\.? ?44[^|]{0,8}?(?:no\.? ?)?3(?![0-9])"]),
     ("Quartet No. 6 Op.80", 0, [op(80)])]),
 ("Mendelssohn Piano Trios Op.49 & Op.66", "mendelssohn", [op(49), op(66)], "PD", [
     ("Piano Trio No. 1 Op.49", 0, [op(49)]), ("Piano Trio No. 2 Op.66", 0, [op(66)])]),
 ("Mendelssohn Variations sérieuses Op.54", "mendelssohn", [op(54), r"s[eé]rieuses|serieuses"], "PD", [
     ("Complete (17 variations)", 0, [r"variations? s[eé]rieuses|serieuses|op\.? ?54"])]),
 ("Mendelssohn 6 Duets Op.63", "mendelssohn", [op(63)], "PD", [
     ("No. 1 Ich wollt'", 0, [r"op\.? ?63[^|]*ich wollt"]), ("No. 2 Abschiedslied der Zugvögel", 0, [r"op\.? ?63[^|]*abschiedslied"]),
     ("No. 3 Gruss", 0, [r"op\.? ?63[^|]*\bgruss"]), ("No. 4 Herbstlied", 0, [r"op\.? ?63[^|]*herbstlied"]),
     ("No. 5 Volkslied", 0, [r"op\.? ?63[^|]*volkslied"]), ("No. 6 Maiglöckchen", 0, [r"op\.? ?63[^|]*maiglock"])]),
 ("Mendelssohn 6 Gesänge Op.86", "mendelssohn", [op(86)], "PD", [
     ("No. 1 Das Fenster", 0, [r"op\.? ?86[^|]*fenster"]), ("No. 2 Morgenlied", 0, [r"op\.? ?86[^|]*morgenlied"]),
     ("No. 3 Die Liebende schreibt", 0, [r"op\.? ?86[^|]*liebende"]), ("No. 4 Allnächtlich im Traume", 0, [r"op\.? ?86[^|]*allnachtlich"]),
     ("No. 5 Der Mond", 0, [r"op\.? ?86[^|]*\bmond"]), ("No. 6 Altdeutsches Frühlingslied", 0, [r"op\.? ?86[^|]*altdeutsches"])]),
 # ---- Schumann (Robert only: composer must contain "robert schumann", so Clara Schumann's songs never count)
 ("Schumann Kinderszenen Op.15", SCH, [op(15), r"kindersz|kindersc"], "PD", mv([
     ("1 Von fremden Ländern", [r"fremden landern|foreign lands"]), ("2 Kuriose Geschichte", [r"c(u|k)riose geschichte|curious story"]),
     ("3 Hasche-Mann", [r"hasche.?mann|blind man"]), ("4 Bittendes Kind", [r"bittendes kind|pleading child"]),
     ("5 Glückes genug", [r"gluckes genug|happy enough"]), ("6 Wichtige Begebenheit", [r"wichtige begebenheit|important event"]),
     ("7 Träumerei", [r"traumerei|reverie"]), ("8 Am Kamin", [r"am kamin|by the fireside|fireside"]),
     ("9 Ritter vom Steckenpferde", [r"steckenpferd|hobby.?horse"]), ("10 Fast zu ernst", [r"fast zu ernst|almost too serious"]),
     ("11 Fürchtenmachen", [r"furchtenmachen|frightening"]), ("12 Kind im Einschlummern", [r"einschlummern|falling asleep"]),
     ("13 Der Dichter spricht", [r"dichter spricht|poet speaks"])])),
 ("Schumann Kreisleriana Op.16", SCH, [op(16), r"kreisleriana"], "PD", numbered(8)),
 ("Schumann Davidsbündlertänze Op.6", SCH, [op(6), r"davidsb"], "PD", numbered(18)),
 ("Schumann Waldszenen Op.82", SCH, [op(82), r"waldszen"], "PD", numbered(9, {
     1: [r"eintritt"], 2: [r"jager auf der lauer|hunters? on the lookout"], 3: [r"einsame blumen|lonely flowers"],
     4: [r"verrufene stelle|haunted place"], 5: [r"freundliche landschaft|friendly landscape"], 6: [r"herberge|wayside inn"],
     7: [r"vogel als prophet|bird as prophet"], 8: [r"jagdlied|hunting song"], 9: [r"abschied|farewell"]})),
 ("Schumann Novelletten Op.21", SCH, [op(21), r"novellet"], "PD", numbered(8)),
 ("Schumann Fantasiestücke Op.12", SCH, [op(12), r"fantasiest"], "PD", numbered(8, {
     1: [r"des abends|of evening"], 2: [r"aufschwung|soaring"], 3: [r"warum|why\b"], 4: [r"grillen|whims"],
     5: [r"in der nacht|in the night"], 6: [r"fabel|fable"], 7: [r"traumes wirren|dream confusion"], 8: [r"ende vom lied|end of the song"]})),
 ("Schumann Papillons Op.2", SCH, [op(2), r"papillon"], "PD", numbered(12)),
 ("Schumann Bunte Blätter Op.99", SCH, [op(99), r"bunte bl"], "PD", numbered(14)),
 ("Schumann Nachtstücke Op.23", SCH, [op(23), r"nachtst"], "PD", numbered(4)),
 ("Schumann Arabeske Op.18", SCH, [op(18), r"arabe"], "PD", numbered(1, {1: [r"arabe"]})),
 ("Schumann Carnaval Op.9 (Sphinxes not counted)", SCH, [op(9), r"carnaval"], "PD", numbered(21, {
     1: [r"carnaval[^|]*preambule"], 2: [r"carnaval[^|]*pierrot"], 3: [r"carnaval[^|]*arlequin"], 4: [r"carnaval[^|]*valse noble"],
     5: [r"carnaval[^|]*eusebius"], 6: [r"carnaval[^|]*florestan"], 7: [r"carnaval[^|]*coquette"], 8: [r"carnaval[^|]*replique"],
     9: [r"carnaval[^|]*papillons"], 10: [r"carnaval[^|]*(lettres dansantes|asch)"], 11: [r"carnaval[^|]*chiarina"],
     12: [r"carnaval[^|]*chopin"], 13: [r"carnaval[^|]*estrella"], 14: [r"carnaval[^|]*reconnaissance"],
     15: [r"carnaval[^|]*pantalon"], 16: [r"carnaval[^|]*valse allemande"], 17: [r"carnaval[^|]*paganini"],
     18: [r"carnaval[^|]*aveu"], 19: [r"carnaval[^|]*promenade"], 20: [r"carnaval[^|]*pause"],
     21: [r"carnaval[^|]*(philistins|philistines)"]})),
 ("Schumann Album für die Jugend Op.68", SCH, [op(68), r"album[^|]*(?:jugend|young)"], "PD", numbered(43, {35: [r"mignon"]})),
 ("Schumann Albumblätter Op.124", SCH, [op(124), r"albumbl"], "PD", numbered(20)),
 ("Schumann Fantasie Op.17", SCH, [op(17), r"fantasie\b"], "PD", numbered(3)),
 ("Schumann Faschingsschwank aus Wien Op.26", SCH, [op(26), r"faschingssch"], "PD", numbered(5)),
 ("Schumann Symphonic Études Op.13 (12 études)", SCH, [op(13), r"symphonic|sinfonische"], "PD", numbered(12, label="Étude {i}")),
 ("Schumann Abegg Variations Op.1", SCH, [op(1), r"abegg"], "PD", numbered(1, {1: [r"abegg"]})),
 ("Schumann Toccata Op.7", SCH, [op(7), r"toccata"], "PD", numbered(1, {1: [r"toccata"]})),
 # ---- Brahms
 ("Brahms Fantasien Op.116", "brahms", [op(116)], "PD", numbered(7)),
 ("Brahms Intermezzi Op.117", "brahms", [op(117)], "PD", numbered(3)),
 ("Brahms Klavierstücke Op.118", "brahms", [op(118)], "PD", numbered(6)),
 ("Brahms Klavierstücke Op.119", "brahms", [op(119)], "PD", numbered(4)),
 # ---- Tchaikovsky / Grieg
 ("Tchaikovsky The Seasons Op.37a", "tchaikovsky", [op("37a?"), r"seasons|saisons|vremena"], "PD",
  mv([(m, [rf"(seasons|saisons|op\.? ?37)[^|]*{m.lower()}|{m.lower()}[^|]*(seasons|saisons|op\.? ?37)"]) for m in
      "January February March April May June July August September October November December".split()])),
 ("Grieg Lyric Pieces Op.12", "grieg", [op(12)], "PD", mv([("1 Arietta", [r"arietta"]), ("2 Waltz", []), ("3 Watchman's Song", [r"watchman|vaegtersang|vektersang"]),
     ("4 Elfin Dance", [r"elfin dance|alfedans|elvedans|fairy dance"]), ("5 Folk Melody", [r"folkevise|folk ?(melody|song)"]), ("6 Norwegian", [r"norsk|norwegian (melody|dance)?$"]),
     ("7 Album Leaf", [r"albumblad|album leaf"]), ("8 National Song", [r"fadrelandssang|national song"])])),
 ("Grieg Lyric Pieces Op.43", "grieg", [op(43)], "PD", mv([("1 Butterfly", [r"sommerfugl|butterfly|papillon"]), ("2 Solitary Traveller", [r"ensom vandrer|solitary"]), ("3 In My Native Country", [r"i hjemmet|native country|homeland"]),
     ("4 Little Bird", [r"smafugl|little bird"]), ("5 Erotikon", [r"erotik"]), ("6 To the Spring", [r"til varen|to (the )?spring"])])),
 ("Grieg Lyric Pieces Op.65", "grieg", [op(65)], "PD", numbered(6, {6: [r"wedding day|bryllupsdag|troldhaugen"]})),
 # ---- Bach
 ("Bach WTC Book I BWV 846-869", "bach", [r"bwv"], "PD", [(f"BWV {b}", b, [rf"bwv\.? ?{b}(?![0-9])"]) for b in range(846, 870)]),
 ("Bach WTC Book II BWV 870-893", "bach", [r"bwv"], "PD", [(f"BWV {b}", b, [rf"bwv\.? ?{b}(?![0-9])"]) for b in range(870, 894)]),
 # ---- Beethoven 32 sonatas (a sonata counts when any movement or the whole sonata is present)
 ("Beethoven 32 Piano Sonatas", "beethoven", [r"sonat|op"], "PD", [(f"No. {i} Op.{o}", i, [rf"\bop\.? ?{o.split('/')[0]}(?![0-9a-z])" + (rf"[^|]{{0,20}}?(no\.? ?{o.split('/')[1]}\b|/ ?{o.split('/')[1]}\b|n\.? ?{o.split('/')[1]}\b)" if "/" in o else "")])
   for i, o in enumerate("2/1 2/2 2/3 7 10/1 10/2 10/3 13 14/1 14/2 22 26 27/1 27/2 28 31/1 31/2 31/3 49/1 49/2 53 54 57 78 79 81a 90 101 106 109 110 111".split(), 1)]),
 # ---- Liszt
 ("Liszt Consolations S.172", "liszt", [r"consolation", cat("s", 172)], "PD", numbered(6)),
 ("Liszt Liebesträume S.541", "liszt", [r"liebestr", cat("s", 541)], "PD", numbered(3)),
 ("Liszt Paganini Études S.141", "liszt", [cat("s", 141), r"paganini"], "PD", numbered(6, {3: [r"campanella"]})),
 ("Liszt Hungarian Rhapsodies S.244 (1-19)", "liszt", [r"hungarian rhaps|rhapsodie hongroise|ungarische rhaps", cat("s", 244)], "PD", numbered(19)),
 # ---- Debussy / Satie / Scriabin / Rachmaninoff
 ("Debussy Children's Corner L.113", "debussy", [r"children"], "PD", mv([("1 Doctor Gradus", [r"gradus"]), ("2 Jimbo's Lullaby", [r"jimbo"]), ("3 Serenade for the Doll", [r"serenade (for|of) the doll|la poupee"]), ("4 The Snow Is Dancing", [r"snow is dancing|neige danse"]), ("5 The Little Shepherd", [r"little shepherd|petit berger"]), ("6 Golliwogg's Cakewalk", [r"golliwog"])])),
 ("Debussy Suite bergamasque L.75", "debussy", [r"bergamasque"], "PD", mv([("Prélude", [r"bergamasque[^|]*prelude|prelude[^|]*bergamasque"]), ("Menuet", [r"menuet"]), ("Clair de lune", [r"clair de lune"]), ("Passepied", [r"passepied"])])),
 ("Debussy Estampes L.100", "debussy", [r"estampes"], "PD", mv([("Pagodes", [r"pagodes"]), ("La soirée dans Grenade", [r"soiree dans grenade"]), ("Jardins sous la pluie", [r"jardins sous la pluie"])])),
 ("Debussy Préludes Book I L.117", "debussy", [r"prelude"], "PD", mv([(t, [t]) for t in ["danseuses de delphes", "voiles", "le vent dans la plaine", "les sons et les parfums", "collines d.anacapri", "des pas sur la neige", "ce qu.a vu le vent", "fille aux cheveux de lin", "serenade interrompue", "cathedrale engloutie", "danse de puck", "minstrels"]], numbered=False)),
 ("Debussy Préludes Book II L.123", "debussy", [r"prelude"], "PD", mv([(t, [t]) for t in ["brouillards", "feuilles mortes", "puerta del vino", "fees sont d.exquises", "bruyeres", "general lavine", "terrasse des audiences", "ondine", "pickwick", "canope", "tierces alternees", "feux d.artifice"]], numbered=False)),
 ("Satie Gymnopédies", "satie", [r"gymnop"], "PD", numbered(3)),
 ("Satie Gnossiennes 1-6", "satie", [r"gnoss"], "PD", numbered(6)),
 ("Satie 3 Sarabandes", "satie", [r"saraband"], "PD", numbered(3)),
 ("Scriabin 2 Poèmes Op.32", "scriabin", [op(32)], "PD", numbered(2)),
 ("Scriabin 12 Études Op.8", "scriabin", [op(8)], "PD", numbered(12)),
 ("Ravel Valses nobles et sentimentales M.61", "ravel", [r"valses nobles"], "US-PD-only", numbered(8, label="Valse {i}")),
 ("Ravel Le Tombeau de Couperin M.68", "ravel", [r"tombeau"], "US-PD-only", mv([(t, [t]) for t in ["prelude", "fugue", "forlane", "rigaudon", "menuet", "toccata"]])),
 ("Rachmaninoff Preludes Op.23", "rachmaninoff", [op(23)], "US-PD-only", numbered(10, {
     1: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*f[ -]?sharp minor"], 2: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*\bb minor"], 3: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*\bd minor"], 4: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*\bd major"],
     5: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*\bg minor"], 6: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*\be minor"], 7: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*\bc minor"], 8: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*a[ -]?flat major"],
     9: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*e[ -]?flat major"], 10: [r"(?=.*\bop(?:us)?\.? ?23(?![0-9]))prelude[^|]*g[ -]?flat major"]})),
 ("Rachmaninoff Preludes Op.32", "rachmaninoff", [op(32)], "US-PD-only", numbered(13, {4: [r"(?=.*\bop(?:us)?\.? ?32(?![0-9]))prelude[^|]*\be minor"]})),
 ("Rachmaninoff Moments musicaux Op.16", "rachmaninoff", [op(16), r"moment(s)? musica"], "US-PD-only", numbered(6, {
     1: [r"(?=.*\bop(?:us)?\.? ?16(?![0-9]))moment[^|]*\bb[ -]?flat minor|moment[^|]*\bbb minor"], 2: [r"(?=.*\bop(?:us)?\.? ?16(?![0-9]))moment[^|]*e[ -]?flat minor|moment[^|]*\bes minor|moment[^|]*\beb minor"],
     3: [r"(?=.*\bop(?:us)?\.? ?16(?![0-9]))moment[^|]*\bb minor"], 4: [r"(?=.*\bop(?:us)?\.? ?16(?![0-9]))moment[^|]*\be minor"], 5: [r"(?=.*\bop(?:us)?\.? ?16(?![0-9]))moment[^|]*d[ -]?flat major|moment[^|]*\bdb major"], 6: [r"(?=.*\bop(?:us)?\.? ?16(?![0-9]))moment[^|]*\bc major"]})),
 ("Rachmaninoff Études-tableaux Op.33", "rachmaninoff", [op(33)], "US-PD-only", numbered(9, {i: [rf"(?=.*{op(33)})[^|]*\bno\.? ?0?{i}\b"] for i in range(1, 10)})),
 ("Rachmaninoff Études-tableaux Op.39", "rachmaninoff", [op(39)], "US-PD-only", numbered(9, {i: [rf"(?=.*{op(39)})[^|]*\bno\.? ?0?{i}\b"] for i in range(1, 10)} | {1: [rf"(?=.*{op(39)})[^|]*c minor"]})),
 ("Rachmaninoff Piano Concerto No. 2 Op.18", "rachmaninoff", [op(18)], "US-PD-only", [
     ("I Moderato", 1, [rf"(?=.*{op(18)})[^|]*moderato"]), ("II Adagio sostenuto", 2, [rf"(?=.*{op(18)})[^|]*adagio sostenuto"]),
     ("III Allegro scherzando", 3, [rf"(?=.*{op(18)})[^|]*allegro scherzando"])]),
 ("Rachmaninoff Piano Concerto No. 3 Op.30", "rachmaninoff", [op(30)], "US-PD-only", [
     ("I Allegro ma non tanto", 1, [rf"(?=.*{op(30)})[^|]*allegro ma non tanto|(?=.*{op(30)})[^|]*(1st|first) movement"]), ("II Intermezzo: Adagio", 2, [rf"(?=.*{op(30)})[^|]*intermezzo"]),
     ("III Alla breve", 3, [rf"(?=.*{op(30)})[^|]*alla breve"])]),
 ("Rachmaninoff Symphony No. 2 Op.27", "rachmaninoff", [op(27)], "US-PD-only", [
     ("I Largo", 1, [rf"(?=.*{op(27)})[^|]*largo"]), ("II Allegro molto", 2, [rf"(?=.*{op(27)})[^|]*allegro molto"]),
     ("III Adagio", 3, [rf"(?=.*{op(27)})[^|]*adagio"]), ("IV Allegro vivace", 4, [rf"(?=.*{op(27)})[^|]*allegro vivace"])]),
 ("Rachmaninoff Cello Sonata Op.19", "rachmaninoff", [op(19), r"cello sonata"], "US-PD-only", [
     ("I Lento - Allegro moderato", 1, [rf"(?=.*{op(19)})[^|]*lento"]), ("II Allegro scherzando", 2, [rf"(?=.*{op(19)})[^|]*scherzando"]),
     ("III Andante - Allegro mosso", 3, [rf"(?=.*{op(19)})[^|]*andante"])]),
 # ---- Rimsky-Korsakov (d.1908; orchestral works, per-movement piano/score files only where they exist)
 ("Rimsky-Korsakov Scheherazade Op.35", "rimsky", [op(35)], "PD", mv([
     ("I The Sea and Sinbad's Ship", [r"sea and sinbad|sinbad.s ship|part i(?![iv])"]), ("II The Kalendar Prince", [r"kalendar|kalandar"]),
     ("III The Young Prince and the Princess", [r"young prince|princess"]), ("IV Festival at Baghdad", [r"baghdad"])])),
 # III has no alias yet: its title/order is not verified against a score, so it only matches by "Op. 34 No. 3"
 ("Rimsky-Korsakov Capriccio espagnol Op.34", "rimsky", [op(34)], "PD", mv([
     ("I Alborada", [r"alborada"]), ("II Variazioni", [r"variazioni|variations"]), ("III", []),
     ("IV Scena e canto gitano", [r"scena e canto|canto gitano|gitano"]), ("V Fandango asturiano", [r"fandango"])])),
 # ---- Richard Strauss (US-PD-only: works published <= 1930; composer match is "richard strauss", not Johann)
 ("Richard Strauss 4 Lieder Op.27", "richard strauss", [op(27)], "US-PD-only", numbered(4, {1: [r"ruhe,? meine seele"], 2: [r"cacilie"], 3: [r"heimliche aufforderung"], 4: [r"morgen"]})),
 ("Richard Strauss Acht Gedichte Op.10", "richard strauss", [op(10)], "US-PD-only", mv([("1 Zueignung", [r"zueignung"]), ("2 Nichts", [r"\bnichts\b"]), ("3 Die Nacht", [r"die nacht"]),
     ("4 Die Georgine", [r"georgine"]), ("5 Geduld", [r"\bgeduld\b"]), ("6 Die Verschwiegenen", [r"verschwiegen"]), ("7 Die Zeitlose", [r"zeitlose"]), ("8 Allerseelen", [r"allerseelen"])])),
 # ---- Vivaldi (d. 1741, fully PD). Concerto-level cycles; movement labels are aliases, not split files.
 ("Vivaldi Four Seasons Op.8 Nos.1-4", "vivaldi", [r"four seasons|quattro stagioni|rv ?(269|315|293|297)\b|op\.? ?8 ?no\.? ?[1-4]\b"], "PD", [
     ("1 Spring (RV 269)", 0, [r"\brv ?269\b|\bop\.? ?8 ?no\.? ?1\b|\bprimavera\b|\bspring\b"]),
     ("2 Summer (RV 315)", 0, [r"\brv ?315\b|\bop\.? ?8 ?no\.? ?2\b|\bl.?estate\b|\bsummer\b|\bsommer\b"]),
     ("3 Autumn (RV 293)", 0, [r"\brv ?293\b|\bop\.? ?8 ?no\.? ?3\b|\bl.?autunno\b|\bautumn\b|\bautomne\b|\bautumno\b"]),
     ("4 Winter (RV 297)", 0, [r"\brv ?297\b|\bop\.? ?8 ?no\.? ?4\b|\bl.?inverno\b|\bl.?hiver\b|\bwinter\b|\binverno\b"])]),
 ("Vivaldi L'estro armonico Op.3", "vivaldi", [op(3), r"estro"], "PD", numbered(12, label="Concerto Op.3 No. {i}")),
 ("Vivaldi La stravaganza Op.4", "vivaldi", [op(4), r"stravaganza"], "PD", numbered(12, label="Concerto Op.4 No. {i}")),
 ("Vivaldi Il cimento Op.8", "vivaldi", [op(8)], "PD", numbered(12, label="Concerto Op.8 No. {i}")),
 ("Vivaldi Gloria RV 589", "vivaldi", [r"\bgloria\b|rv ?589"], "PD", [(lab, 0, [al]) for lab, al in [
     ("I Gloria in excelsis Deo", r"gloria in excelsis"), ("II Et in terra pax", r"et in terra pax|in terra pax"),
     ("III Laudamus te", r"laudamus te"), ("IV Gratias agimus tibi", r"gratias agimus"),
     ("V Propter magnam gloriam", r"propter magnam"), ("VI Domine Deus", r"domine deus(?![^|]*agnus)"),
     ("VII Domine Fili unigenite", r"domine fili"), ("VIII Domine Deus, Agnus Dei", r"agnus dei"),
     ("IX Qui tollis", r"qui tollis"), ("X Qui sedes", r"qui sedes"), ("XI Quoniam tu solus", r"quoniam tu solus"),
     ("XII Cum Sancto Spiritu", r"cum sancto spiritu")]]),
 ("Vivaldi Magnificat RV 611", "vivaldi", [r"magnificat|rv ?61[01]\b"], "PD", [(lab, 0, [al]) for lab, al in [
     ("1 Magnificat anima mea", r"magnificat anima"), ("2 Et exultavit", r"et exultavit"), ("3 Quia respexit", r"quia respexit"),
     ("4 Quia fecit", r"quia fecit"), ("5 Et misericordia", r"et misericordia"), ("6 Fecit potentiam", r"fecit potentiam"),
     ("7 Deposuit", r"deposuit"), ("8 Esurientes", r"esurientes"), ("9 Suscepit Israel", r"suscepit israel"),
     ("10 Sicut locutus est", r"sicut locutus"), ("11 Gloria Patri", r"gloria patri"), ("12 Sicut erat", r"sicut erat")]]),
# ---- Mussorgsky (Pictures at an Exhibition, 1874: ten numbered pictures; Promenades are interludes and not counted)
 ("Mussorgsky Pictures at an Exhibition (1874)", "mussorgsky", [r"pictures at an exhibition|tableaux d.une exposition|bilder einer ausstellung|exposition"], "PD", mv([
     ("1 Gnomus", [r"gnomus|gnome"]), ("2 Il vecchio castello", [r"vecchio castello|old castle|alte schloss|castello"]),
     ("3 Tuileries", [r"tuileries|tuilerie"]), ("4 Bydło", [r"bydlo|bydło|ox.?cart|oxcart"]),
     ("5 Ballet of the Unhatched Chicks", [r"ballet des poussins|unhatched|ballet of the chicks|chicks"]),
     ("6 Samuel Goldenberg und Schmuÿle", [r"goldenberg|schmuyle|schmuy|two jews|goldberg"]),
     ("7 Limoges", [r"limoges"]), ("8 Catacombae", [r"catacomb|sepulcrum|con mortuis|cum mortuis|lingua mortua"]),
     ("9 Baba Yaga (La cabane sur des pattes de poule)", [r"baba.?yaga|cabane|hut on fowl|fowl.?s legs|pattes de poule|baba(?![a-z])"]),
     ("10 The Great Gate of Kiev", [r"great gate|grande porte|kiev|kyiv"])])),
]

# extra guards: an item must match REQUIRE[set] to count; WHOLE[set] = a single file holding every movement
REQUIRE = {"Beethoven 32 Piano Sonatas": r"sonat|pathetique|moonlight|mondschein|appassionata|waldstein|tempest|sturm|hammerklavier|adieux|pastoral|aurora|hunt",
           "Ravel Le Tombeau de Couperin M.68": r"tombeau", "Debussy Préludes Book I L.117": r"prelude|l\.? ?117|l\.? ?125",
           "Debussy Préludes Book II L.123": r"prelude|l\.? ?123|l\.? ?131"}
# per-set exclusions (voice parts of a single movement; arrangements of a concerto) applied on top of EXCLUDE
EXTRA_EXCLUDE = {"Vivaldi Gloria RV 589": r"\b(soprano|alto|tenor|bass|basso|canto)\b",
                 "Vivaldi Magnificat RV 611": r"\b(soprano|alto|tenor|bass|basso|canto)\b|\bmagnificat\b(?![^|]*anima)",
                 "Vivaldi Four Seasons Op.8 Nos.1-4": r"clarinet|guitar|celtic|brass|quintet|lute|flute|harp|organ|mandolin|piano|simple|didattica|duo|cello|oboe|mission|puddle|designing|lago|february|angeli|sonata|trio|vocal|mix"}
EXCLUDE = r"\b(violin|cello|horn|flute|clarinet) sonata|\bfor (clarinet|flute|violin|cello|orchestra|band|guitar|organ|string|wind|brass)|\barr\.|arranged|arrangement|transcri|\beasy\b|simplified"
WHOLE = {"Ravel Le Tombeau de Couperin M.68": r"^le tombeau de couperin \| +\|"}
# Robert Schumann sets: an item must carry the set's own opus/title word (a title alias alone is not enough),
# so a same-named song or Clara Schumann's opus numbers cannot count
for _s in SETS:
    if _s[1] == SCH: REQUIRE.setdefault(_s[0], "|".join(_s[2]))
SET_WORDS = {"chopin": r"etude|prelude|nocturne|valse|waltz|ballad|scherz", "schubert": r"impromptu|moment", "mendelssohn": r"lied|song", "brahms": r"intermezz|capriccio|ballade|romanze|rhapsod|fantasi|klavierst|piece", "scriabin": r"etude|poem|poeme"}

# ---- Mahler (d. 1911: PD worldwide). Titles are folded to ascii (umlauts become plain vowels, ß is dropped) before matching.
# Symphony movements are matched by movement name plus a symphony-number guard (REQUIRE), not by number alone.
def _sym_req(n):
    return rf"symph[a-z]*\.? ?(?:no\.? ?|nr\.? ?|n\.? ?)?0?{n}(?![0-9])|(?<![0-9]){n}(?:st|nd|rd|th) symph" + (r"|\b9 adagio" if n == 9 else "")
MAHLER_SYM = {
 1: [("I Langsam, schleppend", [r"langsam[^|]*schleppend|slow(ly)?,? dragging"]), ("II Kraftig bewegt", [r"kraftig bewegt"]),
     ("III Feierlich und gemessen (Trauermarsch)", [r"feierlich und gemessen|trauermarsch|funeral march"]), ("IV Sturmisch bewegt", [r"sturmisch bewegt|stormy"])],
 2: [("I Allegro maestoso (Todtenfeier)", [r"allegro maestoso|todtenfeier"]), ("II Andante moderato", [r"andante moderato"]),
     ("III In ruhig fliessender Bewegung", [r"ruhig fl\w*ender"]), ("IV Urlicht", [r"urlicht"]), ("V Im Tempo des Scherzo (Auferstehung)", [r"tempo des scherzo|auferstehung|resurrection"])],
 3: [("I Kraftig. Entschieden", [r"entschieden"]), ("II Tempo di Menuetto", [r"menuett|menuet"]), ("III Comodo (Scherzando)", [r"comodo|scherzando"]),
     ("IV Was mir die Liebe erzahlt", [r"was mir die liebe|what love tells"]), ("V Es sungen drei Engel", [r"es sungen drei engel|drei engel|three angels|lustig im tempo"]),
     ("VI Langsam. Ruhevoll", [r"langsam[^|]*ruhevoll(?![^|]*liebe)"])],
 4: [("I Bedachtig, nicht eilen", [r"bedachtig|nicht eilen"]), ("II In gemachlicher Bewegung", [r"gemachlicher bewegung|gemachlich"]),
     ("III Ruhevoll", [r"ruhevoll"]), ("IV Sehr behaglich (Das himmlische Leben)", [r"sehr behaglich|himmlische leben|behaglich"])],
 5: [("I Trauermarsch", [r"trauermarsch|in gemessenem schritt"]), ("II Sturmisch bewegt", [r"sturmisch bewegt|vehemenz"]),
     ("III Scherzo", [r"scherzo"]), ("IV Adagietto", [r"adagietto"]), ("V Rondo-Finale", [r"rondo.?finale"])],
 6: [("I Allegro energico, ma non troppo", [r"allegro energico"]), ("II Scherzo", [r"scherzo"]), ("III Andante moderato", [r"andante moderato"]), ("IV Finale", [r"finale"])],
 7: [("I Langsam - Allegro risoluto", [r"allegro risoluto"]), ("II Nachtmusik I", [r"nachtmusik (?:i|1)(?![i0-9])"]), ("III Scherzo (Schattenhaft)", [r"schattenhaft|scherzo"]),
     ("IV Nachtmusik II", [r"nachtmusik (?:ii|2)(?![0-9])"]), ("V Rondo-Finale", [r"rondo.?finale"])],
 8: [("Teil I Veni creator spiritus", [r"veni creator"]), ("Teil II Faust (Schlussszene)", [r"faust"])],
 9: [("I Andante comodo", [r"andante comodo"]), ("II Im Tempo eines gemachlichen Landlers", [r"landler"]), ("III Rondo-Burleske", [r"rondo.?burles"]), ("IV Adagio", [r"adagio"])],
}
MAHLER_SONGS = [
 ("Mahler Lieder eines fahrenden Gesellen", r"gesellen", [("1 Wenn mein Schatz Hochzeit macht", [r"wenn mein schatz|hochzeit macht"]), ("2 Gieng heut morgen uber's Feld", [r"gieng heut|ging heut"]),
     ("3 Ich hab' ein gluhend Messer", [r"gluhend messer|hab ein gluh"]), ("4 Die zwei blauen Augen", [r"zwei blauen augen|blauen augen"])]),
 ("Mahler Kindertotenlieder", r"kindertotenlied", [("1 Nun will die Sonn' so hell aufgeh'n", [r"sonn so hell|son so hell"]), ("2 Nun seh' ich wohl, warum so dunkle Flammen", [r"dunkle flamm"]),
     ("3 Wenn dein Mutterlein", [r"mutterlein"]), ("4 Oft denk' ich, sie sind nur ausgegangen", [r"oft denk|sind nur ausgegangen"]), ("5 In diesem Wetter", [r"in diesem wetter"])]),
 ("Mahler Ruckert-Lieder", r"ruckert|welt abhanden|blicke mir|um mitternacht|linden duft|liebst du um", [("Ich atmet' einen linden Duft", [r"linden duft"]), ("Blicke mir nicht in die Lieder", [r"blicke mir nicht"]),
     ("Um Mitternacht", [r"um mitternacht"]), ("Ich bin der Welt abhanden gekommen", [r"welt abhanden"]), ("Liebst du um Schonheit", [r"liebst du um sch"])]),
 ("Mahler Lieder aus Des Knaben Wunderhorn", r"wunderhorn|rheinlegend|urlicht|himmlische leben|revelge|tambourg|fischpredigt|trompeten|schildwache|verlorne muh|irdische leben|ablosung|scheiden und meiden|lob des hohen|wiedergeseh|trost im ungluck|wer hat dies", [
     ("Rheinlegendchen", [r"rheinlegend"]), ("Verlorne Muh'", [r"verlorne muh"]), ("Trost im Ungluck", [r"trost im ung"]), ("Wer hat dies Liedlein erdacht?", [r"liedlein erdacht|wer hat dies"]),
     ("Das irdische Leben", [r"irdische leben"]), ("Des Antonius von Padua Fischpredigt", [r"fischpredigt"]), ("Lob des hohen Verstands", [r"hohen verstands|lob des hohen"]),
     ("Der Schildwache Nachtlied", [r"schildwache"]), ("Ablosung im Sommer", [r"ablosung"]), ("Scheiden und Meiden", [r"scheiden und meiden"]), ("Nicht wiedergesehn!", [r"wiedergeseh"]),
     ("Wo die schonen Trompeten blasen", [r"trompeten blasen"]), ("Revelge", [r"revelge"]), ("Der Tambourg'sell", [r"tambourg"]), ("Urlicht", [r"urlicht"]), ("Das himmlische Leben", [r"himmlische leben"])]),
 ("Mahler Das Lied von der Erde", r"lied von der erde|song of the earth|lied der erde", [("I Das Trinklied vom Jammer der Erde", [r"trinklied|drinking song"]), ("II Der Einsame im Herbst", [r"einsame im herbst|lonely (one|man) in autumn"]),
     ("III Von der Jugend", [r"von der jugend|youth"]), ("IV Von der Schonheit", [r"von der sch.nheit|beauty"]), ("V Der Trunkene im Fruhling", [r"trunkene im fr|drunken"]), ("VI Der Abschied", [r"abschied|farewell"])]),
]
for _n, _mv in MAHLER_SYM.items():
    _name = f"Mahler Symphony No. {_n}"
    SETS.append((_name, "mahler", [r"symph"], "PD", mv(_mv, numbered=False)))
    REQUIRE[_name] = _sym_req(_n)
for _name, _req, _mv in MAHLER_SONGS:
    SETS.append((_name, "mahler", [r"\."], "PD", mv(_mv, numbered=False)))
    REQUIRE[_name] = _req
def _num_ok(lab, n, cats, h):
    if n and re.search(num_rx(cats, n), h): return True
    return False

def match_set(items, s):
    """-> (have labels, missing labels, {label: [ids]})"""
    name, comp, cats, scope, mvts = s
    pool = [(it.get("id"), hay(it)) for it in items if comp in fold(it.get("composer"))
            and not re.search(r"voice|vocal|lieder", fold(f"{it.get('instrumentation') or ''} {it.get('source_name') or ''}"))]
    if comp == SCH:  # a Schumann item naming a different opus ("Intermezzo op 46 ... Faschingsschwank") is not this set
        own = re.search(r"op\.(\d+)", name, re.I).group(1)
        pool = [(i, h) for i, h in pool if own in re.findall(r"\bop(?:us)?\.? ?(\d+)", h) or not re.search(r"\bop(?:us)?\.? ?\d", h)]
    pool = [(i, h) for i, h in pool if not re.search(EXCLUDE, h) and (name not in REQUIRE or re.search(REQUIRE[name], h))]
    if name in EXTRA_EXCLUDE: pool = [(i, h) for i, h in pool if not re.search(EXTRA_EXCLUDE[name], h)]
    labs = [m[0] for m in mvts]
    if name in WHOLE:
        w = [i for i, h in pool if re.search(WHOLE[name], h)]
        if w: return labs, [], {l: w for l in labs}
    whole_cat = re.compile("|".join(cats))
    have = {}
    for lab, n, aliases in mvts:
        for iid, h in pool:
            hit = any(re.search(a, h) for a in aliases)
            if not hit and n and whole_cat.search(h) and name.startswith(("Chopin Bal", "Chopin 4 S")) is False:
                hit = _num_ok(lab, n, cats, h)
            if not hit and n and name.startswith(("Chopin 4", "Satie", "Liszt Cons", "Liszt Lieb", "Liszt Hung", "Liszt Pag")) and whole_cat.search(h):
                hit = bool(re.search(rf"(?:{'|'.join(cats)})[^|]{{0,30}}?\b(no\.? ?|nr\.? ?|n\.? ?)?0?{n}\b(?![.,]?\d)", h))
            if hit:
                have.setdefault(lab, []).append(iid)
    labs = [m[0] for m in mvts]
    return [l for l in labs if l in have], [l for l in labs if l not in have], have
