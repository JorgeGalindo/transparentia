# Arquitectura · Fase 2: ¿quién ocupa los puestos que deberían ser técnicos?

Versión 1 · 1/11/2026 · Documento de diseño, con las decisiones de Jorge del 1/11 incorporadas (sección 12). Todavía no se ha ejecutado nada de lo que aquí se describe.
Lo usan Claude, Codex y la cola de tareas por API como contexto común.

## 0. Objetivo

**Pregunta.** En los puestos del ejecutivo y de las empresas públicas que, por norma o por función, deberían ocupar
perfiles técnicos, ¿cuántos están ocupados por personas **con afiliación política clara** y **sin experiencia
relevante** para el puesto?

**Alcance.** El análisis es descriptivo. Parte de la foto del 1/11/2026, que es la base ya construida, y sigue hacia
delante: nombramientos, ceses, elecciones del 29/11 y el Gobierno siguiente. **No se reconstruye el pasado** en esta
fase, aunque el modelo de datos lo permite más adelante.

**Fuera del indicador:** los asesores parlamentarios (Congreso y Senado) y el personal eventual. Si aparecen en un CV
se registran, pero no cuentan como afiliación.

## 1. Decisiones de diseño que mandan

1. **Unidad de análisis: la ocupación** (persona × puesto × periodo). Una persona puede ocupar varias sillas.
2. **Clases de puesto, fijadas antes de mirar a las personas:**
   - **T-legal**: subsecretarios, secretarios generales técnicos y directores generales. La Ley 40/2015 (arts. 63–66)
     exige que sean funcionarios de carrera A1, salvo excepción en el real decreto de estructura.
   - **T-empresa**: primeros ejecutivos y consejeros de empresas públicas, **incluidas las sillas dominicales que ocupan
     funcionarios de ministerios**: no van aparte. Las directrices de la OCDE sobre empresas públicas piden consejos
     profesionales.
   - **T-regulador**: presidencias y consejos de reguladores y agencias técnicas.
   - **P (político por diseño)**: secretarios de Estado, secretarios generales de libre designación, gabinetes y
     comisionados. **Es el grupo de referencia.**
   - **Fuera del análisis**: embajadores (también los políticos), delegados del Gobierno, mandos militares y mutuas.
3. **Estándar de evidencia.** Cada hecho codificado lleva fuente (URL y fecha) y una cita textual. Sin evidencia no hay
   código.
   - La afiliación se mide como **«afiliación documentada»**, una cota inferior, porque en España no hay registro
     público de militancia.
   - «No detectada» y «verificado que no tiene» son cosas distintas.
4. **Simetría.** El mismo codebook se aplica a todos los partidos y se fija antes de codificar (preregistro ligero).
   El seguimiento hacia delante permite comparar a este Gobierno con el siguiente: es la mejor defensa de la neutralidad
   de EsadeEcPol.
5. **Datos personales.** La opinión política es categoría especial (RGPD, art. 9). Por eso:
   - Solo se usa información **manifiestamente pública**: cargos electos, candidaturas, cargos orgánicos y
     declaraciones públicas.
   - No se infiere militancia de indicios débiles.
   - **Se publica también a nivel individual**, pero la ficha de cada persona solo muestra afiliación **pública y
     notoria** (niveles 3 y 4: cargo electo, cargo orgánico, miembro de un gobierno), siempre con su fuente. Las
     candidaturas y los indicios débiles solo entran en los agregados de robustez, nunca en una ficha.
6. **Hacia delante y automático.** Cada nombramiento nuevo que detectan los vigías dispara, por cola, la búsqueda de su
   CV, la extracción y la codificación.

## 2. Diagrama

