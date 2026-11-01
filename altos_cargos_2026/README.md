# Altos cargos del Estado y consejos de empresas públicas (a 1/11/2026)

Base construida el 1 de noviembre de 2026. Complementa el scraping de Transparentia (Newtral) que hay en la raíz
del repo. Ese scraping tiene muy desfasado quién ocupa cada cargo de la AGE (Lucas en Vivienda, Pingarrón en
Universidades, Bar Cendón en Educación…), así que aquí no se usa para fijar titulares.

**Aviso de vigencia.** Las elecciones generales están convocadas para el 29/11/2026. A partir del 30/11 el
Gobierno estará en funciones y habrá ceses y nombramientos: la foto caduca rápido.

## Ficheros (`data/`)

| Fichero | Qué es | Filas |
|---|---|---|
| `altos_cargos_estructura.csv` | Taxonomía de la AGE de director general hacia arriba: una fila por unidad, con su titular | 351 |
| `otros_altos_cargos.csv` | Altos cargos que no son titulares de una unidad de esa estructura | 371 |
| `empresas_publicas_consejos.csv` | Primer ejecutivo y consejo de administración de empresas públicas: una fila por persona y empresa | 974 (105 entidades, 891 personas) |
| `consejos_por_bloque/` | Los CSV originales de cada bloque de investigación | |
| `verificacion/` | Huecos, conflictos y muestra aleatoria contrastados con el BOE | 47 |

### `altos_cargos_estructura.csv`

| Nivel | Contenido | Nº |
|---|---|---|
| 1 | Presidente y ministros | 23 |
| 2 | Secretarías de Estado (más el CNI) | 37 |
| 3 | Secretarías generales y subsecretarías | 53 |
| 4 | Direcciones generales y unidades de rango DG | 231 |
| 5 | Otras (oficinas) | 7 |

El nivel 4 incluye:
- 129 direcciones generales de ministerio.
- 37 direcciones de organismos con rango de director general (AEAT, INSS, TGSS, SEPE, INE, IMSERSO…).
- 22 secretarías generales técnicas.
- 26 departamentos de Presidencia del Gobierno.
- 13 comisionados.
- 3 delegaciones del Gobierno temáticas.

Columnas principales:
- `titular` y `fuente_titular`.
- `fuentes_que_coinciden`.
- `conflicto`: quedan 0; todos se resolvieron en la verificación.
- `en_transparentia_newtral`: solo como referencia.
- `origen_unidad`: `organigrama` o `solo_transparencia_cv`.
- `verificacion`, `fuente_verificacion`, `fecha_nombramiento` y `nota`.

Puestos sin titular:
- Vacantes según el BOE: DG de Promoción de la Memoria Democrática, DG de Régimen Jurídico Autonómico y Local (cese del 15/10/2026) y Comisionado para las Energías Renovables.
- Sin titular propio: la Oficina de la Conferencia de Presidentes.

### `otros_altos_cargos.csv`

Recoge 162 embajadores y representantes permanentes, 51 presidentes o directores de organismos, 25 directores de
gabinete, 24 mandos militares, 20 delegados del Gobierno en CCAA, 18 miembros de reguladores (CNMC, CNMV, CSN, AEPD,
AIPI), 17 directores gerentes de mutuas colaboradoras, 11 primeros ejecutivos de EPE y algunos más.

La fuente es la lista oficial de currículos. Ojo: el BOE recoge 8 delegados del Gobierno nombrados el 20 y el 27 de
octubre de 2026 que pueden no estar aún en esa lista.

### `empresas_publicas_consejos.csv`

| Bloque | Entidades |
|---|---|
| SEPI mayoritarias | Las 14 de sepi.es (Correos, Navantia, Tragsa, Mercasa, Hunosa, Enusa, ENSA, EFE, Sepides, MAYASA, Cetarsa, Hipódromo, SAECA, Cofivacasa), la propia SEPI, Alimentos y Aceites, y IZAR y el Ente RTVE (estas dos en liquidación) |
| SEPI minoritarias + Aena | Ebro, Enagás, Airbus, Enresa, Hispasat, IAG, Indra, Redeia, Telefónica, Epicom, Talgo y Aena. Se marcan los dominicales a propuesta de SEPI o de ENAIRE |
| Transportes | Adif, Adif AV, el grupo Renfe (y Rodalies), ENAIRE, ENAIRE Global Services, CRIDA y Startical (estas dos incompletas), Puertos del Estado y los presidentes de las 28 autoridades portuarias, Ineco, SEITT, SASEMAR y SENASA |
| Financieras/económicas/digitales | ICO, AXIS, CESCE, COFIDES, ENISA, CERSA, SELAE, FNMT-RCM, SEGIPSA, ICEX, Paradores, SEGITTUR, CDTI, Red.es, SETT, INCIBE, Sareb y la Comisión Rectora del FROB |
| Resto | Casa 47, IDAE, Acuamed, ACUAES, SEIASA, Isdefe, SIEPSE, AC/E y Corporación RTVE |
| Huecos | Consorcio de Compensación de Seguros e Hispasat ampliada; Sareb (completo, web leída en Chrome, 1/11/2026) y SELAE (lista oficial de consejeros del 29/01/2025, último dato publicado) |

