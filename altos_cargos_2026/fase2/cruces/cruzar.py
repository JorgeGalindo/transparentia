"""Tarea 109: cruza personas del universo con cargos electos/de gobierno. Solo librería estándar + pandas.
Ejecutar desde fase2/: uv run -q --with pandas python -I cruces/cruzar.py"""
import pandas as pd, re, unicodedata, os, glob, collections
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'cruces')
PART = {'de','del','la','las','los','el','i','y','e','da','do','dos','das','d','l','van','von','di','du'}

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s.replace("'", ' '))
    return tuple(t for t in s.split() if t not in PART)

def txt(s): return ' '.join(norm(s))

# ---------- personas
per = pd.read_csv(f'{BASE}/db/export/persona.csv')
per = per[per.excluir_universo.astype(str).str.lower() != 'true'].copy()
per['tok'] = per.nombre_completo.map(norm)
ocu = pd.read_csv(f'{BASE}/db/export/ocupacion.csv')
ocu_cargos = ocu.groupby('persona_id').cargo.apply(lambda s: ' | '.join(map(str, s))).to_dict()

# ---------- CV text por persona
man = pd.read_csv(f'{BASE}/fuentes/cv/manifiesto_cv.csv')
cvtext = collections.defaultdict(str)
cv_by_name = collections.defaultdict(list)
for r in man.itertuples():
    cv_by_name[norm(r.nombre)].append(r.ruta_local)
def cv_for(tok):
    t = ''
    for f in cv_by_name.get(tok, []):
        try: t += ' ' + txt(open(f, encoding='utf-8', errors='ignore').read())
        except OSError: pass
    return t
CV = {r.persona_id: cv_for(r.tok) for r in per.itertuples()}

# ---------- cargos
KW = {  # institución -> palabras en el CV (normalizadas)
 'Senado': ['senador', 'senado'], 'Congreso de los Diputados': ['diputado', 'diputada', 'congreso'],
 'Parlamento Europeo': ['eurodiputad', 'parlamento europeo'], 'Parlamento autonómico': ['diputado', 'diputada', 'parlament', 'asamblea', 'cortes'],
 'Alcaldía': ['alcalde', 'alcaldesa', 'concejal'], 'Gobierno autonómico': ['consejer', 'conseller', 'presidente de la comunidad', 'presidente de la junta', 'presidenta de la'],
 'Gobierno de España': ['ministr', 'vicepresident', 'presidente del gobierno'],
}
NIVEL = {'Senado': 'nacional', 'Congreso de los Diputados': 'nacional', 'Parlamento Europeo': 'europeo', 'Parlamento autonómico': 'autonómico',
         'Alcaldía': 'local', 'Gobierno autonómico': 'gobierno', 'Gobierno de España': 'gobierno'}
of = pd.read_csv(f'{BASE}/fuentes/electos/cargo_electo_oficial.csv', dtype=str)
of['nivel'] = of.institucion.map(NIVEL)
of['cargo_nombre'] = of.persona_nombre
of['tok'] = of.persona_nombre.map(norm)
of['origen_tabla'] = 'oficial'

lo = pd.read_csv(f'{BASE}/fuentes/locales/cargo_electo_local.csv', dtype=str)
def loc_inst(r):
    c = (r.cargo or '').lower(); a = r.ambito
    if re.match(r'(ministr|vicepresident|presidente del gobierno)', c): return 'Gobierno de España'
    if re.match(r'(consejer|conseller|president[ea] de (la )?(comunidad|junta|generalitat|gobierno))', c): return 'Gobierno autonómico'
    if c.startswith('senador'): return 'Senado'
    if c.startswith('eurodiput') or a == 'Europeo': return 'Parlamento Europeo'
    if re.match(r'(alcald|concejal)', c): return 'Alcaldía'
    if c.startswith('diputad'): return 'Congreso de los Diputados' if a == 'Nacional' else 'Parlamento autonómico'
    return None