<!--DIAGRAMA-->
```
FUENTES                 INGESTA                 EXTRACCIÓN              BASE (DuckDB)            CODIFICACIÓN Y SALIDAS
Oficiales accesibles ─▶ Vigías semanales ───────────── eventos ─────────▶ persona               Codificación
 BOE, BORME, Moncloa     (BOE·BORME·CM, sin LLM)                          posición · entidad  ─▶  reglas + Sonnet 5.5
 Transparencia (CV)    ▶ Cargadores/scrapers ─▶ Parsers deterministas ─┐  ocupación · eventos     doble: Opus 5.5
 Senado, P. Europeo      (Codex)                 Extracción LLM ───────┼▶ trayectoria             validación humana
 Wikidata, concejales    │                       (Haiku 5.5, batch)    │  funcionario · formación   │
Bloqueadas a scripts ──▶ │ (Chrome, manual)      Enlace de identidades ┘  cargo electo              ├▶ Descriptivos D1–D11
 Congreso, Infoelect.    ▼                       + cola de revisión       candidatura · partido     ├▶ Panel (artifact)
 CNMV                   Almacén bruto (docs + hash)                       evidencia (url + cita)    └▶ Paquete de replicación
Web abierta ──────────────────────────────────▶ Enriquecimiento agéntico ◀─ huecos ─┘
 webs, prensa, partidos                          (Sonnet 5.5 + búsqueda web) ─ hechos + evidencia ─▶ base

LITERATURA: OpenAlex·Dialnet ▶ cribado (Haiku) ▶ lectura completa con cita y página (Opus) ▶ re-chequeo (Sonnet) ▶ paquetes de replicación ▶ CODEBOOK
ORQUESTACIÓN: tareas/ (agente: codex | api | claude-p | chrome | jorge) · actualizar.sh semanal · Claude = arquitectura y QA
```
<!--/DIAGRAMA-->

## 3. Quién hace qué

| Pieza | Quién | Modelo | Por qué |
|---|---|---|---|
| Cargadores, scrapers, parsers, esquema DuckDB y tests | **Codex** | — | Es trabajo de código: no gasta tokens de Claude |
| Extracción estructurada de CV (texto limpio a JSON) | API, Batch | **Haiku 5.5**; control del 10 % con Sonnet 5.5 | Barato y suficiente con esquema JSON |
| Búsqueda abierta de afiliación o experiencia por persona | API, agente | **Sonnet 5.5** + búsqueda y lectura web | Haiku falló en los barridos abiertos (1/11) |
| Clasificación de puestos y codificación de personas | API, Batch | **Sonnet 5.5** | Requiere criterio; con Batch cuesta la mitad |
| Doble codificación y desacuerdos | API, Batch | **Opus 5.5** | Mide la fiabilidad del codificador |
| Lectura completa de artículos (cita y página) | API | **Opus 5.5**; re-chequeo con Sonnet 5.5 | Regla de la casa: lectura completa y verificada |
| Arquitectura, codebook, QA, revisión de lo que entrega Codex y panel | **Claude** (esta sesión) | — | Mínimo: lee resúmenes y diffs, no datos en bruto |
| Decisiones, validación muestral e interpretación | **Jorge** (o un asistente de investigación) | — | Unas 4–6 h de validación en la fase 5 |

**Coordinación.**
- Todo vive en el repo; Codex lee `AGENTS.md` y este documento.
- Cada tarea de `tareas/` lleva un campo `agente:` y solo la ejecuta ese agente.
- Se commitea a main con pull antes.
- Claude revisa los commits de Codex antes de dar una fase por cerrada.
- La clave de API va en el llavero y se lee en cada proceso; nunca en ficheros ni en el chat.

## 4. Modelo de datos (DuckDB, con exportación a CSV/Parquet)

