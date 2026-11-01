#!/usr/bin/env python3
"""Regenera los bloques de Moncloa cuyo texto quedó pisado en fuentes/cv/texto/ (bug de la tarea 106: la regex de fecha
`/(\\d{8})` no casa con URLs `.../refc20230110.aspx`, así que 224 bloques se guardaron como `moncloa_sd_N` y 186 se
sobrescribieron). Usa el HTML bruto de data/raw/cv/moncloa/ y la MISMA lógica de bloques que construir_manifiesto.py.
No toca fuentes/: escribe work/texto_moncloa/ y manifiesto_cv_corregido.csv. Comprueba que el sha1 de cada bloque
regenerado coincide con el del manifiesto original, en el mismo orden.
Uso: uv run -q python -I fase2/extraccion/reparar_moncloa.py
"""
import csv, hashlib, html, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CV = RAIZ / "fase2/fuentes/cv"
OUT = RAIZ / "fase2/extraccion"
DEST = OUT / "work/texto_moncloa"
DEST.mkdir(parents=True, exist_ok=True)
NAME = re.compile(r"^(D\.|Dª\.?|Dña\.?|Don|Doña)\s+([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ' .-]+)$")


def txt(f):
    t = Path(f).read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"</(p|h\d|li|div|tr)>", "\n", t); t = re.sub(r"<br\s*/?>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t)); t = re.sub(r"[ \t\xa0]+", " ", t)
    return [l.strip() for l in re.split(r"\n", t) if l.strip()]


def clave_ref(url, ruta):
    m = re.search(r"(\d{8})", Path(ruta).name) or re.search(r"(\d{8})", url)
    if m:
        return m.group(1)
    return "u" + hashlib.sha1(url.encode()).hexdigest()[:8]     # sin fecha en nombre ni URL


orig = list(csv.DictReader(open(CV / "manifiesto_cv.csv", encoding="utf-8")))
mon = [r for r in orig if r["fuente"] == "moncloa"]
nuevos, n = [], 0
for ref in csv.DictReader(open(CV / "moncloa_referencias.csv", encoding="utf-8")):
    L = txt(ref["ruta_local"])
    for j, l in enumerate(L):
        if l.startswith("Mapa del sitio"):
            L = L[:j]; break
    idx = [i for i, l in enumerate(L) if NAME.match(l)]
    clave = clave_ref(ref["url"], ref["ruta_local"])
    for k, i in enumerate(idx):
        end = (idx[k + 1] - 2) if k + 1 < len(idx) else min(len(L), i + 9)
        bio = L[i + 1:max(i + 1, end)]
        for j, l in enumerate(bio):
            if re.match(r"^(ACUERDO|REAL DECRETO|ORDEN|RESOLUCI[ÓO]N|CORRECCI[ÓO]N)\b", l) or (len(l) > 25 and l.isupper()):
                bio = bio[:j]; break
        cargo_tmp = L[i - 1] if i >= 1 else ""
        bt = "\n".join(bio)
        if len(bt) < 150 or not re.search(r"(?i)licencia|licenciad|ingenier|doctor|grado|máster|funcionari|carrera|ha sido|ejerci", bt):
            continue
        cargo = cargo_tmp if len(cargo_tmp) < 200 else cargo_tmp[:200] + "…"
        mini = L[i - 2] if i >= 2 else ""
        body = f"{L[i]}\n{cargo}\n{mini}\n{bt}\n"
        sha = hashlib.sha1(body.encode()).hexdigest()
        assert sha == mon[n]["sha1"], f"bloque {n} no coincide con el manifiesto original ({ref['url']})"
        f = DEST / f"moncloa_{clave}_{k + 1}.txt"
        f.write_text(body, encoding="utf-8")
        nuevos.append({**mon[n], "ruta_local": str(f)})
        n += 1
assert n == len(mon), (n, len(mon))
res, it = [], iter(nuevos)
for r in orig:
    res.append(next(it) if r["fuente"] == "moncloa" else r)
with open(OUT / "manifiesto_cv_corregido.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(orig[0].keys())); w.writeheader(); w.writerows(res)
print("bloques Moncloa regenerados:", n, "| ids únicos:", len({Path(r['ruta_local']).stem for r in res}), "de", len(res))
