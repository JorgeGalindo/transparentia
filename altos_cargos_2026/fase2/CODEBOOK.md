# CODEBOOK v0 · Politización de puestos técnicos

v0 · 1/11/2026 · Borrador operativo que se fija con Jorge en la F0. Mandan las secciones 1, 5 y 12 de `ARQUITECTURA.md`.
**Preregistro ligero:** una vez fijado, no se cambia sin subir la versión y anotarlo en la sección 9. Cada codificación guarda
la versión con la que se hizo. Las reglas son las mismas para todos los partidos.

| Fichero | Qué es |
|---|---|
| `fase2/codebook/clases.py` → `clase_posicion.csv` | Reglas de la sección 1 aplicadas a S0 (1.703 filas) |
| `fase2/codebook/sectores.csv` | 24 sectores: definición, ejemplos, cuerpos A1, campos ISCED-F |
| `fase2/codebook/esquemas/*.schema.json` | Extracción de CV, búsqueda de afiliación, codificación por ocupación |
| `fase2/codebook/validar_esquemas.py` | Comprobación de esquemas y de `sectores.csv` |

**Unidad:** la ocupación (persona × posición × periodo). La clase y el sector son de la **posición** y se fijan sin mirar a
la persona. La afiliación es de la **persona**. La experiencia es de la **ocupación**: se mide en la fecha de inicio.

---

## 1. Clases de puesto

### 1.1 Definición

| Clase | Qué incluye | Base |
|---|---|---|
| **T-legal** | Subsecretarías, SGT, DG de ministerio (incluidas las de rango DG); puestos reservados a cuerpos A1 (IGAE, Abogacía General, interventores e inspectores generales civiles); dirección o gerencia de organismos públicos que no son empresa ni regulador (organismos autónomos, entidades gestoras de la SS, consorcios, fundaciones, museos) | L40/2015: arts. 63.3 y 65.3 («entre funcionarios de carrera… pertenecientes al Subgrupo A1») y 66.2 («salvo que el Real Decreto de estructura permita que… su titular no reúna dicha condición»). L3/2015, art. 2.1: idoneidad = «la debida formación y experiencia en la materia» |
| **T-empresa** | Primeros ejecutivos, alta dirección y **todas las sillas** de consejo de sociedades estatales, EPE, autoridades portuarias, SEPI y participadas con control público (>50 %), **incluidas las dominicales que ocupan funcionarios de ministerios**. En participadas no controladas (≤50 %), solo las sillas del accionista público | Directrices de la OCDE sobre empresas públicas: consejos profesionales (ARQUITECTURA §1) |
| **T-regulador** | Presidencias, consejos y direcciones de reguladores y supervisores (CNMC, CNMV, CSN, AEPD, AIReF, FROB, AESIA…), agencias de inspección y seguridad (AESA, AESF, AEMPS, AESAN, ITSS, CELAD, ICAC, OCI, TEAC, Comisionado para el Mercado de Tabacos), estadística y agencias científico-técnicas (INE, CIS, AEMET, OEPM, CSIC, ISCIII, AEI, CIEMAT, INTA, CEDEX, ONT…) y la AEAT | Función técnica por diseño |
| **P** | Secretarías de Estado y puestos con su rango; secretarías generales de ministerio; comisionados y oficinas ad hoc; gabinetes y departamentos del Gabinete de la Presidencia. **Grupo de referencia** | L40/2015, art. 64.3: los SG se nombran «entre personas con cualificación y experiencia», sin requisito de funcionario |
| **FUERA** | Gobierno (presidente, ministros), embajadores (también los políticos), delegados del Gobierno en CCAA, mandos militares y puestos de oficial general, mutuas, rectores, sillas privadas en participadas no controladas, secretarios no consejeros | Decisiones de Jorge del 1/11 (§12.6); el resto, por coherencia (sección 1.4) |

### 1.2 Reglas de asignación (gana la primera que casa)

Las listas cerradas de entidades y los patrones están en `clases.py`. Una posición nueva detectada por los vigías pasa por
las mismas funciones (`clase_puesto`, `clase_silla`).

**Unidades AGE y otros altos cargos** (`clase_puesto`):

