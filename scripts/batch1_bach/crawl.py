import re, urllib.request, json, concurrent.futures as cf, os
BASE="https://www.mutopiaproject.org/ftp/BachJS/"
def ls(u):
    h=urllib.request.urlopen(u,timeout=60).read().decode("utf-8","replace")
    return [x for x in re.findall(r'href="([^"?/][^"]*)"',h)]
top=[d for d in ls(BASE) if d.endswith("/")]
print(len(top),"BWV dirs")
def sub(d):
    out=[]
    for p in ls(BASE+d):
        if p.endswith("/"):
            try:
                files=ls(BASE+d+p)
                out.append((d+p,files))
            except Exception as e: out.append((d+p,["ERR "+str(e)]))
    return out
res=[]
with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(sub,top): res.extend(r)
json.dump(res,open("/tmp/bachwork/listing.json","w"),indent=0)
print(len(res),"pieces")
