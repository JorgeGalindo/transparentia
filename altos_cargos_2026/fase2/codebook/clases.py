"""Asigna la clase de puesto (CODEBOOK v0, sección 1) a la foto S0.

Entrada (solo lectura): data/altos_cargos_estructura.csv, data/otros_altos_cargos.csv,
data/empresas_publicas_consejos.csv.
Salida: fase2/codebook/clase_posicion.csv (una fila por unidad, por fila de otros altos cargos y por silla).

Reglas deterministas, por orden: la primera que casa gana. Cada fila lleva el código de la regla aplicada,
que remite a la tabla de reglas de fase2/CODEBOOK.md. No mira a las personas: solo cargo, tipo, entidad y,
en las participadas no controladas, quién propuso la silla.

Ejecución (desde la raíz de altos_cargos_2026/):
    uv run -q --with duckdb --with pandas --with requests python -I fase2/codebook/clases.py
"""

import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
OUT = Path(__file__).resolve().parent / "clase_posicion.csv"


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


def rx(*pats):
    return re.compile("|".join(pats))


# --- Listas cerradas de entidades (texto normalizado: minúsculas, sin tildes) ---

# T-regulador. R1: autoridades independientes, supervisores e inspección.
R1 = rx(
    r"comision nacional de los mercados y la competencia", r"\bcnmc\b",
    r"comision nacional del mercado de valores", r"\bcnmv\b",
    r"consejo de seguridad nuclear", r"proteccion de datos", r"proteccion del informante",
    r"supervision de inteligencia artificial", r"responsabilidad fiscal", r"\bairef\b", r"banco de espana",
    r"reestructuracion ordenada bancaria", r"\bfrob\b",
    r"mercado de tabacos", r"oficina de conflictos de intereses",
    r"agencia estatal de seguridad aerea", r"agencia estatal de seguridad ferroviaria",
    r"medicamentos y productos sanitarios", r"agencia espanola de seguridad alimentaria",
    r"lucha antidopaje", r"inspeccion de trabajo", r"instituto de contabilidad y auditoria",
    r"tribunal economico-administrativo",
)
# R2: estadística, medición y agencias científico-técnicas.
R2 = rx(
    r"instituto nacional de estadistica", r"\(ine\)", r"planificacion estadistica",
    r"investigaciones sociologicas", r"meteorologia", r"patentes y marcas",
    r"consejo superior de investigaciones cientificas", r"\bcsic\b", r"instituto de salud carlos iii",
    r"agencia estatal de investigacion", r"\bciemat\b", r"tecnica aeroespacial", r"\bcedex\b",
    r"estudios y experimentacion de obras publicas", r"astrofisica de canarias", r"supercomputacion",
    r"investigaciones cardiovasculares", r"laboratorio subterraneo de canfranc", r"agencia espacial",
    r"evaluacion de la calidad y acreditacion", r"organizacion nacional de trasplantes",
    r"fundacion espanola para la ciencia", r"instituto geografico nacional", r"oceanografia",
)
# R3: administración tributaria (AEAT y sus departamentos).
R3 = rx(
    r"administracion tributaria", r"informatica tributaria", r"gestion tributaria",
    r"aduanas e impuestos especiales", r"inspeccion financiera y tributaria",
)
# T-empresa fuera del fichero de consejos: EPE, sociedades estatales y consorcios empresariales.
EMP = rx(
    r"entidad publica empresarial", r"e\.p\.e", r"\bepe\b", r"red\.es", r"\bidae\b",
    r"fabrica nacional de moneda", r"\benaire\b", r"\bicex\b", r"desarrollo tecnologico y de la innovacion",
    r"\bcdti\b", r"\bsasemar\b", r"\brenfe\b", r"administrador de infraestructuras ferroviarias",
    r"puertos del estado", r"casa 47", r"participaciones industriales", r"residuos radiactivo",
    r"instituto de credito oficial", r"zona franca",
)
# FUERA por patrón (además de las categorías de otros_altos_cargos).
MILITAR = rx(
    r"inspector general del ejercito", r"asesor juridico general de la defensa",
    r"interventora? general de la defensa", r"\bceseden\b", r"estudios de la defensa nacional",
    r"jefe de estado mayor",
)
MUTUA = rx(r"mutua")
RECTOR = rx(r"^rector")
# P por patrón: gabinetes, oficinas de Presidencia y oficinas ad hoc.
GABINETE = rx(
    r"gabinete", r"oficina de asuntos economicos", r"conferencia de presidentes",
    r"coordinacion juridica de la vicepresidenta",
)
AD_HOC = rx(r"reconstruccion de ucrania")
SG_MINISTERIAL_ADSCRITA = rx(r"secretari[oa] general de instituciones penitenciarias")
OECC = rx(r"oficina espanola del cambio climatico")
AEAT_DPTO = R3
# Secretario/vicesecretario no consejero.
SECRETARIO_NC = rx(r"secretari[oa].*no consejer", r"vicesecretari")
# Prueba de que la silla de una participada la propuso o la ocupa el accionista público.
PROP_PUBLICA = rx(
    r"propuest[oa] por (la )?sepi", r"sepi lo propuso", r"sepi propon", r"en representacion de (la )?sepi",
    r"^sociedad estatal de participaciones industriales",
)
PROP_PUBLICA_OTRO_CARGO = rx(r"\benaire\b", r"\bsepi\b")
# Silla de un accionista privado identificado en la nota de origen («Accionista: X», o directivo del socio privado).
ACCIONISTA_PRIVADO = rx(r"accionista: ", r"de sidenor")
# DG marcadas como «adscritas» en origen que en realidad son DG del ministerio (sin nombre de organismo).
ORGANISMO = rx(
    r"instituto", r"agencia", r"centro", r"consorcio", r"\bcasa\b", r"servicio publico", r"tesoreria",
    r"biblioteca", r"fundacion", r"parque movil", r"organismo (autonomo|estatal|publico)", r"turespana", r"consejo", r"\bitj\b", r"\bo\.a\b",
)