| Orden | Código | Condición | Clase |
|---|---|---|---|
| 1 | F0 | Nivel 1 (ministerio, Presidencia del Gobierno), ministro/a o presidente del Gobierno | FUERA |
| 1 | F1 | Embajador/a o representante permanente | FUERA |
| 1 | F2 | Delegado/a del Gobierno en una CCAA (las delegaciones **temáticas** no: van a L3) | FUERA |
| 1 | F3 | Mando militar; inspector general del Ejército, asesor jurídico general o interventor general de la Defensa, CESEDEN | FUERA |
| 1 | F4 | Mutua colaboradora (también «DG de Ibermutua») | FUERA |
| 1 | F5 | Rector de universidad | FUERA |
| 2 | R1 | Entidad en la lista de autoridades independientes, supervisores e inspección | T-regulador |
| 2 | R2 | Entidad en la lista de estadística y agencias científico-técnicas | T-regulador |
| 2 | R3 | AEAT y sus departamentos | T-regulador |
| 3 | E1 | Categoría «Empresa pública / EPE» o entidad en la lista de EPE/SME (ENAIRE, ICEX, CDTI, IDAE, Red.es, FNMT, Renfe, Adif, Puertos del Estado, SEPI, Casa 47, Enresa, ICO, zonas francas) | T-empresa |
| 4 | P1 | Secretaría de Estado, o «con rango de secretario de Estado» | P |
| 4 | P2 | Secretaría general de ministerio (no técnica). Una SG «adscrita» a un organismo va a L5, salvo la de Instituciones Penitenciarias, que es ministerial | P |
| 4 | P3 | Comisionado; oficina ad hoc (Reconstrucción de Ucrania) | P |
| 4 | P4 | Gabinete, director/a de gabinete, departamentos del Gabinete de la Presidencia, oficinas de Presidencia (Asuntos Económicos y G-20, Conferencia de Presidentes) | P |
| 5 | L1 | Subsecretaría | T-legal |
| 5 | L2 | Secretaría general técnica | T-legal |
| 5 | L3 | Dirección general de ministerio, delegación del Gobierno temática, director/a general, Oficina Española de Cambio Climático | T-legal |
| 5 | L4 | Interventor/a general, Abogado/a General del Estado, inspector/a general (civiles) | T-legal |
| 5 | L5 | Resto de direcciones, presidencias o gerencias de organismos públicos | T-legal |
| 6 | X | Nada casa → **el script se detiene**; se amplían las listas | — |

**Sillas de consejo** (`clase_silla`):

| Orden | Código | Condición | Clase |
|---|---|---|---|
| 1 | R1 | Órgano de un regulador (Comisión Rectora del FROB) | T-regulador |
| 2 | F7 | Secretario/a o vicesecretario/a no consejero | FUERA |
| 3 | E3 | Participada con ≤50 % público y prueba de que la silla es del accionista público (`propuesto por SEPI`, persona jurídica SEPI, cargo en SEPI/ENAIRE; se propaga a filas duplicadas de la misma persona) | T-empresa |
| 3 | F6 | Participada con ≤50 % público: dominical de un accionista privado identificado, independiente, ejecutivo u «otro externo» sin propuesta pública | FUERA |
| 3 | X2 | Participada con ≤50 % público: dominical o tipo no publicado sin accionista identificado | **REVISAR** (Jorge) |
| 4 | E1 | Primer ejecutivo (también si no es consejero) | T-empresa |
| 4 | E2 | Dirección ejecutiva no consejera (director de autoridad portuaria) | T-empresa |
| 4 | E7 | Consejo de RTVE elegido por las Cortes | T-empresa |
| 4 | E4/E5/E6/E8 | Dominical / independiente / ejecutivo / tipo no publicado | T-empresa |

El % público se toma por empresa: es el primer valor legible entre sus filas. Si no consta («n.d.»), se trata como
empresa controlada, porque todas las que están en ese caso son SME, EPE o entidades públicas.

### 1.3 Resultado en S0 (`clase_posicion.csv`)

| Origen | T-legal | T-empresa | T-regulador | P | FUERA | REVISAR | Total |
|---|---|---|---|---|---|---|---|
| Estructura (unidades) | 197 | 7 | 18 | 105 | 24 | 0 | 351 |
| Otros altos cargos | 24 | 11 | 49 | 35 | 252 | 0 | 371 |
| Consejos (sillas) | 0 | 778 | 14 | 0 | 162 | 27 | 981 |
| **Total** | **221** | **796** | **81** | **140** | **438** | **27** | **1.703** |

