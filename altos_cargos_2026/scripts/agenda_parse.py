import re,json,sys
L=open('agenda/agenda.txt',encoding='utf-8').read().split('\n')[509:3200]
out=[];minis=None;unidad=[]
rx=re.compile(r'^\s{10,}([^,\d@:]{2,60}),\s([^,\d@:]{2,50}),\s(.{3,120})$')
for ln in L:
    m=re.match(r'^(Ministerio .+|Presidencia del Gobierno)\s*$',ln.strip())
    if m and not ln.startswith(' '): minis=m.group(1).strip(); continue
    left=ln[:26].strip() if not ln.startswith(' '*20) else ''
    if left and not re.search(r'Teléf|e-Mail|internet|Fax',left):
        if re.match(r'^[A-ZÁÉÍÓÚ]',left) and (not unidad or unidad[-1]=='__'): unidad=[left]
        else: unidad.append(left)
    if ln.strip()=='' : unidad.append('__') if unidad and unidad[-1]!='__' else None
    m=rx.match(ln)
    if m and 'Teléf' not in ln:
        out.append(dict(ministerio=minis,unidad=' '.join(u for u in unidad if u!='__'),apellidos=m.group(1).strip(),nombre=m.group(2).strip(),cargo=m.group(3).strip()))
json.dump(out,open('agenda/agenda_gob.json','w'),ensure_ascii=False,indent=0)
import collections
print(len(out))
c=collections.Counter(re.sub(r'\s(de|del|para)\s.*','',o['cargo']) for o in out); print(c.most_common(40))