| Tabla | Campos clave |
|---|---|
| `persona` | id, nombre, apellidos, nombre normalizado, género, año de nacimiento (si es público), id de Wikidata |
| `posicion` | id, tipo (unidad AGE, organismo, silla de consejo, primer ejecutivo), nivel, ministerio, entidad, **clase (T-legal / T-empresa / T-regulador / P)**, requisito de funcionario A1, excepción en el RD, intensidad técnica de las funciones (0–3), sector, tipo de silla, retribución |
| `entidad` | id, forma jurídica, matriz, ministerio de adscripción, % público, cotizada, sector, empleados, presupuesto |
| `ocupacion` | persona, posición, inicio, fin, fuente del nombramiento (BOE, BORME o Consejo de Ministros), socio de coalición del ministerio, gobierno |
| `evento` | registro solo de altas: fecha, tipo (nombramiento, cese, alta o baja en consejo), persona, posición, fuente, aplicado o revisado |
| `trayectoria` | persona, organización, tipo (AGE, CCAA, local, empresa pública, privada, partido, sindicato, universidad, internacional), cargo, nivel de responsabilidad, sector, fechas, designación política (sí/no), evidencia |
| `formacion` | persona, nivel, título, campo (ISCED-F), institución |
| `funcionario` | persona, cuerpo, subgrupo, año de ingreso, BOE |
| `cargo_electo` | persona, institución (Congreso, Senado, Parlamento Europeo, parlamento autonómico, ayuntamiento, diputación o cabildo), partido, legislatura, fechas, fuente, calidad del cruce |
| `candidatura` | persona, elección, circunscripción, partido, puesto en la lista, si salió elegido |
| `cargo_partido` | persona, partido, órgano (ejecutiva federal, autonómica o local…), cargo, fechas, evidencia |
| `evidencia` | url, fecha de consulta, tipo de fuente, **cita textual**, extractor (script o modelo, versión y prompt), confianza, revisor |
| `codificacion` | persona × posición × versión del codebook: las variables de la sección 5, modelo codificador, acuerdo y validación humana |

## 5. Variables (codebook v0, a fijar en la fase 0)

**Afiliación documentada** (ordinal):

| Nivel | Qué cuenta |
|---|---|
| 0 | Sin evidencia |
| 1 | Indicio débil: gabinete político, fundación de partido. No entra en el indicador principal |
| 2 | Candidato en listas, sin salir elegido |
| 3 | Cargo orgánico de partido o cargo electo local |
| 4 | Cargo electo autonómico, nacional o europeo, o miembro de un gobierno (ministro, consejero autonómico, alcalde) |

- Se registra además el **partido** (PSOE/PSC, espacio Sumar, PP, Vox, nacionalistas…).
- **Indicador principal: nivel 3 o más.** El nivel 2 o más, como robustez.

**Experiencia relevante.** Tres componentes:
- (a) Años de experiencia en el **sector del puesto** antes del nombramiento.
- (b) Experiencia directiva previa en una organización comparable.
- (c) Credencial técnica: un cuerpo A1 relevante (Abogados del Estado, Técnicos Comerciales y Economistas del Estado,
  Inspectores de Hacienda, Ingenieros de Caminos…) o formación de posgrado en el campo.

«Sin experiencia relevante» = (a) menos de 3 años, sin (b) y sin (c). Como sensibilidad se prueban 0 y 5 años. La
referencia normativa es la idoneidad que exige la Ley 3/2015 (conocimientos y experiencia).

**Indicador clave, PPSE (perfil político sin experiencia relevante):** afiliación de nivel 3 o más y sin experiencia
relevante.

**Tipología de perfil:** técnico, político, híbrido o sin perfil reconocible. Es comparable con la de la literatura
sobre secretarios de Estado (ver sección 7).

**Otras variables:** ministerio, socio de coalición, sector, tamaño de la entidad, si cotiza, tipo de silla, género,
edad, fecha de nombramiento (ventana preelectoral), retribución, y meses desde el último cargo electo («aterrizaje»).

## 6. Qué testaríamos (descriptivos)

