# cruces — cargos electos y de gobierno de las personas del universo (tarea 109)

Cruce de `db/export/persona.csv` (universo = personas con `excluir_universo=false`, 1.269) con `fuentes/electos/cargo_electo_oficial.csv`
(Senado, PE, Wikidata) y `fuentes/locales/cargo_electo_local.csv` (Transparentia). Consulta de las fuentes: 2026-11-01.

## Salidas
- `cargo_electo_persona.csv` — un mandato por fila, solo `seguro` y `probable`, ya deduplicados entre fuentes. Columnas pedidas
  (persona_id, nombre, institucion, nivel_institucion, partido, partido_origen, inicio, fin, fuente, url, calidad) + `legislatura`,
  `detalle` (cargo exacto/circunscripción), `nota_fecha`, `n_fuentes_fusionadas`.
- `revision_cruces.csv` — cruces `dudoso` (no entran en la salida), con el motivo. Para revisar a mano.
- `cruzar.py` — script (pandas; `cd fase2 && uv run -q --with pandas python -I cruces/cruzar.py`). Idempotente. 

## Método
1. Normalización: sin tildes/mayúsculas ni partículas (de, del, la, i, y…). Tipos de cruce: `exacto` (misma secuencia de ≥3 palabras, nombre
   + dos apellidos), `exacto_2_palabras`, `permutado` (mismas palabras, otro orden) y `prefijo` (un nombre es prefijo del otro: «Ana Palacio» vs «Ana Palacio Vallelersundi»).
2. Clasificación:
   - **seguro**: nombre exacto en la ficha de Transparentia de esa misma persona, o exacto (≥3 palabras, un solo homónimo en Wikidata) + señal de contexto.
   - **probable**: exacto sin homónimos pero sin contexto verificable; o cruce parcial con señal fuerte (Transparentia, puesto actual de gobierno o ≥2 menciones en el CV).
   - **dudoso**: parciales sin señal fuerte, homónimos múltiples sin señal, cronología imposible. Solo van a `revision_cruces.csv`.
   - Señales de contexto: el CV (`fuentes/cv/texto/`) menciona el tipo de cargo y/o el municipio/circunscripción; Transparentia coincide en institución;
     el puesto actual es de gobierno. **No hay comprobación de coherencia de partido** (el partido del mandato casi nunca está en Wikidata) ni año de nacimiento (`persona.anio_nacimiento` casi vacío).
3. Deduplicación: mandatos de la misma persona e institución con rangos de fechas solapados se funden en una fila (Senado oficial + Wikidata + Transparentia; PE API + Wikidata).
   Para Senado oficial (solo legislatura, sin fechas) se usa un calendario aproximado de legislaturas **solo para detectar solapes**; no se vuelca a la salida.
   Mandatos de Wikidata sin fechas solo se funden con otro igual (mismo id). Alcaldías: si ambas filas traen municipio, deben coincidir.
4. Fechas: año <1900 o >2026 se descarta (p. ej. `0008-08-01`) con `nota_fecha`; inicio>fin descarta el inicio. No se «corrigen» a ojo: no hay forma verificable.
5. `nivel_institucion`: Congreso y Senado = nacional; Parlamento autonómico = autonómico; PE = europeo; Alcaldía = local; Gobierno de España y gobiernos autonómicos = gobierno.
   No hay filas `provincial` (diputaciones/cabildos no están en las fuentes).

## Cifras
universo (no excluidos): 1269
personas con algún cargo (seguro+probable): 96
  con al menos un seguro: 90  solo probable: 6
filas de mandato: 255; filas fusionadas por duplicado entre fuentes: 136
cruces dudosos (revision_cruces.csv): 147 filas, 47 personas
POR NIVEL
```
                   personas
nivel_institucion          
nacional                 48
gobierno                 43
autonómico               28
local                    21
europeo                   6
```
POR NIVEL Y CALIDAD
```
calidad            probable  seguro
nivel_institucion                  
autonómico               11      20
europeo                   2       4
gobierno                 14      39
local                     9      13
nacional                 20      43
```
POR INSTITUCION
```
                           personas
institucion                        
Congreso de los Diputados        40
Parlamento autonómico            28
Gobierno de España               27
Alcaldía                         21
Gobierno autonómico              19
Senado                           15
Parlamento Europeo                6
```
POR PARTIDO (normalizado; una persona cuenta en cada partido con el que aparece)
```
                               personas
partido_n                              
PSOE (incl. PSC, PSdeG, PSE)         52
sin partido / no consta              26
Podemos/Sumar/IU/confluencias        15
PP                                    8
CiU/Junts/PDeCAT                      2
independiente                         2
otros                                 2
Coalición Canaria                     1
Geroa Bai                             1
PNV                                   1
```
partido del mandato (qualifier P39 o equivalente) en 2 filas; resto es partido de la persona sin fechas o de Transparentia

## Límites (leer antes de usar)
- **Cobertura baja y sesgada**: 96 personas de 1.269. Las fuentes no cubren concejales, diputaciones ni consejos; Congreso solo vía Wikidata (incompleto); el partido casi
  siempre es el P102 *de la persona sin fechas* (`partido_origen`), no el del mandato; el Senado oficial no trae partido (se anota el grupo en `partido_origen`).
  «Sin partido / no consta» no significa independiente.
- **Sin DNI**: todo cruce es por nombre. `seguro` descansa en nombre completo + contexto, no en identidad verificada; Transparentia tampoco da DNI.
- Los `probable` sin contexto (88 filas) deberían confirmarse antes de codificar afiliación. Los dudosos con nombre de dos palabras son casi todos prefijos
  de personas conocidas (p. ej. Ana Palacio, Beatriz Corredor): probablemente son la misma persona, pero no se acepta sin señal.
- Contar personas por partido suma más que el total (una persona puede tener varios partidos en Wikidata).
- Fechas de Transparentia solo con granularidad de año.
