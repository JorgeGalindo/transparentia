#!/bin/zsh
# Rutina de actualización (semanal; diaria en semanas de cambio de Gobierno). Ejecutar desde altos_cargos_2026/.
#   1. vigía del BOE (sin LLM)       -> data/seguimiento/boe_cambios.csv
#   2. genera tareas por datos viejos -> tareas/NNN-*.md
#   3. corre la cola por API          -> data/consejos_por_bloque/tarea_*.csv, data/verificacion/*
#   4. reconstruye tablas y panel     -> data/*.csv, panel/index.html
# Opciones: --sin-cola (solo 1, 2 y 4), --max N (paralelismo de la cola, por defecto 3)
set -e
PYX=${PYX:-"uv run -q --with pandas --with openpyxl python"}
MAX=3; COLA=1
while [ $# -gt 0 ]; do case $1 in --sin-cola) COLA=0;; --max) MAX=$2; shift;; esac; shift; done
python3 -I scripts/boe_vigia.py
eval $PYX -I scripts/generar_tareas.py
[ $COLA = 1 ] && python3 -I scripts/cola.py run --max $MAX
./scripts/build.sh | grep -E "BOE|filas|altos cargos AGE" || true
eval $PYX -I scripts/panel.py
echo "Hecho. Revisa data/seguimiento/boe_sin_encaje.csv y publica panel/index.html (artifact) si quieres compartirlo."