| # | Pregunta | Corte |
|---|---|---|
| D1 | % con afiliación documentada | Clases T frente a P, con IC al 95 % |
| D2 | % sin experiencia relevante | Por clase |
| D3 | **% PPSE (titular del informe)** | Por clase; T-empresa frente a T-legal frente a P |
| D4 | Heterogeneidad | Ministerio, **socio de coalición (PSOE o Sumar)**, sector, tamaño de la empresa, cotizada o no, tipo de silla (presidente ejecutivo, dominical, independiente) |
| D5 | Directores generales que no son funcionarios (excepciones del art. 66.2) | Su perfil frente al de los DG funcionarios |
| D6 | «Aterrizajes»: meses entre el fin de un cargo electo y el nombramiento | Recolocación en 12 meses o menos, por partido |
| D7 | Credenciales | % de cuerpos de élite y de experiencia privada, por clase |
| D8 | Género y edad | Por perfil |
| D9 | Retribución | PPSE frente al resto (grupos retributivos de empresas públicas) |
| D10 | Dinámica hacia delante | (a) ¿son más políticos los nombramientos de la ventana preelectoral (sept.–nov. 2026)? (b) ¿se cesa antes a los perfiles políticos cuando cambia el Gobierno? (c) foto del nuevo Gobierno frente al saliente |
| D11 | Validación externa | Concordancia con el Dedómetro de Hay Derecho (SEPI) y con la tipología académica de secretarios de Estado |

Proporciones con intervalos de Wilson. Modelos lineales de probabilidad o logit de PPSE sobre la clase y controles,
leídos como asociación descriptiva, no causal. Robustez a los umbrales y al nivel de evidencia.

## 7. Pata de literatura

**Protocolo** (regla de la casa: lectura completa, cita y página por cada afirmación, re-chequeo independiente):
1. Búsqueda en OpenAlex, Dialnet, RePEc y Dataverse/Zenodo/OSF, en español e inglés, centrada en 2015–2026, con los
   clásicos.
2. Cribado de resúmenes con Haiku.
3. Lectura completa de 15–25 trabajos con Opus. Para cada uno: universo, cómo miden afiliación y pericia, fuentes,
   fiabilidad, resultados y paquete de replicación.
4. Re-chequeo independiente de cada cita con Sonnet.
5. Descarga y evaluación de los paquetes de replicación: ¿se pueden fusionar con nuestra base o ampliar?
6. Matriz y nota de 2 páginas: qué tomar prestado para el codebook y qué hueco cubre este trabajo.

**Semillas que han salido en el barrido del 1/11** (aún sin leer):
- Gómez y Verge (2012), «Party Patronage in Spain: Extensive But Not Pervasive Use of Appointments as a Tool of Party
  Government», capítulo del libro de Kopecký, Mair y Spirova (OUP).
- «Politicians, experts or both? Democratic delegation and junior ministers in Spain», *Acta Politica* (2016):
  secretarios de Estado 1977–2010, con tipología de políticos, expertos e híbridos.
- Fundación Hay Derecho: *Estudio sobre la meritocracia en la designación…* (2020) y las ediciones del *Dedómetro*
  (la de SEPI es de mayo de 2026).
- Staronova y Rybář (2021), sobre el efecto del cambio de ministro en los altos funcionarios (Eslovaquia).
- Van Dorp (2023), sobre el nombramiento de secretarios generales (Países Bajos).
- Toral, «How Patronage Delivers» (Brasil).

**De memoria, a verificar antes de citarlas:**
- Kopecký, Mair y Spirova (2012), la encuesta a expertos sobre patronazgo.
- Ennser-Jedenastik (2014), sobre la supervivencia de los directivos de empresas públicas austriacas.
- Colonnelli, Prem y Teso (2020, *AER*), con paquete de la AEA.
- Toral (2024), sobre la rotación de los gobiernos salientes (lame duck).
- Cuñat y Garicano (2010), sobre la gobernanza y el capital humano de las cajas.
- Dahlström y Lapuente (2017).

**Primer hallazgo:** no aparece ningún estudio académico español reciente con paquete de replicación sobre la
politización de directivos y consejos de empresas públicas. Lo que hay son informes de think tanks y prensa (*The
Objective*, *El Debate*) sin metodología publicada. Ese es el hueco que cubriría este trabajo.

## 8. Fases, días y coste

