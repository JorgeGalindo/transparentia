import pandas as pd,re,unicodedata
exec(open('taxo.py').read().split("if __name__")[0]); cv=df
o=pd.read_csv('altos_cargos_estructura.csv').fillna('')
def nz(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
ST=set('de del la las los el y e para en a con al direccion general secretaria oficina departamento comisionado especial director directora gobierno presidencia estado'.split())
def k(s): return set(w for w in re.findall(r'[a-z0-9]+',nz(s)) if w not in ST and len(w)>1)
def base(t): return t.split(' — ')[0]
drop=set()
# drop garbled duplicates
for i,r in o.iterrows():
    if r.unidad in ('Dirección Pública y Redes General de Comunicación, Diplomacia','Oficina y G20'): drop.add(i)
for i,r in o[(o.titular=='')&(o.origen_unidad=='organigrama')].iterrows():
    best=None
    for j,s in o[(o.ministerio==r.ministerio)&(o.origen_unidad!='organigrama')].iterrows():
        if j in drop: continue
        a,b=k(r.unidad),k(s.unidad)
        if not a or not b: continue
        jac=len(a&b)/len(a|b)
        if jac>=0.5 or a<=b and len(b-a)<=2:
            if not best or jac>best[0]: best=(jac,j)
    if best:
        s=o.loc[best[1]]
        for c in ('titular','fuente_titular','fuentes_que_coinciden','conflicto','en_transparentia_newtral'): o.at[i,c]=s[c]
        o.at[i,'origen_unidad']='organigrama+transparencia_cv'
        drop.add(best[1])
# Oficinas / otras: match with CV persons "Director/a de la Oficina ..."
for i,r in o[(o.titular=='')].iterrows():
    a=k(r.unidad)
    c=cv[cv.ministerio.map(nz).str.contains(nz(r.ministerio).split(',')[0].split(' y ')[0][:10],regex=False)]
    best=None
    for _,p in c.iterrows():
        b=k(p.cargo)
        if a and b and (len(a&b)/len(a|b)>=0.6 or a<=b):
            best=p;break
    if best is not None:
        o.at[i,'titular']=best.nombre; o.at[i,'fuente_titular']='transparencia_cv'; o.at[i,'fuentes_que_coinciden']='transparencia_cv'
o=o.drop(index=list(drop))
o.to_csv('altos_cargos_estructura.csv',index=False)
print(len(o),'vacías',(o.titular=='').sum())
print(o[o.titular==''][['ministerio','unidad']].to_string())
