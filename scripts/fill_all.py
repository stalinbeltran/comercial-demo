"""
scripts/fill_all.py
Ejecuta todos los pasos de carga en orden:
  1. seed_db.py          → comercial             (datos transaccionales)
  2. fill_reporte_ventas → comercialdesnormalized (linea_venta, carga completa)
  3. fill_resumen_ventas → comercialaggregated    (resumen_ventas, rango de fechas)

Uso:
    # Rango por defecto: últimos 2 años hasta hoy
    python scripts/fill_all.py

    # Rango explícito
    python scripts/fill_all.py --desde 2025-01-01 --hasta 2026-12-31

    # Sin correr seed (solo fills de desnorm y agg)
    python scripts/fill_all.py --skip-seed

    # Seed sin --reset (agrega sin borrar datos existentes)
    python scripts/fill_all.py --no-reset
"""

import os
import sys
import argparse
import subprocess
from datetime import date, timedelta

sys.stdout.reconfigure(encoding="utf-8")

PYTHON = sys.executable
ROOT   = os.path.dirname(os.path.dirname(__file__))


def run(step: str, cmd: list[str]):
    print(f"\n{'─' * 50}")
    print(f"PASO: {step}")
    print(f"CMD : {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"\nERROR en '{step}' (código {result.returncode}). Abortando.")
        sys.exit(result.returncode)


def main():
    hoy = date.today()
    hace_dos_anos = (hoy.replace(year=hoy.year - 2)).isoformat()

    p = argparse.ArgumentParser(description="Ejecuta todos los pasos de carga")
    p.add_argument("--desde",     default=hace_dos_anos, metavar="YYYY-MM-DD",
                   help=f"Inicio del rango para resumen_ventas (default: {hace_dos_anos})")
    p.add_argument("--hasta",     default=hoy.isoformat(), metavar="YYYY-MM-DD",
                   help=f"Fin del rango para resumen_ventas (default: {hoy})")
    p.add_argument("--skip-seed", action="store_true",
                   help="Omite el paso de seed_db (útil si comercial ya tiene datos)")
    p.add_argument("--no-reset",  action="store_true",
                   help="Corre seed_db sin --reset (agrega en lugar de reemplazar)")
    args = p.parse_args()

    # ── Paso 1: seed ──────────────────────────────────────────────────────────
    if not args.skip_seed:
        seed_cmd = [PYTHON, "scripts/seed_db.py"]
        if not args.no_reset:
            seed_cmd.append("--reset")
        run("seed_db (comercial)", seed_cmd)

    # ── Paso 2: linea_venta ───────────────────────────────────────────────────
    run(
        "fill_reporte_ventas (comercialdesnormalized)",
        [PYTHON, "scripts/fill_reporte_ventas.py", "--full"],
    )

    # ── Paso 3: resumen_ventas ────────────────────────────────────────────────
    run(
        "fill_resumen_ventas (comercialaggregated)",
        [PYTHON, "scripts/fill_resumen_ventas.py",
         "--desde", args.desde, "--hasta", args.hasta],
    )

    print(f"\n{'─' * 50}")
    print("✓ fill_all completado")


if __name__ == "__main__":
    main()
