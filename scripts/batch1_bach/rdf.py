import json, urllib.request, re, concurrent.futures as cf, html
BASE="https://www.mutopiaproject.org/ftp/BachJS/"
L=json.load(open("/tmp/bachwork/listing.json"))
def get(item):
    path,files=item
    rdfs=[f for f in files if f.endswith(".rdf")]
    if not rdfs: return {"path":path,"files":files,"err":"no rdf"}
    t=urllib.request.urlopen(BASE+path+rdfs[0],timeout=60).read().decode("utf-8","replace")
    d={k:html.unescape(v.strip()) for k,v in re.findall(r"<mp:(\w+)>(.*?)</mp:\1>",t,re.S)}
    d["path"]=path; d["files"]=files
    return d
with cf.ThreadPoolExecutor(10) as ex: R=list(ex.map(get,L))
json.dump(R,open("/tmp/bachwork/rdfs.json","w"),indent=1,ensure_ascii=False)
from collections import Counter
print(Counter(r.get("licence","?") for r in R))
