"""L2: cribado. Relevancia 3 = lista manual (criterio=manual, tras ver título/resumen/metadatos); resto heurístico por palabras clave (criterio=heuristico).
Descarga PDFs abiertos de los de relevancia 3 (oa_url de OpenAlex) a fase2/data/raw/literatura/pdf/."""
import csv, os, re, requests, time
HERE=os.path.dirname(os.path.abspath(__file__)); PDF=os.path.join(HERE,"..","data","raw","literatura","pdf"); os.makedirs(PDF,exist_ok=True)
DV="https://doi.org/10.7910/DVN/"
# doi -> (relevancia, motivo, replicacion, estado_semilla)
M={
"10.1093/acprof:oso/9780199599370.003.0016":(3,"Capítulo sobre patronazgo de partido en España (semilla); título real: «Party Patronage in Spain: Appointments for Party Government»","No localizado","Semilla verificada (OpenAlex/Crossref); título difiere del anotado en §7"),
"10.1057/ap.2016.6":(3,"Secretarios de Estado en España: tipología político/experto/híbrido; medición directa de pericia","No localizado (Dataverse sin resultado)","Semilla verificada"),
"10.1111/1475-6765.12135":(3,"Encuesta a expertos patronazgo en 22 países (incluye España); medidas comparables","Datos de la encuesta: no localizados en Dataverse; revisar web del proyecto","Verificada (2016, EJPR; §7 citaba solo el libro de 2012)"),
"10.1093/acprof:oso/9780199599370.001.0001":(3,"Libro base de patronazgo de partido y gobierno de partido (Kopecký, Mair, Spirova 2012)","No localizado","Verificada (OUP 2012)"),
"10.1111/gove.12023":(3,"Supervivencia directiva en empresas públicas austriacas según control político: diseño replicable","No localizado","Verificada: Governance 2013 (§7 decía 2014)"),
"10.1111/1467-9248.12031":(3,"Cómo reparten los partidos puestos directivos en empresas públicas (coaliciones)","No localizado","Hallada en verificación (Political Studies 2013)"),
"10.1257/aer.20181491":(3,"Patronazgo y selección en organizaciones públicas (Brasil); referencia de diseño causal","AEA / openICPSR (URL por confirmar); no verificado en Dataverse","Verificada (AER 2020)"),
"10.1111/ajps.12758":(3,"Patronazgo, rendición de cuentas y provisión de servicios; medición de nombramientos políticos","Sí: Harvard Dataverse "+DV+"GHJ8JL","Semilla verificada (AJPS 2023)"),
"10.1086/729961":(3,"Rotación de gobiernos salientes y burocracia (lame duck); diseño de rotación tras elecciones","Sí: Harvard Dataverse "+DV+"KO2VPS","Verificada (JOP 2024)"),
"10.1177/0095399720956996":(3,"Efecto del cambio de ministro sobre nombramientos de altos funcionarios (Eslovaquia)","No localizado","Semilla verificada; es Administration & Society 2020 (§7 decía 2021)"),
"10.1057/s41269-016-0005-1":(3,"Politización partidista de las élites administrativas en Países Bajos (probable sustituto de la semilla Van Dorp)","No localizado","Semilla Van Dorp (2023) NO localizada; esta es otra obra hallada"),
"10.1017/9781316822869":(3,"Marco teórico/empírico sobre organización de burocracia y políticos (Dahlström y Lapuente)","Datos QoG expert survey (Gotemburgo), no localizados en Dataverse","Verificada (CUP 2017)"),
"10.1111/padm.12967":(3,"Mide politización con datos de carrera (backstage/frontstage): útil para codebook","No localizado","Hallada"),
"10.1111/padm.12560":(3,"Tipología de nombramientos por patronazgo (roles, confianza, pericia)","No localizado","Hallada"),
"10.1080/01402382.2022.2148195":(3,"Cambio político y rotación administrativa en sistemas meritocráticos","No localizado","Hallada"),
"10.1057/s41269-016-0006-0":(3,"Predictores de permanencia de altos funcionarios: control partidista vs profesional","No localizado","Hallada"),
"10.1093/jopart/mux041":(3,"Determinantes de promoción a alto cargo en Alemania: lealtad partidista vs competencia","No localizado","Hallada"),
"10.1177/2340944420924417":(3,"Políticos encubiertos vs expertos financieros en consejos de cajas españolas","No localizado","Hallada"),
"10.1080/02102412.2021.2024012":(3,"Gobernanza, capital humano y politización de bancos españoles (cajas)","No localizado","Hallada; sustituye a Cuñat–Garicano (no localizado)"),
"10.1016/j.brq.2014.10.002":(3,"Empresas con conexiones políticas en España","No localizado","Hallada"),
"10.1093/jleo/ewad014":(3,"Composición de consejos de empresas públicas y desempeño (cuasi-experimento, Italia)","No localizado","Hallada"),
"10.1086/708240":(3,"Combinar patronazgo y mérito en reclutamiento público (Ghana)","Sí: Harvard Dataverse "+DV+"O0JVDU","Hallada"),
"10.1515/9781400837687":(3,"Clásico sobre nombramientos políticos y competencia de los designados","No localizado","Hallada"),
"10.1111/j.1540-5907.2006.00215.x":(2,"Clásico EEUU: nombramientos y competencia burocrática; poco encaje con España","No localizado",""),
"10.1080/01402382.2016.1176368":(2,"Asesores ministeriales Dinamarca: política vs competencia","No localizado",""),
"10.1111/gove.12691":(2,"Puertas giratorias en reguladores (Portugal)","No localizado",""),
"10.1108/arla-07-2015-0172":(2,"Puertas giratorias y bolsa española","No localizado",""),
"10.1080/09540962.2020.1793496":(2,"Politización y mora en cajas españolas","No localizado",""),
"10.1016/j.jbusres.2022.01.096":(2,"Políticos en cajas españolas y beneficios privados","No localizado",""),
"10.5209/cgap.65913":(2,"Función directiva pública en España (marco normativo)","No localizado",""),
"10.24965/da.11561":(2,"Profesionalización de la función directiva en España (autonómica)","No localizado",""),
"10.1111/padm.12276":(2,"Leyes de servicio civil, mérito y politización (percepciones)","No localizado",""),
"10.1093/jopart/mur010":(2,"Patronazgo presidencial y desempeño de agencias (EEUU)","Zenodo (registro hallado, verificar)",""),
"10.1017/bap.2021.5":(2,"Poder de nombramiento en empresas públicas (China)","No localizado",""),
"10.2478/nispa-2020-0015":(2,"Nombramiento de altos funcionarios y trayectorias (Eslovaquia)","No localizado",""),
"10.1093/jopart/muu016":(2,"Cronyismo vs competencia neutral en nombramientos ejecutivos (EEUU)","No localizado",""),
}
def doi(u):
    m=re.search(r"10\.\d{4,9}/\S+",u or ""); return m.group(0).lower().rstrip(".") if m else ""