def clase_puesto(texto, tipo="", categoria="", nivel=""):
    """Clase para unidades AGE (estructura) y otros altos cargos. Devuelve (clase, regla)."""
    t = norm(texto)
    tipo_n = norm(tipo)
    cat = norm(categoria)

    # 1. Fuera del análisis
    if nivel == "1" or cat in ("ministro/a", "presidente del gobierno"):
        return "FUERA", "F0 Gobierno (presidente, ministros, departamento)"
    if cat.startswith("embajador"):
        return "FUERA", "F1 embajador o representante permanente"
    if cat.startswith("delegado/a del gobierno en ccaa"):
        return "FUERA", "F2 delegado del Gobierno en CCAA"
    if cat == "mando militar" or MILITAR.search(t):
        return "FUERA", "F3 mando militar o puesto de oficial general"
    if cat.startswith("mutua") or MUTUA.search(t):
        return "FUERA", "F4 mutua colaboradora"
    if RECTOR.search(t):
        return "FUERA", "F5 rector de universidad (autonomía universitaria)"

    # 2. Entidad: regulador o agencia técnica
    if R1.search(t):
        return "T-regulador", "R1 autoridad independiente, supervisor o inspección"
    if R2.search(t):
        return "T-regulador", "R2 estadística o agencia científico-técnica"
    if R3.search(t):
        return "T-regulador", "R3 administración tributaria (AEAT)"

    # 3. Entidad: empresa pública
    if cat.startswith("empresa publica") or EMP.search(t):
        return "T-empresa", "E1 primer ejecutivo o alta dirección"

    # 4. Político por diseño
    if tipo_n.startswith("secretaria de estado") or "rango de secretario de estado" in t:
        return "P", "P1 secretaría de Estado o rango de SE"
    if tipo_n.startswith("secretaria general") and "tecnica" not in tipo_n:
        if "adscrita" not in tipo_n or SG_MINISTERIAL_ADSCRITA.search(t):
            return "P", "P2 secretaría general de ministerio (art. 64 L40/2015)"
        return "T-legal", "L5 dirección o gerencia de organismo público"
    if cat == "secretario/a general":
        return "P", "P2 secretaría general de ministerio (art. 64 L40/2015)"
    if tipo_n == "comisionado":
        return "P", "P3 comisionado u oficina ad hoc"
    if AD_HOC.search(t):
        return "P", "P3 comisionado u oficina ad hoc"
    if (tipo_n.startswith("departamento (presidencia") or tipo_n == "gabinete"
            or cat in ("director/a de gabinete", "gabinete y oficinas de presidencia") or GABINETE.search(t)):
        return "P", "P4 gabinete u oficina de Presidencia"

    # 5. Técnico por norma
    if tipo_n == "subsecretaria":
        return "T-legal", "L1 subsecretaría (art. 63 L40/2015)"
    if tipo_n == "secretaria general tecnica":
        return "T-legal", "L2 secretaría general técnica (art. 65 L40/2015)"
    if tipo_n.startswith("delegacion del gobierno (tematica)") or cat.startswith("delegado/a del gobierno (tematico)"):
        return "T-legal", "L3 dirección general o rango DG (art. 66 L40/2015)"
    if tipo_n == "direccion general" or cat == "director/a general" or OECC.search(t):
        return "T-legal", "L3 dirección general o rango DG (art. 66 L40/2015)"
    if cat.startswith("interventor") or "abogado general del estado" in t:
        return "T-legal", "L4 puesto reservado a cuerpo A1 (intervención, abogacía, inspección)"
    if tipo_n.startswith("direccion general") and not ORGANISMO.search(t.split(" | ")[0]):
        return "T-legal", "L3 dirección general o rango DG (art. 66 L40/2015)"
    if "adscrita" in tipo_n or cat.startswith("presidencia/direccion de organismo"):
        return "T-legal", "L5 dirección o gerencia de organismo público"
    return "REVISAR", "X sin regla"


