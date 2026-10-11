import json,re
rows=json.load(open('/tmp/midionly_rows.json'))
G=['Bach','Mozart','Beethoven','Chopin','Schubert','Schumann','Brahms','Debussy','Ravel','Liszt','Mendelssohn','Tchaikovsky','Rachmaninoff','Haydn','Handel','Grieg','Satie','Dvořák','Fauré','Vivaldi','Scarlatti','Mussorgsky']
FAMOUS=r'elise|clair de lune|traumerei|träumerei|pathétique|pathetique|moonlight|turca|raindrop|revolutionary|nocturne|prelude|invention|goldberg|well-tempered|arabesque|impromptu|moment|waltz|valse|mazurka|consolation|lieder ohne|song without|seasons|kinderscen|gymnop|gnoss|sonata|etude|étude|ballade|intermezzo'
def rank(r):
  k,comp,title,cat,n=r
  ci=next((i for i,g in enumerate(G) if g.lower() in comp.lower()),99)
  return (0 if cat=='piano/keyboard' else 1, ci, 0 if re.search(FAMOUS,title.lower()) else 1, n)
done=set(open('/tmp/mb_pilot/ids.txt').read().split())
q=[r[0] for r in sorted(rows,key=rank) if r[0] not in done]
open('scripts/midi2score/queue.txt','w').write('\n'.join(q)+'\n'); print(len(q),q[:12])
