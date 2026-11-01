modelo: opus
salida: fase2/CODEBOOK.md
estado: pendiente
prioridad: 1
comun: fase2
agente: claude-p
---
Carpeta asignada: fase2/codebook/ (y el fichero fase2/CODEBOOK.md).
Redacta el CODEBOOK v0 operativo a partir de ARQUITECTURA.md (secciones 1, 5 y 12 mandan). Debe permitir que un modelo
o una persona codifique sin ambigüedad. Contenido:
1. Clases de puesto (T-legal, T-empresa con dominicales dentro, T-regulador, P; fuera: embajadores, delegados del
   Gobierno, mandos militares, mutuas) con reglas de asignación por tipo/cargo. Aplícalas a la foto S0 y guarda
   fase2/codebook/clase_posicion.csv (una fila por unidad de data/altos_cargos_estructura.csv, por fila de
   data/otros_altos_cargos.csv y por silla de data/empresas_publicas_consejos.csv; columnas: origen, id_fila, cargo,
   entidad_o_ministerio, nombre, clase, regla_aplicada). Hazlo con un script reproducible (fase2/codebook/clases.py).
2. Taxonomía de sectores (15–25 sectores de política pública) con definición y ejemplos de puestos y de experiencias.
   Guárdala también en fase2/codebook/sectores.csv.
3. Afiliación documentada, niveles 0–4, con ejemplos positivos y negativos de cada nivel, qué fuentes valen, cómo se
   registra el partido, y la regla de publicación (fichas: solo niveles 3–4, públicos y notorios). Asesores
   parlamentarios y personal eventual: se registran, no cuentan.
4. Experiencia relevante: componentes (a) años en el sector, (b) dirección previa comparable, (c) credencial técnica
   (lista de cuerpos A1 relevantes por sector), umbral principal 3 años y sensibilidad 0/5; reglas para años parciales,
   experiencia académica, experiencia en el propio ministerio, etc.
5. PPSE y tipología de perfil (técnico, político, híbrido, sin perfil).
6. Esquemas JSON (fase2/codebook/esquemas/*.json) para: extracción de CV (trayectoria, formacion, funcionario),
   resultado de la búsqueda de afiliación por persona (con evidencias url+cita), y codificación final por ocupación.
7. Protocolo de validación humana (muestra estratificada de 120, kappa objetivo ≥0,7) y de doble codificación.
Sé concreto y breve: tablas y reglas, no prosa.
