"""L3 (tarea 107): compila fase2/literatura/matriz.csv a partir de las fichas de lectura (fichas/<id>.json), del estado
de descarga (textos_estado.json) y de los trabajos de relevancia 3 de cribado.csv que no se pudieron leer.

Comprueba además la trazabilidad interna de cada ficha leída: toda referencia [n] de un campo tiene su cita n, toda cita
se usa, y todo campo de contenido lleva al menos una [n], [ausencia] o el sufijo «(API Dataverse…)».
La comprobación de que cada cita está literalmente en su página la hace verificar_citas.py.

Uso: uv run -q python -I fase2/literatura/compilar_matriz.py
"""
import csv, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FICHAS = os.path.join(HERE, "fichas")
EST = json.load(open(os.path.join(HERE, "textos_estado.json")))
CRIB = [r for r in csv.DictReader(open(os.path.join(HERE, "cribado.csv"))) if r["relevancia"] == "3"]

VERSION = {
 "guerra_bona_santana2014": "Versión publicada (BRQ 18(4), 2015), copia en EconStor",
 "kopecky_etal2016": "Versión publicada (EJPR 55, 2016), copia en el repositorio de la Universidad de Leiden",
 "fleischer2016": "Versión publicada en abierto (Acta Politica, Springer)",
 "deandres_etal2020": "Versión publicada (BRQ 24(2), 2021), copia en EconStor",
 "colonnelli_prem_teso2020": "Documento de trabajo (Stigler Center WP 292, 2019), copia en EconStor; NO es la versión publicada en AER",
 "garciacestona_sagarra2022": "Versión del autor depositada en el Dipòsit Digital de la UB (no es la maquetada de la revista)",
 "veit_vedder2023": "Versión publicada en abierto (Public Administration), copia en EconStor",
 "baltrunaite_etal2023": "Documento de trabajo (Banca d'Italia, Temi di discussione 1328, abril 2021); NO es la versión publicada en JLEO",
 "toral2023": "Copia del repositorio de IE University (ver referencia para la versión)",
 "toral2024": "Manuscrito aceptado (8 de mayo de 2023), repositorio de IE University; NO es la maquetada de JOP",
}

# id -> (estado, nota de acceso)
NO_LEIDOS = {
 "lewis2008": ("sin texto completo", "Libro (Princeton UP). OpenAlex: cerrado, sin ubicación abierta. Sin copia legal localizada."),
 "gomez_verge2012": ("sin texto completo", "Capítulo de libro (OUP, cap. 16). OpenAlex: cerrado. Búsqueda web: solo la ficha de OUP."),
 "kopecky_mair_spirova2012": ("sin texto completo", "Libro (OUP). Cadmus (EUI) solo tiene el registro; su API respondió 403 y no hay fichero abierto."),
 "ennser2013_gov": ("sin texto completo", "Governance (Wiley), cerrado. Sin manuscrito de autor localizado."),
 "ennser2013_ps": ("sin texto completo", "Political Studies (SAGE), cerrado. IDEAS/RePEc solo tiene la ficha."),
 "ennser2016_nl": ("sin texto completo", "Acta Politica (Springer), cerrado. Sin manuscrito de autor localizado."),
 "realdato_rodriguezteruel2016": ("sin texto completo", "Acta Politica (Springer), cerrado. La ficha de producciocientifica.uv.es no enlaza PDF. Vía: biblioteca o petición a los autores."),
 "dahlstrom_lapuente2017": ("sin texto completo", "Libro (CUP), cerrado. Sin copia legal localizada."),
 "bach_veit2017": ("bloqueado", "Hay manuscrito aceptado legal (DUO, Univ. de Oslo, migrado a NVA/Sikt), pero la API de NVA responde 403 y OUP (bronze) devuelve paywall a scripts. Descarga manual (Chrome)."),
 "panizza_peters_ramos2018": ("bloqueado", "Hay manuscrito aceptado legal en LSE Research Online, pero el dominio no responde a scripts ni a WebFetch (Cloudflare). Descarga manual (Chrome)."),
 "brierley2020": ("bloqueado", "Hay manuscrito aceptado legal en LSE Research Online y en SSRN; LSE no responde a scripts y SSRN da 403. Descarga manual (Chrome)."),
 "staronova_rybar2020": ("bloqueado", "Hay versión aceptada en SSRN (403 a scripts) y fichero en el repositorio de Masaryk (desafío JavaScript). Descarga manual (Chrome)."),
 "askim_bach_christensen2022": ("bloqueado", "Hay postprint legal en DUO (Univ. de Oslo, migrado a NVA/Sikt); la API de NVA responde 403. Descarga manual (Chrome)."),
}
# replicación comprobada por API aunque el trabajo no se haya leído
REPLI_NO_LEIDOS = {
 "brierley2020": ("https://doi.org/10.7910/DVN/O0JVDU",
                  "8 ficheros: main_rep_data.csv, rep_data_menial.csv, paper_replicate.R, paper_replicate_menial.R, appendix_replicate.R, readme.rtf y codebook de variables (API Dataverse, 2026-11-01)",
                  "CC0 1.0 (API Dataverse, 2026-11-01)"),
}