| Fase | Qué sale | Días | Quién | Coste API |
|---|---|---|---|---|
| F0 Codebook y decisiones | `CODEBOOK.md` v0, clases de puesto, umbrales, consulta al DPO | 1–2 | Claude + Jorge (1 h) | — |
| L Literatura (en paralelo) | Matriz, nota, paquetes de replicación | 3–4 | API + QA de Claude | 10–20 $ |
| F1 Base relacional | DuckDB, foto inicial migrada, identidades únicas, atributos de las entidades | 2 | Codex | — |
| F2 Cargos electos y candidaturas | Senado, Congreso (Chrome o Wikidata), Parlamento Europeo, parlamentos autonómicos (Wikidata + Transparentia), concejales, Infoelectoral (Chrome); cruces y cola de revisión | 3–4 | Codex (+ Chrome) | — |
| F3 Trayectorias (en paralelo a F2) | CV de Transparencia (~700), CV de las referencias del Consejo de Ministros, bios de cotizadas, cuerpo de funcionario por el BOE | 2–3 | Codex + API Batch | 3–10 $ |
| F4 Enriquecimiento agéntico | Partido, candidaturas y huecos de experiencia de ~1.400 personas, con evidencia | 2–3 | API (Sonnet + búsqueda) | 190–270 $ |
| F5 Codificación y validación | Clases de puesto, experiencia, afiliación, PPSE; doble codificación; validación de 100–150 casos; kappa | 3–4 | API + Jorge (4–6 h) | 30–40 $ |
| F6 Descriptivos v1 + panel v2 | Tablas y gráficos D1–D11, esquema del brief | 2 | Claude/Codex | — |
| F7 Sistema hacia delante | Vigías BORME y Consejo de Ministros, disparadores de enriquecimiento, foto S1 tras la investidura | 1–2, luego continuo | Codex + cola | 15–30 $/mes |

**Tiempo:** el camino crítico es F0 → F1 → (F2 ∥ F3) → F4 → F5 → F6, de **13 a 16 días laborables**. Decisión: los
descriptivos v1 salen **antes del 29/11**, así que el calendario va apretado y sin holgura para retrasos en la clave de
API o en Codex:

| Fechas | Fase |
|---|---|
| 2–3 nov. | F0 codebook (y arranca la literatura, que corre en paralelo hasta el 5) |
| 3–4 nov. | F1 base relacional |
| 5–10 nov. | F2 cargos electos ∥ F3 trayectorias |
| 10–12 nov. | F4 enriquecimiento agéntico |
| 12–17 nov. | F5 codificación; **tu validación (4–6 h) el 16–17** |
| 18–19 nov. | F6 descriptivos v1 y fichas |
| 20–27 nov. | Margen, revisión y publicación |

**Coste API (clave de pago):**
- Arranque: **unos 300–400 $**, con techo de 500 $ si hay que repetir pasadas.
- La mayor partida es la búsqueda agéntica: unos 70.000 tokens por persona, buena parte en caché; Sonnet 5.5 cuesta
  2 $ de entrada y 10 $ de salida por millón, y la búsqueda web 10 $ por cada 1.000.
- Mantenimiento: **15–30 $ al mes**. Tras el cambio de Gobierno, un pico de **100–200 $** por 300–500 nombramientos
  nuevos.
- Codex corre con tu plan de OpenAI. Esta sesión de Claude solo orquesta.

**Precios** (verificados el 1/11/2026 en la página oficial de precios), por millón de tokens de entrada / salida:

| Modelo | Entrada / salida | Lectura de caché |
|---|---|---|
| Haiku 5.5 | 0,10 $ / 0,50 $ | 0,01 $ |
| Sonnet 5.5 | 2 $ / 10 $ | 0,10 $ |
| Opus 5.5 | 4 $ / 20 $ | 0,20 $ |

La Batch API tiene un 50 % de descuento y la búsqueda web cuesta 10 $ por cada 1.000 búsquedas.

## 9. Fuentes: estado de acceso (comprobado el 1/11/2026)

