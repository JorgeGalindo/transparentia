"""Une los CSV de consejos (bloques + jobs API) y enlaza consejeros con la tabla de altos cargos."""
import pandas as pd, glob, re, unicodedata
H="empresa,forma_juridica,adscripcion_o_matriz,participacion_publica_pct,cargo,nombre,primer_ejecutivo,tipo_consejero,otro_cargo_publico,fuente_url,fecha_dato,nota".split(",")
BLOQ={'bloque1':'SEPI mayoritarias','bloque2':'SEPI minoritarias + Aena','bloque3':'Transportes','bloque4':'Financieras/económicas/digitales','bloque5':'Resto','api_A':'Transportes','api_B':'Huecos varios','api_C':'Barrido cobertura (solo primer ejecutivo)','api_D':'Huecos varios'}
fr=[]
for f in sorted(glob.glob('empresas/bloque*.csv'))+sorted(glob.glob('empresas/api_*.csv')):
    d=pd.read_csv(f,dtype=str).fillna('')
    miss=[c for c in H if c not in d.columns]
    if miss: print('AVISO columnas',f,miss); [d.__setitem__(c,'') for c in miss]
    d=d[H]; b=f.split('/')[-1]; d.insert(0,'bloque',next(v for k,v in BLOQ.items() if b.startswith(k))); d['fichero_origen']=b
    fr.append(d)
e=pd.concat(fr,ignore_index=True)
ALIAS={'Hispasat, S.A.':'Hispasat','Loterías y Apuestas del Estado (SELAE) S.M.E., S.A.':'SELAE (Sociedad Estatal Loterías y Apuestas del Estado, S.M.E., S.A.)'}
e['empresa']=e.empresa.str.strip().replace(ALIAS)
e=e[e.nombre.str.strip()!='']
def nz(s): return ' '.join(w for w in re.sub(r'[^a-z ]',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).split() if w not in ('de','del','la','y','las','los'))
# dedupe: same empresa+persona+cargo
e['_k']=e.empresa.map(nz)+'|'+e.nombre.map(lambda n: ' '.join(sorted(nz(re.sub(r'\(.*?\)','',n)).split())))
dup=e._k.duplicated(keep='last'); print('duplicados eliminados',dup.sum()); e=e[~dup]
# enlazar con altos cargos
ac=pd.read_csv('altos_cargos_estructura.csv').fillna('')
ot=pd.read_csv('otros_altos_cargos.csv').fillna('')
idx={}
for _,r in ac.iterrows():
    if r.titular and r.titular!='(vacante)': idx.setdefault(nz(r.titular),[]).append(f"{r.unidad} ({r.ministerio})")
for _,r in ot.iterrows(): idx.setdefault(nz(r.nombre),[]).append(f"{r.cargo} ({r.ministerio})")
RANK=r'^(tg|gd|gb|ge|almte|valmte|calmte|gral|general|teniente general|almirante|d|dna|dona|don|sr|sra)\s+'
def link(n):
    n=re.sub(r'\(.*?\)','',str(n)); n=re.sub(r'^.*representad[oa] por ','',n,flags=re.I)
    k=re.sub(RANK,'',nz(n))
    if k in idx: return ' | '.join(idx[k])
    t=set(k.split())
    for kk,v in idx.items():
        s=set(kk.split())
        if min(len(t),len(s))>=3 and (t<=s or s<=t): return ' | '.join(v)+' [match parcial: nombre contenido]'
    return ''
e['alto_cargo_AGE_actual']=e.nombre.map(link)
e=e.drop(columns='_k')
e.to_csv('empresas_publicas_consejos.csv',index=False)
print('filas',len(e),'empresas',e.empresa.nunique(),'personas',e.nombre.map(nz).nunique())
print('consejeros que son altos cargos AGE (según lista):',(e.alto_cargo_AGE_actual!='').sum())
print(e.groupby('bloque').agg(empresas=('empresa','nunique'),filas=('nombre','size')).to_string())