CAMPOS = ["pregunta", "universo_periodo", "unidad_analisis", "mide_afiliacion", "mide_pericia", "fuentes_datos",
          "fiabilidad_validacion", "resultado_principal", "replicacion_url", "replicacion_contenido",
          "replicacion_licencia", "para_codebook"]
COLS = ["id", "estado", "referencia", "doi_url", "version_leida", "url_texto", "fecha_consulta", "pdf_ruta",
        "paginas_pdf", "paginas_leidas", "nota_acceso"] + CAMPOS + ["citas"]

def doi_de(i):
    d = EST.get(i, {}).get("doi")
    return "https://doi.org/" + d if d else ""

def ref_cribado(i):
    doi = doi_de(i)
    for r in CRIB:
        if r["doi_url"].lower() == doi.lower():
            return f'{r["autores"]} ({r["anio"][:4]}). {r["titulo"]}. {r["revista"]}. {r["doi_url"]}'
    return ""

def trazabilidad(d):
    errs = []
    ns = {c["n"] for c in d["citas"]}
    usados = set()
    for k in CAMPOS:
        v = d.get(k, "") or ""
        refs = {int(x) for grp in re.findall(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]", v) for x in re.findall(r"\d+", grp)}
        usados |= refs
        for n in refs - ns: errs.append(f"{k}: [{n}] sin cita")
        if not refs and "[ausencia]" not in v and "API Dataverse" not in v and "por confirmar" not in v:
            errs.append(f"{k}: sin referencia")
    for n in sorted(ns - usados): errs.append(f"cita {n} no usada")
    return errs

def main():
    filas, problemas = [], {}
    leidos = {}
    for fn in sorted(glob.glob(os.path.join(FICHAS, "*.json"))):
        d = json.load(open(fn)); leidos[d["id"]] = d
    for i, e in EST.items():
        if i in leidos:
            d = leidos[i]
            p = trazabilidad(d)
            if p: problemas[i] = p
            citas = " | ".join(f'[{c["n"]}] p. {c["pagina"]}: "{c["cita"]}"' for c in sorted(d["citas"], key=lambda c: c["n"]))
            f = {k: d.get(k, "") for k in CAMPOS}
            f.update(id=i, estado="leído", referencia=d["referencia"], doi_url=doi_de(i), version_leida=VERSION.get(i, ""),
                     url_texto=e.get("url") or "", fecha_consulta=e.get("fecha", ""),
                     pdf_ruta=f"fase2/data/raw/literatura/pdf/{i}.pdf", paginas_pdf=e.get("paginas", ""),
                     paginas_leidas=d.get("paginas_leidas", ""), nota_acceso="", citas=citas)
        else:
            est, nota = NO_LEIDOS.get(i, ("pendiente", "Texto descargado; ficha de lectura aún no escrita."))
            f = {k: "" for k in COLS}
            f.update(id=i, estado=est, referencia=ref_cribado(i), doi_url=doi_de(i), fecha_consulta=e.get("fecha", ""),
                     nota_acceso=nota)
            if est == "pendiente":
                f.update(url_texto=e.get("url") or "", pdf_ruta=f"fase2/data/raw/literatura/pdf/{i}.pdf",
                         paginas_pdf=e.get("paginas", ""))
            if i in REPLI_NO_LEIDOS:
                f["replicacion_url"], f["replicacion_contenido"], f["replicacion_licencia"] = REPLI_NO_LEIDOS[i]
        filas.append(f)
    orden = {"leído": 0, "pendiente": 1, "bloqueado": 2, "sin texto completo": 3}
    filas.sort(key=lambda f: (orden.get(f["estado"], 9), f["id"]))
    with open(os.path.join(HERE, "matriz.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
    from collections import Counter
    print(Counter(f["estado"] for f in filas), "· citas:", sum(len(d["citas"]) for d in leidos.values()))
    for i, p in problemas.items(): print("TRAZABILIDAD", i, p)
    sys.exit(1 if problemas else 0)

if __name__ == "__main__":
    main()
