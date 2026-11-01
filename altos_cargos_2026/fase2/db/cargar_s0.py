"""Carga la foto S0 (data/) en fase2/db/base.duckdb con resolución de identidades.

Uso (desde cualquier carpeta):
    uv run -q --with duckdb --with pandas --with requests python -I fase2/db/cargar_s0.py

Reconstruye la base entera en cada ejecución (idempotente). Solo escribe en fase2/db/.
"""
import difflib
import json
import re
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
DATA = RAIZ / "data"
DB = AQUI / "base.duckdb"

# ----------------------------------------------------------------------------- normalización
PARTICULAS = {"de", "del", "la", "las", "los", "el", "y", "e", "i", "d", "dels", "da", "do", "das", "dos", "l"}
TITULOS = {"don", "dona", "dna", "d", "da", "excmo", "excma", "ilmo", "ilma", "sr", "sra", "dr", "dra", "prof"}
RANGOS = {"general", "gral", "almirante", "almte", "teniente", "tte", "coronel", "cnl", "capitan", "cpt",
          "comandante", "cte", "contralmirante", "vicealmirante", "jemad", "gen", "gd", "tg", "tcol"}


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def separar_representante(raw: str):
    """-> (persona|None, entidad_representada|None). «X (repr.: P)», «X, representada por P»."""
    m = re.match(r"^(?P<ent>.+?)[,\s]*\(?\s*(?:repr\.:|representad[oa]s? por)\s*(?P<per>.+?)\)?\s*$", raw, re.I)
    if m:
        per = m.group("per").strip()
        if re.match(r"^su\s", per, re.I):  # «representado por su presidente»: sin persona concreta
            return None, m.group("ent").strip(" ,(")
        return per, m.group("ent").strip(" ,(")
    return raw, None


def quitar_parentesis(raw: str) -> str:
    """«Manuel (Imanol) Leza» -> sin alias; «Marisa Galán (María Luisa Galán Camino)» -> el contenido si es el nombre largo."""
    m = re.search(r"\(([^)]*)\)", raw)
    if not m:
        return raw
    dentro, fuera = m.group(1).strip(), (raw[:m.start()] + " " + raw[m.end():]).strip()
    if len(dentro.split()) >= 3 and len(dentro.split()) > len(fuera.split()):
        return dentro
    return fuera


def tokens_nombre(raw: str):
    s = quitar_parentesis(raw)
    s = sin_tildes(s).lower()
    s = re.sub(r"\bm\s*\.?\s*[ªa]\b\.?|\bmª|\bm\.ª|\bma\.", "maria", s)
    s = s.replace("ª", "")
    s = re.sub(r"[-–—/]", " ", s)
    s = re.sub(r"[^a-z0-9ñç ]", " ", s.replace("'", " "))
    toks = s.split()
    while len(toks) > 3 and toks[0] in RANGOS:   # rangos militares al inicio
        toks = toks[1:]
    while toks and toks[0] in TITULOS and len(toks) > 2:
        toks = toks[1:]
    return [t for t in toks if t not in PARTICULAS]


def es_subsecuencia(corto, largo):
    it = iter(largo)
    return all(t in it for t in corto)


# ----------------------------------------------------------------------------- exclusiones
RE_EMB = re.compile(r"embajad|representante permanente|representaci[oó]n permanente", re.I)
RE_MIL = re.compile(r"almirante|jefe de estado mayor|teniente general|general jefe|general de (?:ej[eé]rcito|divisi[oó]n|brigada)|comandante del mando|mando de operaciones", re.I)
RE_MUT = re.compile(r"mutua|fremap|\bmac-?mutua|director gerente", re.I)
RE_DEL = re.compile(r"delegad[oa] del gobierno en", re.I)


def motivo_exclusion(categoria, cargo, tabla):
    cat, cg = categoria or "", cargo or ""
    if cat.startswith("Embajador") or RE_EMB.search(cg):
        return "embajador"
    if cat == "Mando militar" or RE_MIL.search(cg):
        return "mando_militar"
    if cat.startswith("Mutua") or (RE_MUT.search(cg) and re.search(r"mutua|fremap|mac-", cg, re.I)):
        return "mutua"
    if cat.startswith("Delegado/a del Gobierno en") or RE_DEL.search(cg):
        return "delegado_gobierno_ccaa"
    return None


