"""L3/L5 (tarea 107): comprueba los paquetes de replicación de los trabajos leídos.

1. Para los DOI de paquete ya conocidos (Dataverse), pide a la API de Harvard Dataverse los metadatos: título, licencia
   o condiciones de uso, versión y lista de ficheros.
2. Para el resto, busca en Harvard Dataverse por título del artículo (y apellido del autor) y guarda los candidatos.
3. openICPSR no tiene API abierta sin cuenta: se anota la URL del proyecto y lo que dice su página pública.
Salida: fase2/literatura/replicacion.json (se fusiona en matriz.csv con compilar_matriz.py).

Uso: uv run -q --with requests python -I fase2/literatura/replicacion.py
"""
import datetime, json, os, re, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "altos_cargos_2026-literatura/0.1 (EsadeEcPol research script; python-requests)"}
DV = "https://dataverse.harvard.edu"
HOY = datetime.date.today().isoformat()

CONOCIDOS = {
    "toral2023": "doi:10.7910/DVN/GHJ8JL",
    "toral2024": "doi:10.7910/DVN/KO2VPS",
    "brierley2020": "doi:10.7910/DVN/O0JVDU",
}
BUSCAR = {
    "guerra_bona_santana2014": "Politically connected firms in Spain",
    "kopecky_etal2016": "Party patronage in contemporary democracies",
    "fleischer2016": "Partisan and professional control: Predictors of bureaucratic tenure in Germany",
    "bach_veit2017": "Determinants of Promotion to High Public Office in Germany",
    "panizza_peters_ramos2018": "Roles, trust and skills patronage appointments",
    "deandres_etal2020": "Politicians in disguise and financial experts on the board",
    "colonnelli_prem_teso2020": "Patronage and Selection in Public Sector Organizations",
    "staronova_rybar2020": "Personal or Party Roots of Civil Service Patronage",
    "askim_bach_christensen2022": "Political change and administrative turnover in meritocratic systems",
    "garciacestona_sagarra2022": "Governance, human capital and politicization of Spanish banks",
    "veit_vedder2023": "Measuring civil service politicization with career data",
    "baltrunaite_etal2023": "Board composition and performance of state-owned enterprises",
}
OPENICPSR = {"colonnelli_prem_teso2020": "https://www.openicpsr.org/openicpsr/project/118165/version/V1/view"}

def get(url, **kw):
    time.sleep(1.2)
    return requests.get(url, headers=UA, timeout=60, **kw)

def dataset(pid):
    r = get(f"{DV}/api/datasets/:persistentId/", params={"persistentId": pid})
    if r.status_code != 200: return {"pid": pid, "status": r.status_code}
    d = r.json()["data"]; v = d.get("latestVersion", {})
    cit = {f["typeName"]: f.get("value") for f in v.get("metadataBlocks", {}).get("citation", {}).get("fields", [])}
    lic = v.get("license") or {}
    files = [(f.get("label"), (f.get("dataFile") or {}).get("contentType"), (f.get("dataFile") or {}).get("filesize"),
              f.get("restricted")) for f in v.get("files", [])]
    return {"pid": pid, "url": "https://doi.org/" + pid.replace("doi:", ""), "status": 200,
            "titulo": cit.get("title"), "version": f"{v.get('versionNumber')}.{v.get('versionMinorNumber')}",
            "fecha_publicacion": d.get("publicationDate"),
            "licencia": lic.get("name") or (v.get("termsOfUse") and "termsOfUse: " + re.sub(r"<[^>]+>", " ", v.get("termsOfUse"))[:300]),
            "licencia_uri": lic.get("uri"), "n_ficheros": len(files), "ficheros": files,
            "restringidos": sum(1 for f in files if f[3])}

def buscar(q):
    r = get(f"{DV}/api/search", params={"q": f'"{q}"', "type": "dataset", "per_page": 10})
    if r.status_code != 200: return {"status": r.status_code}
    items = r.json().get("data", {}).get("items", [])
    return [{"titulo": x.get("name"), "url": x.get("url"), "global_id": x.get("global_id"),
             "autores": x.get("authors"), "fecha": x.get("published_at")} for x in items]

def main():
    out = {"fecha_consulta": HOY, "dataverse": {}, "busqueda": {}, "openicpsr": {}}
    for i, pid in CONOCIDOS.items():
        out["dataverse"][i] = dataset(pid); print(i, out["dataverse"][i].get("licencia"), out["dataverse"][i].get("n_ficheros"))
    for i, q in BUSCAR.items():
        out["busqueda"][i] = buscar(q); print(i, len(out["busqueda"][i]) if isinstance(out["busqueda"][i], list) else out["busqueda"][i])
    for i, u in OPENICPSR.items():
        r = get(u); t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
        m = re.search(r"(Terms of Use|License)[^.]{0,300}", t)
        out["openicpsr"][i] = {"url": u, "status": r.status_code, "extracto": t[:1500], "licencia_extracto": m.group(0) if m else None}
        print(i, r.status_code)
    json.dump(out, open(os.path.join(HERE, "replicacion.json"), "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