Son filas, no personas ni posiciones únicas: estructura y otros se solapan, hay vacantes y hay filas repetidas entre
bloques de consejos. La deduplicación se hace en F1. Las 27 REVISAR son: Airbus (10), Hispasat (9), Epicom (3), Startical (2),
IAG (2) y Enagás (1).

### 1.4 Casos límite ya decididos en v0 (Jorge puede revertirlos)

| Caso | Decisión v0 | Por qué |
|---|---|---|
| Presidente y ministros | FUERA (F0) | Son el principal que nombra, no puestos delegados; además, «miembro de un gobierno» es nivel 4 por definición |
| Museos, Cervantes, SEPE, IMSERSO, Casas (África, Árabe, Mediterráneo), INJUVE… | T-legal (L5) | Dirección de organismo con rango DG; si hay requisito de cualificación, lo pone su estatuto (`requisito_A1 = estatuto`). Robustez: L5 aparte |
| INE, CIS, AEMET, CSIC, ISCIII, AEI, OEPM, AEAT | T-regulador (R2/R3) | Función técnica o científica por diseño. La clase se fija por función, no por quién la ocupa |
| Comisionado para el Mercado de Tabacos | T-regulador (R1), no P3 | Es un organismo autónomo regulador, aunque se llame «comisionado» |
| Delegaciones temáticas (Violencia de Género, Plan Nacional sobre Drogas, Autopistas) | T-legal (L3) | Son órganos directivos de ministerio; la exclusión de §12.6 se refiere a los delegados territoriales |
| Delegado especial del Estado en la Zona Franca | T-empresa (E1) | Dirige un consorcio con actividad empresarial |
| Departamento de Seguridad Nacional y Departamento de Seguridad (Presidencia) | P (P4) | Pertenecen al Gabinete de la Presidencia |
| Secretario general del CNI, secretaria general del Cervantes | T-legal (L5) | Gerencia de un organismo, no SG del art. 64 |
| Autoridades portuarias y Puertos del Estado | T-empresa | Organismos que actúan en régimen de derecho privado y se financian con su actividad |
| RTVE | T-empresa (E7) | Empresa pública; `tipo_silla = elegido_cortes` para cortes de D4 |
| Participadas minoritarias (Telefónica, Indra, Redeia, Enagás…) | Solo las sillas del accionista público (E3) | El resto no lo nombra el sector público |

### 1.5 Variables de la posición

| Variable | Valores | Regla |
|---|---|---|
| `tipo_silla` | primer_ejecutivo, presidente_no_ejecutivo, dominical_funcionario_ministerio, dominical_otro_publico, independiente, ejecutivo, elegido_cortes, otro_externo, representante_privado_o_social, no_publicado, no_aplica | Del fichero de consejos. `dominical_funcionario_ministerio` si `otro_cargo_publico` es un puesto en un ministerio |
| `requisito_A1` | ley / estatuto / no / no_consta | ley: L1, L2 y L3 de ministerio. estatuto: L5 y R, si su norma lo dice. no: P y T-empresa |
| `excepcion_rd` | sí / no / null | Solo DG: el RD de estructura exime del requisito (art. 66.2). Se lee en el BOE |
| `intensidad_tecnica` | 0–3 | 0 coordinación política o comunicación · 1 gestión general (servicios comunes) · 2 gestión sectorial o dirección de empresa · 3 función técnico-científica o de supervisión |

---

## 2. Sectores

### 2.1 Taxonomía (detalle, ejemplos, cuerpos y campos ISCED-F en `sectores.csv`)

| Código | Sector | Código | Sector |
|---|---|---|---|
| S01 | Hacienda pública y presupuestos | S13 | Educación, universidades y deporte |
| S02 | Finanzas, crédito y seguros | S14 | Ciencia, investigación e innovación |
| S03 | Comercio exterior, promoción internacional y turismo | S15 | Cultura, patrimonio y medios públicos |
| S04 | Industria, PYME y participaciones empresariales | S16 | Vivienda, urbanismo y territorio |
| S05 | Energía | S17 | Justicia, derechos y asuntos jurídicos |
| S06 | Transporte e infraestructuras | S18 | Interior, seguridad y protección civil |
| S07 | Telecomunicaciones, digitalización y servicios postales | S19 | Defensa |
| S08 | Medio ambiente, agua y clima | S20 | Exteriores, UE y cooperación |
| S09 | Agricultura, pesca y alimentación | S21 | Administración general y función pública |
| S10 | Sanidad y salud pública | S22 | Estadística, estudios y prospectiva |
| S11 | Trabajo, empleo y Seguridad Social | S23 | Competencia, consumo, juego y regulación de mercados |
| S12 | Inclusión, servicios sociales, igualdad y migraciones | S24 | Comunicación y coordinación política e institucional |

