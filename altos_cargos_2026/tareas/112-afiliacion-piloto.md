modelo: sonnet
salida: fase2/afiliacion/piloto.jsonl
estado: pendiente
prioridad: 1
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 22:33
---
Carpeta asignada: fase2/afiliacion/.
Construye el buscador de afiliación por persona y pruébalo en un piloto de 50.
- Script buscar_afiliacion.py con el SDK de Anthropic (credencial: `security find-generic-password -s
  anthropic-api-agentes -w`, solo en memoria), modelo `claude-sonnet-5-5` con las herramientas de servidor de búsqueda y
  lectura web (tipos `web_search_20260209` y `web_fetch_20260209`, máximo 5 búsquedas por persona).
- Entrada por persona: nombre, puesto actual, entidad o ministerio, y lo que ya sabemos (cargos electos de
  fase2/fuentes/electos/ y fase2/fuentes/locales/ si los hay). Tarea del modelo: encontrar hechos públicos y notorios de
  afiliación (cargo electo, cargo orgánico de partido, candidatura publicada, miembro de un gobierno) con url y cita, y
  devolver JSON según el esquema de búsqueda de afiliación de fase2/codebook/esquemas/ y los niveles de CODEBOOK.md §3.
  Nunca inferir militancia; distinguir «no encontrado» de «consta que no».
- Piloto: 50 personas estratificadas (10 T-legal, 15 T-empresa con primer ejecutivo, 10 T-empresa consejeros,
  5 T-regulador, 10 P) tomadas de fase2/codebook/clase_posicion.csv. Registra tokens y búsquedas por persona.
Salidas: piloto.jsonl, coste_piloto.md (coste medio por persona y proyección para ~1.100 personas, calidad observada,
falsos positivos detectados, homónimos) y README.md. No lances más allá del piloto.
