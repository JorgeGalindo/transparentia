"""L3 (tarea 107): consigue el texto completo LEGAL de los trabajos de relevancia 3 de cribado.csv.

Para cada trabajo prueba, en orden, las URL candidatas de abajo (repositorio institucional, versión de trabajo del
autor, SSRN/RePEc, editorial en abierto). Nada de webs piratas. User-agent honesto y >=1,2 s entre peticiones.
Guarda el PDF en fase2/data/raw/literatura/pdf/<id>.pdf, el texto por páginas en fase2/data/raw/literatura/txt/<id>.txt
(pdftotext; las páginas van separadas por \f) y anota cada intento en textos_log.csv. Reanudable: si el PDF ya existe,
no lo vuelve a bajar.

Uso: uv run -q --with requests python -I fase2/literatura/textos.py
"""
import csv, datetime, json, os, re, subprocess, sys, time
from urllib.parse import urljoin, urlparse
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.normpath(os.path.join(HERE, "..", "data", "raw", "literatura"))
PDF = os.path.join(RAW, "pdf"); TXT = os.path.join(RAW, "txt")
os.makedirs(PDF, exist_ok=True); os.makedirs(TXT, exist_ok=True)
UA = {"User-Agent": "altos_cargos_2026-literatura/0.1 (EsadeEcPol research script; python-requests)"}
LOG = os.path.join(HERE, "textos_log.csv")
HOY = datetime.date.today().isoformat()

