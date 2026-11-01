import json,re,collections,unicodedata
B=json.load(open('org/blocks.json'))
MIN={'mapa':'Agricultura, Pesca y Alimentación','mauc':'Asuntos Exteriores, UE y Cooperación','mclt':'Cultura','mcnu':'Ciencia, Innovación y Universidades','mdca':'Derechos Sociales, Consumo y Agenda 2030','mdef':'Defensa','mecm':'Economía, Comercio y Empresa','mefd':'Educación, FP y Deportes','mhac':'Hacienda','migd':'Igualdad','mint':'Interior','mism':'Inclusión, Seguridad Social y Migraciones','mitu':'Industria y Turismo','mjui':'Juventud e Infancia','mpjc':'Presidencia, Justicia y Relaciones con las Cortes','msnd':'Sanidad','mtdf':'Transformación Digital y Función Pública','mted':'Transición Ecológica y Reto Demográfico','mtes':'Trabajo y Economía Social','mtmd':'Política Territorial y Memoria Democrática','mtrm':'Transportes y Movilidad Sostenible','mvau':'Vivienda y Agenda Urbana','pg':'Presidencia del Gobierno'}
CAP=r"[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ\.\-'’()0-9]*"
UNITRX=re.compile(r"((?:SECRETAR[ÍI]A DE ESTADO|SECRETAR[ÍI]A GENERAL|SUBSECRETAR[ÍI]A|DIRECCI[ÓO]N GENERAL|DIRECCI[ÓO]N\b|COMISIONADO|ALTO COMISIONADO|DEPARTAMENTO|OFICINA|DELEGACI[ÓO]N DEL GOBIERNO|GABINETE|SECRETARIA DE ESTADO|SUBSECRETARIA)(?:[\s,]+(?:"+CAP+r"|DE|DEL|LA|LAS|LOS|EL|Y|E|PARA|EN|A))*)")
def lvl(u):
    s=unicodedata.normalize('NFKD',u).encode('ascii','ignore').decode().upper()
    if s.startswith('SECRETARIA DE ESTADO'): return 2,'Secretaría de Estado'
    if s.startswith('SECRETARIA GENERAL TECNICA'): return 4,'Secretaría General Técnica'
    if s.startswith('SECRETARIA GENERAL'): return 3,'Secretaría General'
    if s.startswith('SUBSECRETARIA'): return 3,'Subsecretaría'
    if s.startswith('DELEGACION DEL GOBIERNO'): return 4,'Delegación del Gobierno (temática)'
    if s.startswith('DIRECCION GENERAL'): return 4,'Dirección General'
    if s.startswith('ALTO COMISIONADO') or s.startswith('COMISIONADO'): return 4,'Comisionado'
    if s.startswith('DEPARTAMENTO'): return 4,'Departamento (Presidencia)'
    if s.startswith('DIRECCION'): return 4,'Dirección (otra, rango DG)'
    if s.startswith('GABINETE'): return 4,'Gabinete'
    if s.startswith('OFICINA'): return 5,'Oficina'
    return 9,'?'
rows=[];seen=set()
for m,bl in B.items():
    head=None
    for p,t in bl:
        for u in UNITRX.findall(t):
            u=re.sub(r'\s+',' ',u).strip(' ,')
            u=re.sub(r'\b(DE|DEL|Y|LA|EL|PARA|EN|A|E)$','',u).strip(' ,')
            if len(u.split())<3: continue
            lv,cat=lvl(u)
            if lv in (2,3) and p>1 and head is None: head=u
            key=(m,unicodedata.normalize('NFKD',u.replace(' ','')).upper())
            if key in seen: continue
            seen.add(key)
            # name in same block: non-caps words
            rest=t.replace(u,' ')
            nm=' '.join(w for w in rest.split() if not re.fullmatch(CAP+r',?',w) and w not in ('de','del','y','la','CV') and re.match(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñü\-’']+",w) or w in('de','del','la','y')).strip()
            nm=re.sub(r'^(de|del|la|y)\s+|\s+(de|del|la|y)$','',nm)
            rows.append(dict(cod=m,ministerio=MIN[m],nivel=lv,tipo=cat,unidad=u.title().replace(' De ',' de ').replace(' Del ',' del ').replace(' Y ',' y ').replace(' La ',' la ').replace(' Para ',' para ').replace(' El ',' el ').replace(' Los ',' los ').replace(' Las ',' las ').replace(' En ',' en ').replace(' E ',' e '),pagina=p,nombre_organigrama=nm if p==1 else ''))
json.dump(rows,open('org/units.json','w'),ensure_ascii=False,indent=0)
if __name__=='__main__':
    c=collections.Counter((r['tipo']) for r in rows); print(c)
    for r in rows:
        if r['cod'] in ('mtes','mhac'): print(r['cod'],r['nivel'],r['tipo'],'|',r['unidad'],'|',r['nombre_organigrama'])
