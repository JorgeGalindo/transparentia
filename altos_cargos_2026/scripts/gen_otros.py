"""Altos cargos de la lista de CV que no son titulares de una unidad de la estructura
(ministros, delegados del Gobierno, organismos, reguladores, embajadores, mandos militares, mutuas...)."""
exec(open('taxo.py').read().split('if __name__')[0])
import pandas as pd
o = pd.read_csv('altos_cargos_estructura.csv').fillna('')
inunits = set(o.titular)
core = ['Secretario/a de Estado', 'Subsecretario/a', 'Secretario/a General', 'Secretario/a General Técnico/a', 'Director/a General',
        'Comisionado/a', 'Delegado/a del Gobierno (temático)', 'Director/a de Departamento (Presidencia)']
x = df[~(df.categoria.isin(core) & df.nombre.isin(inunits))].copy()
x = x[x.categoria != 'Histórico (ex)']
x = x[['nivel', 'categoria', 'ministerio', 'cargo', 'nombre']].sort_values(['nivel', 'categoria', 'ministerio', 'cargo'])
x['fuente'] = 'transparencia.gob.es — currículos de altos cargos (historico=false), descarga 01/11/2026'
x.to_csv('otros_altos_cargos.csv', index=False)
print('otros altos cargos:', len(x))
