Investigación para EsadeEcPol (base de altos cargos del Estado y consejos de empresas públicas).
Hoy es {HOY}. Usa SOLO fuentes vivas: tu memoria no vale (cambios frecuentes; elecciones generales el 29-11-2026,
Gobierno en funciones desde el 30-11). Herramientas: WebSearch, WebFetch, curl vía Bash.
Si una web bloquea (403/503), NO falsees cabeceras ni user-agent: usa alternativas (web corporativa, cuentas anuales e
informes de gobierno corporativo en transparencia.gob.es, BORME y BOE en boe.es — su buscador es accesible —,
referencias del Consejo de Ministros en lamoncloa.gob.es, prensa). Sé eficiente (≈10-15 búsquedas por entidad).
No inventes: lo que no conste, vacío y explicado en `nota`.

FORMATO DE SALIDA (consejos): CSV UTF-8 escrito con el módulo csv de Python, cabecera exacta:
empresa,forma_juridica,adscripcion_o_matriz,participacion_publica_pct,cargo,nombre,primer_ejecutivo,tipo_consejero,otro_cargo_publico,fuente_url,fecha_dato,nota
- Una fila por persona y entidad (incluye secretario/a no consejero/a).
- `empresa`: usa EXACTAMENTE el nombre de entidad que se te da en la tarea.
- primer_ejecutivo = sí/no. tipo_consejero = ejecutivo/dominical/independiente/otro externo/n.d. (solo si la fuente lo dice).
- otro_cargo_publico: el que la fuente atribuya al consejero.
- fecha_dato en formato AAAA-MM-DD (fecha de la fuente o de consulta).
- nota empieza por [actual verificado] (fuente de 2026 con composición vigente) o [último dato disponible].
Al terminar imprime 5 líneas de resumen: entidades, filas, huecos, dudas de vigencia.
