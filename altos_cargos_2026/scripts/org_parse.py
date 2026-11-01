import subprocess,re,sys,html,json,glob,os
def blocks(pdf):
    x=subprocess.run(['pdftotext','-bbox-layout',pdf,'-'],capture_output=True,text=True).stdout
    out=[]
    for pi,page in enumerate(re.findall(r'<page.*?</page>',x,flags=re.S)):
        for b in re.findall(r'<block[^>]*>(.*?)</block>',page,flags=re.S):
            lines=[]
            for l in re.findall(r'<line[^>]*>(.*?)</line>',b,flags=re.S):
                lines.append(' '.join(html.unescape(w) for w in re.findall(r'<word[^>]*>(.*?)</word>',l)))
            t=re.sub(r'\s+',' ',' '.join(lines)).strip()
            if t: out.append((pi+1,t))
    return out
KEY=r'(SECRETAR[ÍI]A DE ESTADO|SECRETAR[ÍI]A GENERAL|SUBSECRETAR[ÍI]A|DIRECCI[ÓO]N GENERAL|DELEGACI[ÓO]N DEL GOBIERNO|COMISIONAD|GABINETE|ALTO COMISIONAD|DEPARTAMENTO|DIRECCI[ÓO]N ADJUNTA|ABOGAC[ÍI]A GENERAL|INTERVENCI[ÓO]N GENERAL|OFICINA|VICEPRESIDENCIA|MINISTR|PRESIDENTE|ESTADO MAYOR|JEFE|COMISI[ÓO]N)'
if __name__=='__main__':
    res={}
    for pdf in sorted(glob.glob('org/*.pdf')):
        m=os.path.basename(pdf)[:-4]
        m=m.lower()
        res[m]=blocks(pdf)
    json.dump(res,open('org/blocks.json','w'),ensure_ascii=False)
    for m in sys.argv[1:]:
        for p,t in res[m]:
            if re.search(KEY,t.upper()) and len(t)<200: print(p,'|',t)