### 2.2 Sector del puesto

1. **Un sector principal** por posición: el de la actividad principal de la entidad, o el de las competencias de la unidad.
   El nombre del ministerio solo sirve para desempatar.
2. Puestos transversales: Subsecretaría → S21; SGT → S17; gabinetes y oficinas de Presidencia → S24; intervención →
   S01; Abogacía → S17. En todos ellos, el **sector secundario** es el del ministerio.
3. Consejeros: el sector es el de la **empresa**, no el del ministerio del dominical. Holdings: SEPI → S04 (secundario: el
   de la filial, si la silla es de una filial); DG del Patrimonio → S01.
4. NC solo si no hay forma de decidir; va a la cola humana.

### 2.3 Sector de una experiencia (trayectoria)

Cada experiencia lleva hasta **2 sectores**: el de la organización y, si es distinto, el de la función. Por ejemplo, una
abogada interna de una eléctrica lleva S05 y S17. La experiencia cuenta para el componente (a) si cualquiera de los dos
coincide con el principal o el secundario del puesto.

---

## 3. Afiliación documentada (persona)

Es una **cota inferior**: «no detectada» ≠ «no tiene». El puesto que se codifica nunca es evidencia, y tampoco lo es una
silla que se ocupa de oficio por ese puesto.

### 3.1 Niveles

| Nivel | Cuenta (ejemplos positivos) | No cuenta en este nivel (ejemplos negativos → nivel correcto) |
|---|---|---|
| **4** | Diputado/a en el Congreso; senador/a (también el designado por un parlamento autonómico); eurodiputado/a; diputado/a autonómico/a; ministro/a; presidente/a o consejero/a autonómico/a; alcalde/sa; presidente/a de diputación, cabildo o consell insular | Secretario de Estado o viceconsejero (no son miembros del Gobierno → 1); diputado provincial (→ 3); candidato a alcalde no elegido (→ 2); teniente de alcalde (→ 3) |
| **3** | Concejal/a de cualquier municipio; diputado/a provincial; consejero/a insular o comarcal; juntero/a foral; miembro de una comisión ejecutiva (estatal, autonómica, provincial o local); secretario/a general de agrupación; miembro del comité federal, junta directiva nacional o consejo ciudadano; gerente o tesorero/a del partido; secretario/a general de las juventudes | Militante de base (→ 2 si lo declara él mismo); apoderado o interventor electoral (→ 1); empleado técnico del partido, de prensa o asesor (→ 1); delegado en un congreso (→ 1); cargo en un sindicato (→ 0: va a trayectoria) |
| **2** | Candidato/a en una lista proclamada (BOE o boletín provincial) que no salió elegido, incluidos los suplentes; militancia autodeclarada en una fuente pública («soy militante de…» en una entrevista, en su CV o en su perfil verificado) | Aparecer en un acto del partido, firmar un manifiesto, que la prensa le cite como posible candidato sin lista publicada (→ 0) |
| **1** | Gabinete de un cargo político; asesor/a de grupo parlamentario o personal eventual (**se registra, no cuenta**); patrono/a o directivo/a de una fundación de partido; alto cargo de libre designación en un gobierno anterior (SE, SG, DG o viceconsejero autonómico); apoderado, interventor o delegado de congreso | Think tank no vinculado a un partido (→ 0); funcionario en un puesto de RPT dentro de un gabinete, no eventual (→ 0) |
| **0** | Sin evidencia tras el protocolo completo (`buscada_sin_hallazgo`), o independiente declarado sin otros hechos (`declarado_independiente`) | — |

