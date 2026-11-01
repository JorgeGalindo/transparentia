#!/bin/zsh
# Reconstruye las tablas desde ./fuentes (ver descargar_fuentes.sh). Ejecutar desde altos_cargos_2026/.
# Requiere: pdftotext (poppler), python3 con pandas y openpyxl.
set -e
PY=${PY:-"uv run -q --with pandas --with openpyxl python"}
mkdir -p work && cd work
for d in org cvdl agenda; do [ -e $d ] || ln -s ../fuentes/$d $d; done
cp ../data/verificacion/verificacion_resultado.csv . && cp ../data/verificacion/resultado_*.csv . 2>/dev/null || true
python3 -I ../scripts/org_parse.py >/dev/null
python3 -I ../scripts/units.py >/dev/null
python3 -I ../scripts/units2.py >/dev/null
python3 -I ../scripts/agenda_parse.py >/dev/null
cp ../scripts/taxo.py .
eval $PY -I -W ignore ../scripts/merge.py
eval $PY -I -W ignore ../scripts/post.py
eval $PY -I -W ignore ../scripts/gen_otros.py
eval $PY -I -W ignore ../scripts/apply_verif.py
eval $PY -I -W ignore ../scripts/aplicar_boe.py
rm -rf empresas && mkdir -p empresas && cp ../data/consejos_por_bloque/*.csv empresas/
eval $PY -I -W ignore ../scripts/consolidate_empresas.py
cp altos_cargos_estructura.csv otros_altos_cargos.csv empresas_publicas_consejos.csv ../data/
