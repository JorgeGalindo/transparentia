modelo: opus
salida: fase2/literatura/matriz.csv
estado: pendiente
prioridad: 1
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 22:33
---
Carpeta asignada: fase2/literatura/ (PDF a fase2/data/raw/literatura/pdf/). No modifiques busqueda.csv ni cribado.csv.
Paso L3. Toma los trabajos de relevancia 3 de fase2/literatura/cribado.csv. Para cada uno consigue el texto completo
(oa_url, repositorio institucional, versión de trabajo del autor, SSRN/RePEc; nada de webs piratas) y léelo ENTERO.
Si no hay texto completo legal, márcalo «sin texto completo» y no lo resumas desde el abstract.
Para cada trabajo leído, una fila en matriz.csv: referencia completa, pregunta, universo y periodo, unidad de análisis,
cómo mide afiliación política (literal), cómo mide pericia/experiencia (literal), fuentes de datos, fiabilidad o
validación, resultado principal, paquete de replicación (url, contenido, licencia), qué tomamos para nuestro codebook.
Regla de la casa: cada afirmación de la matriz lleva cita textual corta y página (columna citas, formato «p. X: "…"»).
Además, escribe fase2/literatura/nota.md (≤2 páginas): qué hace la literatura, cómo miden lo que queremos medir, qué
tomamos prestado y qué hueco cubre este trabajo. Sin afirmaciones que no estén en la matriz.
