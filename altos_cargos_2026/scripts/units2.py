import json,re,unicodedata
rows=json.load(open('org/units.json'))
STOP=set('de del la las los el y e para en a con al'.split())
def key(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'-\s+','',s)
    s=re.sub(r'^(secretaria de estado|secretaria general tecnica|secretaria general|subsecretaria|direccion general|direccion|comisionado|alto comisionado|departamento|oficina|delegacion del gobierno|gabinete)\b','',s)
    return frozenset(w for w in re.findall(r'[a-z0-9]+',s) if w not in STOP and len(w)>1)
def jac(a,b): return len(a&b)/max(1,len(a|b))
out=[]
for cod in sorted(set(r['cod'] for r in rows)):
    R=[r for r in rows if r['cod']==cod]
    later=[r for r in R if r['pagina']>1]
    for r in R:
        r['k']=key(r['unidad'])
        if r['tipo']=='Secretaría General Técnica': r['k']=frozenset(['sgt'])
    keep=[]
    for r in sorted(R,key=lambda r:-r['pagina']):
        dup=[k for k in keep if k['tipo']==r['tipo'] and (jac(k['k'],r['k'])>=0.6 or (r['k']<=k['k'] and len(r['k'])>0) or (k['k']<=r['k'] and len(k['k'])>0))]
        if dup:
            if r['nombre_organigrama'] and not dup[0]['nombre_organigrama']: dup[0]['nombre_organigrama']=r['nombre_organigrama']
            continue
        keep.append(r)
    out+=sorted(keep,key=lambda r:(r['nivel'],r['unidad']))
for r in out: r['k']=sorted(r['k'])
json.dump(out,open('org/units_clean.json','w'),ensure_ascii=False,indent=0)
import collections
print(len(out),collections.Counter(r['tipo'] for r in out))
for r in out: print(r['cod'],r['nivel'],r['pagina'],'|',r['unidad'][:110],'|',r['nombre_organigrama'])