- **Indicador principal: nivel ≥3.** Robustez: ≥2 y ≥4. El nivel 1 **no entra en ningún indicador**: solo se registra.
- **Independiente en un gobierno** (ministro o consejero que entró como independiente): es nivel 4, como dice ARQUITECTURA
  §5, con `independiente_en_gobierno = true`. Hay una robustez que excluye estos casos.

### 3.2 Nivel de la persona

`nivel` = máximo de los hechos que cumplen las tres condiciones: (i) cruce de identidad exacto o probable (3.5), (ii) el
mínimo de fuentes de 3.3 y (iii) que no sean posteriores a la fecha de corte.

### 3.3 Fuentes

| Tipo | Valen | Mínimo por nivel |
|---|---|---|
| **A oficial** | BOE y boletines oficiales (nombramientos, candidaturas proclamadas); webs del Congreso, del Senado, del Parlamento Europeo y de los parlamentos autonómicos; Infoelectoral; registro de concejales; webs de ayuntamientos y diputaciones; organigrama oficial del partido; Transparencia (CV, declaraciones) | Nivel 3–4: ≥1 A **o** ≥2 B independientes |
| **B secundaria** | Wikidata con referencia; prensa con redacción identificable y cita textual; nota de prensa del partido; perfil verificado de la propia persona; Wikipedia **solo** a través de su referencia (se cita la referencia) | Nivel 2: ≥1 A o B |
| **C no vale sola** | Wikipedia sin referencia, blogs, foros, agregadores, redes de terceros, salidas de IA | Nivel 1: ≥1 B |

**Nunca son indicio:** apellidos o familia, pareja, donaciones, asistencia a actos, «me gusta», artículos de opinión, el
medio donde escribe, firma de manifiestos o afiliación sindical. Cada evidencia guarda url, fecha de consulta y una cita
literal de ≤300 caracteres con el nombre y el cargo o partido.

### 3.4 Partido

Se guarda `partido_literal` tal como lo dice la fuente y la `familia`:

| Familia | Incluye |
|---|---|
| PSOE | PSOE y federaciones (PSC, PSdeG, PSE-EE…), JSE |
| SUMAR | Movimiento Sumar, IU, PCE, Comuns/ICV, Más Madrid/Más País, Compromís, CHA y demás integrantes del espacio cuando concurren en él |
| PODEMOS | Podemos y sus confluencias propias (se codifica aparte también antes de 2023) |
| PP | PP, AP, NNGG |
| VOX · CS · ERC · PNV · BNG · CC | La formación correspondiente |
| JUNTS | Junts, CiU, CDC, PDeCAT |
| BILDU | EH Bildu y partidos integrantes |
| OTRO | Resto (UPN, PRC, Teruel Existe, Geroa Bai, UPyD…), con el literal |
| IND_GOBIERNO | Independiente en un gobierno; la familia del gobierno se anota en el literal |

Si hay hechos de varias familias: `familia` = la del hecho de mayor nivel; si empatan, la del más reciente. Se guardan todos.

### 3.5 Identidad (homónimos)

| Calidad | Condición | ¿Cuenta? |
|---|---|---|
| exacto | Nombre y dos apellidos + ≥1 dato de contexto (territorio, fechas, trayectoria compatible, bio o foto enlazada, fuente que cita el cargo actual) | Sí |
| probable | Nombre y dos apellidos, nombre poco frecuente y ninguna contradicción | Sí, pero no basta para una ficha |
| dudoso | Un solo apellido, nombre frecuente o alguna contradicción | No: va a la cola humana |

### 3.6 Tiempo

- Cuentan los hechos anteriores al nombramiento y los simultáneos, hasta la fecha de corte. `solo_hechos_posteriores`
  marca los casos en que todo es posterior, por ejemplo, ir en una lista el 29/11 estando en el puesto.
- No caducan. La robustez «reciente» exige que el último hecho sea de ≤10 años antes del nombramiento.
- `meses_desde_ultimo_cargo_electo` = inicio de la ocupación − fin del último cargo electo (D6). Es negativo si los dos
  se solapan.

### 3.7 Publicación (RGPD art. 9)

1. La ficha individual muestra **solo** los niveles 3–4 con cruce exacto, ≥1 fuente A (o ≥2 B), url y cita.
2. Nunca muestra los niveles 1–2, el nivel 0 como «sin afiliación» ni ningún indicio. El texto fijo para el nivel 0 es
   «sin afiliación documentada en las fuentes consultadas».
