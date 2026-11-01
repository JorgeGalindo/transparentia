"""Comprueba que cada cita de las fichas (fase2/literatura/fichas/<id>.json) está en la página del PDF que dice.

«p. X» = página X del PDF leído (1 = primera página del fichero), tal como la separa pdftotext con \f.
Normaliza ligaduras, comillas, guiones de fin de línea y espacios. Una cita con «…» o «...» se parte en trozos y
cada trozo debe aparecer en esa página, en orden. «p. 5-6» busca en las dos páginas juntas.
Resultado por cita: exacta | aprox (coincide sin espacios ni guiones, sin mayúsculas) | otra_pagina:<n> | no.

Uso:
  uv run -q python -I fase2/literatura/verificar_citas.py            # todas las fichas
  uv run -q python -I fase2/literatura/verificar_citas.py <id> ...   # solo esas
  uv run -q python -I fase2/literatura/verificar_citas.py --paginar <id>   # escribe txt/<id>.paginado.txt
Sale con código 1 si alguna cita queda en «no» u «otra_pagina».
"""
import glob, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.normpath(os.path.join(HERE, "..", "data", "raw", "literatura", "txt"))
FICHAS = os.path.join(HERE, "fichas")

def paginas(i):
    t = open(os.path.join(TXT, i + ".txt"), encoding="utf-8", errors="replace").read()
    return t.split("\f")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")
    for a, b in (("“", '"'), ("”", '"'), ("„", '"'), ("‘", "'"), ("’", "'"), ("`", "'"), ("´", "'"),
                 ("–", "-"), ("—", "-"), ("‐", "-"), ("‑", "-"), ("−", "-"), ("«", '"'), ("»", '"')):
        s = s.replace(a, b)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)     # guion de fin de línea
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def laxo(s):
    return re.sub(r"[\s\-'\".,;:()\[\]]", "", norm(s)).lower()

def trozos(c):
    return [x.strip() for x in re.split(r"…|\.\.\.|\[\.\.\.\]|\[…\]", c) if x.strip()]

def en(texto, c, f):
    pos = 0; T = f(texto)
    for tr in trozos(c):
        k = T.find(f(tr), pos)
        if k < 0: return False
        pos = k
    return True

def rango(p):
    m = re.fullmatch(r"\s*(\d+)\s*(?:[-–]\s*(\d+))?\s*", str(p))
    if not m: return None
    a = int(m.group(1)); b = int(m.group(2) or a)
    return list(range(a, b + 1))

def comprobar(i, cita, pag, P):
    r = rango(pag)
    if not r or r[0] < 1 or r[-1] > len(P): return "no (página fuera de rango)"
    texto = "\n".join(P[k - 1] for k in r)
    # al unir guiones de fin de línea, «well-\nknown» queda «wellknown»: el modo laxo lo cubre
    if en(texto, cita, norm): return "exacta"
    if en(texto, cita, laxo): return "aprox"
    for k in range(1, len(P) + 1):
        tt = P[k - 1] + "\n" + (P[k] if k < len(P) else "")
        if en(tt, cita, laxo): return f"otra_pagina:{k}"
    return "no"

def paginar(i):
    P = paginas(i)
    out = os.path.join(TXT, i + ".paginado.txt")
    with open(out, "w", encoding="utf-8") as f:
        for k, p in enumerate(P, 1):
            if k == len(P) and not p.strip(): break
            f.write(f"\n=== PÁGINA PDF {k} ===\n{p}")
    print(out)

def main():
    a = sys.argv[1:]
    if a and a[0] == "--paginar":
        for i in a[1:]: paginar(i)
        return
    fs = [os.path.join(FICHAS, x + ".json") for x in a] if a else sorted(glob.glob(os.path.join(FICHAS, "*.json")))
    malas = 0; tot = 0
    for fn in fs:
        d = json.load(open(fn))
        if d.get("estado") != "leído": continue
        P = paginas(d["id"])
        for c in d.get("citas", []):
            tot += 1
            res = comprobar(d["id"], c["cita"], c["pagina"], P)
            if not (res in ("exacta", "aprox")):
                malas += 1
                print(f"{d['id']} [{c['n']}] p. {c['pagina']}: {res} :: {c['cita'][:90]}")
    print(f"citas: {tot} · fallos: {malas}")
    sys.exit(1 if malas else 0)

if __name__ == "__main__":
    main()
