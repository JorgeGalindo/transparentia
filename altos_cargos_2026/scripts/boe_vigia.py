"""Vigía del BOE (sin LLM). Lee los sumarios diarios (API datosabiertos), sección II.A, y extrae
nombramientos y ceses por Real Decreto de altos cargos de la AGE. Los cruza con la tabla de estructura.

Uso:  python3 boe_vigia.py [--desde AAAAMMDD] [--hasta AAAAMMDD]
- Sin --desde, sigue desde la última fecha en data/seguimiento/boe_estado.json.
- Escribe/actualiza data/seguimiento/boe_cambios.csv (append, sin duplicados por identificador).
Lo aplica build.sh vía aplicar_boe.py: un nombramiento posterior a la fecha de la base sustituye al titular.
"""
import json, re, csv, sys, os, datetime, unicodedata, urllib.request, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEG = os.path.join(BASE, 'data', 'seguimiento'); os.makedirs(SEG, exist_ok=True)
EST = os.path.join(SEG, 'boe_estado.json'); OUT = os.path.join(SEG, 'boe_cambios.csv')
H = ['fecha_boe', 'identificador', 'departamento', 'tipo', 'nombre', 'cargo', 'titulo', 'url']
CARGO = r'(Secretari[oa] de Estado|Subsecretari[oa]|Secretari[oa] General|Director[a]? General|Director[a]? del Gabinete|Delegad[oa] del Gobierno|Comisionad[oa]|Presidente|Presidenta|Director[a]? del Departamento|Director[a]? de la Oficina|Embajador[a]?|Jefe del Estado Mayor|Fiscal General|Abogad[oa] General|Interventor[a]? General)'

def get(fecha):
    req = urllib.request.Request(f'https://www.boe.es/datosabiertos/api/boe/sumario/{fecha}', headers={'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
    except Exception:
        return None          # domingos / sin BOE -> 404

def L(x): return x if isinstance(x, list) else ([] if x is None else [x])

def parse(t):
    t = re.sub(r'\s+', ' ', t)
    m = re.search(r'por el que se nombra (.+?) a (?:don|doña|D\.|Dña\.) (.+?)\.?$', t)
    if m and re.search(CARGO, m.group(1)): return 'nombramiento', m.group(2).strip(' .'), m.group(1).strip()
    m = re.search(r'por el que se dispone el cese (?:, a petición propia, )?de (?:don|doña|D\.|Dña\.) (.+?) como (.+?)\.?$', t)
    if m and re.search(CARGO, m.group(2)): return 'cese', m.group(1).strip(' ,.'), m.group(2).strip()
    return None

def main():
    a = sys.argv
    est = json.load(open(EST)) if os.path.exists(EST) else {'ultima_fecha': '20261031'}
    desde = a[a.index('--desde') + 1] if '--desde' in a else (datetime.datetime.strptime(est['ultima_fecha'], '%Y%m%d') + datetime.timedelta(days=1)).strftime('%Y%m%d')
    hasta = a[a.index('--hasta') + 1] if '--hasta' in a else datetime.date.today().strftime('%Y%m%d')
    prev = {}
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding='utf-8')): prev[r['identificador']] = r
    d = datetime.datetime.strptime(desde, '%Y%m%d'); fin = datetime.datetime.strptime(hasta, '%Y%m%d'); n = 0
    while d <= fin:
        f = d.strftime('%Y%m%d'); js = get(f)
        if js:
            for dia in L(js['data']['sumario']['diario']):
                for sec in L(dia['seccion']):
                    if sec.get('codigo') != '2A': continue
                    for dep in L(sec.get('departamento')):
                        for ep in L(dep.get('epigrafe')):
                            for it in L(ep.get('item')):
                                t = it['titulo']
                                if not t.startswith('Real Decreto'): continue
                                p = parse(t)
                                if not p: continue
                                prev[it['identificador']] = dict(fecha_boe=f, identificador=it['identificador'], departamento=dep['nombre'],
                                    tipo=p[0], nombre=p[1], cargo=p[2], titulo=t, url=(it.get('url_html') or ''))
                                n += 1
            time.sleep(0.3)
        d += datetime.timedelta(days=1)
    rows = sorted(prev.values(), key=lambda r: (r['fecha_boe'], r['identificador']))
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=H); w.writeheader(); w.writerows(rows)
    json.dump({'ultima_fecha': hasta, 'actualizado': datetime.datetime.now().isoformat(timespec='seconds')}, open(EST, 'w'))
    print(f'BOE {desde}-{hasta}: {n} nombramientos/ceses de altos cargos; total en registro {len(rows)}')

if __name__ == '__main__':
    main()
