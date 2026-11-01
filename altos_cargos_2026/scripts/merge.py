"""Cruza las unidades de los organigramas (Portal de Transparencia, 27/10/2026) con
los titulares de tres fuentes y genera altos_cargos_estructura.csv.
Prioridad del titular: CV de transparencia.gob.es > nombre en organigrama > Agenda Moncloa (jul-2026).
Transparentia (Newtral) se usa solo como columna de referencia (está desfasado)."""
import json, re, unicodedata, csv, collections
import pandas as pd

exec(open('taxo.py').read().split("if __name__")[0])   # df: lista de CV clasificada
cv = df.copy()
units = json.load(open('org/units_clean.json'))
ag = json.load(open('agenda/agenda_gob.json'))
tr = [r for r in csv.DictReader(open('../../transparentia_cargos.csv'))
      if r['activo'] == 'True' and r['ambito'] == 'Nacional']

def nz(s): return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()

MINKEY = {'mapa': 'agricultura', 'mauc': 'exteriores', 'mclt': 'cultura', 'mcnu': 'ciencia',
          'mdca': 'derechos sociales', 'mdef': 'defensa', 'mecm': 'economia, comercio', 'mefd': 'educacion',
          'mhac': 'hacienda', 'migd': 'igualdad', 'mint': 'interior', 'mism': 'inclusion', 'mitu': 'industria',
          'mjui': 'juventud', 'mpjc': 'presidencia, justicia', 'msnd': 'sanidad', 'mtdf': 'transformacion digital',
          'mted': 'transicion ecologica', 'mtes': 'trabajo y economia', 'mtmd': 'politica territorial',
          'mtrm': 'transportes', 'mvau': 'vivienda', 'pg': 'presidencia del gobierno'}
def mincod(s):
    s = nz(s)
    for k, v in MINKEY.items():
        if v in s: return k
    return None

STOP = set('de del la las los el y e para en a con al'.split())
ROLE = r'^(vicepresident[ea] .*? y )?(secretari[oa] de estado|secretari[oa] general tecnic[oa]|secretari[oa] general|subsecretari[oa]|director[a]? general|director[a]? adjunt[oa]|director[a]?|comisionad[oa] especial|comisionad[oa]|alto comisionad[oa]|delegad[oa] del gobierno|jef[ea] del departamento|ministr[oa]|presidente|presidenta)\b'
UROLE = r'^(secretaria de estado|secretaria general tecnica|secretaria general|subsecretaria|direccion general|direccion adjunta|direccion|comisionado especial|comisionado|alto comisionado|delegacion del gobierno|departamento|gabinete|oficina)\b'

def rolekind(s, unit=False):
    s = nz(s).strip()
    if unit:
        if s.startswith('secretaria de estado'): return 'SE'
        if s.startswith('secretaria general tecnica'): return 'SGT'
        if s.startswith('secretaria general'): return 'SG'
        if s.startswith('subsecretaria'): return 'SUB'
        if s.startswith('direccion general'): return 'DG'
        if 'comisionado' in s[:20]: return 'COM'
        if s.startswith('delegacion'): return 'DEL'
        if s.startswith('departamento'): return 'DEP'
        if s.startswith('gabinete'): return 'GAB'
        return 'OTRO'
    s = re.sub(r'^vicepresident[ea] [a-z]+ del gobierno y ', '', s)
    if re.match(r'secretari[oa] de estado', s): return 'SE'
    if re.match(r'secretari[oa] general tecnic', s): return 'SGT'
    if re.match(r'secretari[oa] general', s): return 'SG'
    if re.match(r'subsecretari', s): return 'SUB'
    if re.match(r'director[a]? general del departamento', s): return 'DEP'
    if re.match(r'director[a]? general', s): return 'DG'
    if re.match(r'(alto )?comisionad', s): return 'COM'
    if re.match(r'delegad[oa] del gobierno (contra|para|en las soc)', s): return 'DEL'
    if re.match(r'director[a]? (general )?del departamento|jef[ea] del departamento', s): return 'DEP'
    if re.match(r'director[a]? (del|de) gabinete', s): return 'GAB'
    return 'OTRO'

FIX = {'evaluacio n': 'evaluacion', 'economicay': 'economica y', 'competividad': 'competitividad',
       'financie ra': 'financiera', 'aninal': 'animal', 'pymes': 'pequena mediana empresa'}
def key(s, unit=False):
    s = nz(s); s = re.sub(r'-\s+', '', s)
    for a, b in FIX.items(): s = s.replace(a, b)
    s = re.sub(r'del gabinete de la presidencia del gobierno|de la secretaria de estado de comunicacion|de la presidencia del gobierno|del ministerio de defensa|del gobierno$', '', s.strip())
    s = re.sub(r'^director[a]? general del departamento', 'departamento', s)
    s = re.sub(UROLE if unit else ROLE, '', s)
    s = re.sub(r'\(.*?\)', '', s)
    return frozenset(w for w in re.findall(r'[a-z0-9]+', s) if w not in STOP and len(w) > 1)