# ----------------------------------------------------------------------------- ministerios
def clave_min(nombre: str) -> str:
    t = tokens_nombre(nombre) if False else None
    s = sin_tildes(nombre).lower()
    s = re.sub(r"[^a-z ]", " ", s)
    t = [w for w in s.split() if w not in PARTICULAS and w not in {"ministerio", "para"}]
    return " ".join(t)


ALIAS_MIN = {"asuntos exteriores cooperacion": "asuntos exteriores union europea cooperacion"}


def num(x):
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None


def fecha(x):
    try:
        return pd.to_datetime(x).date() if isinstance(x, str) and x.strip() else None
    except Exception:
        return None


def main():
    est = pd.read_csv(DATA / "altos_cargos_estructura.csv", dtype=str)
    otr = pd.read_csv(DATA / "otros_altos_cargos.csv", dtype=str)
    con = pd.read_csv(DATA / "empresas_publicas_consejos.csv", dtype=str)
    boe = pd.read_csv(DATA / "seguimiento" / "boe_cambios.csv", dtype=str)

    # nombres cortos de ministerios (los de la estructura mandan)
    min_corto = {}
    for m in est["ministerio"].dropna().unique():
        min_corto[clave_min(m)] = m

    def ministerio(m):
        if not isinstance(m, str):
            return None
        k = clave_min(m)
        k = ALIAS_MIN.get(k, k)
        return min_corto.get(k) or min_corto.get(ALIAS_MIN.get(k, k)) or m

    # ------------------------------------------------------------------ registros
    recs = []  # una fila por (fuente, persona, cargo)

    def es_vacio(n):
        return (not isinstance(n, str)) or n.strip().startswith("(") or n.strip().lower() in {"n.d.", "n.d", "", "nan"}

    for i, r in est.iterrows():
        cargo = r["unidad"]
        pto = "organismo" if "organismo/entidad" in (r["tipo"] or "") else "unidad_age"
        recs.append(dict(tabla="estructura", fila=i + 2, nombre=r["titular"], cargo=cargo, tipo=pto,
                         nivel=int(r["nivel"]), min=ministerio(r["ministerio"]), cat=r["tipo"],
                         inicio=fecha(r["fecha_nombramiento"]), boe=r["fuente_boe"] if isinstance(r["fuente_boe"], str) else None,
                         url=r["fuente_verificacion"] if isinstance(r["fuente_verificacion"], str) and r["fuente_verificacion"].startswith("http") else None,
                         estado="S0 estructura", fecha_dato=date(2026, 11, 1), vigente=True, nota=r["nota"] if isinstance(r["nota"], str) else None))
    for i, r in otr.iterrows():
        cat = r["categoria"]
        pto = ("primer_ejecutivo" if cat.startswith("Empresa pública") else
               "organismo" if cat.startswith(("Presidencia/dirección de organismo", "Regulador")) else "unidad_age")
        boe_id = r["fuente_boe"] if isinstance(r["fuente_boe"], str) else None
        recs.append(dict(tabla="otros", fila=i + 2, nombre=r["nombre"], cargo=r["cargo"], tipo=pto, nivel=int(r["nivel"]),
                         min=ministerio(r["ministerio"]), cat=cat, inicio=None, boe=boe_id, url=None,
                         estado="S0 otros", fecha_dato=date(2026, 11, 1), vigente=True, nota=None))
    for i, r in con.iterrows():
        cg = r["cargo"]
        pto = ("primer_ejecutivo" if r["primer_ejecutivo"] == "sí" else
               "secretaria_consejo" if re.search(r"no consejer|secretari|vicesecretari", cg, re.I) else "silla_consejo")
        recs.append(dict(tabla="consejos", fila=i + 2, nombre=r["nombre"], cargo=cg, tipo=pto, nivel=None,
                         min=ministerio(r["adscripcion_o_matriz"]) if isinstance(r["adscripcion_o_matriz"], str) and clave_min(r["adscripcion_o_matriz"]) in min_corto else None,
                         cat=r["bloque"], inicio=None, boe=None, url=r["fuente_url"], estado=r["estado_dato"],
                         fecha_dato=fecha(r["fecha_dato_iso"]), vigente=True if r["estado_dato"] == "actual verificado" else None,
                         nota=r["nota"] if isinstance(r["nota"], str) else None, empresa=r["empresa"],
                         tipo_silla=r["tipo_consejero"], row=r))

    # ------------------------------------------------------------------ nombre -> persona
    for rc in recs:
        raw = rc["nombre"]
        rc["persona_raw"], rc["representa"], rc["vacante"], rc["juridica"] = None, None, False, False
        if es_vacio(raw):
            rc["vacante"] = True
            continue
        per, ent = separar_representante(raw.strip())
        rc["representa"] = ent
        if per is None or re.search(r"\(ver filas|S\.A\.|S\.L\.|S\.M\.E", per):
            rc["juridica"] = True
            continue
        if re.match(r"^(Sociedad|Comunidad Aut|Fundaci|Banco|Instituto|Agencia|Ministerio|Grupo|Consorcio)", per):
            rc["juridica"] = True
            continue
        rc["persona_raw"] = per

    # eventos BOE: nombres (todos van a persona)
    ev = []
    for i, r in boe.iterrows():
        ev.append(dict(fila=i + 2, nombre=r["nombre"], tipo=r["tipo"], fecha=fecha(r["fecha_boe"]), cargo=r["cargo"], dep=r["departamento"],
                       fid=r["identificador"], url=r["url"], titulo=r["titulo"]))

    # variantes de nombre -> clave
    variantes = defaultdict(lambda: defaultdict(int))   # clave -> {raw: n}
    tablas_clave = defaultdict(set)
    for rc in recs:
        if rc["persona_raw"]:
            k = " ".join(tokens_nombre(rc["persona_raw"]))
            rc["clave"] = k
            variantes[k][rc["persona_raw"]] += 1
            tablas_clave[k].add(rc["tabla"])
    for e in ev:
        k = " ".join(tokens_nombre(e["nombre"]))
        e["clave"] = k
        variantes[k][e["nombre"]] += 1
        tablas_clave[k].add("boe")

    claves = sorted(variantes)
    toks = {k: k.split() for k in claves}
    padre = {k: k for k in claves}

    def raiz(k):
        while padre[k] != k:
            padre[k] = padre[padre[k]]
            k = padre[k]
        return k

    # índice por token
    por_token = defaultdict(set)
    for k in claves:
        for t in toks[k]:
            por_token[t].add(k)

    def candidatos(k):
        c = defaultdict(int)
        for t in toks[k]:
            for o in por_token[t]:
                if o != k:
                    c[o] += 1
        return [o for o, n in c.items() if n >= 2]

    # regla 2: contenido (≥3 tokens, subsecuencia, candidato único) -> automático con marca
    revision, auto_marcadas = [], []
    marca_clave = set()
    ya_dudoso = set()
    for k in claves:
        if len(toks[k]) < 3:
            continue
        sup = [o for o in candidatos(k) if len(toks[o]) > len(toks[k]) and es_subsecuencia(toks[k], toks[o])]
        if len(sup) == 1:
            o = sup[0]
            padre[raiz(k)] = raiz(o)
            marca_clave.update([k, o])
            auto_marcadas.append(dict(nombre_corto=sorted(variantes[k])[0], nombre_largo=sorted(variantes[o])[0],
                                      tablas_corto=";".join(sorted(tablas_clave[k])), tablas_largo=";".join(sorted(tablas_clave[o])),
                                      regla="contenido>=3_tokens"))
        elif len(sup) > 1:
            for o in sup:
                revision.append(dict(motivo="contenido_ambiguo (varios superconjuntos)", a=sorted(variantes[k])[0], b=sorted(variantes[o])[0],
                                     tablas_a=";".join(sorted(tablas_clave[k])), tablas_b=";".join(sorted(tablas_clave[o])), ratio=""))
                ya_dudoso.add(frozenset((k, o)))

    # regla 3: dudosos (no se fusionan)
    vistos = set()
    for k in claves:
        for o in candidatos(k):
            par = frozenset((k, o))
            if par in vistos or raiz(k) == raiz(o):
                continue
            vistos.add(par)
            if par in ya_dudoso:
                continue
            a, b = (k, o) if len(toks[k]) <= len(toks[o]) else (o, k)
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            motivo = None
            if sorted(toks[a]) == sorted(toks[b]):
                motivo = "mismos_tokens_distinto_orden"
            elif set(toks[a]) < set(toks[b]) and len(toks[a]) >= 3:
                motivo = "contenido_sin_orden"
            elif set(toks[a]) < set(toks[b]) and len(toks[a]) == 2:
                motivo = "contenido_2_tokens"
            elif ratio >= 0.9 and len(a) >= 10:
                motivo = "grafia_parecida"
            elif toks[a][-2:] == toks[b][-2:] and len(toks[a]) >= 3 and toks[a][0] != toks[b][0] and (
                    toks[a][0].startswith(toks[b][0]) or toks[b][0].startswith(toks[a][0])):
                motivo = "mismo_apellido_nombre_abreviado"
            if motivo:
                revision.append(dict(motivo=motivo, a=sorted(variantes[a])[0], b=sorted(variantes[b])[0],
                                     tablas_a=";".join(sorted(tablas_clave[a])), tablas_b=";".join(sorted(tablas_clave[b])),
                                     ratio=round(ratio, 3)))

    # clusters -> persona_id
    grupos = defaultdict(list)
    for k in claves:
        grupos[raiz(k)].append(k)
    persona_de_clave, personas = {}, []
    for pid, (rt, ks) in enumerate(sorted(grupos.items(), key=lambda kv: kv[0]), start=1):
        todas = defaultdict(int)
        for k in ks:
            for raw, n in variantes[k].items():
                todas[raw] += n
        # nombre canónico: más tokens, sin «Mª», más frecuente
        canon = sorted(todas, key=lambda r: (-len(tokens_nombre(r)), "Mª" in r, -todas[r], r))[0]
        canon = re.sub(r"\s+", " ", quitar_parentesis(canon)).strip()
        canon = re.sub(r"^(?:(?:%s)\b\.?\s+)+(?=\S+\s+\S+\s+\S+)" % "|".join(sorted(RANGOS, key=len, reverse=True)), "", canon, flags=re.I)
        con_marca = any(k in marca_clave for k in ks)
        regla = "contenido" if len(ks) > 1 else ("exacto" if sum(todas.values()) > 1 and len(todas) >= 1 and False else "unico")
        n_apar = sum(todas.values())
        if len(ks) == 1 and n_apar > 1:
            regla = "exacto"
        personas.append(dict(persona_id=pid, nombre_completo=canon, nombre_norm=" ".join(tokens_nombre(canon)),
                             n_variantes=len(todas), regla=regla, marca=con_marca, variantes=dict(todas), claves=ks))
        for k in ks:
            persona_de_clave[k] = pid
    # los cruces «exacto» entre tablas distintas también cuentan como tal
    for p in personas:
        if p["regla"] == "unico":
            tabs = set().union(*[tablas_clave[k] for k in p["claves"]])
            if len(tabs) > 1:
                p["regla"] = "exacto"

    # ------------------------------------------------------------------ entidades
    entidades, ent_id = [], {}
    for k, m in sorted(min_corto.items(), key=lambda kv: kv[1]):
        ent_id[("min", m)] = len(entidades) + 1
        entidades.append(dict(entidad_id=len(entidades) + 1, nombre=m, tipo="ministerio"))
    for emp, g in con.groupby("empresa", sort=True):
        r = g.iloc[0]
        pct = r["participacion_publica_pct"]
        entidades.append(dict(entidad_id=len(entidades) + 1, nombre=emp, tipo="empresa_organismo", forma_juridica=r["forma_juridica"],
                              matriz=r["adscripcion_o_matriz"] if isinstance(r["adscripcion_o_matriz"], str) else None,
                              ministerio_adscripcion=ministerio(r["adscripcion_o_matriz"]) if isinstance(r["adscripcion_o_matriz"], str) and clave_min(r["adscripcion_o_matriz"]) in min_corto else None,
                              pct_publico_txt=pct if isinstance(pct, str) else None,
                              pct_publico=num(pct) if isinstance(pct, str) and re.fullmatch(r"\d+([.,]\d+)?", pct.strip()) else None))
        ent_id[("emp", emp)] = len(entidades)

    # ------------------------------------------------------------------ posiciones y ocupaciones
    pos_key, posiciones, ocup_key, ocupaciones = {}, [], {}, []

    def clave_cargo(c):
        return " ".join(tokens_nombre("x " + c)[0:]) if False else re.sub(r"\W+", " ", sin_tildes(c).lower()).strip()

    # primero, titulares por clave de posición AGE para detectar choques
    titulares_por_pos = defaultdict(set)
    for rc in recs:
        if rc["tabla"] != "consejos" and rc["persona_raw"]:
            titulares_por_pos[(rc["min"], clave_cargo(rc["cargo"]))].add(persona_de_clave[rc["clave"]])

    for rc in recs:
        pid = persona_de_clave[rc["clave"]] if rc.get("persona_raw") else None
        if rc["tabla"] == "consejos":
            key = ("c", rc["fila"])      # cada fila es una silla distinta
        else:
            base = (rc["min"], clave_cargo(rc["cargo"]))
            key = ("a",) + base + ((pid,) if len(titulares_por_pos[base]) > 1 and pid else ())
        mot = motivo_exclusion(rc["cat"] if rc["tabla"] == "otros" else None, rc["cargo"], rc["tabla"])
        if key not in pos_key:
            pos_key[key] = len(posiciones) + 1
            e_id = ent_id.get(("emp", rc.get("empresa"))) if rc["tabla"] == "consejos" else ent_id.get(("min", rc["min"]))
            posiciones.append(dict(posicion_id=pos_key[key], tipo=rc["tipo"], cargo=rc["cargo"], nivel=rc["nivel"], ministerio=rc["min"],
                                   entidad_id=e_id, categoria_origen=rc["cat"], tipo_silla=rc.get("tipo_silla"),
                                   vacante=rc["vacante"], excluir_universo=mot is not None, motivo_exclusion=mot, fuente_tabla=rc["tabla"]))
        else:
            p = posiciones[pos_key[key] - 1]
            if rc["nivel"] is not None and (p["nivel"] is None or rc["nivel"] < p["nivel"]) and rc["tabla"] != "otros":
                p["nivel"] = rc["nivel"]
            if p["vacante"] and not rc["vacante"]:
                p["vacante"] = False
            p["fuente_tabla"] = ";".join(sorted(set(p["fuente_tabla"].split(";")) | {rc["tabla"]}))
        rc["posicion_id"] = pos_key[key]
        if pid:
            ok = (pid, pos_key[key])
            if ok not in ocup_key:
                ocup_key[ok] = len(ocupaciones) + 1
                ocupaciones.append(dict(ocupacion_id=ocup_key[ok], persona_id=pid, posicion_id=pos_key[key], inicio=rc["inicio"],
                                        vigente=rc["vigente"], fuente_nombramiento=rc["boe"], representa_a=rc["representa"],
                                        nombre_original=rc["nombre"], estado_dato=rc["estado"], fecha_dato=rc["fecha_dato"],
                                        fuente_url=rc["url"], fuentes=rc["tabla"], nota=rc["nota"]))
            else:
                o = ocupaciones[ocup_key[ok] - 1]
                o["fuentes"] = ";".join(sorted(set(o["fuentes"].split(";")) | {rc["tabla"]}))
                o["inicio"] = o["inicio"] or rc["inicio"]
                o["fuente_nombramiento"] = o["fuente_nombramiento"] or rc["boe"]

    # ------------------------------------------------------------------ eventos
    personas_s0 = {persona_de_clave[rc["clave"]] for rc in recs if rc.get("persona_raw")}
    ocup_por_persona = defaultdict(list)
    for o in ocupaciones:
        ocup_por_persona[o["persona_id"]].append(o)
    def pref(c):
        return {w[:5] for w in re.sub(r"\W+", " ", sin_tildes(c).lower()).split() if w not in PARTICULAS and len(w) > 2}

    def cargo_parecido(a, b):
        x, y = pref(a), pref(b)
        return bool(x and y) and len(x & y) / len(x | y) >= 0.7

    eventos = []
    for e in ev:
        pid = persona_de_clave[e["clave"]]
        pos = None
        for o in ocup_por_persona.get(pid, []):
            if cargo_parecido(posiciones[o["posicion_id"] - 1]["cargo"], e["cargo"]):
                pos = o["posicion_id"]
        mot = motivo_exclusion(None, e["cargo"], "boe")
        en_s0 = pid in personas_s0
        if e["tipo"] == "cese":
            estado = "revisar" if pos is not None else "reflejado_en_s0"   # cese: S0 aún lo lista en ese cargo -> revisar
        else:
            estado = "reflejado_en_s0" if pos is not None else "revisar"
        eventos.append(dict(evento_id=len(eventos) + 1, fecha=e["fecha"], tipo=e["tipo"], persona_id=pid, posicion_id=pos,
                            cargo_texto=e["cargo"], departamento=e["dep"], fuente_id=e["fid"], fuente_url=e["url"], titulo=e["titulo"],
                            estado=estado, excluir_universo=mot is not None))
        e["mot"] = mot

    # exclusión a nivel persona
    motivos_p = defaultdict(set)
    todas_ocup = defaultdict(list)
    for o in ocupaciones:
        todas_ocup[o["persona_id"]].append(posiciones[o["posicion_id"] - 1])
    for p in personas:
        ps = todas_ocup.get(p["persona_id"], [])
        evs = [e for e in eventos if e["persona_id"] == p["persona_id"]] if p["persona_id"] not in todas_ocup else []
        if ps:
            excl = all(x["excluir_universo"] for x in ps)
            mots = {x["motivo_exclusion"] for x in ps if x["excluir_universo"]}
        elif evs:
            excl = all(x["excluir_universo"] for x in evs)
            mots = set()
            for x, e in zip(evs, [e for e in ev if persona_de_clave[e["clave"]] == p["persona_id"]]):
                if e["mot"]:
                    mots.add(e["mot"])
        else:
            excl, mots = False, set()
        p["excluir"], p["motivo"] = excl, ";".join(sorted(mots)) if excl else None

    # ------------------------------------------------------------------ escribir base
    if DB.exists():
        DB.unlink()
    cx = duckdb.connect(str(DB))
    cx.execute((AQUI / "schema.sql").read_text())

    def vol(tabla, df):
        if len(df):
            cx.register("_t", df)
            cols = ",".join(df.columns)
            cx.execute(f"INSERT INTO {tabla} ({cols}) SELECT {cols} FROM _t")
            cx.unregister("_t")

    vol("persona", pd.DataFrame([dict(persona_id=p["persona_id"], nombre_completo=p["nombre_completo"], nombre_norm=p["nombre_norm"],
                                      n_variantes=p["n_variantes"], regla_resolucion=p["regla"], marca_revision=p["marca"],
                                      excluir_universo=p["excluir"], motivo_exclusion=p["motivo"]) for p in personas]))
    vol("entidad", pd.DataFrame(entidades))
    vol("posicion", pd.DataFrame(posiciones))
    vol("ocupacion", pd.DataFrame(ocupaciones))
    vol("evento", pd.DataFrame(eventos))
    alias = []
    for p in personas:
        for raw, n in p["variantes"].items():
            k = " ".join(tokens_nombre(raw))
            alias.append(dict(persona_id=p["persona_id"], nombre_original=raw, nombre_norm=k,
                              fuente_tabla=";".join(sorted(tablas_clave[k])), regla=p["regla"]))
    vol("persona_alias", pd.DataFrame(alias))

    # revisión
    pid_de = lambda nombre: persona_de_clave.get(" ".join(tokens_nombre(nombre)))
    rev = pd.DataFrame(revision).drop_duplicates() if revision else pd.DataFrame(columns=["motivo", "a", "b", "tablas_a", "tablas_b", "ratio"])
    if len(rev):
        rev["persona_id_a"] = rev["a"].map(pid_de)
        rev["persona_id_b"] = rev["b"].map(pid_de)
    # personas jurídicas sin persona física identificada
    jur = [dict(motivo="persona_juridica_sin_representante", a=rc["nombre"], b=rc.get("empresa") or rc["cargo"], tablas_a=rc["tabla"], tablas_b="", ratio="",
                persona_id_a=None, persona_id_b=None) for rc in recs if rc["juridica"]]
    rev = pd.concat([rev, pd.DataFrame(jur)], ignore_index=True)
    rev.to_csv(AQUI / "revision_identidades.csv", index=False)
    pd.DataFrame(auto_marcadas).to_csv(AQUI / "identidades_automaticas_marcadas.csv", index=False)

    # exportación
    cx.execute(f"""COPY (SELECT * FROM persona ORDER BY persona_id) TO '{AQUI}/export/persona.csv' (HEADER)""")
    cx.execute(f"""COPY (
        SELECT o.ocupacion_id, o.persona_id, pe.nombre_completo, pe.excluir_universo AS persona_excluida,
               o.posicion_id, po.cargo, po.tipo AS tipo_posicion, po.nivel, po.ministerio, en.nombre AS entidad, po.tipo_silla,
               po.categoria_origen, po.excluir_universo AS posicion_excluida, po.motivo_exclusion,
               o.inicio, o.fin, o.vigente, o.representa_a, o.estado_dato, o.fecha_dato, o.fuente_nombramiento, o.fuente_url, o.fuentes
        FROM ocupacion o JOIN persona pe USING (persona_id) JOIN posicion po USING (posicion_id)
        LEFT JOIN entidad en ON en.entidad_id = po.entidad_id ORDER BY o.ocupacion_id) TO '{AQUI}/export/ocupacion.csv' (HEADER)""")

    q = lambda s: cx.execute(s).fetchone()[0]
    cif = dict(
        personas=q("SELECT count(*) FROM persona"), personas_univ=q("SELECT count(*) FROM persona WHERE NOT excluir_universo"),
        excl=cx.execute("SELECT coalesce(motivo_exclusion,'(mixto/otro)'), count(*) FROM persona WHERE excluir_universo GROUP BY 1 ORDER BY 2 DESC").fetchall(),
        posiciones=q("SELECT count(*) FROM posicion"), pos_vac=q("SELECT count(*) FROM posicion WHERE vacante"),
        ocup=q("SELECT count(*) FROM ocupacion"), ocup_univ=q("SELECT count(*) FROM ocupacion o JOIN posicion p USING(posicion_id) WHERE NOT p.excluir_universo"),
        ocup_tabla=cx.execute("SELECT fuentes, count(*) FROM ocupacion GROUP BY 1 ORDER BY 2 DESC").fetchall(),
        entidades=q("SELECT count(*) FROM entidad"), eventos=q("SELECT count(*) FROM evento"),
        ev_estado=cx.execute("SELECT estado, count(*) FROM evento GROUP BY 1").fetchall(),
        multi=q("SELECT count(*) FROM (SELECT persona_id FROM ocupacion GROUP BY 1 HAVING count(*)>1)"),
        cruces_tablas=q("SELECT count(*) FROM (SELECT persona_id FROM (SELECT persona_id, unnest(string_split(fuentes, ';')) t FROM ocupacion) GROUP BY 1 HAVING count(DISTINCT t)>1)"),
        regla=cx.execute("SELECT regla_resolucion, count(*) FROM persona GROUP BY 1 ORDER BY 2 DESC").fetchall(),
        marcadas=len(auto_marcadas), nrev=len(rev), rev_motivos=rev["motivo"].value_counts().to_dict(),
        filas_in=len(est) + len(otr) + len(con), vacantes=sum(r["vacante"] for r in recs), juridicas=len(jur),
        eventos_nuevos=q("SELECT count(*) FROM persona p WHERE NOT EXISTS (SELECT 1 FROM ocupacion o WHERE o.persona_id=p.persona_id)"),
    )
    cx.close()
    escribir_readme(cif)
    print(json.dumps(cif, ensure_ascii=False, indent=1, default=str))


