modelo: sonnet
salida: fase2/cruces/cargo_electo_persona.csv
estado: hecha
prioridad: 1
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 22:19
---
Carpeta asignada: fase2/cruces/.
Cruza los cargos electos y de gobierno con las personas del universo:
- personas: fase2/db/export/persona.csv (persona_id y nombre) y ocupacion.csv (para contexto: puesto, ministerio).
- cargos: fase2/fuentes/electos/cargo_electo_oficial.csv (Senado, PE, Wikidata) y fase2/fuentes/locales/cargo_electo_local.csv.
Reglas: cruce por nombre completo normalizado (dos apellidos); los cruces parciales o con nombres comunes exigen una
señal de contexto compatible (partido coherente con el gobierno o la región, cronología plausible, misma persona en
Wikidata con otros cargos que casan con su CV en fase2/data/raw/cv/ o su puesto actual). Clasifica cada cruce:
seguro / probable / dudoso. Deduplica mandatos repetidos entre fuentes (Senado y PE salen dos veces).
Corrige o descarta las fechas imposibles de Wikidata (años 0xxx).
Salidas: cargo_electo_persona.csv (persona_id, nombre, institucion, nivel_institucion: local/provincial/autonómico/
nacional/europeo/gobierno, partido, partido_origen, inicio, fin, fuente, url, calidad), revision_cruces.csv con los
dudosos y README.md con cifras: personas del universo con algún cargo electo o de gobierno, por nivel y por partido.
