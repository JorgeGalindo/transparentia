"""
Scraper de fichas individuales de Transparentia.
Extrae historial completo de cargos y desglose salarial de cada político.

Uso:
    python scrape_fichas.py

Output:
    - transparentia_historial.csv  (un registro por cargo/período)
"""

import csv
import re
import time
import json
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE_URL = "https://transparentia.newtral.es"
OUTPUT_DIR = Path(__file__).parent
PROGRESS_FILE = OUTPUT_DIR / ".scrape_progress.json"
MAX_WORKERS = 10
DELAY_PER_REQUEST = 0.1  # seconds between requests per thread


def load_slugs() -> list[dict]:
    """Load unique slugs from the main CSV."""
    seen = {}
    with open(OUTPUT_DIR / "transparentia_cargos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            slug = r["slug"]
            if slug not in seen:
                seen[slug] = {
                    "slug": slug,
                    "nombre": r["nombre"],
                    "id": r["id"],
                }
    return list(seen.values())


def load_progress() -> set:
    """Load already-scraped slugs."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return set(json.load(f))
    return set()


def save_progress(done: set):
    """Save progress to disk."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(done), f)


def fetch_ficha(slug: str) -> str | None:
    """Fetch a profile page HTML."""
    url = f"{BASE_URL}/ficha/{slug}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (research scraper)"})
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as e:
        print(f"  ERROR {slug}: {e}")
        return None


def parse_ficha(html: str, slug: str, nombre: str, pid: str) -> list[dict]:
    """Parse all salary blocks from a profile page."""
    records = []
    parts = re.split(r'<div class="b-data', html)

    for i, part in enumerate(parts[1:], 1):
        block = re.sub(r"\s+", " ", part[:3000])

        inactive = "retribution-inactive" in block[:60]

        # Cargo
        cargo_m = re.search(r"<span>(.*?)</span>", block)
        cargo = cargo_m.group(1).strip() if cargo_m else ""

        # Partido
        partido_m = re.search(r"<div>(.*?)</div>", block)
        partido = partido_m.group(1).strip() if partido_m else ""

        # Período
        times = re.findall(r"<time>(.*?)</time>", block)
        prefix_m = re.search(r"cta-date\">.*?<span>(Hasta|Desde)\s*</span>", block)
        if prefix_m and times:
            periodo = f"{prefix_m.group(1)} {times[0]}"
            periodo_inicio = "" if prefix_m.group(1) == "Hasta" else times[0]
            periodo_fin = times[0] if prefix_m.group(1) == "Hasta" else ""
        elif len(times) >= 2:
            periodo = f"{times[0]} - {times[1]}"
            periodo_inicio = times[0]
            periodo_fin = times[1]
        elif times:
            periodo = times[0]
            periodo_inicio = times[0]
            periodo_fin = times[0]
        else:
            periodo = "Actual"
            periodo_inicio = ""
            periodo_fin = ""

        # Salary table rows: <th>label:</th> <td>value</td>
        rows = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>\s*<td[^>]*>(.*?)</td>", block)

        salario_mensual = ""
        salario_anual = ""
        salario_base = ""
        complementos = {}
        nota = ""

        for label_raw, value_raw in rows:
            label = re.sub(r"<[^>]+>", "", label_raw).strip().rstrip(":")
            value = re.sub(r"<[^>]+>", "", value_raw).strip()

            label_lower = label.lower()
            if "mensual" in label_lower:
                salario_mensual = value
            elif "anual" in label_lower:
                salario_anual = value
            elif "base" in label_lower:
                salario_base = value
            elif label and value:
                complementos[label] = value

        # Also get from tfoot (additional breakdown items)
        tfoot = re.search(r"<tfoot>(.*?)</tfoot>", block, re.DOTALL)
        if tfoot:
            tfoot_rows = re.findall(
                r"<t[hd][^>]*>(.*?)</t[hd]>\s*<td[^>]*>(.*?)</td>",
                tfoot.group(1),
            )
            for label_raw, value_raw in tfoot_rows:
                label = re.sub(r"<[^>]+>", "", label_raw).strip().rstrip(":")
                value = re.sub(r"<[^>]+>", "", value_raw).strip()
                label_lower = label.lower()
                if "base" in label_lower:
                    salario_base = value
                elif label and value:
                    complementos[label] = value

        # Nota explicativa
        nota_m = re.search(r'class="e-message">\s*<p>\s*<p>(.*?)</p>', block, re.DOTALL)
        if nota_m:
            nota = re.sub(r"<[^>]+>", "", nota_m.group(1)).strip()
            nota = re.sub(r"\s+", " ", nota)

        records.append(
            {
                "id": pid,
                "slug": slug,
                "nombre": nombre,
                "bloque": i,
                "activo": not inactive,
                "cargo": cargo,
                "partido": partido,
                "periodo": periodo,
                "periodo_inicio": periodo_inicio,
                "periodo_fin": periodo_fin,
                "salario_mensual": salario_mensual,
                "salario_anual": salario_anual,
                "salario_base": salario_base,
                "complementos": json.dumps(complementos, ensure_ascii=False) if complementos else "",
                "nota": nota,
                "url_ficha": f"{BASE_URL}/ficha/{slug}",
            }
        )

    return records