def jac(a, b): return len(a & b) / max(1, len(a | b))

# --- candidatos (personas) ---
P = []
for _, r in cv.iterrows():
    P.append(dict(src='transparencia_cv', cod=mincod(r.ministerio), nombre=r.nombre, cargo=r.cargo,
                  kind=rolekind(r.cargo), k=key(r.cargo)))
for r in ag:
    kd = rolekind(r['cargo']) if rolekind(r['cargo']) != 'OTRO' else rolekind(r['unidad'], True)
    P.append(dict(src='agenda_moncloa_jul2026', cod=mincod(r['ministerio'] or ''), nombre=f"{r['nombre']} {r['apellidos']}",
                  cargo=r['cargo'] + ' — ' + r['unidad'], kind=kd, k=key(r['cargo']) or key(r['unidad'], True)))
for r in tr:
    if r['rol'] not in ('Altos cargos', '', 'Ministro'): continue
    P.append(dict(src='transparentia_newtral', cod=None, nombre=r['nombre'], cargo=r['cargo'],
                  kind=rolekind(r['cargo']), k=key(r['cargo'])))
NAMERX = r"[A-ZÁÉÍÓÚÑ][\wáéíóúñü'’\-]+(?: (?:de |del |la |y )?[A-ZÁÉÍÓÚÑ][\wáéíóúñü'’\-]+){1,4}"
for u in units:
    n = u['nombre_organigrama']
    if n and len(n.split()) >= 3 and not re.search(r'Secretar|Direcci|Ministr|Estado|General|Interior|Subsecretar', n) and re.fullmatch(NAMERX, n):
        P.append(dict(src='organigrama_pag_27oct2026', cod=u['cod'], nombre=n, cargo=u['unidad'],
                      kind=rolekind(u['unidad'], True), k=key(u['unidad'], True)))

# --- universo de unidades ---
U = []; seen_one = set()
for u in units:
    u['unidad'] = re.sub(r'(\s+[A-Z])+$', '', u['unidad']).strip(' ,')
    kd = rolekind(u['unidad'], True)
    if kd in ('SUB', 'SGT'):
        if (u['cod'], kd) in seen_one: continue
        seen_one.add((u['cod'], kd))
        if kd == 'SUB': u['unidad'] = 'Subsecretaría (' + u['ministerio'] + ')'
    if kd not in ('SUB', 'SGT') and len(key(u['unidad'], True)) == 0: continue
    U.append(dict(cod=u['cod'], ministerio=u['ministerio'], kind=kd, unidad=u['unidad'],
                  k=key(u['unidad'], True), origen='organigrama'))

def match(u, p):
    if p['kind'] != u['kind']: return 0
    if p['cod'] and u['cod'] and p['cod'] != u['cod']: return 0
    if u['kind'] == 'SGT': return 1 if p['cod'] == u['cod'] else 0
    if u['kind'] == 'SUB' and p['cod'] == u['cod']: return 1
    if not u['k'] or not p['k']: return 0
    j = jac(u['k'], p['k'])
    if p['k'] <= u['k']: j = max(j, 0.8)
    if p['cod'] is None and j < 0.75: return 0
    return j

PRI = {'transparencia_cv': 0, 'organigrama_pag_27oct2026': 1, 'agenda_moncloa_jul2026': 2, 'transparentia_newtral': 3}
used = set()
for u in U: u['cands'] = []
for i, p in enumerate(P):             # cada persona va solo a su(s) mejor(es) unidad(es)
    if p['kind'] == 'OTRO': continue
    sc = [(match(u, p), j) for j, u in enumerate(U) if u['kind'] != 'OTRO']
    sc = [x for x in sc if x[0] >= 0.6]
    if not sc: continue
    best = max(s for s, _ in sc)
    for s, j in sc:
        if s == best: U[j]['cands'].append((s, i)); used.add(i)
for u in U:
    if u['kind'] == 'OTRO':
        for i, p in enumerate(P):
            if p['src'] == 'organigrama_pag_27oct2026' and p['cod'] == u['cod'] and p['cargo'] == u['unidad']:
                u['cands'].append((1, i)); used.add(i)
