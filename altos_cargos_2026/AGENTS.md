# AGENTS.md — reglas para agentes (Codex, claude -p) en altos_cargos_2026/

Contexto obligatorio: lee `ARQUITECTURA.md` (diseño de la fase 2, decisiones de Jorge en la sección 12) y, si existe,
`fase2/CODEBOOK.md`. La foto S0 está en `data/` (altos_cargos_estructura.csv, otros_altos_cargos.csv,
empresas_publicas_consejos.csv). Hoy la investigación es descriptiva y solo hacia delante.

## Reglas
1. **Fuentes vivas y verificables.** Nada de memoria. Cada dato que se guarde lleva url, fecha de consulta y, cuando sea
   un hecho sobre una persona, cita textual corta.
2. **No falsear cabeceras ni user-agent.** Si una web bloquea (403/503), anótalo y usa una alternativa (Wikidata, BOE,
   otra fuente oficial). Ritmo educado: ≥1 s entre peticiones al mismo dominio.
3. **Datos personales.** Solo información manifiestamente pública. Afiliación política: solo hechos públicos y notorios
   (cargo electo, cargo orgánico de partido, candidatura publicada, miembro de un gobierno). Nunca inferir militancia.
4. **Secretos.** Nunca escribir tokens ni claves en ficheros, logs o salidas. Si hace falta la API de Anthropic, leer el
   token del llavero en el propio proceso: `security find-generic-password -s anthropic-api-agentes -w`.
5. **Carpetas.** Cada tarea escribe SOLO en la carpeta que se le asigna dentro de `fase2/`. No toques `data/`, `scripts/`,
   `tareas/` ni otras carpetas de `fase2/`. Datos brutos grandes (PDF, HTML, zips) van a `fase2/data/raw/<fuente>/`, que
   no se versiona.
6. **Python con uv**: `uv run -q --with duckdb --with pandas --with requests python -I script.py`. Scripts idempotentes,
   reanudables y con un README corto en su carpeta (qué hace, fuente, cómo se ejecuta, límites).
7. **No hagas commit ni push.** Claude revisa y commitea.
8. Al terminar, imprime un resumen de ≤10 líneas: qué has producido (rutas), cifras, huecos, bloqueos.