M={k.lower():v for k,v in M.items()}
rows=[]
for fn in ("busqueda.csv","busqueda_repos.csv"):
    rows+=list(csv.DictReader(open(os.path.join(HERE,fn))))
EXTRA=[ # semillas hallazgo verificado pero no devuelto por las consultas generales
("Patronage and Selection in Public Sector Organizations","Colonnelli; Prem; Teso","2020","American Economic Review","https://doi.org/10.1257/aer.20181491"),
("Political Control and Managerial Survival in State-Owned Enterprises","Ennser-Jedenastik","2013","Governance","https://doi.org/10.1111/gove.12023"),
("The Politics of Patronage and Coalition: How Parties Allocate Managerial Positions in State-Owned Enterprises","Ennser-Jedenastik","2013","Political Studies","https://doi.org/10.1111/1467-9248.12031"),
("Personal or Party Roots of Civil Service Patronage? Ministerial Change Effects on the Appointment of Top Civil Servants","Staronova; Rybář","2020","Administration & Society","https://doi.org/10.1177/0095399720956996"),
("Turnover: How Lame-Duck Governments Disrupt the Bureaucracy and Service Delivery before Leaving Office","Toral","2024","The Journal of Politics","https://doi.org/10.1086/729961"),
("Organizing Leviathan","Dahlström; Lapuente","2017","Cambridge University Press","https://doi.org/10.1017/9781316822869"),
("Party Patronage and Party Government in European Democracies","Kopecký; Mair; Spirova","2012","Oxford University Press","https://doi.org/10.1093/acprof:oso/9780199599370.001.0001"),
("The party politicization of administrative elites in the Netherlands","Ennser-Jedenastik","2016","Acta Politica","https://doi.org/10.1057/s41269-016-0005-1"),
("Dedómetro (Fundación Hay Derecho): ediciones estatal, Cataluña 2025, C. Valenciana — informes de think tank, sin metodología replicable verificada","Fundación Hay Derecho","2025","Informe","https://www.economistjurist.es/actualidad-juridica/el-dedometro-denuncia-la-politizacion-de-los-altos-cargos-en-el-sector-publico-genera-directivos-dociles-y-manejables/"),
]
for t,a,y,j,u in EXTRA: rows.append(dict(titulo=t,autores=a,anio=y,revista=j,doi_url=u,fuente="Verificación semillas",consulta="semilla §7",oa_url="",citas="",resumen=""))
KW=[("patronage",3),("appointee",3),("appointment",2),("politiciz",3),("politicis",3),("state-owned",2),("public enterprise",2),("senior civil",3),("junior minister",3),("spain",2),("spanish",2),("españa",2),("patronazgo",3),("nombramiento",2),("revolving",2),("puertas giratorias",3),("directiv",2),("empresas públicas",3),("cajas",2),("meritocra",2)]
seen={}; out=[]
for r in rows:
    d=doi(r["doi_url"]); k=d or r["doi_url"] or r["titulo"].lower()
    if k in seen:
        if r["consulta"] not in seen[k]["consulta"]: seen[k]["consulta"]+=" | "+r["consulta"]
        if not seen[k].get("oa_url") and r.get("oa_url"): seen[k]["oa_url"]=r["oa_url"]
        continue
    seen[k]=r; r["_d"]=d
