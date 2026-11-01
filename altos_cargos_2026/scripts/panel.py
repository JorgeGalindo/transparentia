"""Genera panel/index.html (autónomo, datos embebidos) con el estado de la base:
cobertura de altos cargos, movimientos del BOE, frescura de consejos, cola de tareas y buscador de personas.
Uso (desde altos_cargos_2026/):  python3 scripts/panel.py   (requiere pandas)"""
import os, re, json, glob, datetime, unicodedata
import pandas as pd
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(BASE, *p)
def nz(s): return ' '.join(re.sub(r'[^a-z ]', ' ', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()).split())

o = pd.read_csv(D('data/altos_cargos_estructura.csv'), dtype=str).fillna('')
ot = pd.read_csv(D('data/otros_altos_cargos.csv'), dtype=str).fillna('')
e = pd.read_csv(D('data/empresas_publicas_consejos.csv'), dtype=str).fillna('')
boe = pd.read_csv(D('data/seguimiento/boe_cambios.csv'), dtype=str).fillna('') if os.path.exists(D('data/seguimiento/boe_cambios.csv')) else pd.DataFrame()
est = json.load(open(D('data/seguimiento/boe_estado.json'))) if os.path.exists(D('data/seguimiento/boe_estado.json')) else {}

vac = o.titular.str.startswith('(') | (o.titular == '')
mins = []
for m, g in o[o.nivel != '1'].groupby('ministerio'):
    v = g.titular.str.startswith('(') | (g.titular == '')
    mins.append(dict(m=m, n=len(g), se=int((g.nivel == '2').sum()), dg=int((g.nivel == '4').sum()), vac=int(v.sum()),
                     boe=int((g.fuente_titular == 'boe_vigia').sum()), cv=int((g.fuente_titular == 'transparencia_cv').sum()),
                     ver=int((g.fuente_titular == 'verificacion_boe').sum()), vacs=[f"{r.unidad}" for _, r in g[v].iterrows()]))
ents = []
for n, g in e.groupby('empresa'):
    ents.append(dict(n=n, b=g.bloque.iloc[0], f=g.fecha_dato_iso.max(), filas=len(g),
                     ver=round((g.estado_dato == 'actual verificado').mean() * 100),
                     pe='; '.join(g[g.primer_ejecutivo == 'sí'].nombre.head(2)), ac=int((g.alto_cargo_AGE_actual != '').sum())))
ents.sort(key=lambda x: x['f'])
mov = boe.sort_values('fecha_boe', ascending=False).head(40)[['fecha_boe', 'tipo', 'nombre', 'cargo', 'identificador']].to_dict('records') if len(boe) else []
tareas = []
for p in sorted(glob.glob(D('tareas/[0-9]*.md'))):
    h = dict(re.findall(r'^(\w+):\s*(.*)$', open(p, encoding='utf-8').read().partition('\n---\n')[0], re.M))
    tareas.append(dict(id=os.path.basename(p)[:3], nombre=os.path.basename(p)[4:-3], estado=h.get('estado', ''), modelo=h.get('modelo', ''),
                       prio=h.get('prioridad', ''), ej=h.get('ejecutada', '')))
# personas: cargos AGE + consejos
P = {}
def add(nombre, tipo, txt):
    if not nombre or nombre.startswith('('): return
    k = nz(re.sub(r'\(.*?\)', '', nombre))
    P.setdefault(k, dict(n=nombre, c=[], j=[]))[tipo].append(txt)
for _, r in o.iterrows(): add(r.titular, 'c', f"{r.unidad} · {r.ministerio}")
for _, r in ot.iterrows(): add(r.nombre, 'c', f"{r.cargo}")
for _, r in e.iterrows(): add(r.nombre, 'j', f"{r.cargo} · {r.empresa[:60]}")
pers = sorted(P.values(), key=lambda x: (-len(x['j']), x['n']))
top = [x for x in pers if len(x['j']) >= 2][:20]
k = dict(unidades=int((o.nivel != '1').sum()), con_titular=int((~vac & (o.nivel != '1')).sum()), vacantes=int((vac & (o.nivel != '1')).sum()),
         otros=len(ot), entidades=e.empresa.nunique(), filas=len(e), personas_consejo=e.nombre.map(nz).nunique(),
         verif=round((e.estado_dato == 'actual verificado').mean() * 100), cruces=int((e.alto_cargo_AGE_actual != '').sum()),
         boe_n=len(boe), boe_hasta=est.get('ultima_fecha', ''), t_pend=sum(t['estado'] == 'pendiente' for t in tareas),
         t_hechas=sum(t['estado'] == 'hecha' for t in tareas), t_fall=sum(t['estado'] == 'fallida' for t in tareas),
         generado=datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
data = dict(k=k, mins=mins, ents=ents, mov=mov, tareas=tareas, pers=[dict(n=x['n'], c=x['c'][:4], j=x['j'][:6]) for x in pers], top=top)
html = open(D('scripts/panel_plantilla.html'), encoding='utf-8').read().replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
os.makedirs(D('panel'), exist_ok=True); open(D('panel/index.html'), 'w', encoding='utf-8').write(html)
print('panel/index.html', len(html) // 1024, 'KB')
