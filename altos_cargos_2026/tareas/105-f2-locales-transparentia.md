modelo: sonnet
salida: fase2/fuentes/locales/cargo_electo_local.csv
estado: pendiente
prioridad: 2
comun: fase2
agente: claude-p
---
Carpeta asignada: fase2/fuentes/locales/.
Dos fuentes de cargos electos locales y autonómicos para las personas de nuestro universo:
1. Transparentia (Newtral), ya en el repo: ../transparentia_historial.csv y ../transparentia_cargos.csv (raíz del repo,
   un nivel por encima de altos_cargos_2026). Extrae los cargos electos y de gobierno (alcaldes, concejales, diputados
   autonómicos y provinciales, diputados, senadores, consejeros) con partido y periodo, normalizados al esquema
   cargo_electo.
2. Buscador de concejales (concejales.redsara.es): consulta por nombre y apellidos para cada persona del universo S0
   (nombres únicos de data/altos_cargos_estructura.csv, data/otros_altos_cargos.csv sin embajadores/militares/mutuas, y
   data/empresas_publicas_consejos.csv). Estudia primero cómo funciona el formulario; si exige captcha o lo bloquea, para
   y documenta. Ritmo educado (≥1,5 s entre consultas), reanudable, caché de respuestas en fase2/data/raw/locales/.
Salida: cargo_electo_local.csv (persona_nombre_buscado, nombre_encontrado, institucion, municipio/provincia, partido,
periodo, fuente, url, calidad_cruce) y README.md con cifras.
