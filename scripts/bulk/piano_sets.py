import sys,re;sys.argv=['x'];exec(open('scripts/bulk/set_coverage.py').read().split('out = []')[0])
def num(comp,label,cat,n,extra=""):
    c=cat.replace(' ',r'\.? ?').replace('Op','op').replace('BWV','bwv').replace('D','d').replace('K','k')
    return (label,comp,c,"PD",[(f"No. {i}",rf"{c}\b.*no\.? ?{i}\b"+extra) for i in range(1,n+1)])
P=[num("chopin","Chopin Études Op.10","Op 10",12),num("chopin","Chopin Études Op.25","Op 25",12),num("chopin","Chopin Préludes Op.28","Op 28",24),
 ("Chopin 4 Ballades","chopin",r"ballade","PD",[(f"No. {i}",rf"ballade.*\b{i}\b") for i in range(1,5)]),
 ("Chopin 4 Scherzi","chopin",r"scherzo","PD",[(f"No. {i}",rf"scherzo.*\b{i}\b") for i in range(1,5)]),
 num("chopin","Chopin Nocturnes Op.9","Op 9",3),num("chopin","Chopin Nocturnes Op.27","Op 27",2),num("chopin","Chopin Nocturnes Op.48","Op 48",2),
 num("chopin","Chopin Waltzes Op.64","Op 64",3),num("chopin","Chopin Waltzes Op.34","Op 34",3),
 ("Beethoven Sonata 8 Pathétique Op.13","beethoven",r"op\.? ?13\b|pathetique","PD",[("mvts 1-3 or complete",r"op\.? ?13\b|pathetique")]),
 ("Beethoven Sonata 14 Moonlight Op.27/2","beethoven",r"moonlight|op\.? ?27","PD",[("mvts or complete",r"moonlight|op\.? ?27 no\.? ?2")]),
 ("Beethoven Sonata 23 Appassionata Op.57","beethoven",r"op\.? ?57|appassionata","PD",[("mvts or complete",r"op\.? ?57|appassionata")]),
 ("Bach WTC Book I BWV 846-869","bach",r"bwv ?8[4-6]\d","PD",[(f"BWV {i}",rf"bwv ?{i}\b") for i in range(846,870)]),
 ("Bach Goldberg Variations BWV 988","bach",r"988|goldberg","PD",[("aria/variations",r"988|goldberg")]),
 ("Schumann Kinderszenen Op.15","schumann",r"op\.? ?15|kinderszenen","PD",[(f"No. {i}",rf"(op\.? ?15|kinderszenen).*no\.? ?{i}\b") for i in range(1,14)]),
 ("Schumann Carnaval Op.9","schumann",r"carnaval","PD",[("complete/mvts",r"carnaval")]),
 num("schubert","Schubert Impromptus D.899","D 899",4),num("schubert","Schubert Impromptus D.935","D 935",4),num("schubert","Schubert Moments musicaux D.780","D 780",6),
 num("mendelssohn","Mendelssohn Songs without Words Op.19b","Op 19",6),num("mendelssohn","Mendelssohn Songs without Words Op.62","Op 62",6),
 ("Liszt Consolations S.172","liszt",r"consolation","PD",[(f"No. {i}",rf"consolation.*\b{i}\b") for i in range(1,7)]),
 ("Liszt Liebesträume S.541","liszt",r"liebestr","PD",[(f"No. {i}",rf"liebestr.*\b{i}\b") for i in range(1,4)]),
 ("Mozart Sonata K.331","mozart",r"331","PD",[("mvts or complete",r"331")]),
 num("grieg","Grieg Lyric Pieces Op.12","Op 12",8),
 ("Tchaikovsky The Seasons Op.37a","tchaikovsky",r"seasons|op\.? ?37","PD",[(m,m.lower()) for m in "January February March April May June July August September October November December".split()]),
 num("rachmaninoff","Rachmaninoff Preludes Op.23","Op 23",10),num("rachmaninoff","Rachmaninoff Preludes Op.32","Op 32",13),
 num("rachmaninoff","Rachmaninoff Études-tableaux Op.33","Op 33",8),num("rachmaninoff","Rachmaninoff Études-tableaux Op.39","Op 39",9),
 num("brahms","Brahms Fantasien Op.116","Op 116",7),num("brahms","Brahms Intermezzi Op.117","Op 117",3),num("brahms","Brahms Klavierstücke Op.118","Op 118",6),num("brahms","Brahms Klavierstücke Op.119","Op 119",4),
]
for name,comp,setre,scope,mv in P:
    pool=[hay(it) for it in items if comp in fold(it.get("composer")) and re.search(setre,hay(it))]
    have=[l for l,r in mv if any(re.search(r,h) for h in pool)];miss=[l for l,_ in mv if l not in have]
    print(f"| {name} | {'COMPLETE' if not miss else f'{len(have)}/{len(mv)}'} | {', '.join(miss) or '-'} |")
