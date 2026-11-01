#!/bin/zsh
# Descarga las fuentes oficiales en ./fuentes (no se versionan). Ejecutar desde altos_cargos_2026/.
set -e
mkdir -p fuentes/org fuentes/cvdl fuentes/agenda
UA="Mozilla/5.0"
B=https://transparencia.gob.es/publicidad-activa/por-materias/organizacion-empleo/estructura
for m in mapa mauc mclt mcnu mdca mdef mecm mefd mhac migd mint mism mitu mjui mpjc msnd mtdf mted mtes mtmd mtrm mvau pg; do
  pdf=$(curl -sL -A "$UA" "$B/estructura-$m" | grep -o '/content/dam/transparencia_home/publicidadactiva/organizacionyempleo/03estructura/[^"]*\.pdf' | head -1)
  curl -sL -A "$UA" -o fuentes/org/$m.pdf "https://transparencia.gob.es$pdf"
done
# Lista de currículos de altos cargos en activo (exportación XLSX del buscador)
P=$(curl -sL -A "$UA" "https://transparencia.gob.es/servicios-buscador/buscar.htm?categoria=curriculos&lang=es&historico=false" | grep -o '/servicios-buscador/buscar/expTab.htm[^"]*' | head -1 | sed 's/&amp;/\&/g')
curl -sL -A "$UA" -o fuentes/cvdl/cv.zip "https://transparencia.gob.es$P" && (cd fuentes/cvdl && unzip -o -q cv.zip)
curl -sL -A "$UA" -o fuentes/agenda/Agenda2026-2027.pdf "https://www.lamoncloa.gob.es/serviciosdeprensa/agendacom/Documents/Agenda2026-2027.pdf"
pdftotext -layout fuentes/agenda/Agenda2026-2027.pdf fuentes/agenda/agenda.txt
echo ok
