modelo: sonnet
salida: fase2/db/base.duckdb
estado: pendiente
prioridad: 1
comun: fase2
agente: claude-p
---
Carpeta asignada: fase2/db/.
Implementa la base relacional de ARQUITECTURA.md §4 en DuckDB: fase2/db/schema.sql (todas las tablas, aunque estén
vacías: persona, posicion, entidad, ocupacion, evento, trayectoria, formacion, funcionario, cargo_electo, candidatura,
cargo_partido, evidencia, codificacion) y fase2/db/cargar_s0.py, que carga la foto S0 desde data/ (estructura, otros
altos cargos, consejos) y data/seguimiento/boe_cambios.csv (como eventos).
Lo central es la **resolución de identidades**: una persona que aparece en varias tablas (p. ej. una secretaria de Estado
que preside un consejo) debe tener un único persona_id. Normaliza nombres (tildes, mayúsculas, «Mª», partículas, nombres
compuestos, rangos militares, «representado por») y define reglas: cruce exacto normalizado = automático; nombre
contenido en otro con ≥3 tokens = automático con marca; resto dudoso = fase2/db/revision_identidades.csv.
Excluye del universo de análisis embajadores, mandos militares y mutuas (déjalos en la base con una marca).
Exporta fase2/db/export/persona.csv y ocupacion.csv y escribe fase2/db/README.md con cifras (personas únicas, ocupaciones,
dudosos).