# id -> (doi, [candidatas]). Tipo de candidata: url directa a PDF, página de aterrizaje (se busca citation_pdf_url
# o enlaces .pdf/bitstream) o "dspace7:<base>|<handle>" (repositorios DSpace 7, que no sirven enlaces en el HTML).
C = {
 "lewis2008": ("10.1515/9781400837687", []),
 "gomez_verge2012": ("10.1093/acprof:oso/9780199599370.003.0016", []),
 "kopecky_mair_spirova2012": ("10.1093/acprof:oso/9780199599370.001.0001",
     ["dspace7:https://cadmus.eui.eu|1814/23874"]),
 "ennser2013_gov": ("10.1111/gove.12023", []),
 "ennser2013_ps": ("10.1111/1467-9248.12031", ["https://ideas.repec.org/a/bla/polstu/v62y2014i2p398-417.html"]),
 "guerra_bona_santana2014": ("10.1016/j.brq.2014.10.002",
     ["https://www.econstor.eu/handle/10419/206329", "https://www.sciencedirect.com/science/article/pii/S2340943614000681/pdf",
      "https://accedacris.ulpgc.es/handle/10553/21487"]),
 "kopecky_etal2016": ("10.1111/1475-6765.12135",
     ["https://scholarlypublications.universiteitleiden.nl/access/item%3A2886272/download",
      "https://ri.conicet.gov.ar/handle/11336/98984",
      "https://researchonline.lse.ac.uk/id/eprint/64829/1/Panizza_Party%20patronage_2016.pdf"]),
 "ennser2016_nl": ("10.1057/s41269-016-0005-1", []),
 "realdato_rodriguezteruel2016": ("10.1057/ap.2016.6",
     ["https://producciocientifica.uv.es/documentos/5eef23b62999522e441e3a71"]),
 "fleischer2016": ("10.1057/s41269-016-0006-0",
     ["https://link.springer.com/content/pdf/10.1057%2Fs41269-016-0006-0.pdf"]),
 "bach_veit2017": ("10.1093/jopart/mux041",
     ["https://www.duo.uio.no/bitstream/handle/10852/59457/1/Bach_Veit_2017_Determinants_of_Promotion_to_High_Public_Office.pdf",
      "https://www.duo.uio.no/handle/10852/59457",
      "https://academic.oup.com/jpart/article-pdf/28/2/254/24283466/mux041.pdf"]),
 "dahlstrom_lapuente2017": ("10.1017/9781316822869", []),
 "panizza_peters_ramos2018": ("10.1111/padm.12560",
     ["https://researchonline.lse.ac.uk/id/eprint/90561/1/Panizza_Roles%2C%20trust%20and%20skills_2018.pdf"]),
 "brierley2020": ("10.1086/708240",
     ["https://researchonline.lse.ac.uk/id/eprint/101430/1/Brierley_Combining_Manuscript.pdf"]),
 "deandres_etal2020": ("10.1177/2340944420924417",
     ["https://www.econstor.eu/handle/10419/261898", "https://repositorio.uam.es/handle/10486/702505",
      "https://journals.sagepub.com/doi/pdf/10.1177/2340944420924417"]),
 "colonnelli_prem_teso2020": ("10.1257/aer.20181491",
     ["dspace7:https://repository.urosario.edu.co|10336/18526", "https://www.econstor.eu/bitstream/10419/262694/1/wp292.pdf",
      "https://repec.cepr.org/repec/cpr/ceprdp/DP13697.pdf"]),
 "staronova_rybar2020": ("10.1177/0095399720956996",
     ["https://www.muni.cz/vyzkum/publikace/1680507", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3693856"]),
 "askim_bach_christensen2022": ("10.1080/01402382.2022.2148195",
     ["https://pure.au.dk/portal/en/publications/d4f4ea36-be3e-4be5-8d6f-04f733306f5e",
      "https://www.duo.uio.no/bitstream/10852/98113/1/Askim_Bach_Christensen_2022_postprint_version.pdf"]),
 "garciacestona_sagarra2022": ("10.1080/02102412.2021.2024012",
     ["dspace7:https://diposit.ub.edu|2445/192708", "https://diposit.ub.edu/dspace/bitstream/2445/192708/1/719486.pdf"]),
 "veit_vedder2023": ("10.1111/padm.12967",
     ["https://www.econstor.eu/handle/10419/306223", "https://doi.org/10.17170/kobra-2024092010859",
      "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/padm.12967"]),
 "baltrunaite_etal2023": ("10.1093/jleo/ewad014",
     ["https://www.bancaditalia.it/pubblicazioni/temi-discussione/2021/2021-1328/en_tema_1328.pdf"]),
 "toral2023": ("10.1111/ajps.12758",
     ["dspace7:https://repositorio.ie.edu|20.500.14417/3111",
      "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ajps.12758"]),
 "toral2024": ("10.1086/729961", ["dspace7:https://repositorio.ie.edu|20.500.14417/3624"]),
}

_last = {}
def get(url, **kw):
    dom = urlparse(url).netloc
    w = 1.2 - (time.time() - _last.get(dom, 0))
    if w > 0: time.sleep(w)
    try:
        return requests.get(url, headers=UA, timeout=(8, 45), allow_redirects=True, **kw)
    finally:
        _last[dom] = time.time()

def log(i, url, status, res):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["id", "url", "status", "resultado", "fecha"])
        w.writerow([i, url, status, res, HOY])

def es_pdf(r):
    return r.status_code == 200 and r.content[:5] == b"%PDF-"

def links_pdf(r):
    html = r.text
    out = re.findall(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', html, re.I)
    out += [l for l in re.findall(r'href=["\']([^"\']+)["\']', html)
            if re.search(r'\.pdf(\?|$)|/bitstream/|/files/|OutputFile|/download', l, re.I)]
    seen, res = set(), []
    for l in out:
        u = urljoin(r.url, l.replace("&amp;", "&"))
        if u not in seen and u != r.url: seen.add(u); res.append(u)
    return res[:6]

def dspace7(base, handle):
    r = get(f"{base}/server/api/pid/find", params={"id": f"hdl:{handle}"})
    if r.status_code != 200: return [], r.status_code
    it = r.json()
    b = get(it["_links"]["bundles"]["href"])
    urls = []
    for bun in b.json().get("_embedded", {}).get("bundles", []):
        if bun.get("name") != "ORIGINAL": continue
        bs = get(bun["_links"]["bitstreams"]["href"]).json()
        for x in bs.get("_embedded", {}).get("bitstreams", []):
            urls.append(x["_links"]["content"]["href"])
    return urls, 200

def bajar(i, cands):
    dest = os.path.join(PDF, i + ".pdf")
    for c in cands:
        if c.startswith("dspace7:"):
            base, h = c[8:].split("|")
            try: urls, st = dspace7(base, h)
            except Exception as e: log(i, c, "ERR", repr(e)[:120]); continue
            log(i, c, st, f"{len(urls)} bitstreams"); sub = urls
        else:
            sub = [c]
        for u in sub:
            try: r = get(u)
            except Exception as e: log(i, u, "ERR", repr(e)[:120]); continue
            if es_pdf(r):
                open(dest, "wb").write(r.content); log(i, u, r.status_code, "pdf"); return u
            ct = r.headers.get("content-type", "")
            log(i, u, r.status_code, ct[:40])
            if r.status_code == 200 and "html" in ct:
                for l in links_pdf(r):
                    try: r2 = get(l)
                    except Exception as e: log(i, l, "ERR", repr(e)[:120]); continue
                    if es_pdf(r2):
                        open(dest, "wb").write(r2.content); log(i, l, r2.status_code, "pdf"); return l
                    log(i, l, r2.status_code, r2.headers.get("content-type", "")[:40])
    return None

def texto(i):
    p, t = os.path.join(PDF, i + ".pdf"), os.path.join(TXT, i + ".txt")
    if os.path.exists(p) and not os.path.exists(t):
        subprocess.run(["pdftotext", "-enc", "UTF-8", p, t], check=False)
    if os.path.exists(t):
        return open(t, encoding="utf-8", errors="replace").read().count("\f")
    return 0

def main():
    ids = sys.argv[1:] or list(C)
    estado = {}
    ef = os.path.join(HERE, "textos_estado.json")
    if os.path.exists(ef): estado = json.load(open(ef))
    # el PDF de Fleischer ya lo bajó la tarea 102 con su nombre por DOI
    old = os.path.join(PDF, "10_1057_s41269_016_0006_0.pdf")
    if os.path.exists(old) and not os.path.exists(os.path.join(PDF, "fleischer2016.pdf")):
        import shutil; shutil.copy(old, os.path.join(PDF, "fleischer2016.pdf"))
    if os.path.exists(os.path.join(PDF, "fleischer2016.pdf")) and not (estado.get("fleischer2016") or {}).get("url"):
        estado["fleischer2016"] = {"doi": C["fleischer2016"][0], "url": C["fleischer2016"][1][0], "fecha": "2026-11-01"}
    for i in ids:
        doi, cands = C[i]
        if not os.path.exists(os.path.join(PDF, i + ".pdf")):
            u = bajar(i, cands)
            if u: estado[i] = {"doi": doi, "url": u, "fecha": HOY}
            else: estado.setdefault(i, {"doi": doi, "url": None, "fecha": HOY})
        n = texto(i)
        if i in estado: estado[i]["paginas"] = n
        print(f"{i:32s} {'OK' if n else '--':3s} {n:3d} págs  {estado.get(i, {}).get('url')}", flush=True)
    json.dump(estado, open(ef, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
