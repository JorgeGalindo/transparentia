modelo: sonnet
salida: fase2/fuentes/cv/manifiesto_cv.csv
estado: hecha
prioridad: 2
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 22:14
---
Carpeta asignada: fase2/fuentes/cv/ (documentos a fase2/data/raw/cv/).
Descarga los currículos oficiales de los altos cargos en activo:
1. Portal de Transparencia: el buscador de currículos (https://transparencia.gob.es/servicios-buscador/buscar.htm?categoria=curriculos&lang=es&historico=false)
   lista ~696 altos cargos; cada resultado enlaza a su CV (PDF o HTML). Recorre la paginación, descarga cada CV y
   extrae su texto (pdftotext o equivalente).
2. Referencias del Consejo de Ministros (lamoncloa.gob.es): para personas de nuestro universo nombradas por el Consejo
   (incluidos presidentes de empresas públicas), localiza la referencia con su nombramiento y extrae el bloque de
   currículum. Empieza por las referencias de 2023–2026.
Salida: manifiesto_cv.csv (nombre, cargo, fuente, url, ruta_local, sha1, paginas, caracteres, fecha_descarga) y
README.md con cobertura (cuántas personas del universo tienen al menos un CV).