3. **Una persona revisa el 100 % de las fichas** con nivel 3–4 antes de publicarlas.
4. Los niveles 2 y 1 solo aparecen en agregados de robustez. Antes de publicar, consulta al DPO y vía de rectificación.

---

## 4. Experiencia relevante (ocupación)

Referencia normativa, L3/2015, art. 2.4: «se prestará especial atención a la naturaleza, complejidad y nivel de
responsabilidad de los puestos desempeñados, que guarden relación con el contenido y funciones del puesto». Todo se
mide **antes** de `fecha_inicio`. El tiempo en el puesto que se codifica y sus renovaciones no cuenta.

### 4.1 (a) Años en el sector

| Regla | Contenido |
|---|---|
| a1 | Cuenta todo periodo en una experiencia con un sector (2.3) igual al principal o al secundario del puesto. Da igual el tipo de organización: pública, privada, académica, internacional o del propio ministerio |
| a2 | Fechas: mes a mes si constan los meses. «2015–2018» = 3 años. El mismo año, o un año suelto = 0,5. «Desde 2019» o «actualidad» = hasta `fecha_inicio`. Sin fechas = 0 y `fechas_incompletas` |
| a3 | Los solapamientos se cuentan una vez (unión de intervalos). Tiempo parcial declarado o profesor asociado = 50 % |
| a4 | Gabinete, personal eventual y asesor parlamentario o de grupo = **0 en el principal**; 100 % en la sensibilidad «gabinete» |
| a5 | Cargos electos legislativos (parlamentario, concejal sin delegación) = 0. Cargos políticos ejecutivos con competencia en el sector (ministro, consejero autonómico del área, concejal delegado del área; un alcalde solo para S16 y S21) y altos cargos de designación del sector (SE, SG, DG) cuentan en el **principal**; en el **estricto**, 0 |
| a6 | El partido = 0 siempre. Sindicatos y organizaciones empresariales: solo para S11, y para el sector de la patronal si es sectorial |
| a7 | Academia: plaza estable o posdoctoral (contratado doctor, titular, catedrático, científico titular o superior) en el campo del sector = 100 %. Predoctorales, becas y prácticas = 0. El doctorado cuenta como credencial (c3), no como años |
| a8 | Propio ministerio o entidad: cuenta como cualquier otra experiencia del sector. Un puesto previo de designación en el mismo ministerio cuenta (salvo a4) |
| a9 | No cuentan: prácticas de menos de 6 meses ni lo anterior al primer título universitario. Periodismo cuenta solo para S15 y S24. «Consultor» sin sector documentado = 0 |

### 4.2 (b) Dirección previa comparable

Exige **≥12 meses acumulados** antes del nombramiento en uno de estos puestos:

| Clase del puesto codificado | Cuenta como dirección comparable |
|---|---|
| T-legal y P | Subdirector general o superior en cualquier administración (incluidos los DG y SG autonómicos); dirección de un organismo o de una empresa pública; alta dirección en una entidad privada de ≥250 empleados; jefatura de unidad de nivel equivalente en un organismo internacional |
| T-empresa, primer ejecutivo | Comité de dirección (CEO, DG, director de área) en una empresa de ≥250 empleados; presidencia o dirección de una empresa pública o de un organismo con actividad empresarial |
| T-empresa, consejero | Silla previa en el consejo de una sociedad con actividad (no instrumental) de ≥50 empleados; alta dirección en una empresa; o, para dominicales, SG o superior en la administración competente sobre el sector de la empresa |
| T-regulador | Dirección en un regulador, supervisor o agencia técnica; subdirector general o superior en un área técnica afín; dirección de departamento o centro de investigación (agencias científicas); alta dirección en una empresa del sector regulado de ≥250 empleados |

- Si no consta el tamaño, se usa el de la organización si es notorio (cotizada, ministerio, gran organismo). Si no, `no_determinable`.
- Cargos políticos ejecutivos (ministro, consejero autonómico, alcalde de un municipio de ≥50.000 habitantes, presidente de
  diputación): cuentan en el **principal**; no cuentan en el **estricto**.

### 4.3 (c) Credencial técnica

