-- Base relacional de la fase 2 (ARQUITECTURA.md §4). DuckDB.
-- Las tablas de la §4 están todas; las que aún no se cargan (trayectoria, formacion, funcionario,
-- cargo_electo, candidatura, cargo_partido, evidencia, codificacion) quedan vacías hasta las tareas 104-106 y la fase de codificación.
-- Extra: persona_alias (trazabilidad de la resolución de identidades).

CREATE TABLE persona (
  persona_id        INTEGER PRIMARY KEY,
  nombre_completo   VARCHAR NOT NULL,          -- variante más completa vista en las fuentes
  nombre            VARCHAR,                   -- sin separar aún (no hay regla fiable nombre/apellidos)
  apellidos         VARCHAR,
  nombre_norm       VARCHAR NOT NULL,          -- sin tildes, minúsculas, sin partículas ni títulos
  genero            VARCHAR,                   -- NULL hasta codificar
  anio_nacimiento   INTEGER,                   -- solo si es público
  wikidata_id       VARCHAR,
  n_variantes       INTEGER,                   -- nº de grafías distintas del nombre en S0
  regla_resolucion  VARCHAR,                   -- unico | exacto | contenido (automático con marca)
  marca_revision    BOOLEAN DEFAULT FALSE,     -- TRUE si algún cruce se hizo por contenido
  excluir_universo  BOOLEAN DEFAULT FALSE,     -- todas sus ocupaciones están excluidas
  motivo_exclusion  VARCHAR
);

CREATE TABLE entidad (
  entidad_id        INTEGER PRIMARY KEY,
  nombre            VARCHAR NOT NULL,
  tipo              VARCHAR,                   -- ministerio | empresa_organismo (consejos S0)
  forma_juridica    VARCHAR,
  matriz            VARCHAR,
  ministerio_adscripcion VARCHAR,
  pct_publico_txt   VARCHAR,                   -- tal cual en la fuente
  pct_publico       DOUBLE,                    -- NULL si no es un número limpio
  cotizada          BOOLEAN,
  sector            VARCHAR,
  empleados         INTEGER,
  presupuesto       DOUBLE
);

CREATE TABLE posicion (
  posicion_id       INTEGER PRIMARY KEY,
  tipo              VARCHAR,                   -- unidad_age | organismo | silla_consejo | primer_ejecutivo | secretaria_consejo
  cargo             VARCHAR NOT NULL,
  nivel             INTEGER,
  ministerio        VARCHAR,                   -- normalizado al nombre corto de la estructura
  entidad_id        INTEGER REFERENCES entidad(entidad_id),
  categoria_origen  VARCHAR,
  clase             VARCHAR,                   -- T-legal | T-empresa | T-regulador | P (a codificar)
  requisito_a1      BOOLEAN,
  excepcion_rd      BOOLEAN,
  intensidad_tecnica INTEGER,                  -- 0-3 (a codificar)
  sector            VARCHAR,
  tipo_silla        VARCHAR,                   -- dominical | independiente | ejecutivo | otro externo | n.d.
  retribucion       DOUBLE,
  vacante           BOOLEAN DEFAULT FALSE,
  excluir_universo  BOOLEAN DEFAULT FALSE,
  motivo_exclusion  VARCHAR,                   -- embajador | mando_militar | mutua | delegado_gobierno_ccaa
  fuente_tabla      VARCHAR                    -- estructura | otros | consejos
);

CREATE TABLE ocupacion (
  ocupacion_id      INTEGER PRIMARY KEY,
  persona_id        INTEGER NOT NULL REFERENCES persona(persona_id),
  posicion_id       INTEGER NOT NULL REFERENCES posicion(posicion_id),
  inicio            DATE,
  fin               DATE,
  vigente           BOOLEAN,                   -- TRUE solo si la fuente lo marca como actual verificado / S0 AGE; NULL = sin confirmar
  fuente_nombramiento VARCHAR,                 -- BOE-A-... si se conoce
  socio_coalicion   BOOLEAN,                   -- a codificar
  gobierno          VARCHAR,                   -- a codificar
  representa_a      VARCHAR,                   -- persona jurídica representada (dominical «representado por»)
  nombre_original   VARCHAR,
  estado_dato       VARCHAR,
  fecha_dato        DATE,
  fuente_url        VARCHAR,
  fuentes           VARCHAR,                   -- tablas S0 que la recogen
  nota              VARCHAR
);

CREATE TABLE evento (
  evento_id         INTEGER PRIMARY KEY,
  fecha             DATE,
  tipo              VARCHAR,                   -- nombramiento | cese | alta_consejo | baja_consejo
  persona_id        INTEGER REFERENCES persona(persona_id),
  posicion_id       INTEGER REFERENCES posicion(posicion_id),
  cargo_texto       VARCHAR,
  departamento      VARCHAR,
  fuente_id         VARCHAR,                   -- BOE-A-...
  fuente_url        VARCHAR,
  titulo            VARCHAR,
  estado            VARCHAR,                   -- reflejado_en_s0 | revisar (heurística)
  excluir_universo  BOOLEAN DEFAULT FALSE
);

CREATE TABLE trayectoria (
  trayectoria_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  organizacion VARCHAR, tipo VARCHAR, cargo VARCHAR, nivel_responsabilidad VARCHAR, sector VARCHAR,
  inicio DATE, fin DATE, designacion_politica BOOLEAN, evidencia_id INTEGER
);
CREATE TABLE formacion (
  formacion_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  nivel VARCHAR, titulo VARCHAR, campo_isced VARCHAR, institucion VARCHAR, evidencia_id INTEGER
);
CREATE TABLE funcionario (
  funcionario_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  cuerpo VARCHAR, subgrupo VARCHAR, anio_ingreso INTEGER, boe VARCHAR, evidencia_id INTEGER
);
CREATE TABLE cargo_electo (
  cargo_electo_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  institucion VARCHAR, partido VARCHAR, legislatura VARCHAR, inicio DATE, fin DATE,
  fuente VARCHAR, calidad_cruce VARCHAR, evidencia_id INTEGER
);
CREATE TABLE candidatura (
  candidatura_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  eleccion VARCHAR, circunscripcion VARCHAR, partido VARCHAR, puesto_lista INTEGER, elegido BOOLEAN, evidencia_id INTEGER
);
CREATE TABLE cargo_partido (
  cargo_partido_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  partido VARCHAR, organo VARCHAR, cargo VARCHAR, inicio DATE, fin DATE, nivel INTEGER, evidencia_id INTEGER
);
CREATE TABLE evidencia (
  evidencia_id INTEGER PRIMARY KEY, url VARCHAR, fecha_consulta DATE, tipo_fuente VARCHAR,
  cita_textual VARCHAR NOT NULL, extractor VARCHAR, confianza DOUBLE, revisor VARCHAR
);
CREATE TABLE codificacion (
  codificacion_id INTEGER PRIMARY KEY, persona_id INTEGER REFERENCES persona(persona_id),
  posicion_id INTEGER REFERENCES posicion(posicion_id), version_codebook VARCHAR,
  variables JSON, modelo_codificador VARCHAR, acuerdo DOUBLE, validacion_humana VARCHAR
);

CREATE TABLE persona_alias (
  persona_id INTEGER REFERENCES persona(persona_id),
  nombre_original VARCHAR, nombre_norm VARCHAR, fuente_tabla VARCHAR, regla VARCHAR
);