| Fuente | Para qué | Acceso |
|---|---|---|
| BOE, API de sumarios | Nombramientos y ceses (el vigía ya funciona) | 200 |
| BORME, API | Altas y bajas en consejos de sociedades estatales | 200 |
| Moncloa, referencias del Consejo de Ministros | CV de los nombrados | 200 |
| Transparencia: CV, declaraciones de bienes y actividades | Trayectoria y actividad previa | 200 |
| Senado, datos abiertos | Senadores de todas las legislaturas | 200 |
| Parlamento Europeo | Eurodiputados | 200 |
| Wikidata (SPARQL) | Cargos ocupados y partido | 200 |
| Concejales (redsara) | Cargos electos locales (buscador por nombre) | 200 |
| Transparentia (Newtral, en el repo) | Historial de cargos electos (los titulares actuales están desfasados) | local |
| Congreso, datos abiertos | Diputados de todas las legislaturas | **403 a scripts**: descarga manual por Chrome o Wikidata |
| Infoelectoral (Interior) | Candidaturas | **403**: descarga manual por Chrome |
| CNMV | Consejeros de cotizadas | **403**: IAGC en PDF desde la web de cada cotizada |
| Parlamentos autonómicos | Diputados autonómicos | 17 webs distintas; primero Wikidata y Transparentia |
| OpenAlex, Dialnet, Dataverse | Literatura y paquetes | 200 |

Regla fija: **no se falsean cabeceras**. Lo que bloquea se baja una vez desde Chrome o se busca por otra vía.

## 10. Riesgos y salvaguardas

| Riesgo | Salvaguarda |
|---|---|
| No hay registro de militancia | Medir «afiliación documentada» como cota inferior y separar «no detectada» de «sin afiliación» |
| Homónimos | Cruce con contexto (partido, territorio, fechas) y cola de revisión para casos dudosos |
| Los CV omiten lo partidista | Triangular con registros electorales, prensa y Wikidata |
| Sesgo de disponibilidad (de quien tuvo cargo electo hay más información) | Reportarlo; la búsqueda agéntica es igual para todos |
| El LLM codifica mal | Esquema cerrado, cita obligatoria, doble codificación y validación humana (objetivo: kappa ≥ 0,7) |
| RGPD art. 9 | Solo hechos manifiestamente públicos, agregados y revisión del DPO |
| Lectura partidista | Codebook fijado antes de codificar, simetría y comparación entre gobiernos |
| Webs bloqueadas | Chrome o alternativas, nunca cabeceras falsas |

## 11. Encaje con lo que ya hay

- La base del 1/11 (351 unidades, 371 otros altos cargos, 106 entidades y 891 consejeros) es la **foto S0**.
- El **vigía del BOE** pasa a alimentar la tabla `evento`. Se le añaden BORME y Consejo de Ministros.
- La **cola `tareas/`** recibe el campo `agente:` y nuevos tipos de tarea (`enriquecer`, `codificar`, `literatura`).
- El **panel** gana pestañas: perfiles, PPSE por clase y evolución.

## 12. Decisiones tomadas (Jorge, 1/11/2026)

1. **Sillas dominicales de funcionarios de ministerios:** no van aparte; entran en T-empresa.
2. **Umbral de experiencia:** 3 años en el sector, o credencial técnica, o dirección comparable; sensibilidad con 0 y
   5 años.
3. **Indicador principal:** afiliación de nivel 3 o más; las candidaturas, solo en la robustez.
4. **Publicación:** también fichas individuales, pero solo con afiliación pública y notoria (niveles 3–4), siempre con
   fuente.
5. **Calendario:** descriptivos v1 antes del 29/11.
6. **Embajadores políticos y delegados del Gobierno:** fuera del análisis.

**Pendiente para arrancar:**
- La clave de API en el llavero. Que no pase por el chat: guárdala desde tu Terminal con
  `security add-generic-password -a "$USER" -s anthropic-api-key-pago -w`, que te la pide sin mostrarla.
- Codex conectado al repo, con un `AGENTS.md` que preparo al arrancar.