for r in seen.values():
    d=r["_d"]
    if d in M: rel,mot,rep,est=M[d]; crit="manual"
    else:
        t=(r["titulo"]+" "+r.get("resumen","")).lower(); s=sum(w for k,w in KW if k in t)
        rel=2 if s>=9 else 1 if s>=4 else 0; crit="heuristico"; est=""
        mot="Palabras clave en título/resumen (puntuación %d); sin lectura"%s
        rep="Posible paquete: "+r["revista"]+" (revisar)" if r["fuente"] in ("Dataverse","Zenodo","OSF") and s>=4 else ("No localizado" if rel else "")
    out.append(dict(titulo=r["titulo"],autores=r["autores"],anio=r["anio"],revista=r["revista"],doi_url=r["doi_url"],fuente=r["fuente"],relevancia=rel,criterio=crit,motivo=mot,paquete_replicacion=rep,estado_verificacion=est,pdf_ruta="",oa_url=r.get("oa_url","")))
out.sort(key=lambda r:(-r["relevancia"],r["criterio"]!="manual",r["anio"]))
# PDFs
for r in out:
    if r["relevancia"]==3 and r["oa_url"] and r["oa_url"].lower().split("?")[0].endswith(".pdf"):
        f=os.path.join(PDF,re.sub(r"\W","_",doi(r["doi_url"]))[:60]+".pdf")
        if not os.path.exists(f):
            try:
                x=requests.get(r["oa_url"],timeout=40)
                if x.status_code==200 and x.content[:4]==b"%PDF": open(f,"wb").write(x.content)
                time.sleep(1.2)
            except Exception: pass
        if os.path.exists(f): r["pdf_ruta"]=os.path.relpath(f,os.path.join(HERE,"..",".."))
    r.pop("oa_url") if False else None
with open(os.path.join(HERE,"cribado.csv"),"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out),Counter((r["relevancia"],r["criterio"]) for r in out),"PDFs:",sum(1 for r in out if r["pdf_ruta"]))
print("sin oa_url (rel3):",[r["titulo"][:40] for r in out if r["relevancia"]==3 and not r["oa_url"]])