| Código | Cuenta |
|---|---|
| c1 | Funcionario de carrera (activo, en excedencia o en servicios especiales) de un cuerpo A1 listado para el sector en `sectores.csv`, de la AGE o equivalente de una CCAA o EELL. También la carrera judicial, fiscal o diplomática (S17 y S20), los oficiales de las FAS (S19) y las escalas científicas y docentes universitarias en el campo |
| c2 | Cuerpo A1 generalista (Administradores Civiles del Estado, administradores A1 autonómicos, habilitación nacional): **solo** para S21, L1 y L2 |
| c3 | Doctorado en un campo ISCED-F del sector |
| c4 | Máster oficial (o equivalente extranjero), ingeniería superior o arquitectura en un campo del sector. Un MBA cuenta para T-empresa y para S02 y S04. No cuentan los títulos propios de menos de 60 ECTS, los cursos ni los programas ejecutivos |
| c5 | Especialidad sanitaria (MIR, FIR, BIR…) para S10 |

Grado o licenciatura solos: no. La lista de cuerpos es orientativa: el nombre exacto se toma del BOE de ingreso.

### 4.4 Variable final y umbrales

`sin_experiencia_uX` = determinable **y** (a) < X años **y** sin (b) **y** sin (c).

| Variante | Regla |
|---|---|
| **u3 (principal)** | (a) < 3,0 |
| u0 | (a) = 0 (ningún periodo en el sector) |
| u5 | (a) < 5,0 |
| estricto | u3 calculado con `anios_sector_estricto` y `direccion_comparable.valor_estricto` |

### 4.5 Determinable

- Con prueba positiva de (a) ≥ umbral, de (b) o de (c), hay experiencia siempre, aunque la trayectoria tenga huecos.
- Afirmar «sin experiencia» exige una cobertura ≥70 %. La cobertura son los meses fechados entre los 23 años, o el primer
  título si es anterior, y `fecha_inicio`. También vale tener ≥10 años continuos documentados justo antes del nombramiento.
- Si no se cumple → `determinable = false`, todas las `sin_experiencia_*` = null y PPSE = null. Se informa de la tasa de nulos por clase.

---

## 5. PPSE y tipología

**PPSE** (perfil político sin experiencia relevante) = afiliación ≥3 **y** `sin_experiencia_u3`. Si falta alguno → null.

| | Experiencia relevante: sí | Sin experiencia relevante | No determinable |
|---|---|---|---|
| **Afiliación ≥3** | híbrido | **político** (= PPSE) | no_determinable |
| **Afiliación ≤2** | técnico | sin_perfil | no_determinable |

Es comparable con la tipología político / experto / híbrido de la literatura sobre secretarios de Estado. La
correspondencia exacta se cierra con la matriz de la tarea de literatura (102).

| Robustez | Cambio respecto al principal |
|---|---|
| afiliacion_2 | Afiliación ≥2 |
| umbral_0 / umbral_5 | u0 / u5 |
| estricto | Experiencia sin cargos políticos ejecutivos ni de designación (a5, 4.2) |
| reciente_10a | Último hecho de afiliación ≤10 años antes del nombramiento |
| sin independientes | Excluye `independiente_en_gobierno` |
| gabinete | a4 al 100 % |
| clases | L5 aparte; sin E3; las 27 REVISAR, primero dentro y luego fuera |

El PPSE principal es **conservador** por partida doble: la afiliación es una cota inferior y la experiencia se cuenta de
forma generosa, porque admite cargos ejecutivos políticos. El estricto da la cota alta.

---

## 6. Esquemas JSON (`fase2/codebook/esquemas/`)

| Esquema | Lo produce | Contenido clave |
|---|---|---|
| `cv_extraccion.schema.json` | Haiku 5.5 en Batch (con un control del 10 % con Sonnet 5.5) | `trayectoria[]` (tipo de organización, nivel, ≤2 sectores, designación política, eventual, tamaño, fechas con precisión, cita), `formacion[]` (nivel, ISCED-F de 4 dígitos), `funcionario[]` (cuerpo literal, subgrupo, BOE), menciones electorales y de partido para la búsqueda |
| `afiliacion_busqueda.schema.json` | Sonnet 5.5 + búsqueda web | `hechos[]` con nivel, familia, cruce de identidad y `evidencias[]` (url, fecha, tipo A/B/C, cita ≤300); homónimos descartados; `nivel_max`, `nivel_max_publicable`, `estado_busqueda` |
| `codificacion_ocupacion.schema.json` | Sonnet 5.5 (primario), Opus 5.5 (doble y adjudicador), humano | Posición (clase, regla, sectores, silla, A1), afiliación, experiencia (a, b, c y sus variantes), PPSE y robustez, perfil, confianza, justificación con ids, cola humana |

