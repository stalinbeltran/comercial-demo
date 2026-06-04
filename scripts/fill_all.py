"""
scripts/fill_all.py
Ciclo completo: drop tablas, crea tablas, seed y fill de todas las DBs.

Uso:
    python scripts/fill_all.py                          # drop + create + seed + fill (default)
    python scripts/fill_all.py --fill-only              # solo seed + fill (tablas deben existir)
    python scripts/fill_all.py --skip-seed              # drop + create + fill (sin seed)
    python scripts/fill_all.py --fill-only --skip-seed  # solo fill (sin drop/create ni seed)
    python scripts/fill_all.py --desde 2025-01-01 --hasta 2026-12-31
"""

import os
import sys
import argparse
import subprocess
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

PYTHON = sys.executable
ROOT   = os.path.dirname(os.path.dirname(__file__))


def run(step: str, cmd: list[str]):
    print(f"\n{'─' * 50}")
    print(f"PASO: {step}")
    print(f"CMD : {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"\nERROR en '{step}' (codigo {result.returncode}). Abortando.")
        sys.exit(result.returncode)


def main():
    hoy = date.today()
    hace_dos_anos = (hoy.replace(year=hoy.year - 2)).isoformat()

    p = argparse.ArgumentParser(description="Ciclo completo de carga del ERP")
    p.add_argument("--fill-only",  action="store_true",
                   help="Omite drop y create — solo corre seed y fills")
    p.add_argument("--skip-seed",  action="store_true",
                   help="Omite el seed de comercial")
    p.add_argument("--no-reset",   action="store_true",
                   help="Corre seed sin --reset (agrega en lugar de reemplazar)")
    p.add_argument("--desde", default=hace_dos_anos, metavar="YYYY-MM-DD",
                   help=f"Inicio del rango para fills agregados (default: {hace_dos_anos})")
    p.add_argument("--hasta", default=hoy.isoformat(), metavar="YYYY-MM-DD",
                   help=f"Fin del rango para fills agregados (default: {hoy})")
    args = p.parse_args()

    # ── Drop + Create ─────────────────────────────────────────────────────────
    if not args.fill_only:
        run("drop_all",   [PYTHON, "scripts/drop_all.py"])
        run("create_all", [PYTHON, "scripts/create_all.py", "--create-only"])

    # ── Seed ──────────────────────────────────────────────────────────────────
    if not args.skip_seed:
        seed_cmd = [PYTHON, "scripts/seed_db.py"]
        if not args.no_reset:
            seed_cmd.append("--reset")
        run("seed_db (comercial)", seed_cmd)

    # ── Fills desnorm ─────────────────────────────────────────────────────────
    run("fill linea_venta",
        [PYTHON, "reportes/ventas_por_categoria/fill_linea_venta.py", "--full"])

    run("fill ventas_consolidado",
        [PYTHON, "reportes/ventas_consolidado/fill_ventas_consolidado.py", "--full"])

    # ── Fills agg ─────────────────────────────────────────────────────────────
    run("fill resumen_ventas",
        [PYTHON, "reportes/ventas_por_categoria/fill_resumen_ventas.py",
         "--desde", args.desde, "--hasta", args.hasta])

    run("fill resumen_ventas_consolidado",
        [PYTHON, "reportes/ventas_consolidado/fill_resumen_ventas_consolidado.py",
         "--desde", args.desde, "--hasta", args.hasta])

    run("fill resumen_ventas_sucursal_mes",
        [PYTHON, "reportes/ventas_sucursal_comparativo/fill_resumen_ventas_sucursal_mes.py",
         "--desde", args.desde, "--hasta", args.hasta])

    print(f"\n{'─' * 50}")
    print("✓ fill_all completado")


if __name__ == "__main__":
    main()
