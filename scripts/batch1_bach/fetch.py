import json, urllib.request, os, re, concurrent.futures as cf, html
BASE="https://www.mutopiaproject.org/ftp/BachJS/"
S=json.load(open('/tmp/bachwork/selected.json'))
def go(r):
    d="/tmp/bachwork/dl/"+r['path'].strip('/').replace('/','__')
    os.makedirs(d,exist_ok=True)
    for f in r['files']:
        if f.endswith(('.mid','.ly','-mids.zip','-lys.zip','.rdf')) and not os.path.exists(d+'/'+f):
            urllib.request.urlretrieve(BASE+r['path']+f, d+'/'+f)
    pid=r['id'].rsplit('-',1)[-1]
    p=urllib.request.urlopen(f"https://www.mutopiaproject.org/cgibin/piece-info.cgi?id={pid}",timeout=60).read().decode('utf-8','replace')
    open(d+'/piece-info.html','w').write(p)
    txt=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',p)))
    m=re.search(r'(Public Domain|Creative Commons [A-Za-z\- ]+\d\.\d)',txt)
    return r['path'],pid,m.group(1) if m else 'NOTFOUND'
with cf.ThreadPoolExecutor(8) as ex:
    out=list(ex.map(go,S))
json.dump(out,open('/tmp/bachwork/pageverify.json','w'))
bad=[o for o in out if o[2] not in ('Public Domain',) and 'Attribution' not in o[2]]
print(len(out),'bad:',bad)