Todos llevan `additionalProperties: false`, campos obligatorios y enums cerrados. Los límites de longitud y de rango van en
`description` y se comprueban al cargar en DuckDB. Así los esquemas sirven tanto para validadores como para salidas
estructuradas. Comprobación: `uv run -q --with jsonschema python -I fase2/codebook/validar_esquemas.py`.

---

## 7. Validación

### 7.1 Doble codificación (todas las ocupaciones T y P)

1. Sonnet 5.5 (primario) y Opus 5.5 (doble) codifican **a ciegas** el uno del otro, con la misma entrada: la posición, el
   JSON del CV, el JSON de afiliación y este codebook.
2. Hay desacuerdo clave si difiere cualquiera de estos: afiliación ≥3 (sí/no), (b), (c), `sin_experiencia_u3` o PPSE.
   Sobre (a), si uno da <3 años y el otro ≥3.
3. Un desacuerdo clave pasa a Opus 5.5 como **adjudicador**, con las dos salidas y las evidencias. Si su confianza es baja
   o contradice a ambos → cola humana.
4. Se informa del kappa entre Sonnet y Opus por variable y clase.

**Cola humana siempre:** fichas publicables (100 %), homónimos dudosos, nivel 3–4 sostenido solo con fuentes B,
confianza baja, posiciones REVISAR y sector NC.

### 7.2 Validación humana (Jorge o un asistente, 16–17 nov., 4–6 h)

| Paso | Regla |
|---|---|
| Muestra | **120 ocupaciones**, estratificadas en 4 clases (T-legal, T-empresa, T-regulador, P) × 2 (afiliación codificada ≥3 sí/no) = 8 estratos × 15. Si un estrato tiene menos de 15, se completa con el vecino de la misma clase. Semilla fija `20261116`; el script de muestreo se guarda con la muestra |
| Simetría | Al menos 10 casos con una familia distinta de PSOE o SUMAR, si existen en la base |
| Ciego | El humano ve la posición, el CV y el paquete de evidencias, no los códigos del modelo. Codifica en una plantilla CSV con los campos del esquema de codificación |
| Recuperación | En 20 de los 60 casos con afiliación <3, el humano hace además una búsqueda libre de 10 minutos. Así se estima cuántos «no detectada» tienen en realidad nivel ≥3 |
| Métricas | Kappa de Cohen para afiliación ≥3, `sin_experiencia_u3`, PPSE y perfil; kappa ponderada cuadrática para el nivel 0–4; % de acuerdo; IC 95 % por bootstrap (1.000 réplicas) |
| Objetivo | **κ ≥ 0,70** en afiliación ≥3 y en PPSE; ≥0,60 en perfil |
| Si no se llega | Se analizan los desacuerdos, se sube la versión del codebook (v0.x), se recodifica todo y se valida una muestra nueva de 60 |
| Clases | Jorge revisa la tabla de reglas 1.2, las 27 REVISAR y 50 filas al azar de `clase_posicion.csv` antes de la F5 |

---

## 8. Pendiente de decisión de Jorge (antes de fijar v0)

1. Gobierno en FUERA (F0).
2. Organismos sin función técnica (museos, Cervantes, SEPE, Casas…) en T-legal (L5), o una subclase aparte.
3. INE, CIS, AEAT y agencias científicas en T-regulador.
4. Participadas minoritarias: solo las sillas del accionista público; las 27 REVISAR.
5. Militancia autodeclarada en nivel 2, para que no salga en fichas.
6. Independientes en un gobierno, en nivel 4 con marca.
7. Experiencia principal generosa (cargos ejecutivos políticos cuentan), con la estricta como robustez.

## 9. Cambios

| Versión | Fecha | Cambio |
|---|---|---|
| v0 | 2026-11-01 | Primera versión: clases y reglas aplicadas a S0, 24 sectores, niveles 0–4, experiencia (a), (b) y (c), PPSE, tres esquemas JSON y protocolo de validación |