Columnas principales:
- `cargo`, `primer_ejecutivo` (sí/no) y `tipo_consejero`. `tipo_consejero` solo se rellena cuando la fuente lo dice; si no, va como n.d.
- `otro_cargo_publico`: el que atribuye la fuente.
- `fuente_url`, `fecha_dato` y `nota`, que empieza por [actual verificado] o [último dato disponible].
- `alto_cargo_AGE_actual`: enlace con las dos tablas anteriores. Hay 98 consejeros que hoy son altos cargos de la AGE.
  - El enlace es por nombre exacto normalizado.
  - Las coincidencias parciales (un nombre contenido en el otro) van marcadas `[match parcial]` y hay que revisarlas.

## Fuentes y método

1. **Unidades.** Salen de los organigramas de los 22 ministerios y de Presidencia del Gobierno en el Portal de
   Transparencia (PDF actualizados el 27/10/2026). Los nombres de las unidades se extraen con `pdftotext -bbox-layout`
   y se deduplican.
2. **Titulares.** Se cruzan tres fuentes. Si dan nombres distintos, se marca conflicto. La prioridad es:
   - (a) la lista de currículos de altos cargos en activo de transparencia.gob.es: 696 personas, exportación XLSX del 01/11/2026;
   - (b) los nombres que aparecen en el propio organigrama;
   - (c) la Agenda de la Comunicación 2026-2027 de la Moncloa, cerrada en julio de 2026.
3. **Personas sin unidad.** Si una persona de la lista de currículos con rango de director general o superior no
   encaja en ninguna unidad del organigrama, se crea la unidad (`origen_unidad = solo_transparencia_cv`). Así entran
   las DG de organismos y las que el parseo de los PDF no captó.
4. **Verificación con el BOE (sección II.A) y las referencias del Consejo de Ministros.** Se revisaron los 12 huecos,
   los 5 conflictos y una muestra aleatoria de 30 filas. En la muestra, el titular estaba desfasado en 2 casos de 30
   (6,7%): el Comisionado del Ciclo del Agua y la DG de Financiación Internacional, ya corregidos. Hay que suponer un
   error parecido en el resto de la tabla.
5. **Empresas.** La fuente es la web corporativa de cada empresa y, en su defecto, los PDF de consejo de la SEPI
   (consolidado del 21/10/2026), las cuentas anuales y el IAGC, el BORME, los OIR de la CNMV y la prensa.

**Webs que bloquean el acceso automático.** No se han falseado cabeceras. Algunas se han leído en Chrome.
- CNMV: 403 a curl, y desde Chrome su ficha pública de entidad no muestra el consejo. Las cotizadas no están contrastadas con su registro; se usaron la web corporativa y los OIR.
- Sareb y SELAE: 403.
- CERSA: 503.
- DIR3 (directorio oficial de unidades): petición rechazada.

## Huecos conocidos

**Empresas incompletas:**
- Sareb: completo (6 consejeros), pero sin secretario publicado.
- SELAE: la última lista oficial es del 29/01/2025; puede haber cambios posteriores.
- CERSA: solo presidente y consejero delegado.
- Epicom: solo presidente y dos consejeros.
- SEITT: la presidencia va con el cargo de secretario general de Transporte Terrestre. El BORME aún no recoge el relevo de Báguena por Sara Hernández del Olmo (BOE-A-2026-18440).
- Hispasat: falta el secretario.
- Airbus e IAG: no consta qué consejeros propone cada accionista.

**Barrido de cobertura sin hacer.** No se ha comprobado si hay sociedades mercantiles estatales o EPE relevantes
fuera de esta lista. Habría que contrastarla con el inventario de entes del sector público (IGAE) desde un navegador.

**Porcentaje de capital público.** Está en n.d. en muchas entidades no SEPI.

**Personas sin cargo actualizado:**
- Navantia: 2 vacantes en el consejo.
- Algunos vocales de ICEX e IDAE aparecen con nombres de ministerio antiguos, señal de que pueden estar desfasados.

## Reproducir

```bash
cd altos_cargos_2026
./scripts/descargar_fuentes.sh      # organigramas, lista de currículos y Agenda en ./fuentes (no versionado)
PY=python3 ./scripts/build.sh       # requiere pandas, openpyxl y pdftotext
```

`build.sh` reconstruye las tres tablas de `data/` a partir de las fuentes, de `data/verificacion/` y de
`data/consejos_por_bloque/`.

Los consejos los recogieron agentes de investigación; los encargos están en `scripts/job*.txt` y se lanzan con
`scripts/run_agent.sh`. Usan `claude -p` con el token del llavero, que no se guarda en ningún fichero.
