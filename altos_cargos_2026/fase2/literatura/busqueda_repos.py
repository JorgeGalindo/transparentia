"""L1 (cont.): Dataverse, Zenodo, OSF, Dialnet, RePEc/IDEAS. Añade filas a busqueda_repos.csv. Cache en data/raw/literatura/."""
import requests, csv, re, os, json, time, html
HERE=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(HERE,"..","data","raw","literatura")
Q=["party patronage","political appointees bureaucrats","politicization civil service","state-owned enterprises political connections boards","junior ministers","Spain political appointments","patronazgo político","altos cargos nombramientos","empresas públicas consejos de administración","puertas giratorias"]
rows=[]; log={}
def add(**k): rows.append(k)
def get(u,p,tag):
    f=os.path.join(RAW,"cache_"+tag+".json")
    if os.path.exists(f): return json.load(open(f))["t"]
    r=requests.get(u,params=p,timeout=40); t=r.text; json.dump({"t":t,"s":r.status_code},open(f,"w")); time.sleep(1.2); return t
for q in Q:
    k=re.sub(r"\W","_",q)
    try:
        d=json.loads(get("https://dataverse.harvard.edu/api/search",{"q":q,"type":"dataset","per_page":15},"dv_"+k))["data"]["items"]
        log["Dataverse|"+q]=len(d)
        for x in d: add(titulo=x["name"],autores="; ".join(x.get("authors",[])[:5]),anio=(x.get("published_at") or "")[:4],revista="Harvard Dataverse",doi_url=x["url"],fuente="Dataverse",consulta=q,resumen=(x.get("description") or "")[:600])
    except Exception as e: log["Dataverse|"+q]=str(e)
    try:
        d=json.loads(get("https://zenodo.org/api/records",{"q":q,"size":15,"sort":"bestmatch"},"zn_"+k))["hits"]["hits"]
        log["Zenodo|"+q]=len(d)
        for x in d:
            m=x["metadata"]; add(titulo=m["title"],autores="; ".join(c["name"] for c in m.get("creators",[])[:5]),anio=(m.get("publication_date") or "")[:4],revista="Zenodo",doi_url=x.get("doi_url") or x["links"]["self_html"],fuente="Zenodo",consulta=q,resumen=re.sub("<[^>]+>","",m.get("description",""))[:600])
    except Exception as e: log["Zenodo|"+q]=str(e)
    try:
        d=json.loads(get("https://api.osf.io/v2/nodes/",{"filter[title]":q.split()[-1] if False else q,"page[size]":10},"osf_"+k))["data"]
        log["OSF|"+q]=len(d)
        for x in d: a=x["attributes"]; add(titulo=a["title"],autores="",anio=a["date_created"][:4],revista="OSF",doi_url="https://osf.io/"+x["id"],fuente="OSF",consulta=q,resumen=(a.get("description") or "")[:600])
    except Exception as e: log["OSF|"+q]=str(e)
    try:
        t=get("https://dialnet.unirioja.es/buscar/documentos",{"querysDismax.DOCUMENTAL_TODO":q},"dn_"+k)
        its=re.findall(r'<a href="(/servlet/articulo\?codigo=\d+|/servlet/libro\?codigo=\d+|/servlet/tesis\?codigo=\d+)"[^>]*>(.*?)</a>',t,re.S)
        log["Dialnet|"+q]=len(its)
        for u,ti in its[:15]: add(titulo=html.unescape(re.sub("<[^>]+>","",ti)).strip(),autores="",anio="",revista="Dialnet",doi_url="https://dialnet.unirioja.es"+u,fuente="Dialnet",consulta=q,resumen="")
    except Exception as e: log["Dialnet|"+q]=str(e)
    try:
        t=get("https://ideas.repec.org/cgi-bin/htsearch",{"q":q,"cmd":"Search!","form":"extended","wm":"wrd","dt":"range","ul":"","wf":"4BFF","s":"R"},"rp_"+k)
        its=re.findall(r'<li class="list-group-item downfree">\s*<b><a href="(/[^"]+)">(.*?)</a>',t,re.S) or re.findall(r'<li class="list-group-item[^"]*">\s*<b><a href="(/[pa]/[^"]+)">(.*?)</a>',t,re.S)
        log["RePEc|"+q]=len(its)
        for u,ti in its[:15]: add(titulo=html.unescape(re.sub("<[^>]+>","",ti)).strip(),autores="",anio="",revista="RePEc/IDEAS",doi_url="https://ideas.repec.org"+u,fuente="RePEc",consulta=q,resumen="")
    except Exception as e: log["RePEc|"+q]=str(e)
with open(os.path.join(HERE,"busqueda_repos.csv"),"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["titulo","autores","anio","revista","doi_url","fuente","consulta","resumen"]); w.writeheader(); w.writerows(rows)
json.dump(log,open(os.path.join(HERE,"busqueda_repos_stats.json"),"w"),indent=1)
from collections import Counter; print(len(rows),Counter(r["fuente"] for r in rows))
