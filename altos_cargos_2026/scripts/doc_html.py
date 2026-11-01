"""Convierte ARQUITECTURA.md en docs/arquitectura.html (autónomo), sustituyendo el bloque ASCII del diagrama
por docs/arquitectura.svg. Uso: uv run -q --with markdown python -I scripts/doc_html.py"""
import os, re, markdown
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
md = open(os.path.join(B, 'ARQUITECTURA.md'), encoding='utf-8').read()
md = re.sub(r'<!--DIAGRAMA-->.*?<!--/DIAGRAMA-->', '@@DIAGRAMA@@', md, flags=re.S)
md = re.sub(r'(?m)^   (- |\S)', r'    \1', md)  # Python-Markdown pide 4 espacios en listas anidadas
body = markdown.markdown(md, extensions=['tables', 'fenced_code'])
svg = open(os.path.join(B, 'docs/arquitectura.svg'), encoding='utf-8').read()
fig = ('<figure>' + svg + '<figcaption>Flujo de la fase 2. En azul, el circuito hacia delante: los vigías semanales '
       '(BOE, BORME y Consejo de Ministros) meten nombramientos y ceses en la base sin pasar por un modelo. El '
       'enriquecimiento agéntico solo rellena huecos y siempre devuelve evidencia citada.</figcaption></figure>')
body = body.replace('<p>@@DIAGRAMA@@</p>', fig).replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
css = """
:root{--bg:#f6f6f3;--panel:#fff;--ink:#1a222b;--muted:#5d6874;--line:#dcdfda;--accent:#1d4e89;
 --f-display:"Archivo","Helvetica Neue",Arial,sans-serif;--f-body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#12171d;--panel:#1a2129;--ink:#e6e9ec;--muted:#9aa5b1;--line:#2b343e;--accent:#8ab8ee;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12171d;--panel:#1a2129;--ink:#e6e9ec;--muted:#9aa5b1;--line:#2b343e;--accent:#8ab8ee;color-scheme:dark}
*{box-sizing:border-box} html,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--f-body)}
main{max-width:980px;margin:0 auto;padding:28px 18px 64px}
h1{font:800 28px/1.15 var(--f-display);margin:0 0 6px;text-wrap:balance}
h2{font:700 19px/1.25 var(--f-display);margin:36px 0 10px;color:var(--accent);text-wrap:balance}
p,li{max-width:72ch} li{margin:3px 0} strong{font-weight:600}
code{font:13.5px var(--f-mono);background:color-mix(in srgb,var(--accent) 10%,transparent);padding:1px 5px;border-radius:4px}
pre{overflow-x:auto} .tw{overflow-x:auto;margin:10px 0;border:1px solid var(--line);border-radius:6px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:14px} th,td{text-align:left;vertical-align:top;padding:7px 10px;border-bottom:1px solid var(--line)}
th{font-size:12.5px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);font-weight:600} tr:last-child td{border-bottom:0}
figure{margin:12px 0 4px;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}
figure svg{display:block;width:100%;min-width:760px;height:auto;color:var(--ink)}
figcaption{font-size:14px;color:var(--muted);margin-top:8px;max-width:80ch}
h1+p{color:var(--muted);font-size:14.5px}
"""
html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arquitectura de la base de nombramientos</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap" rel="stylesheet">
<style>{css}</style></head><body><main>{body}</main></body></html>"""
os.makedirs(os.path.join(B, 'docs'), exist_ok=True)
open(os.path.join(B, 'docs/arquitectura.html'), 'w', encoding='utf-8').write(html)
print('docs/arquitectura.html', len(html) // 1024, 'KB')