lo['institucion_n'] = lo.apply(loc_inst, axis=1)
def per_dates(p):
    ys = re.findall(r'(19\d\d|20\d\d)', p or '')
    if p and p.startswith('Hasta'): return None, ys[0] if ys else None
    if p and p.startswith('Desde'): return ys[0] if ys else None, None
    if p == 'Actual': return None, None
    return (ys[0], ys[1]) if len(ys) == 2 else (None, None)
rows = []
for r in lo.itertuples():
    if r.institucion_n is None: continue
    i, f = per_dates(r.periodo)
    rows.append(dict(persona_nombre=r.persona_nombre_buscado, institucion=r.institucion_n,
        partido=None if r.partido == 'Sin partido' else r.partido, legislatura=None, fecha_inicio=i, fecha_fin=f,
        fuente='Transparentia ' + r.fuente.replace('transparentia_', ''), url=r.url, grupo=None, id_externo='tp:' + txt(r.nombre_encontrado),
        procedencia=f'{r.cargo} ({r.institucion}; periodo «{r.periodo}»)', partido_origen='Transparentia (partido en la ficha)', nivel=NIVEL[r.institucion_n],
        calidad_local=r.calidad_cruce, origen_tabla='local'))
lo2 = pd.DataFrame(rows); lo2['tok'] = lo2.persona_nombre.map(norm)
allc = pd.concat([of, lo2], ignore_index=True)

# ---------- fechas: corregir/descartar imposibles
def fix(d):
    if not isinstance(d, str) or not d: return None, ''
    m = re.match(r'(\d{4})', d)
    if not m: return None, 'fecha ilegible'
    y = int(m.group(1))
    if y < 1900 or y > 2026: return None, f'fecha imposible descartada ({d})'
    return d, ''
notes = []
for c in ('fecha_inicio', 'fecha_fin'):
    res = allc[c].map(fix); allc[c] = res.map(lambda x: x[0]); notes.append(res.map(lambda x: x[1]))
allc['nota_fecha'] = [';'.join(x for x in z if x) for z in zip(*notes)]
bad = allc.fecha_inicio.notna() & allc.fecha_fin.notna() & (allc.fecha_inicio > allc.fecha_fin)
allc.loc[bad, 'nota_fecha'] += ';inicio>fin: inicio descartado'; allc.loc[bad, 'fecha_inicio'] = None
allc['nota_fecha'] = allc.nota_fecha.str.strip(';')

# ---------- candidatos de cruce
by_full = collections.defaultdict(list)
by_set = collections.defaultdict(list)
by_pref = collections.defaultdict(list)
for i, t in zip(allc.index, allc.tok):
    if len(t) >= 2:
        by_full[t].append(i); by_set[frozenset(t)].append(i); by_pref[t[:2]].append(i)
cands = []  # (persona_id, idx, tipo)
for r in per.itertuples():
    t = r.tok; seen = set()
    for i in by_full.get(t, []):
        cands.append((r.persona_id, i, 'exacto' if len(t) >= 3 else 'exacto_2_palabras')); seen.add(i)
    if len(t) >= 3:
        for i in by_set.get(frozenset(t), []):
            if i not in seen: cands.append((r.persona_id, i, 'permutado')); seen.add(i)
    if len(t) >= 2:
        for i in by_pref.get(t[:2], []):
            if i in seen: continue
            ct = allc.tok[i]
            if len(ct) != len(t) and (t[:len(ct)] == ct or ct[:len(t)] == t): cands.append((r.persona_id, i, 'prefijo')); seen.add(i)
        # primer nombre + último apellido de la persona frente a cargo de 2-3 palabras
cd = pd.DataFrame(cands, columns=['persona_id', 'idx', 'tipo_cruce'])
print('candidatos', len(cd), cd.tipo_cruce.value_counts().to_dict())

