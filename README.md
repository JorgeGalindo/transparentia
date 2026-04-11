# Transparentia Scraper

Scraping completo de [Transparentia](https://transparentia.newtral.es), el buscador de sueldos públicos de Newtral. Extrae salarios de todos los cargos públicos de España: gobierno central, autonómicos, parlamentos, ayuntamientos y organismos públicos.

## Datos

### `transparentia_cargos.csv`
Listado completo de cargos públicos con su salario actual. ~23.500 registros únicos (activos e inactivos). Un registro por persona.

| Campo | Descripción |
|---|---|
| `id` | Identificador único en Transparentia |
| `nombre` | Nombre completo |
| `slug` | Identificador URL |
| `genero` | male / female |
| `activo` | Si está actualmente en el cargo |
| `cargo` | Título completo (ej. "Alcalde Del Ayuntamiento De Vigo") |
| `rol` | Categoría: Alcalde, Diputado, Senador, Ministro, Altos cargos, Concejal, Presidente, Asesor, Cargo europeo |
| `ambito` | Local, Autonómico, Nacional, Europeo, Provincial |
| `partido` | Afiliación política |
| `institucion` | Institución donde ejerce |
| `institucion_categoria` | Tipo de institución (Council, etc.) |
| `salario_anual` | Retribución bruta anual (€) |
| `salario_mensual` | Retribución bruta mensual (€) |
| `url_ficha` | Enlace a la ficha en Transparentia |

### `transparentia_historial.csv`
Historial completo de cargos y salarios extraído de las fichas individuales. Múltiples registros por persona (uno por cada cargo/período).

| Campo | Descripción |
|---|---|
| `id` | Identificador único |
| `nombre` | Nombre completo |
| `activo` | Si es el cargo actual o un histórico |
| `cargo` | Título del cargo en ese período |
| `partido` | Partido en ese período |
| `periodo` | Texto del período (ej. "2019 - 2023", "Hasta 2020") |
| `periodo_inicio` | Año de inicio |
| `periodo_fin` | Año de fin |
| `salario_mensual` | Bruto mensual |
| `salario_anual` | Bruto anual |
| `salario_base` | Salario base (cuando se desglosa) |
| `complementos` | JSON con desglose adicional (complementos, dietas, etc.) |
| `nota` | Nota explicativa (fuente, tipo de dedicación, etc.) |

## Scripts

### `scrape_transparentia.py`
Descarga todos los registros vía la API interna de Transparentia (`/api/advanced-search`). Genera `transparentia_cargos.csv`.

```bash
python scrape_transparentia.py
```

### `scrape_fichas.py`
Descarga y parsea las ~23.500 fichas individuales para extraer historial de cargos y desglose salarial. Genera `transparentia_historial.csv`.

- Reanudable: guarda progreso en `.scrape_progress.json`. Si se interrumpe, al relanzar retoma donde iba.
- Multihilo (10 workers por defecto).

```bash
python scrape_fichas.py
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
export TRANSPARENTIA_API_KEY="tu-api-key"
```

La API key se puede obtener inspeccionando las peticiones de red en [transparentia.newtral.es](https://transparentia.newtral.es).

## Cobertura

Según la [metodología de Transparentia](https://www.newtral.es/metodologia-transparentia/):

- **Gobierno central**: ministros, secretarios de estado, altos cargos
- **Congreso y Senado**: todos los parlamentarios
- **Gobiernos y parlamentos autonómicos**: consejeros, diputados autonómicos, altos cargos
- **Ayuntamientos**: alcaldes de más de 8.000 municipios (actualización anual vía ISPA)
- **Instituciones europeas**: eurodiputados y cargos españoles en instituciones UE
- **Organismos públicos**: presidentes y directivos de empresas públicas (SEPI, etc.)

Los salarios son retribuciones brutas oficiales. No incluyen topes salariales de partido.

## Notas

- Los datos provienen de portales de transparencia oficiales, presupuestos y regulaciones económicas de cada administración.
- Algunas instituciones pueden no estar actualizadas (ej. empresas que han cambiado de naturaleza jurídica).
- Los salarios de alcaldes de municipios pequeños pueden ser simbólicos (dedicación parcial).
