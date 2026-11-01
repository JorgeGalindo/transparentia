modelo: sonnet
salida: data/consejos_por_bloque/tarea_completar_barrido_pge.csv
estado: pendiente
prioridad: 2
---
Barrido de cobertura. Lista de entidades ya cubiertas: columna `empresa` de {BASE}/data/empresas_publicas_consejos.csv.
Fuente principal: Presupuestos Generales del Estado — sector público empresarial y fundacional (presupuestos de explotación y capital,
web de la SEPG, sepg.pap.hacienda.gob.es) y, si es accesible, el Inventario de Entes del Sector Público Estatal (IGAE).
Identifica sociedades mercantiles estatales y entidades públicas empresariales con participación MAYORITARIA estatal directa
(o de primer nivel de un grupo) que NO estén cubiertas. Excluye filiales menores de grupos ya cubiertos, fundaciones, consorcios,
organismos autónomos y agencias. Para cada una: SOLO el primer ejecutivo (presidente y/o consejero delegado/director general), con fuente.
Máximo 25 entidades, por relevancia. En `nota` indica además el ministerio de adscripción y la cifra de presupuesto si la tienes.