# identidades distintas por persona+tipo de nombre (homónimos en Wikidata)
def ident(r): return r.id_externo if isinstance(r.id_externo, str) and r.id_externo.startswith(('wd:', 'ep:', 'tp:')) else 'sen:' + txt(r.persona_nombre)
allc['ident'] = allc.apply(ident, axis=1)
# senado oficial y wikidata: misma persona si mismo nombre; id_externo wd distinto = posible homónimo
cd = cd.join(allc[['ident', 'institucion', 'origen_tabla', 'procedencia', 'tok']].rename(columns={'tok': 'ctok'}), on='idx')
n_ident = cd[cd.tipo_cruce == 'exacto'].groupby('persona_id').ident.apply(lambda s: len({x for x in s if not x.startswith('sen:')}))
n_ident = n_ident.to_dict()
tp_pairs = {(r.persona_id, r.institucion) for r in cd.itertuples() if r.origen_tabla == 'local' and r.tipo_cruce == 'exacto'}
tp_persona = {p for p, _ in tp_pairs}

def place(proc):
    proc = proc if isinstance(proc, str) else ''
    m = re.match(r'(?:alcald[ea]|concejal[a]?) de (.+)', proc or '')
    if m: return txt(m.group(1))
    m = re.search(r'\| (.+)$', proc or '')
    return txt(m.group(1)) if m else ''

def signal(r):
    s = []
    cv = CV.get(r.persona_id, '')
    kws = KW.get(r.institucion, [])
    hit = [k for k in kws if re.search(r'\b' + k, cv)]
    if hit:
        s.append('CV menciona «' + hit[0] + '»')
        pl = place(r.procedencia)
        if pl and len(pl) > 3 and pl in cv: s.append(f'CV menciona «{pl}»')
    if r.origen_tabla == 'oficial' and (r.persona_id, r.institucion) in tp_pairs: s.append('Transparentia coincide en institución')
    if r.institucion == 'Gobierno de España' and re.search(r'ministr|vicepresident|presidente del gobierno', ocu_cargos.get(r.persona_id, '').lower()): s.append('puesto actual de gobierno')
    return '; '.join(s)
cd['senal'] = [signal(r) for r in cd.itertuples()]
cd['n_ident_exacto'] = cd.persona_id.map(n_ident).fillna(0).astype(int)
cd['n_tok'] = cd.persona_id.map(per.set_index('persona_id').tok.map(len))

def cronologia_ok(i):
    f = allc.fecha_fin[i]; s = allc.fecha_inicio[i]
    return not (isinstance(f, str) and f < '1977') and not (isinstance(s, str) and s > '2026-11-02')
cd['cron_ok'] = [cronologia_ok(i) for i in cd.idx]

def clasif(r):
    sig = bool(r.senal); lo_ = r.origen_tabla == 'local'
    if not r.cron_ok: return 'dudoso', 'cronología imposible'
    if r.tipo_cruce == 'exacto':
        homon = r.n_ident_exacto > 1 and not lo_
        if lo_: return 'seguro', 'nombre completo exacto en ficha Transparentia del mismo altos cargo' + (f' + {r.senal}' if sig else '')
        if homon:
            return ('probable', f'varios homónimos en Wikidata; señal: {r.senal}') if sig else ('dudoso', 'varios homónimos en Wikidata sin señal de contexto')
        if sig: return 'seguro', 'nombre completo exacto + ' + r.senal
        return 'probable', 'nombre completo exacto (dos apellidos), sin contexto verificable'
    # cruces parciales: exigen señal
    if sig and r.tipo_cruce != 'exacto_2_palabras' or (sig and len(r.ctok) >= 2 and 'Transparentia' in r.senal): return 'probable', f'{r.tipo_cruce}; ' + r.senal
    return 'dudoso', f'{r.tipo_cruce} sin señal de contexto suficiente'
res = cd.apply(clasif, axis=1, result_type='expand'); cd['calidad'] = res[0]; cd['motivo'] = res[1]
# señal débil del CV (solo palabra genérica) no basta para parcial: exigir lugar/institución concreta o Transparentia
def parcial_fuerte(r):
    return 'Transparentia' in r.senal or 'puesto actual' in r.senal or r.senal.count('CV menciona') >= 2