def pct_publico(v):
    s = norm(v)
    if not s or s.startswith("n.a") or s.startswith("n.d. (filial"):
        return None
    if "mayoria" in s or "= 100" in s:
        return 100.0
    if s.startswith(">50"):
        return 51.0
    m = re.search(r"\d+(?:[.,]\d+)?", s)
    return float(m.group().replace(",", ".")) if m else None


def tokens(nombre):
    return {w for w in re.findall(r"[a-z]+", norm(nombre)) if len(w) > 2}


def clase_silla(r, nombres_publicos, pct_empresa):
    emp = norm(r["empresa"])
    cargo = norm(r["cargo"])
    tipo = norm(r["tipo_consejero"])
    pe = norm(r["primer_ejecutivo"])
    nota = norm(r["nota"])
    otro = norm(r["otro_cargo_publico"])
    nombre_n = norm(r["nombre"])

    if R1.search(emp):
        return "T-regulador", "R1 autoridad independiente, supervisor o inspección"
    if SECRETARIO_NC.search(cargo) and pe != "si":
        return "FUERA", "F7 secretario o vicesecretario no consejero"

    pct = pct_empresa.get(emp)
    if pct is not None and pct <= 50:
        tk = tokens(r["nombre"])
        es_publica = (PROP_PUBLICA.search(nota) or PROP_PUBLICA.search(nombre_n)
                      or PROP_PUBLICA_OTRO_CARGO.search(otro)
                      or any(len(tk & p) >= 2 and (tk <= p or p <= tk) for p in nombres_publicos.get(emp, [])))
        if es_publica:
            return "T-empresa", "E3 silla del accionista público en participada no controlada"
        if ACCIONISTA_PRIVADO.search(nota) or tipo in ("independiente", "ejecutivo", "otro externo"):
            return "FUERA", "F6 silla no designada por el sector público (participada no controlada)"
        return "REVISAR", "X2 participada no controlada: accionista proponente sin identificar"

    if pe == "si":
        return "T-empresa", "E1 primer ejecutivo o alta dirección"
    if "no consejero" in tipo:
        return "T-empresa", "E2 dirección ejecutiva no consejera"
    if "radio y television" in emp and tipo == "otro externo":
        return "T-empresa", "E7 consejero elegido por las Cortes (RTVE)"
    sub = {"dominical": "E4 dominical", "independiente": "E5 independiente", "ejecutivo": "E6 ejecutivo"}
    return "T-empresa", sub.get(tipo, "E8 consejero (tipo no publicado)")


def leer(nombre):
    with open(DATA / nombre, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    filas = []
    for i, r in enumerate(leer("altos_cargos_estructura.csv"), 1):
        texto = f'{r["unidad"]} | {r["tipo"]}'
        c, regla = clase_puesto(texto, tipo=r["tipo"], nivel=r["nivel"])
        filas.append(["estructura", i, r["unidad"], r["ministerio"], r["titular"] or "", c, regla])

    for i, r in enumerate(leer("otros_altos_cargos.csv"), 1):
        texto = f'{r["cargo"]} | {r["ministerio"]}'
        c, regla = clase_puesto(texto, categoria=r["categoria"], nivel=r["nivel"])
        filas.append(["otros", i, r["cargo"], r["ministerio"], r["nombre"] or "", c, regla])

    consejos = leer("empresas_publicas_consejos.csv")
    # Primera pasada: nombres con prueba de propuesta pública, para propagar a filas duplicadas de la misma empresa.
    nombres_publicos = {}
    for r in consejos:
        if PROP_PUBLICA.search(norm(r["nota"])) or PROP_PUBLICA_OTRO_CARGO.search(norm(r["otro_cargo_publico"])):
            nombres_publicos.setdefault(norm(r["empresa"]), []).append(tokens(r["nombre"]))
    # % público a nivel de empresa: el primer valor legible entre sus filas (hay bloques sin el dato).
    pct_empresa = {}
    for r in consejos:
        v = pct_publico(r["participacion_publica_pct"])
        if v is not None:
            pct_empresa.setdefault(norm(r["empresa"]), v)
    for i, r in enumerate(consejos, 1):
        c, regla = clase_silla(r, nombres_publicos, pct_empresa)
        filas.append(["consejos", i, r["cargo"], r["empresa"], r["nombre"] or "", c, regla])

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origen", "id_fila", "cargo", "entidad_o_ministerio", "nombre", "clase", "regla_aplicada"])
        w.writerows(filas)

    print(f"{len(filas)} filas -> {OUT.relative_to(BASE)}")
    for (o, c), n in sorted(Counter((f[0], f[5]) for f in filas).items()):
        print(f"  {o:10s} {c:12s} {n:4d}")
    for (c, regla), n in sorted(Counter((f[5], f[6]) for f in filas).items()):
        print(f"  {n:4d}  {c:12s} {regla}")
    if any(f[5] == "REVISAR" and f[6].startswith("X sin") for f in filas):
        sys.exit("Hay filas sin regla: amplía las listas antes de seguir.")


if __name__ == "__main__":
    main()
