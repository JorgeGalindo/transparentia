# Literatura: búsqueda y cribado (tarea 102, pasos L1–L2)

Consulta: 2026-11-01. Pregunta: nombramientos políticos, patronazgo y pericia en altos cargos y en directivos/consejos de empresas públicas (España 2015–2026, comparados y clásicos).

## Qué hay
- `busqueda.csv`: 1.440 filas (24 consultas × OpenAlex y Crossref; ~40 y 20 resultados por consulta). Script `busqueda.py`.
- `busqueda_repos.csv`: 315 filas (Dataverse 150, Zenodo 150, Dialnet 15). Script `busqueda_repos.py`. Cifras por consulta en `*_stats.json`.
- `cribado.csv`: 1.576 registros únicos (tras deduplicar por DOI y añadir 9 semillas verificadas aparte). Script `cribado.py`.
  - Relevancia 3: **23** (manual). Relevancia 2: 13 manual + 8 heurísticos. Relevancia 1: 240. Relevancia 0: 1.292.
  - `criterio=manual` significa que la decidí con título, metadatos y (cuando había) resumen, **sin lectura completa**. `heuristico` es solo puntuación por palabras clave: no vale como cribado fino; las relevancias 1–2 heurísticas hay que revisarlas.
- Datos brutos y caché de API: `fase2/data/raw/literatura/`.

## Consultas
ES/EN: party patronage Spain, patronazgo político España, politización administración, political appointees senior civil service, junior ministers, secretarios de Estado, state-owned enterprises boards political connections, empresas públicas consejos, directivos públicos, revolving doors / puertas giratorias, cajas de ahorros, bureaucratic turnover, meritocracia… (lista completa en `busqueda.py` y `busqueda_repos.py`).

## Verificación de semillas (§7)
| Semilla | Estado |
|---|---|
| Gómez y Verge 2012 | Verificada (OUP, cap. 16). Título real: «Party Patronage in Spain: Appointments for Party Government» |
| Real-Dato y Rodríguez-Teruel 2016, *Acta Politica* | Verificada |
| Staronova y Rybář | Verificada, pero es *Administration & Society* **2020** (no 2021) |
| Van Dorp 2023 | **No localizada.** Sí hay Ennser-Jedenastik 2016 (*Acta Politica*, élites administrativas holandesas) |
| Toral, *How Patronage Delivers* | Verificada (AJPS 2023), con paquete en Dataverse |
| Kopecký, Mair, Spirova 2012 | Verificada; además la encuesta de expertos en *EJPR* 2016 |
| Ennser-Jedenastik | Verificada pero es *Governance* **2013** (no 2014); hay un segundo artículo en *Political Studies* 2013 |
| Colonnelli, Prem, Teso 2020 *AER* | Verificada; paquete AEA no confirmado |
| Toral 2024 lame duck | Verificada (*JOP* 2024), con paquete en Dataverse |
| Cuñat y Garicano 2010 | **No localizada** en OpenAlex ni Crossref (documento de trabajo). Se sustituye por García-Cestona et al. 2022 y De Andrés et al. 2020 sobre cajas |
| Dahlström y Lapuente 2017 | Verificada (CUP) |
| Hay Derecho: estudio 2020 y Dedómetro SEPI mayo 2026 | **No confirmados.** Sí hay ediciones del Dedómetro (estatal, Cataluña 2025, C. Valenciana) en prensa (Economist & Jurist, Valencia Plaza, The Objective). Sin metodología replicable verificada. Consultar hay-derecho directamente |

## Paquetes de replicación hallados (Dataverse)
Toral 2023 (`doi:10.7910/DVN/GHJ8JL`), Toral 2024 (`KO2VPS`), Brierley 2020 (`O0JVDU`). Colonnelli et al.: AEA/openICPSR por confirmar. Ningún estudio español de relevancia 3 tiene paquete localizado: confirma el hueco de §7.

## Límites y bloqueos
- **Dialnet** devolvió HTML con un solo resultado útil (15 filas) y **RePEc/IDEAS y OSF devolvieron 0**: parser/endpoint no válido o bloqueo; no se insistió. Lo español se cubre vía OpenAlex (indexa Dialnet) pero queda sin barrer Dialnet a fondo. Semantic Scholar respondió 429, no usado.
- OpenAlex sin clave (presupuesto compartido); no se creó clave porque implica dar el correo de Jorge a un servicio externo.
- Solo 1 PDF descargado (`fase2/data/raw/literatura/pdf/`): `oa_url` rara vez apunta a un PDF directo. La columna `oa_url` en `cribado.csv` queda para la fase siguiente.
- Relevancia 3 ligada a metadatos y títulos, no a lectura; el paso 3 debe confirmar universo, medición y fiabilidad.