m = (cd.tipo_cruce != 'exacto') & (cd.calidad == 'probable') & ~cd.apply(parcial_fuerte, axis=1)
cd.loc[m, ['calidad', 'motivo']] = ['dudoso', cd.loc[m, 'tipo_cruce'] + ' con señal débil']

# ---------- construir filas y deduplicar
x = cd.join(allc.drop(columns=['institucion', 'tok', 'ident', 'origen_tabla', 'procedencia']), on='idx')
x = x.merge(per[['persona_id', 'nombre_completo']], on='persona_id')
x['procedencia'] = allc.procedencia.reindex(x.idx).values
x['origen_tabla'] = allc.origen_tabla.reindex(x.idx).values
x['ident'] = allc.ident.reindex(x.idx).values
def yr(d): return int(d[:4]) if isinstance(d, str) else None
LEG = {  # calendario aproximado SOLO para detectar solapes Senado oficial/Wikidata (no se vuelca a la salida)
 'S0': ('1977-06-01', '1979-03-31'), 'S1': ('1979-03-01', '1982-08-31'), 'S2': ('1982-10-01', '1986-07-31'), 'S3': ('1986-07-01', '1989-10-31'),
 'S4': ('1989-11-01', '1993-04-30'), 'S5': ('1993-06-01', '1996-01-31'), 'S6': ('1996-03-01', '2000-01-31'), 'S7': ('2000-03-01', '2004-01-31'),
 'S8': ('2004-03-01', '2008-01-31'), 'S9': ('2008-03-01', '2011-09-30'), 'S10': ('2011-12-01', '2015-10-31'), 'S11': ('2015-12-01', '2016-05-31'),
 'S12': ('2016-07-01', '2019-03-31'), 'S13': ('2019-04-01', '2019-10-01'), 'S14': ('2019-11-01', '2023-05-31'), 'S15': ('2023-08-01', '2026-12-31')}
def rango(r):
    if r.institucion == 'Senado' and isinstance(r.legislatura, str) and r.legislatura in LEG: return LEG[r.legislatura]
    if not isinstance(r.fecha_inicio, str) and not isinstance(r.fecha_fin, str): return ('0000-00-00', '9999-99-99')  # sin fechas: no fusiona con fechados
    a = r.fecha_inicio if isinstance(r.fecha_inicio, str) else '1977-01-01'
    b = r.fecha_fin if isinstance(r.fecha_fin, str) else '2026-12-31'
    if len(a) == 4: a += '-01-01'
    if len(b) == 4: b += '-12-31'
    return (a, b)
x['ra'] = [rango(r)[0] for r in x.itertuples()]; x['rb'] = [rango(r)[1] for r in x.itertuples()]
x['sin_fecha'] = x.ra == '0000-00-00'
# prioridad: oficial con fecha (PE) > wikidata (fechas) > senado oficial (legislatura) > transparentia
prio = {'europarl': 0, 'Wikidata': 1, 'senado': 2, 'Transparentia': 3}
def pr(f):
    for k, v in prio.items():
        if k in f: return v
    return 9
x['pr'] = x.fuente.map(pr)
cal_ord = {'seguro': 0, 'probable': 1, 'dudoso': 2}
x['co'] = x.calidad.map(cal_ord)
x = x.sort_values(['persona_id', 'institucion', 'co', 'pr', 'ra']).reset_index(drop=True)

