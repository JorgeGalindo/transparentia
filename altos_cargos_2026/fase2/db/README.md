# fase2/db — base relacional DuckDB (tarea 103)

Implementa ARQUITECTURA.md §4. Contenido: `schema.sql` (13 tablas de la §4 + `persona_alias`), `cargar_s0.py` (carga S0 y resuelve identidades),
`base.duckdb` (salida), `export/persona.csv`, `export/ocupacion.csv`, `revision_identidades.csv` (dudosos), `identidades_automaticas_marcadas.csv` (cruces automáticos por contenido, para auditar).

## Cómo se ejecuta
`uv run -q --with duckdb --with pandas --with requests python -I fase2/db/cargar_s0.py` (reconstruye todo; tarda segundos).
Fuentes: `data/altos_cargos_estructura.csv`, `data/otros_altos_cargos.csv`, `data/empresas_publicas_consejos.csv` (todas, incluidas filas «último dato disponible» y «sin marcar»), `data/seguimiento/boe_cambios.csv` (→ `evento`).

## Cifras (carga actual)
- Filas de entrada S0: 1703 (estructura+otros+consejos), de ellas 12 sin titular (vacante/n.d.) y 2 titulares persona jurídica sin persona física.
- **Personas únicas: 1489** (1269 dentro del universo de análisis). Excluidas por motivo:
  - embajador: 156
  - delegado_gobierno_ccaa: 29
  - mutua: 18
  - mando_militar: 17
- Posiciones: 1680 (11 vacantes). Entidades: 129 (ministerios + empresas/organismos con consejo).
- **Ocupaciones: 1667** (1446 en posiciones dentro del universo). Por tabla(s) de origen:
  - consejos: 977
  - otros: 346
  - estructura: 323
  - estructura;otros: 21
- Personas con >1 ocupación: 158. Personas que aparecen en más de una tabla de S0: 110.
- Eventos BOE: 52 (revisar: 2, reflejado_en_s0: 50). Personas solo presentes en eventos BOE (sin ocupación S0): 17.
- Resolución: unico=1291, exacto=188, contenido=10.
- **Cruces automáticos por contenido (con marca): 10** → `identidades_automaticas_marcadas.csv`.
- **Dudosos para revisión humana: 17** → `revision_identidades.csv` (contenido_2_tokens: 11, grafia_parecida: 3, persona_juridica_sin_representante: 2, contenido_sin_orden: 1). No se fusionan.

## Reglas de identidad
1. Normalización: sin tildes, minúsculas, «Mª/Ma.» → «maría», guiones fuera, apóstrofos separan, se quitan partículas (de, del, la, las, los, y, dels…), títulos (don, doña, Excmo.) y rangos militares iniciales; alias entre paréntesis se descartan (salvo que el paréntesis sea el nombre largo); «X (repr.: P)» y «X, representada por P» → persona = P, entidad representada en `ocupacion.representa_a`.
2. **Cruce exacto** de la clave normalizada = mismo `persona_id` (automático).
3. **Contenido**: si la clave de A (≥3 tokens) es subsecuencia ordenada de la de B y B es el único candidato → automático, `persona.marca_revision = TRUE`, regla `contenido`.
4. Resto dudoso (mismos tokens en otro orden, contenido de 2 tokens o sin orden, grafía parecida ratio ≥ 0.9, mismo apellido con nombre abreviado, contenido con varios candidatos) → `revision_identidades.csv`; no se fusiona hasta que Jorge decida.
5. Personas jurídicas sin representante persona física (p. ej. «FROB, representado por su presidente») no crean persona: van a la hoja de revisión.

## Exclusiones (marca, no borrado)
`posicion.excluir_universo` + `motivo_exclusion`: **embajador** (categoría o cargo; incluye representantes permanentes), **mando_militar**, **mutua**, y **delegado_gobierno_ccaa** (decisión 6 de §12: delegados del Gobierno fuera; los delegados *temáticos* NO se excluyen). La persona se marca excluida solo si todas sus ocupaciones lo están. Por eso 7 mandos militares que además ocupan una silla de consejo siguen en el universo (su puesto militar sí está excluido). Los eventos BOE llevan su propia marca.

## Posiciones y ocupaciones
- AGE (estructura + otros): una posición por (ministerio normalizado, cargo normalizado); si dos titulares distintos comparten texto de cargo, se separan por titular. Una persona que sale en estructura y en otros con el mismo cargo tiene una sola ocupación (`fuentes` lista ambas).
- Consejos: una posición por fila (cada silla), enlazada a su `entidad`.
- `ocupacion.vigente`: TRUE para S0 AGE y filas «actual verificado»; NULL para «último dato disponible» y «sin marcar» (no se sabe).

## Límites
- `clase`, `requisito_a1`, `excepcion_rd`, `intensidad_tecnica`, `genero`, `nombre/apellidos`, `socio_coalicion`, `gobierno`, retribución, sector: vacíos a propósito (codebook / tareas posteriores).
- Las posiciones de `otros` de tipo empresa pública no se enlazan aún con la `entidad` de consejos (nombres distintos).
- `evento.estado` es una heurística (cargo parecido en S0), no una verificación: «revisar» = comprobar a mano.
- Una misma persona con grafías muy distintas (apellidos compuestos reordenados, nombre de pila distinto) no se detecta si no entra en las reglas de dudosos.
