# Next steps

Estado a 1/11/2026. Las tareas con id son ficheros en `tareas/` y se ejecutan con `scripts/cola.py`, salvo las
marcadas como trabajo manual o de Chrome.

## Calendario que manda

| Fecha | Qué pasa | Qué hacer |
|---|---|---|
| Hasta el 29/11/2026 | Campaña. Siguen los nombramientos de última hora (delegados del Gobierno, embajadores) | Pasar `scripts/actualizar.sh --sin-cola` cada semana |
| Desde el 30/11/2026 | Gobierno en funciones: ceses en cascada solo cuando haya nuevo Gobierno | Pasar el vigía del BOE cada semana |
| Investidura y nuevo Gobierno | Nuevo real decreto de estructura de ministerios y relevo de casi todos los SE, subsecretarios y DG | **Rehacer la estructura**: `descargar_fuentes.sh` cuando el Portal de Transparencia actualice los organigramas, después `build.sh`, y crear una tarea de verificación grande con todos los niveles 2 y 3 |
| Primeros 3 meses del nuevo Gobierno | Relevo de presidentes de empresas públicas y de consejeros dominicales | `generar_tareas.py --corte <fecha de toma de posesión>`, que refresca todos los consejos |

## Prioridad 1: calidad de lo que ya hay

- [ ] **012 · Verificación muestral de noviembre** (Sonnet). Hay que repetirla cada mes: `generar_tareas.py` la crea sola.
- [ ] **001 · Completar CERSA y Epicom** (Sonnet).
- [ ] **013–017 · Refresco de consejos con datos anteriores a junio de 2026** (Sonnet): SELAE, Hunosa, MAYASA, Tragsa,
      Cetarsa, Aena, COFIDES, ICO, Enusa, ENSA, Acuamed, SIEPSE, Correos, Ebro, Enagás, Rodalies, SEITT, EGS…
- [ ] **Revisar `data/seguimiento/boe_sin_encaje.csv`** (manual). Son los nombramientos que el vigía no sabe colocar;
      hoy solo queda el delegado del Gobierno en la Comunitat Valenciana.
- [ ] **003 · Delegado en la Comunitat Valenciana y presidencia de SEITT** (Haiku).
- [ ] **Contraste de las cotizadas con la CNMV** (Chrome; la ficha pública no muestra el consejo). Alternativa: el IAGC
      2025 en PDF de cada cotizada, que puede ser una tarea Sonnet.

## Prioridad 2: cobertura

- [ ] **002 · Barrido con los PGE (SEPG) de sociedades estatales y EPE que falten** (Sonnet). Después, crear tareas de
      consejo completo para las relevantes.
- [ ] **Organismos públicos con consejo rector**: AEAT, CSIC, ICEX ya está, IDAE ya está, CNMC/CNMV son reguladores. Hay
      que decidir si entran en la base de consejos.
- [ ] **Fundaciones del sector público estatal**: la Fundación SEPI, FECYT, Fundación EOI… Decidir si entran.
- [ ] **Autoridades portuarias**: hoy solo están los presidentes. Sus consejos de administración, con representantes
      autonómicos y municipales, serían 28 tareas Haiku o Sonnet.

## Prioridad 3: análisis (para EsadeEcPol)

- [ ] **Puertas giratorias internas**: cuántas sillas de consejo ocupan los altos cargos y funcionarios de cada ministerio,
      con la columna `alto_cargo_AGE_actual` más `otro_cargo_publico` normalizado.
- [ ] **Perfil de los primeros ejecutivos**: trayectoria política o técnica. Comparable con el Dedómetro de Hay Derecho.
- [ ] **Serie temporal**: con el vigía del BOE corriendo, cada actualización deja rastro en
      `data/seguimiento/boe_cambios.csv`. Sirve para medir la duración en el cargo y la rotación antes y después de las
      elecciones.

## Deuda técnica

- El parseo de los organigramas (PDF) pierde algunas unidades; las recupera la lista de CV. Hay que comprobarlo de nuevo
  cuando cambien los PDF tras el nuevo Gobierno.
- `aplicar_boe.py` cruza cargos por solapamiento de palabras. Revisar `boe_sin_encaje.csv` y, si hay errores de encaje,
  añadir sinónimos.
- El panel se republica a mano, como artifact, desde una sesión de Claude: `panel/index.html`.
