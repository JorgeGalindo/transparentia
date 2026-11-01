modelo: sonnet
salida: fase2/literatura/cribado.csv
estado: pendiente
prioridad: 1
comun: fase2
agente: claude-p
---
Carpeta asignada: fase2/literatura/ (PDF a fase2/data/raw/literatura/).
Pasos L1–L2 de la pata de literatura (ARQUITECTURA.md §7). Pregunta: nombramientos políticos, patronazgo y pericia en
altos cargos del ejecutivo y en directivos/consejos de empresas públicas; foco España 2015–2026, más comparados clave y
clásicos. Usa APIs abiertas (OpenAlex api.openalex.org, Crossref, Semantic Scholar si responde, Dialnet, RePEc/IDEAS,
Harvard Dataverse, Zenodo, OSF) y búsqueda web. Consultas en español e inglés (patronazgo, politización, nombramientos,
directivos públicos, empresas públicas, consejos de administración, puertas giratorias, party patronage, political
appointees, state-owned enterprises boards, political connections, senior civil service, junior ministers, Spain…).
Incluye y verifica las semillas de ARQUITECTURA.md §7.
Salidas: fase2/literatura/busqueda.csv (todo lo encontrado: titulo, autores, año, revista, doi/url, fuente, consulta),
fase2/literatura/cribado.csv (relevancia 0–3 con motivo de una línea; marca si tiene paquete de replicación y dónde;
si hay PDF abierto, descárgalo y anota la ruta), fase2/literatura/README.md con el registro de búsqueda (consultas,
fechas, cifras). Objetivo: 15–25 trabajos de relevancia 3 para lectura completa en la fase siguiente.
