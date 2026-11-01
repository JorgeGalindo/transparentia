"""Comprueba que los esquemas son JSON Schema 2020-12 válidos y que sectores.csv está bien formado.

    uv run -q --with jsonschema python -I fase2/codebook/validar_esquemas.py
"""

import csv
import json
from pathlib import Path

from jsonschema import Draft202012Validator

DIR = Path(__file__).resolve().parent

for p in sorted((DIR / "esquemas").glob("*.json")):
    esquema = json.loads(p.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(esquema)
    print(f"ok  {p.name}")

with open(DIR / "sectores.csv", newline="", encoding="utf-8") as f:
    filas = list(csv.DictReader(f))
codigos = [r["codigo"] for r in filas]
assert codigos == [f"S{i:02d}" for i in range(1, len(filas) + 1)], codigos
assert 15 <= len(filas) <= 25 and all(all(v.strip() for v in r.values()) for r in filas)
enum = json.loads((DIR / "esquemas" / "cv_extraccion.schema.json").read_text())["$defs"]["sector"]["enum"]
assert enum[:-1] == codigos, "el enum de sectores de los esquemas no coincide con sectores.csv"
print(f"ok  sectores.csv ({len(filas)} sectores)")