final = []; dropped = 0
for (pid, inst), g in x[x.calidad != 'dudoso'].groupby(['persona_id', 'institucion']):
    groups = []  # cada grupo = mandato; lista de filas solapadas
    for r in g.itertuples():
        for gr in groups:
            if any(((r.sin_fecha and o.sin_fecha and r.ident == o.ident) or (not r.sin_fecha and not o.sin_fecha and r.ra <= o.rb and o.ra <= r.rb)) and (inst != 'Alcaldía' or place(r.procedencia) == place(o.procedencia) or not place(r.procedencia) or not place(o.procedencia)) for o in gr):
                gr.append(r); break
        else: groups.append([r])
    for gr in groups:
        base = gr[0]; d = base._asdict()
        fuentes = sorted({o.fuente for o in gr}); urls = [o.url for o in gr]
        # fechas: preferir Wikidata/PE (con fecha), si no las que haya
        for o in gr:
            if isinstance(o.fecha_inicio, str): d['fecha_inicio'] = o.fecha_inicio; d['fecha_fin'] = o.fecha_fin; break
        for o in gr:
            if isinstance(o.partido, str) and not isinstance(d['partido'], str): d['partido'] = o.partido; d['partido_origen'] = o.partido_origen
        # partido con prioridad a qualifier P39 (partido del mandato)
        for o in gr:
            if isinstance(o.partido, str) and o.partido_origen == 'qualifier P39': d['partido'] = o.partido; d['partido_origen'] = o.partido_origen; break
        if not isinstance(d['partido'], str):
            g_ = [o.grupo for o in gr if isinstance(o.grupo, str)]
            if g_: d['partido_origen'] = f'sin partido; grupo parlamentario {g_[0]}'
        d['fuente'] = ' + '.join(fuentes); d['url'] = ' ; '.join(dict.fromkeys(urls))
        d['n_fuentes_fusionadas'] = len(gr); dropped += len(gr) - 1
        d['calidad'] = min((o.calidad for o in gr), key=cal_ord.get)
        d['legislatura'] = next((o.legislatura for o in gr if isinstance(o.legislatura, str)), None)
        final.append(d)
f = pd.DataFrame(final)
# duplicados exactos residuales (misma persona, institución, inicio, fin)
f = f.sort_values(['persona_id', 'institucion', 'fecha_inicio', 'co']).drop_duplicates(['persona_id', 'institucion', 'fecha_inicio', 'fecha_fin', 'partido'])
f['institucion_detalle'] = f.procedencia
out = pd.DataFrame({'persona_id': f.persona_id, 'nombre': f.nombre_completo, 'institucion': f.institucion, 'nivel_institucion': f.nivel,
    'partido': f.partido, 'partido_origen': f.partido_origen, 'inicio': f.fecha_inicio, 'fin': f.fecha_fin, 'fuente': f.fuente, 'url': f.url, 'calidad': f.calidad,
    'legislatura': f.legislatura, 'detalle': f.procedencia, 'nota_fecha': f.nota_fecha, 'n_fuentes_fusionadas': f.n_fuentes_fusionadas})
out = out.sort_values(['persona_id', 'inicio', 'institucion'])
out.to_csv(f'{OUT}/cargo_electo_persona.csv', index=False)

rev = x[x.calidad == 'dudoso']
rv = pd.DataFrame({'persona_id': rev.persona_id, 'nombre_persona': rev.nombre_completo, 'puesto_actual': rev.persona_id.map(ocu_cargos).str.slice(0, 120),
    'nombre_cargo': allc.persona_nombre.reindex(rev.idx).values, 'tipo_cruce': rev.tipo_cruce, 'institucion': rev.institucion, 'detalle': rev.procedencia,
    'partido': rev.partido, 'inicio': rev.fecha_inicio, 'fin': rev.fecha_fin, 'fuente': rev.fuente, 'url': rev.url, 'motivo_duda': rev.motivo})
rv = rv.drop_duplicates(['persona_id', 'institucion', 'nombre_cargo', 'detalle', 'inicio', 'fin']).sort_values(['persona_id', 'institucion'])
rv.to_csv(f'{OUT}/revision_cruces.csv', index=False)

