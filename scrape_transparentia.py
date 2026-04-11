"""
Scraper completo de Transparentia (transparentia.newtral.es)
Descarga todos los cargos públicos y sus salarios via la API interna.

Uso:
    python scrape_transparentia.py

Outputs:
    - transparentia_cargos.csv      (todos los registros)
    - transparentia_resumen.txt     (estadísticas)
"""

import requests
import csv
import time
import sys
import os
from pathlib import Path

BASE_URL = "https://transparentia.newtral.es"
API_KEY = os.environ.get("TRANSPARENTIA_API_KEY", "")
HEADERS = {"X-API-KEY": API_KEY}
OUTPUT_DIR = Path(__file__).parent


def fetch_advanced_search(page: int, inactive: bool = False) -> dict:
    """Fetch one page of advanced search results."""
    params = {
        "page": page,
        "salaryRange[]": [0, -1],
        "salaryType": "annualSalary",
        "inactive": str(inactive).lower(),
    }
    resp = requests.get(
        f"{BASE_URL}/api/advanced-search",
        params=params,
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def parse_record(r: dict) -> dict:
    """Flatten one politician record into a flat dict for CSV."""
    return {
        "id": r.get("id", ""),
        "nombre": r.get("name", ""),
        "slug": r.get("slug", ""),
        "genero": r.get("gender", ""),
        "activo": r.get("active", ""),
        "cargo": r.get("jobTitle", ""),
        "rol": r.get("role", {}).get("name", "") if r.get("role") else "",
        "rol_slug": r.get("role", {}).get("slug", "") if r.get("role") else "",
        "ambito": r.get("spatial", {}).get("name", "") if r.get("spatial") else "",
        "ambito_slug": r.get("spatial", {}).get("slug", "") if r.get("spatial") else "",
        "partido": r.get("affiliation", {}).get("name", "") if r.get("affiliation") else "",
        "partido_slug": r.get("affiliation", {}).get("slug", "") if r.get("affiliation") else "",
        "institucion": r.get("currentMemberOf", {}).get("name", "") if r.get("currentMemberOf") else "",
        "institucion_slug": r.get("currentMemberOf", {}).get("slug", "") if r.get("currentMemberOf") else "",
        "institucion_categoria": r.get("currentMemberOf", {}).get("category", "") if r.get("currentMemberOf") else "",
        "salario_anual": r.get("currentAnnualSalary", ""),
        "salario_mensual": r.get("currentMonthlySalary", ""),
        "imagen_url": r.get("image", {}).get("url", "") if r.get("image") else "",
        "url_ficha": f"{BASE_URL}/ficha/{r.get('slug', '')}",
    }


def scrape_all(include_inactive: bool = True) -> list[dict]:
    """Scrape all politicians, active and optionally inactive."""
    all_records = []

    for inactive in ([False, True] if include_inactive else [False]):
        label = "inactivos" if inactive else "activos"
        print(f"\n--- Descargando cargos {label} ---")

        # First request to get total pages
        data = fetch_advanced_search(page=1, inactive=inactive)
        inner = data.get("data", {})
        total_pages = inner.get("pages", 0)
        results = inner.get("results", [])
        all_records.extend(results)

        print(f"  Páginas totales: {total_pages}")
        print(f"  Página 1/{total_pages} - {len(results)} registros")

        for page in range(2, total_pages + 1):
            try:
                data = fetch_advanced_search(page=page, inactive=inactive)
                results = data.get("data", {}).get("results", [])
                all_records.extend(results)

                if page % 50 == 0 or page == total_pages:
                    print(f"  Página {page}/{total_pages} - total acumulado: {len(all_records)}")

                # Rate limiting: be polite
                time.sleep(0.3)

            except requests.exceptions.RequestException as e:
                print(f"  ERROR página {page}: {e}")
                time.sleep(2)
                # Retry once
                try:
                    data = fetch_advanced_search(page=page, inactive=inactive)
                    results = data.get("data", {}).get("results", [])
                    all_records.extend(results)
                except Exception as e2:
                    print(f"  FALLO DEFINITIVO página {page}: {e2}")

    return all_records


def save_csv(records: list[dict], filename: str):
    """Save parsed records to CSV."""
    if not records:
        print("No hay registros para guardar.")
        return

    parsed = [parse_record(r) for r in records]

    # Deduplicate by id (API returns same person in active + inactive searches)
    seen = set()
    unique = []
    for r in parsed:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique.append(r)
    dupes = len(parsed) - len(unique)
    if dupes:
        print(f"\nEliminados {dupes:,} duplicados por ID")
    parsed = unique

    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=parsed[0].keys())
        writer.writeheader()
        writer.writerows(parsed)

    print(f"\nGuardado: {filepath} ({len(parsed)} registros)")
    return parsed


def print_summary(parsed: list[dict]):
    """Print summary statistics."""
    total = len(parsed)
    activos = sum(1 for r in parsed if r["activo"] == True or r["activo"] == "True")
    con_salario = sum(1 for r in parsed if r["salario_anual"] and float(r["salario_anual"] or 0) > 0)

    # By role
    roles = {}
    for r in parsed:
        rol = r["rol"] or "Sin rol"
        roles[rol] = roles.get(rol, 0) + 1

    # By ámbito
    ambitos = {}
    for r in parsed:
        a = r["ambito"] or "Sin ámbito"
        ambitos[a] = ambitos.get(a, 0) + 1

    # By partido (top 10)
    partidos = {}
    for r in parsed:
        p = r["partido"] or "Sin partido"
        partidos[p] = partidos.get(p, 0) + 1
    top_partidos = sorted(partidos.items(), key=lambda x: -x[1])[:15]

    summary = f"""
{'='*70}
TRANSPARENTIA - RESUMEN DEL SCRAPING
{'='*70}

Total registros:     {total:,}
Activos:             {activos:,}
Con salario > 0:     {con_salario:,}

POR ÁMBITO:
{chr(10).join(f'  {k:25s} {v:>6,}' for k, v in sorted(ambitos.items(), key=lambda x: -x[1]))}

POR ROL:
{chr(10).join(f'  {k:25s} {v:>6,}' for k, v in sorted(roles.items(), key=lambda x: -x[1]))}

TOP PARTIDOS:
{chr(10).join(f'  {k:25s} {v:>6,}' for k, v in top_partidos)}
{'='*70}
"""
    print(summary)

    with open(OUTPUT_DIR / "transparentia_resumen.txt", "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: Set TRANSPARENTIA_API_KEY environment variable")
        sys.exit(1)

    print("=" * 70)
    print("SCRAPER TRANSPARENTIA - transparentia.newtral.es")
    print("=" * 70)

    records = scrape_all(include_inactive=True)
    print(f"\nTotal registros descargados: {len(records):,}")

    parsed = save_csv(records, "transparentia_cargos.csv")
    if parsed:
        print_summary(parsed)
