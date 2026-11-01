import pandas as pd,glob,re,sys,unicodedata
df=pd.read_excel(glob.glob('cvdl/*.xlsx')[0])
df['nombre']=df['Título'].str.replace('Curriculum de ','',regex=False).str.replace(r'\s+',' ',regex=True).str.strip(' .')
df['cargo']=df['Cargo'].str.replace(r'\s+',' ',regex=True).str.strip()
df['ministerio']=df['Ministerio'].str.strip()
def n(s): return unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()
R=[ # (nivel, categoria, regex) en orden
 (0,'Histórico (ex)', r'^ex(-|\s|director|embajador)'),
 (1,'Presidente del Gobierno', r'^presidente del gobierno'),
 (1,'Ministro/a', r'^(vicepresident[ea]\s.*)?ministr[oa]\b|^vicepresident[ea] (primer|segund|tercer)'),
 (2,'Secretario/a de Estado', r'^secretari[oa] de estado'),
 (3,'Subsecretario/a', r'^subsecretari'),
 (3,'Secretario/a General', r'^secretari[oa] general (?!tecnic)'),
 (3,'Delegado/a del Gobierno en CCAA', r'^delegad[oa] del gobierno (en|de) (la |las |el |los )?(comunidad|ciudad|andalucia|aragon|principado|illes|islas|canarias|cantabria|castilla|cataluna|extremadura|galicia|madrid|region|navarra|pais|rioja|valencia|ceuta|melilla)'),
 (4,'Secretario/a General Técnico/a', r'^secretari[oa] general tecnic'),
 (4,'Director/a General', r'^director[a]? general\b(?! adjunt)'),
 (4,'Director/a de Gabinete', r'^(ex-)?director[a]? (del |de )gabinete'),
 (4,'Director/a de Departamento (Presidencia)', r'^director[a]? del departamento'),
 (4,'Comisionado/a', r'^comisionad[oa]'),
 (4,'Delegado/a del Gobierno (temático)', r'^delegad[oa] (del gobierno|especial)'),
 (4,'Interventor/a, Abogado/a o Inspector/a General', r'^(interventor|abogad|inspector|asesor juridico)[a]? general'),
 (5,'Mando militar', r'^(jefe|segundo jefe|almirante|general jefe|comandante|teniente general)'),
 (5,'Embajador/a y representante permanente', r'^(embajador|representante (permanente|militar)|consul)'),
 (5,'Regulador / autoridad independiente', r'(comision nacional de los mercados|comision nacional del mercado de valores|consejo de seguridad nuclear|proteccion de datos|proteccion del informante|supervision de inteligencia)'),
 (5,'Empresa pública / EPE (primer ejecutivo)', r'(sociedad estatal|entidad publica empresarial|renfe|residuos radiactivo|instituto de credito oficial|icex|puertos del estado|administrador de infraestructuras|salvamento|casa 47|sepi\b|frob|reestructuracion ordenada)'),
 (5,'Mutua colaboradora (director gerente)', r'(mutua|fremap|asepeyo|mutualia|umivale|egarsat|ibermutua|solimat|muprespa|mutual\b)'),
 (5,'Gabinete y oficinas de Presidencia', r'^(director[a]? (adjunt[oa] del gabinete|de asuntos|de informacion|de comunicacion|de la oficina de asuntos economicos)|departamento de)'),
 (5,'Presidencia/dirección de organismo público', r'^(presidente|presidenta|director|directora|vicepresidente|vicepresidenta|rector|gerente|consejero|consejera|secretari[oa]|delegad[oa])\b'),
]
def cl(c,m):
    s=n(c)
    for lv,cat,rx in R:
        if re.search(rx,s): return lv,cat
    return 9,'Otro'
df[['nivel','categoria']]=df.apply(lambda r: pd.Series(cl(r.cargo,r.ministerio)),axis=1)
if __name__=='__main__':
    print(df.categoria.value_counts().to_string())
    for cat in sys.argv[1:]:
        print('==',cat); print(df[df.categoria==cat][['nombre','cargo','ministerio']].to_string(max_colwidth=95))
