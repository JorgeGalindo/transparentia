"""Cola de tareas por API (claude -p headless con el token OAuth del llavero, solo en el proceso hijo).

Cada tarea es tareas/NNN-nombre.md con cabecera:
    modelo: haiku|sonnet|opus
    salida: ruta relativa a altos_cargos_2026/
    estado: pendiente|hecha|fallida|manual
    prioridad: 1-3
    ---
    <encargo>
El encargo se antepone con tareas/_comun.md.

Uso (desde altos_cargos_2026/):
    python3 scripts/cola.py               # estado de la cola
    python3 scripts/cola.py run [--max 3] [--solo 004] [--build]
"""
import os, re, sys, glob, subprocess, datetime, concurrent.futures as cf
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TD = os.path.join(BASE, 'tareas'); LOG = os.path.join(TD, 'logs'); os.makedirs(LOG, exist_ok=True)

def leer(p):
    t = open(p, encoding='utf-8').read(); head, _, body = t.partition('\n---\n')
    h = dict(re.findall(r'^(\w+):\s*(.*)$', head, re.M)); h['body'] = body.strip(); h['path'] = p
    h['id'] = os.path.basename(p).split('-')[0]; h['nombre'] = os.path.basename(p)[:-3]; return h

def marcar(p, estado):
    t = open(p, encoding='utf-8').read()
    t = re.sub(r'^estado:.*$', f'estado: {estado}', t, count=1, flags=re.M)
    t = re.sub(r'^ejecutada:.*\n', '', t, flags=re.M).replace('\n---\n', f'\nejecutada: {datetime.datetime.now():%Y-%m-%d %H:%M}\n---\n', 1)
    open(p, 'w', encoding='utf-8').write(t)

def tareas(): return sorted([leer(p) for p in glob.glob(os.path.join(TD, '[0-9]*.md'))], key=lambda h: (h.get('prioridad', '2'), h['id']))

def correr(h):
    comun = open(os.path.join(TD, '_comun.md'), encoding='utf-8').read().replace('{HOY}', datetime.date.today().isoformat())
    salida = os.path.join(BASE, h['salida'])
    prompt = comun + '\n\nTAREA ' + h['nombre'] + ':\n' + h['body'].replace('{BASE}', BASE) + f'\n\nEscribe la salida en: {salida}'
    tok = subprocess.run(['security', 'find-generic-password', '-a', os.environ['USER'], '-s', 'anthropic-api-key', '-w'],
                         capture_output=True, text=True).stdout.strip()
    env = dict(os.environ, CLAUDE_CODE_OAUTH_TOKEN=tok)
    if os.path.exists(salida): os.remove(salida)
    with open(os.path.join(LOG, h['nombre'] + '.log'), 'w') as lg:
        r = subprocess.run(['claude', '-p', prompt, '--model', h.get('modelo', 'sonnet'), '--allowedTools', 'Bash,Read,Write,Edit,WebSearch,WebFetch',
                            '--permission-mode', 'acceptEdits', '--add-dir', BASE, '--output-format', 'text'],
                           cwd=BASE, env=env, stdout=lg, stderr=subprocess.STDOUT)
    ok = r.returncode == 0 and os.path.exists(salida)
    marcar(h['path'], 'hecha' if ok else 'fallida')
    return h['nombre'], ok

def main():
    a = sys.argv; ts = tareas()
    if len(a) < 2:
        for h in ts: print(f"{h['id']}  {h.get('estado','?'):9} {h.get('modelo','?'):7} p{h.get('prioridad','?')}  {h['nombre']}")
        return
    mx = int(a[a.index('--max') + 1]) if '--max' in a else 3
    sel = [h for h in ts if h.get('estado') == 'pendiente']
    if '--solo' in a: sel = [h for h in ts if h['id'] == a[a.index('--solo') + 1]]
    print('lanzando:', [h['nombre'] for h in sel])
    with cf.ThreadPoolExecutor(mx) as ex:
        for nombre, ok in ex.map(correr, sel): print(('OK   ' if ok else 'FALLO'), nombre)
    if '--build' in a: subprocess.run(['./scripts/build.sh'], cwd=BASE)

if __name__ == '__main__':
    main()
