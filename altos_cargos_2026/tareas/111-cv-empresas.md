modelo: sonnet
salida: fase2/fuentes/cv_empresas/trayectorias_empresas.csv
estado: pendiente
prioridad: 2
comun: fase2
agente: claude-p
ejecutada: 2026-11-01 22:33
---
Carpeta asignada: fase2/fuentes/cv_empresas/ (brutos a fase2/data/raw/cv_empresas/).
Hueco principal: primeros ejecutivos y consejeros de empresas públicas sin CV (solo 16 de 110 primeros ejecutivos lo
tienen en fase2/fuentes/cv/manifiesto_cv.csv). Universo: personas de data/empresas_publicas_consejos.csv que no tienen
CV en el manifiesto, empezando por primer_ejecutivo = sí y siguiendo por consejeros que no son funcionarios de un
ministerio (los que no tienen otro_cargo_publico).
Fuentes, por orden: bio en la web corporativa o de la SEPI, informe de gobierno corporativo o memoria anual (las
cotizadas publican el perfil de cada consejero), referencia del Consejo de Ministros del nombramiento, BOE, prensa
solvente. Guarda el texto de cada bio en brutos.
Salida: trayectorias_empresas.csv (nombre, empresa, cargo, fuente, url, fecha, texto_bio) para que la extracción en
lote pueda procesarlo igual que los CV, y README.md con cobertura (primeros ejecutivos y consejeros con bio).
