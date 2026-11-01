"""Aplica verificacion_resultado.csv (BOE / Consejo de Ministros, 01/11/2026) sobre altos_cargos_estructura.csv
y añade las DG que perdían el cruce por nombre parecido."""
import pandas as pd
o=pd.read_csv('altos_cargos_estructura.csv').fillna('')
v=pd.read_csv('verificacion_resultado.csv').fillna('')
for c in ('verificacion','fuente_verificacion','fecha_nombramiento','nota'): o[c]=''
for _,r in v.iterrows():
    m=(o.ministerio==r.ministerio)&(o.unidad.str[:50]==r.unidad[:50])
    if m.sum()!=1:
        print('SIN MATCH',r.ministerio,r.unidad); continue
    i=o[m].index[0]
    o.at[i,'verificacion']=r.estado; o.at[i,'fuente_verificacion']=r.fuente_url; o.at[i,'fecha_nombramiento']=r.fecha_nombramiento; o.at[i,'nota']=r.nota
    if r.estado in ('corregido','nuevo (era hueco)'):
        o.at[i,'titular']=r.titular_actual; o.at[i,'fuente_titular']='verificacion_boe'
    if r.estado=='vacante':
        o.at[i,'titular']='(vacante)'; o.at[i,'fuente_titular']='verificacion_boe'
    if o.at[i,'conflicto']:
        o.at[i,'nota']=('Conflicto resuelto: '+r.nota)[:400]; o.at[i,'conflicto']=''
extra=[('Dirección General','Economía, Comercio y Empresa','Dirección General de Política Económica','Francisco Javier Muñoz Moldes'),
       ('Dirección General — organismo/entidad adscrita','Cultura','Dirección General del Instituto Nacional de las Artes Escénicas y de la Música (INAEM)','Paz Santa Cecilia Aristu'),
       ('Dirección General — organismo/entidad adscrita','Economía, Comercio y Empresa','Dirección General de Estadísticas de la Población (INE)','Cristina Casaseca Polo')]
for t,mi,u,n in extra:
    o.loc[len(o)]=dict(nivel=4,tipo=t,ministerio=mi,unidad=u,titular=n,fuente_titular='transparencia_cv',fuentes_que_coinciden='transparencia_cv',conflicto='',en_transparentia_newtral='',origen_unidad='solo_transparencia_cv',verificacion='',fuente_verificacion='',fecha_nombramiento='',nota='Separada tras verificación (antes en conflicto con otra DG de nombre parecido)')
o=o.sort_values(['ministerio','nivel','unidad'])
o.to_csv('altos_cargos_estructura.csv',index=False)
print(len(o),'sin titular:',(o.titular=='').sum(),'vacantes:',(o.titular=='(vacante)').sum(),'conflictos:',(o.conflicto!='').sum())
# nivel 1: presidente y ministros (lista CV)
ot=pd.read_csv('otros_altos_cargos.csv').fillna('')
l1=ot[ot.categoria.isin(['Presidente del Gobierno','Ministro/a'])]
for _,r in l1.iterrows():
    o.loc[len(o)]=dict(nivel=1,tipo='Presidencia del Gobierno' if r.categoria.startswith('Presidente') else 'Ministerio',ministerio=r.ministerio.replace('Ministerio de ','').replace('Ministerio para la ','').replace('Ministerio del ',''),unidad=r.cargo,titular=r.nombre,fuente_titular='transparencia_cv',fuentes_que_coinciden='transparencia_cv;lamoncloa_composicion',conflicto='',en_transparentia_newtral='',origen_unidad='transparencia_cv',verificacion='',fuente_verificacion='https://www.lamoncloa.gob.es/gobierno/composiciondelgobierno/Paginas/index.aspx',fecha_nombramiento='',nota='')
o=o.sort_values(['nivel','ministerio','unidad'])
o.to_csv('altos_cargos_estructura.csv',index=False)
print('con nivel 1:',len(o))
import unicodedata
short=sorted(set(o[o.nivel>1].ministerio))
def nz(s): return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
def best(m):
    a=set(nz(m).replace(',',' ').split())-{'de','y','la','el','del','para'}
    return max(short,key=lambda s: len(a & (set(nz(s).replace(',',' ').split())-{'de','y','la','el','del','para'})))
o.loc[o.nivel==1,'ministerio']=o.loc[o.nivel==1,'ministerio'].map(best)
o=o.sort_values(['nivel','ministerio','unidad']); o.to_csv('altos_cargos_estructura.csv',index=False)
print(o[o.nivel==1].ministerio.tolist())
