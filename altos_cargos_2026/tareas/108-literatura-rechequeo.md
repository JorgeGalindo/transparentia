modelo: sonnet
salida: fase2/literatura/rechequeo.csv
estado: espera
prioridad: 2
comun: fase2
agente: claude-p
---
Carpeta asignada: fase2/literatura/ (solo escribe rechequeo.csv y rechequeo.md).
Re-chequeo independiente de fase2/literatura/matriz.csv: para cada cita con página, abre el texto completo
(fase2/data/raw/literatura/pdf/ o la url) y comprueba que la cita existe literalmente en esa página y que la afirmación
que la acompaña es fiel. Una fila por cita: trabajo, pagina, cita, existe (sí/no/aprox), fiel (sí/no/parcial), nota.
Resume en rechequeo.md la tasa de error y lista lo que hay que corregir.