# personas de la lista CV sin unidad en el organigrama -> unidad nueva
for i, p in enumerate(P):
    if i in used or p['src'] in ('transparentia_newtral', 'agenda_moncloa_jul2026'): continue
    if p['kind'] in ('SE', 'SG', 'SUB', 'SGT', 'DG', 'COM', 'DEL', 'DEP') and p['cod']:
        ex = [u for u in U if u['origen'] != 'organigrama' and match(u, p) >= 0.6]
        if ex: ex[0]['cands'].append((1, i)); continue
        U.append(dict(cod=p['cod'], ministerio=next(v['ministerio'] for v in units if v['cod'] == p['cod']),
                      kind=p['kind'], unidad=p['cargo'], k=p['k'], origen='solo_' + p['src'], cands=[(1, i)]))
        used.add(i)

LEVEL = {'SE': 2, 'SG': 3, 'SUB': 3, 'SGT': 4, 'DG': 4, 'COM': 4, 'DEL': 4, 'DEP': 4, 'GAB': 4, 'OTRO': 5}
TIPO = {'SE': 'Secretaría de Estado', 'SG': 'Secretaría General', 'SUB': 'Subsecretaría', 'SGT': 'Secretaría General Técnica',
        'DG': 'Dirección General', 'COM': 'Comisionado', 'DEL': 'Delegación del Gobierno (temática)',
        'DEP': 'Departamento (Presidencia del Gobierno)', 'GAB': 'Gabinete', 'OTRO': 'Otra unidad'}
def canon(n):
    n = nz(n); n = re.sub(r'[^a-z ]', ' ', n)
    return ' '.join(sorted(w for w in n.split() if w not in ('de', 'del', 'la', 'y') and len(w) > 1))

out = []
for u in U:
    cs = sorted(u['cands'], key=lambda x: (PRI[P[x[1]]['src']], -x[0]))
    names = collections.OrderedDict()
    for s, i in cs:
        p = P[i]; cn = canon(p['nombre'])
        hit = next((k for k in names if len(set(k.split()) & set(cn.split())) >= 2), None)
        names.setdefault(hit or cn, []).append(p)
    lst = list(names.values())
    lst = [g for g in lst if any(p['src'] != 'transparentia_newtral' for p in g)] + \
          [g for g in lst if all(p['src'] == 'transparentia_newtral' for p in g)]
    tit = lst[0][0] if lst and lst[0][0]['src'] != 'transparentia_newtral' else None
    out.append(dict(nivel=LEVEL[u['kind']], tipo=TIPO[u['kind']], ministerio=u['ministerio'], unidad=u['unidad'],
        titular=tit['nombre'] if tit else '', fuente_titular=tit['src'] if tit else '',
        fuentes_que_coinciden=';'.join(sorted(set(p['src'] for p in lst[0]))) if tit else '',
        conflicto=' | '.join(f"{g[0]['nombre']} ({g[0]['src']}: {g[0]['cargo'][:60]})" for g in lst[1:] if g[0]['src'] != 'transparentia_newtral'),
        en_transparentia_newtral=' | '.join(sorted(set(p['nombre'] for g in lst for p in g if p['src'] == 'transparentia_newtral'))),
        origen_unidad=u['origen']))

ORG = r'(agencia|instituto|centro|organismo|fundacion|consorcio|casa |casa$|entidad|e\.p\.e|tesoreria|servicio publico|organizacion|biblioteca|parque movil|fabrica|red\.es|enaire|turespana|icex|estadistica|inteligencia \(cni\)|nacional de inteligencia|\bitj\b|cdti|ibermutua|ciemat|cervantes|consejo superior|trabajo penitenciario|idae)'
for r in out:
    if r['origen_unidad'] != 'organigrama' and re.search(ORG, nz(r['unidad'])):
        r['tipo'] = r['tipo'] + ' — organismo/entidad adscrita'
    u = r['unidad']
    for a, b in [('Evaluació N', 'Evaluación'), ('Económicay', 'Económica y'), ('Competividad', 'Competitividad'),
                 ('Financie- Ra', 'Financiera'), ('Polícia', 'Policía'), ('Aninal', 'Animal'), ('Victímas', 'Víctimas'),
                 ('Economica', 'Económica'), (' A la ', ' a la '), (' A las ', ' a las '), (' Con ', ' con '),
                 (' Contra ', ' contra '), (' Por ', ' por '), (' Sobre ', ' sobre '), (' Lo ', ' lo '),
                 ('Lgtbi', 'LGTBI+'), ('Perte', 'PERTE'), ('Europea Europea', 'Europea')]:
        u = u.replace(a, b)
    r['unidad'] = u.strip(' .')
o = pd.DataFrame(out).sort_values(['ministerio', 'nivel', 'unidad'])
o.to_csv('altos_cargos_estructura.csv', index=False)
print(len(o)); print(o.groupby('tipo').agg(n=('unidad', 'size'), con_titular=('titular', lambda s: (s != '').sum())).to_string())
print('conflictos', (o.conflicto != '').sum())
