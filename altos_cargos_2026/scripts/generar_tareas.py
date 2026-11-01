"""Genera tareas de la cola a partir del estado de los datos (sin LLM):
- refresco de consejos con fecha_dato anterior a CORTE o sin verificar (grupos de 5 entidades, Sonnet);
- verificación muestral mensual de titulares de altos cargos (30 filas al azar, Sonnet).
No duplica tareas pendientes ya existentes. Uso: python3 scripts/generar_tareas.py [--corte AAAA-MM-DD]"""
import os, sys, glob, re, datetime, pandas as pd
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); TD = os.path.join(BASE, 'tareas')
a = sys.argv
corte = a[a.index('--corte') + 1] if '--corte' in a else (datetime.date.today() - datetime.timedelta(days=150)).isoformat()
exist = [open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(TD, '[0-9]*.md'))]
pend = '\n'.join(t for t in exist if re.search(r'^estado:\s*pendiente', t, re.M))
nid = max([int(os.path.basename(p)[:3]) for p in glob.glob(os.path.join(TD, '[0-9]*.md'))] + [0]) + 1
def nueva(nombre, modelo, salida, prio, cuerpo):
    global nid
    p = os.path.join(TD, f'{nid:03d}-{nombre}.md')
    open(p, 'w', encoding='utf-8').write(f'modelo: {modelo}\nsalida: {salida}\nestado: pendiente\nprioridad: {prio}\n---\n{cuerpo}\n')
    print('creada', os.path.basename(p)); nid += 1
e = pd.read_csv(os.path.join(BASE, 'data/empresas_publicas_consejos.csv')).fillna('')
g = e.groupby('empresa').agg(fecha=('fecha_dato_iso', 'max'), verif=('estado_dato', lambda s: (s == 'actual verificado').mean()), bloque=('bloque', 'first'))
g = g[~g.index.str.contains('Autoridad Portuaria|liquidación')]
st = g[(g.fecha < corte) | ((g.verif == 0) & (g.fecha < '2026-09-01'))].sort_values('fecha')
st = st[[n not in pend for n in st.index]]
ents = list(st.index)
for i in range(0, len(ents), 5):
    grupo = ents[i:i + 5]; tag = datetime.date.today().strftime('%Y%m%d')
    lista = '\n'.join(f'- {n} (dato actual: {st.loc[n, "fecha"] or "sin fecha"})' for n in grupo)
    nueva(f'refresco-consejos-{tag}-{i // 5 + 1}', 'sonnet', f'data/consejos_por_bloque/tarea_refresco_{tag}_{i // 5 + 1}.csv', 2,
          'Refresca el consejo de administración COMPLETO y el primer ejecutivo de estas entidades (sustituye a lo que hay en la base; '
          'puedes ver lo actual en {BASE}/data/empresas_publicas_consejos.csv). Busca cambios posteriores a la fecha del dato actual:\n' + lista)
mes = datetime.date.today().strftime('%Y%m')
if not glob.glob(os.path.join(TD, f'*-verificacion-{mes}.md')):
    o = pd.read_csv(os.path.join(BASE, 'data/altos_cargos_estructura.csv')).fillna('')
    s = o[(o.nivel > 1) & (o.titular != '') & (~o.titular.str.startswith('('))].sample(30, random_state=int(mes))
    os.makedirs(os.path.join(BASE, 'data/verificacion'), exist_ok=True)
    s[['ministerio', 'unidad', 'titular']].to_csv(os.path.join(BASE, f'data/verificacion/muestra_{mes}.csv'), index=False)
    nueva(f'verificacion-{mes}', 'sonnet', f'data/verificacion/resultado_{mes}.csv', 1,
          f'Verifica si cada titular de {{BASE}}/data/verificacion/muestra_{mes}.csv sigue en el cargo hoy (BOE sección II.A, '
          'Consejo de Ministros). NO uses el formato de consejos: escribe CSV con columnas '
          'ministerio,unidad,titular_actual,estado,fuente_url,fecha_nombramiento,nota (estado: confirmado/corregido/vacante/no verificable). '
          'Resume la tasa de error.')
