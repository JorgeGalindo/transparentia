"""L1: búsqueda en OpenAlex y Crossref. Reanudable: cachea por consulta en fase2/data/raw/literatura/cache_*.json."""
import json, os, sys, time, csv, requests
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw", "literatura")
os.makedirs(RAW, exist_ok=True)
Q = [
 "party patronage Spain", "patronazgo político España", "politización administración pública España",
 "political appointees senior civil service", "politicization of senior civil service",
 "junior ministers experts politicians", "secretarios de Estado altos cargos nombramientos",
 "state-owned enterprises boards political connections", "political connections board of directors state-owned enterprises appointments",
 "empresas públicas consejos de administración nombramientos políticos", "directivos públicos España profesionalización",
 "revolving doors politicians firms Spain", "puertas giratorias políticos empresas España",
 "political appointments bureaucrats expertise patronage", "patronage appointments public enterprises managers turnover",
 "party patronage Europe appointments", "political appointees competence", "ministerial advisers Spain",
 "politicians on boards of state-owned firms", "meritocracy public appointments Spain",
 "cajas de ahorros gobernanza consejos políticos", "savings banks politicians boards Spain",
 "bureaucratic turnover after elections", "partisan appointments public managers",
]
def oa(q):
    f = os.path.join(RAW, "cache_oa_%d.json" % abs(hash(q) % 10**8)) if False else os.path.join(RAW, "cache_oa_" + "".join(c if c.isalnum() else "_" for c in q)[:60] + ".json")
    if os.path.exists(f): return json.load(open(f))
    r = requests.get("https://api.openalex.org/works", params={"search": q, "per-page": 40,
        "filter": "from_publication_date:1990-01-01", "select": "id,title,doi,publication_year,authorships,primary_location,abstract_inverted_index,cited_by_count,open_access"}, timeout=40)
    r.raise_for_status(); d = r.json().get("results", []); json.dump(d, open(f, "w")); time.sleep(1.2); return d
def cr(q):
    f = os.path.join(RAW, "cache_cr_" + "".join(c if c.isalnum() else "_" for c in q)[:60] + ".json")
    if os.path.exists(f): return json.load(open(f))
    r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": 20}, timeout=40)
    r.raise_for_status(); d = r.json()["message"]["items"]; json.dump(d, open(f, "w")); time.sleep(1.2); return d
def abstract(ii):
    if not ii: return ""
    w = {}
    for k, v in ii.items():
        for p in v: w[p] = k
    return " ".join(w[i] for i in sorted(w))
rows = []; stats = {}
for q in Q:
    for src in ("openalex", "crossref"):
        try: res = oa(q) if src == "openalex" else cr(q)
        except Exception as e: print("ERR", src, q, e, file=sys.stderr); stats[(src, q)] = -1; continue
        stats[(src, q)] = len(res)
        for w in res:
            if src == "openalex":
                loc = w.get("primary_location") or {}; so = (loc.get("source") or {}).get("display_name", "")
                rows.append(dict(titulo=w.get("title") or "", autores="; ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:6]),
                    anio=w.get("publication_year") or "", revista=so, doi_url=w.get("doi") or w.get("id"), fuente="OpenAlex", consulta=q,
                    oa_url=((w.get("open_access") or {}).get("oa_url") or ""), citas=w.get("cited_by_count", 0), resumen=abstract(w.get("abstract_inverted_index"))[:1500]))
            else:
                rows.append(dict(titulo=(w.get("title") or [""])[0], autores="; ".join("%s %s" % (a.get("given", ""), a.get("family", "")) for a in w.get("author", [])[:6]),
                    anio=((w.get("issued") or {}).get("date-parts") or [[""]])[0][0], revista=(w.get("container-title") or [""])[0],
                    doi_url=("https://doi.org/" + w["DOI"]) if w.get("DOI") else w.get("URL", ""), fuente="Crossref", consulta=q, oa_url="", citas=w.get("is-referenced-by-count", 0), resumen=""))
with open(os.path.join(HERE, "busqueda.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
json.dump({"%s|%s" % k: v for k, v in stats.items()}, open(os.path.join(HERE, "busqueda_stats.json"), "w"), ensure_ascii=False, indent=1)
print(len(rows), "filas;", sum(1 for v in stats.values() if v < 0), "errores")
