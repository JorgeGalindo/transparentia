modelo: sonnet
salida: fase2/fuentes/electos/cargo_electo_oficial.csv
estado: hecha
prioridad: 2
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 21:57
---
Carpeta asignada: fase2/fuentes/electos/ (brutos a fase2/data/raw/electos/).
Construye cargadores reproducibles de cargos electos y de gobierno a partir de fuentes abiertas, normalizados al esquema
cargo_electo (persona_nombre, institucion, partido, legislatura, fecha_inicio, fecha_fin, fuente, url):
1. Senado: datos abiertos de senadores de todas las legislaturas (senado.es, datos abiertos).
2. Parlamento Europeo: eurodiputados españoles, todas las legislaturas (europarl.europa.eu).
3. Wikidata (SPARQL, query.wikidata.org): personas con nacionalidad española y P39 en Congreso de los Diputados,
   Senado, parlamentos autonómicos, Parlamento Europeo, alcaldías, consejerías autonómicas, ministerios; con qualifiers
   de inicio/fin y P102 (partido). Hazlo por lotes para no saturar el endpoint.
4. Congreso: datos abiertos devuelve 403 a scripts; no lo fuerces. Cubre el Congreso vía Wikidata y anota el hueco.
Une todo en cargo_electo_oficial.csv (sin cruzar todavía con nuestras personas) y documenta cobertura por institución y
legislatura en README.md.
