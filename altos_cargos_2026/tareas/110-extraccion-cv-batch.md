modelo: sonnet
salida: fase2/extraccion/trayectorias.jsonl
estado: pendiente
prioridad: 1
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 22:34
---
Carpeta asignada: fase2/extraccion/.
Extrae trayectoria, formación y condición de funcionario de los CV descargados (fase2/fuentes/cv/manifiesto_cv.csv;
textos en fase2/data/raw/cv/) con la **Batch API de Anthropic**, usando el esquema
fase2/codebook/esquemas/ (el de extracción de CV) y las reglas de fase2/CODEBOOK.md (sectores de sectores.csv).
- SDK oficial de Python (`uv run --with anthropic ...`). Credencial: token del llavero leído en el proceso
  (`security find-generic-password -s anthropic-api-agentes -w`), pasado como api_key; nunca a disco ni a logs.
- Modelo `claude-haiku-5-5` para todos; `claude-sonnet-5-5` para un 10 % aleatorio como control de calidad.
  Salida JSON validada contra el esquema (structured outputs). Prompt de sistema estable y cacheado.
- Primero un piloto de 20 CV en llamadas normales: revisa la calidad, ajusta el prompt y estima el coste. Después lanza
  el lote completo por Batch, espera a que termine y recoge resultados por custom_id.
- Una persona puede tener varios CV (Transparencia + Moncloa): fusiona y deja constancia de la fuente de cada tramo.
Salidas: trayectorias.jsonl (una línea por persona), control_calidad.csv (acuerdo Haiku vs Sonnet por campo),
extraer.py reproducible y README.md con cifras, coste real (usage) y problemas.