def process_one(entry: dict) -> list[dict]:
    """Fetch and parse one profile."""
    html = fetch_ficha(entry["slug"])
    if not html:
        return []
    return parse_ficha(html, entry["slug"], entry["nombre"], entry["id"])


def main():
    print("=" * 70)
    print("SCRAPER DE FICHAS - transparentia.newtral.es")
    print("=" * 70)

    entries = load_slugs()
    done = load_progress()
    pending = [e for e in entries if e["slug"] not in done]

    print(f"Total fichas únicas:  {len(entries):,}")
    print(f"Ya descargadas:       {len(done):,}")
    print(f"Pendientes:           {len(pending):,}")
    print(f"Workers:              {MAX_WORKERS}")
    print()

    if not pending:
        print("Nada pendiente.")
        return

    # Open CSV in append mode if resuming, write mode if fresh
    csv_path = OUTPUT_DIR / "transparentia_historial.csv"
    fieldnames = [
        "id", "slug", "nombre", "bloque", "activo", "cargo", "partido",
        "periodo", "periodo_inicio", "periodo_fin",
        "salario_mensual", "salario_anual", "salario_base",
        "complementos", "nota", "url_ficha",
    ]

    is_fresh = len(done) == 0 or not csv_path.exists()
    csv_file = open(csv_path, "a" if not is_fresh else "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if is_fresh:
        writer.writeheader()

    total_records = 0
    errors = 0
    batch_size = 500  # save progress every N

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {}
            for entry in pending:
                future = executor.submit(process_one, entry)
                futures[future] = entry

            completed = 0
            for future in as_completed(futures):
                entry = futures[future]
                completed += 1

                try:
                    records = future.result()
                    if records:
                        for r in records:
                            writer.writerow(r)
                        total_records += len(records)
                    else:
                        errors += 1

                    done.add(entry["slug"])

                    if completed % 200 == 0:
                        csv_file.flush()
                        save_progress(done)
                        pct = completed / len(pending) * 100
                        print(
                            f"  [{completed:>6,}/{len(pending):,}] {pct:5.1f}%  "
                            f"registros={total_records:,}  errores={errors}"
                        )

                except Exception as e:
                    errors += 1
                    print(f"  EXCEPTION {entry['slug']}: {e}")

                time.sleep(DELAY_PER_REQUEST)

    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario. Guardando progreso...")

    finally:
        csv_file.flush()
        csv_file.close()
        save_progress(done)

    print(f"\n{'=' * 70}")
    print(f"COMPLETADO")
    print(f"  Fichas procesadas:  {completed:,}")
    print(f"  Registros totales:  {total_records:,}")
    print(f"  Errores:            {errors}")
    print(f"  Guardado en:        {csv_path}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