def escribir_readme(c):
    fmt = lambda l: "\n".join(f"  - {a}: {b}" for a, b in l)
    txt = f"""# fase2/db — base relacional DuckDB (tarea 103)

Implementa ARQUITECTURA.md §4. Contenido: `schema.sql` (13 tablas de la §4 + `persona_alias`), `cargar_s0.py` (carga S0 y resuelve identidades),
`base.duckdb` (salida), `export/persona.csv`, `export/ocupacion.csv`, `revision_identidades.csv` (dudosos), `identidades_automaticas_marcadas.csv` (cruces automáticos por contenido, para auditar).

## Cómo se ejecuta
`uv run -q --with duckdb --with pandas --with requests python -I fase2/db/cargar_s0.py` (reconstruye todo; tarda segundos).
Fuentes: `data/altos_cargos_estructura.csv`, `data/otros_altos_cargos.csv`, `data/empresas_publicas_consejos.csv` (todas, incluidas filas «último dato disponible» y «sin marcar»), `data/seguimiento/boe_cambios.csv` (→ `evento`).

## Cifras (carga actual)
- Filas de entrada S0: {c['filas_in']} (estructura+otros+consejos), de ellas {c['vacantes']} sin titular (vacante/n.d.) y {c['juridicas']} titulares persona jurídica sin persona física.
- **Personas únicas: {c['personas']}** ({c['personas_univ']} dentro del universo de análisis). Excluidas por motivo:
{fmt(c['excl'])}
- Posiciones: {c['posiciones']} ({c['pos_vac']} vacantes). Entidades: {c['entidades']} (ministerios + empresas/organismos con consejo).
- **Ocupaciones: {c['ocup']}** ({c['ocup_univ']} en posiciones dentro del universo). Por tabla(s) de origen:
{fmt(c['ocup_tabla'])}
- Personas con >1 ocupación: {c['multi']}. Personas que aparecen en más de una tabla de S0: {c['cruces_tablas']}.
- Eventos BOE: {c['eventos']} ({', '.join(f'{a}: {b}' for a, b in c['ev_estado'])}). Personas solo presentes en eventos BOE (sin ocupación S0): {c['eventos_nuevos']}.
- Resolución: {', '.join(f'{a}={b}' for a, b in c['regla'])}.
- **Cruces automáticos por contenido (con marca): {c['marcadas']}** → `identidades_automaticas_marcadas.csv`.
- **Dudosos para revisión humana: {c['nrev']}** → `revision_identidades.csv` ({', '.join(f'{a}: {b}' for a, b in c['rev_motivos'].items())}). No se fusionan.

## Reglas de identidad
1. Normalización: sin tildes, minúsculas, «Mª/Ma.» → «maría», guiones fuera, apóstrofos separan, se quitan partículas (de, del, la, las, los, y, dels…), títulos (don, doña, Excmo.) y rangos militares iniciales; alias entre paréntesis se descartan (salvo que el paréntesis sea el nombre largo); «X (repr.: P)» y «X, representada por P» → persona = P, entidad representada en `ocupacion.representa_a`.
2. **Cruce exacto** de la clave normalizada = mismo `persona_id` (automático).
3. **Contenido**: si la clave de A (≥3 tokens) es subsecuencia ordenada de la de B y B es el único candidato → automático, `persona.marca_revision = TRUE`, regla `contenido`.
4. Resto dudoso (mismos tokens en otro orden, contenido de 2 tokens o sin orden, grafía parecida ratio ≥ 0.9, mismo apellido con nombre abreviado, contenido con varios candidatos) → `revision_identidades.csv`; no se fusiona hasta que Jorge decida.
5. Personas jurídicas sin representante persona física (p. ej. «FROB, representado por su presidente») no crean persona: van a la hoja de revisión.

## Exclusiones (marca, no borrado)
`posicion.excluir_universo` + `motivo_exclusion`: **embajador** (categoría o cargo; incluye representantes permanentes), **mando_militar**, **mutua**, y **delegado_gobierno_ccaa** (decisión 6 de §12: delegados del Gobierno fuera; los delegados *temáticos* NO se excluyen). La persona se marca excluida solo si todas sus ocupaciones lo están. Por eso 7 mandos militares que además ocupan una silla de consejo siguen en el universo (su puesto militar sí está excluido). Los eventos BOE llevan su propia marca.

## Posiciones y ocupaciones
- AGE (estructura + otros): una posición por (ministerio normalizado, cargo normalizado); si dos titulares distintos comparten texto de cargo, se separan por titular. Una persona que sale en estructura y en otros con el mismo cargo tiene una sola ocupación (`fuentes` lista ambas).
- Consejos: una posición por fila (cada silla), enlazada a su `entidad`.
- `ocupacion.vigente`: TRUE para S0 AGE y filas «actual verificado»; NULL para «último dato disponible» y «sin marcar» (no se sabe).

## Límites
- `clase`, `requisito_a1`, `excepcion_rd`, `intensidad_tecnica`, `genero`, `nombre/apellidos`, `socio_coalicion`, `gobierno`, retribución, sector: vacíos a propósito (codebook / tareas posteriores).
- Las posiciones de `otros` de tipo empresa pública no se enlazan aún con la `entidad` de consejos (nombres distintos).
- `evento.estado` es una heurística (cargo parecido en S0), no una verificación: «revisar» = comprobar a mano.
- Una misma persona con grafías muy distintas (apellidos compuestos reordenados, nombre de pila distinto) no se detecta si no entra en las reglas de dudosos.
"""
    (AQUI / "README.md").write_text(txt)


if __name__ == "__main__":
    main()