# ---------- cifras
pers_ok = out.persona_id.nunique()
print('filas salida', len(out), 'personas', pers_ok, 'universo', len(per), 'fusionadas', dropped, 'dudosos', len(rv), 'personas dudosas', rv.persona_id.nunique())
print(out.calidad.value_counts().to_dict())
lv = out.groupby('nivel_institucion').persona_id.nunique().sort_values(ascending=False)
print(lv)
FAM = [('socialista obrero', 'PSOE (incl. PSC, PSdeG, PSE)'), ('psoe', 'PSOE (incl. PSC, PSdeG, PSE)'), ('socialistas de catalu', 'PSOE (incl. PSC, PSdeG, PSE)'),
       ('psc', 'PSOE (incl. PSC, PSdeG, PSE)'), ('psde', 'PSOE (incl. PSC, PSdeG, PSE)'), ('pse-ee', 'PSOE (incl. PSC, PSdeG, PSE)'),
       ('partido popular', 'PP'), ('pp', 'PP'), ('alianza popular', 'PP'), ('nacionalista vasco', 'PNV'), ('esquerra', 'ERC'),
       ('convergència', 'CiU/Junts/PDeCAT'), ('convergencia', 'CiU/Junts/PDeCAT'), ('junts', 'CiU/Junts/PDeCAT'), ('pdecat', 'CiU/Junts/PDeCAT'),
       ('ciudadanos', 'Cs'), ('podemos', 'Podemos/Sumar/IU/confluencias'), ('sumar', 'Podemos/Sumar/IU/confluencias'), ('comunista', 'Podemos/Sumar/IU/confluencias'),
       ('izquierda unida', 'Podemos/Sumar/IU/confluencias'), ('más madrid', 'Podemos/Sumar/IU/confluencias'), ('en comú', 'Podemos/Sumar/IU/confluencias'),
       ('verds', 'Podemos/Sumar/IU/confluencias'), ('equo', 'Podemos/Sumar/IU/confluencias'), ('marea', 'Podemos/Sumar/IU/confluencias'),
       ('cambiemos', 'Podemos/Sumar/IU/confluencias'), ('vox', 'Vox'), ('unión de centro', 'UCD'), ('bildu', 'EH Bildu'),
       ('coalición canaria', 'Coalición Canaria'), ('geroa', 'Geroa Bai'), ('independiente', 'independiente')]
def party_fams(p):
    if not isinstance(p, str): return {'sin partido / no consta'}
    out_ = set()
    for part in p.split(';'):
        t = part.strip().lower()
        out_.add(next((v for k, v in FAM if k in t), 'otros'))
    return out_
# una persona puede tener varios partidos: contar personas por partido normalizado (sobre filas)
pe_ = out.assign(partido_n=out.partido.map(party_fams)).explode('partido_n')
pp = pe_.groupby('partido_n').persona_id.nunique().sort_values(ascending=False)
print(pp)
ni = out.groupby(['nivel_institucion', 'calidad']).persona_id.nunique().unstack(fill_value=0)
ps = out.groupby('persona_id').calidad.apply(lambda s: 'seguro' if 'seguro' in set(s) else 'probable')
vs = out.groupby('persona_id').partido_origen.apply(lambda s: 'mandato' if (s == 'qualifier P39').any() else 'otro')
def md(df): return df.to_markdown() if hasattr(df, 'to_markdown') else df.to_string()
try:
    import tabulate  # noqa
except ImportError:
    md = lambda d: '```\n' + d.to_string() + '\n```'
inst = out.groupby('institucion').persona_id.nunique().sort_values(ascending=False)
open(f'{OUT}/cifras.txt', 'w').write('\n'.join([
 f'universo (no excluidos): {len(per)}', f'personas con algún cargo (seguro+probable): {pers_ok}',
 f'  con al menos un seguro: {(ps=="seguro").sum()}  solo probable: {(ps=="probable").sum()}',
 f'filas de mandato: {len(out)}; filas fusionadas por duplicado entre fuentes: {dropped}',
 f'cruces dudosos (revision_cruces.csv): {len(rv)} filas, {rv.persona_id.nunique()} personas',
 'POR NIVEL', md(lv.to_frame('personas')), 'POR NIVEL Y CALIDAD', md(ni), 'POR INSTITUCION', md(inst.to_frame('personas')),
 'POR PARTIDO (normalizado; una persona cuenta en cada partido con el que aparece)', md(pp.to_frame('personas')),
 f'partido del mandato (qualifier P39 o equivalente) en {(out.partido_origen=="qualifier P39").sum()} filas; resto es partido de la persona sin fechas o de Transparentia']))
