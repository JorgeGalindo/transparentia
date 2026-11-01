"""Aplica data/seguimiento/boe_cambios.csv (vigía del BOE) a las tablas de altos cargos, en orden cronológico.
- nombramiento: la unidad cuyo nombre encaja con el cargo pasa a tener ese titular (fuente boe:<id>).
- cese: si el titular actual es esa persona, la unidad queda '(vacante tras cese BOE)'.
Solo cambios con fecha >= FECHA_BASE (la base se cerró con fuentes de finales de octubre de 2026).
Lo que no encaja con ninguna unidad va a data/seguimiento/boe_sin_encaje.csv para revisión."""
import pandas as pd, re, unicodedata, os, sys
FECHA_BASE = '20260901'
SEG = '../data/seguimiento'
def nz(s): return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
STOP = set('de del la las los el y e para en a con al don dona'.split())
ROLE = r'^(secretari[oa] de estado|secretari[oa] general tecnic[oa]|secretari[oa] general|subsecretari[oa]|director[a]? general|director[a]? del departamento|director[a]? de la oficina|director[a]?|comisionad[oa] especial|comisionad[oa]|delegad[oa] del gobierno|presidente|presidenta|embajador[a]?)\b'
UROLE = r'^(secretaria de estado|secretaria general tecnica|secretaria general|subsecretaria|direccion general|departamento|oficina|comisionado especial|comisionado|delegacion del gobierno|direccion)\b'
def kind(s):
    s = nz(s)
    for k, rx in [('SE', r'secretari[oa] de estado'), ('SGT', r'secretari[oa] general tecnic'), ('SG', r'secretari[oa] general'),
                  ('SUB', r'subsecretari'), ('DG', r'(director[a]?|direccion) general'), ('DEL', r'delegad[oa]|delegacion'),
                  ('COM', r'comisionad'), ('EMB', r'embajador')]:
        if re.match(rx, s): return k
    return 'OTRO'
def key(s, unit=False):
    s = nz(s); s = re.sub(r'\(.*?\)', '', s); s = re.sub(UROLE if unit else ROLE, '', s.strip())
    return set(w for w in re.findall(r'[a-z0-9]+', s) if w not in STOP and len(w) > 1)
def jac(a, b): return len(a & b) / max(1, len(a | b))
def ovl(a, b): return len(a & b) / max(1, min(len(a), len(b)))
def same(a, b):
    A, B = key(a), key(b); return len(A & B) >= 2 and (A <= B or B <= A or jac(A, B) >= 0.6)

p = os.path.join(SEG, 'boe_cambios.csv')
if not os.path.exists(p): print('sin boe_cambios.csv'); sys.exit()
ch = pd.read_csv(p, dtype=str).fillna('')
ch = ch[ch.fecha_boe >= FECHA_BASE].copy()
ch['ord'] = ch.tipo.map({'cese': 0, 'nombramiento': 1})
ch = ch.sort_values(['fecha_boe', 'ord'])
o = pd.read_csv('altos_cargos_estructura.csv', dtype=str).fillna('')
ot = pd.read_csv('otros_altos_cargos.csv', dtype=str).fillna('')
for c in ('fuente_boe',): o[c] = o.get(c, ''); ot[c] = ''
SUBMIN = {'trabajo': 'Trabajo', 'exteriores': 'Exteriores'}
sin = []; aplic = 0
for _, c in ch.iterrows():
    k = kind(c.cargo); ck = key(c.cargo)
    # estructura
    best = None
    for i, r in o.iterrows():
        rk = kind(r.unidad) if not r.unidad.startswith('Subsecretaría (') else 'SUB'
        if r.nivel == '1' or rk != k: continue
        uk = key(r.unidad, True) if rk != 'SUB' else key(r.ministerio, True)
        if k in ('SUB', 'SGT'):
            uk = key(r.ministerio, True)
            ck2 = key(re.sub(r'^.*?(subsecretari[oa]|secretari[oa] general tecnic[oa])( del ministerio)?( de| del| para la| para el)?', '', nz(c.cargo)), True) or ck
            s = ovl(uk, ck2) if k == 'SUB' else (1 if nz(r.ministerio)[:12] in nz(c.departamento + ' ' + c.cargo) else 0)
        else:
            s = jac(uk, ck) if not (uk <= ck or ck <= uk) or not uk else max(jac(uk, ck), 0.8)
        if s >= 0.6 and (best is None or s > best[0]): best = (s, i)
    if best:
        i = best[1]
        if c.tipo == 'nombramiento':
            o.at[i, 'titular'] = c.nombre; o.at[i, 'fuente_titular'] = 'boe_vigia'; o.at[i, 'fecha_nombramiento'] = c.fecha_boe
            o.at[i, 'fuente_boe'] = c.identificador; aplic += 1
        elif same(o.at[i, 'titular'], c.nombre) or set(nz(o.at[i, 'titular']).split()) & set(nz(c.nombre).split()) >= set(nz(c.nombre).split()[-2:]):
            o.at[i, 'titular'] = '(vacante tras cese BOE)'; o.at[i, 'fuente_titular'] = 'boe_vigia'; o.at[i, 'fuente_boe'] = c.identificador; aplic += 1
        continue
    # otros altos cargos (delegados del Gobierno, embajadores, organismos)
    best = None
    for i, r in ot.iterrows():
        if kind(r.cargo) != k or k == 'OTRO' and re.match(r'ministr', nz(r.cargo)): continue
        s = ovl(key(r.cargo), ck) if k in ('DEL', 'EMB') else jac(key(r.cargo), ck)
        if s >= 0.75 and (best is None or s > best[0]): best = (s, i)
    if best:
        i = best[1]
        if c.tipo == 'nombramiento':
            ot.at[i, 'nombre'] = c.nombre; ot.at[i, 'fuente'] = f'BOE {c.identificador} ({c.fecha_boe})'; ot.at[i, 'fuente_boe'] = c.identificador; aplic += 1
        elif set(nz(c.nombre).split()[-2:]) <= set(nz(ot.at[i, 'nombre']).split()):
            ot.at[i, 'nombre'] = '(vacante tras cese BOE)'; ot.at[i, 'fuente'] = f'BOE {c.identificador} ({c.fecha_boe})'; ot.at[i, 'fuente_boe'] = c.identificador; aplic += 1
        continue
    if c.tipo == 'nombramiento': sin.append(c)
o.to_csv('altos_cargos_estructura.csv', index=False); ot.to_csv('otros_altos_cargos.csv', index=False)
pd.DataFrame(sin).drop(columns='ord', errors='ignore').to_csv(os.path.join(SEG, 'boe_sin_encaje.csv'), index=False)
print(f'BOE aplicados: {aplic} | nombramientos sin encaje (revisar): {len(sin)}')
