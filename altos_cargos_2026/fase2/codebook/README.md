# fase2/codebook/

Material del CODEBOOK v0 (`../CODEBOOK.md`). Tarea 101-f0-codebook.

| Fichero | Qué hace |
|---|---|
| `clases.py` | Aplica las reglas de clase de puesto (CODEBOOK §1.2) a la foto S0 y escribe `clase_posicion.csv`. Solo usa la biblioteca estándar. Es determinista e idempotente: reescribe la salida en cada pasada. Se detiene si alguna unidad u otro alto cargo no casa con ninguna regla |
| `clase_posicion.csv` | Una fila por unidad (`data/altos_cargos_estructura.csv`), por otro alto cargo (`data/otros_altos_cargos.csv`) y por silla (`data/empresas_publicas_consejos.csv`). Columnas: origen, id_fila (fila de datos, empezando en 1), cargo, entidad_o_ministerio, nombre, clase, regla_aplicada |
| `sectores.csv` | 24 sectores con definición, ejemplos de puestos y de experiencias, cuerpos A1 relevantes y campos ISCED-F 2013 |
| `esquemas/*.schema.json` | JSON Schema 2020-12: extracción de CV, búsqueda de afiliación y codificación por ocupación |
| `validar_esquemas.py` | Comprueba los esquemas contra el metaesquema y la coherencia de `sectores.csv` con el enum de sectores |

Ejecución, desde `altos_cargos_2026/`:

```
uv run -q --with duckdb --with pandas --with requests python -I fase2/codebook/clases.py
uv run -q --with jsonschema python -I fase2/codebook/validar_esquemas.py
```

**Fuentes:** los tres CSV de S0 (`data/`, 1/11/2026); Ley 40/2015, arts. 63–66, y Ley 3/2015, art. 2, consultados el
1/11/2026 en la API de legislación consolidada del BOE (BOE-A-2015-10566 y BOE-A-2015-3444).

**Límites:**
- Las listas de entidades son cerradas y están escritas a mano para S0. Una entidad nueva que no esté en ellas cae en la
  regla por tipo (L5 o E8), así que hay que revisar los nombramientos nuevos.
- En las participadas no controladas, la silla se clasifica según la nota de origen («propuesto por SEPI»,
  «Accionista: …»). Quedan 27 sillas en REVISAR, sin accionista identificado.
- Las filas no están deduplicadas: estructura y otros se solapan, y hay filas repetidas entre bloques de consejos. Eso se hace en F1.
