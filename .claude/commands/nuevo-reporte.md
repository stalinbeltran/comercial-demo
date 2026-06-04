Vas a implementar un nuevo reporte en el ERP Comercial siguiendo el procedimiento estándar del proyecto.

## Antes de empezar — verificar el catálogo

Lee el archivo `api/data/catalogo.json`.

- Si el reporte solicitado ya tiene `"estado": "implementado"`, notifícalo al usuario y muestra el `endpoint` existente. No continues con el procedimiento.
- Si está `"pendiente"`, continúa normalmente.
- Si el reporte no existe en el catálogo, agrégalo al JSON antes de continuar (con `"estado": "pendiente"`).

## Entrada

El usuario te dará una de estas dos cosas:
- El **nombre** del reporte (ej. "ventas por cliente", "stock por bodega") o su número (ej. "1.4")
- Los **campos** que debe mostrar el reporte

Si te da solo el nombre, deduce los campos lógicos a partir del esquema transaccional en `comercial`.
Si hay ambigüedad, pregunta antes de continuar.

---

## Procedimiento

Sigue estos pasos en orden. Completa cada uno antes de pasar al siguiente.

### 1. Definir el reporte

Establece claramente:
- Nombre del reporte (snake_case, ej. `ventas_por_cliente`)
- Campos que devuelve
- Grain (nivel de detalle): ¿una fila por qué?
- Filtros que soportará (fechas, sucursal, etc.)
- Tablas de `comercial` que necesita

### 2. Escribir el query SQL fuente

Query que lee de `comercial` con los JOINs necesarios.
- Sin agregación para la tabla desnormalizada
- Con GROUP BY / SUM / AVG para la tabla agregada

### 3. Crear script SQL — tabla desnormalizada

Archivo: `scripts/create_<nombre>.sql`
- DB destino: `comercialdesnormalized`
- Sin claves foráneas
- Grain: un registro por fila del query fuente
- Columna `fecha_carga DATETIME` de auditoría
- PRIMARY KEY en el ID de origen
- Índices en columnas de filtro y join frecuentes

### 4. Crear script SQL — tabla agregada

Archivo: `scripts/create_resumen_<nombre>.sql`  
- DB destino: `comercialaggregated`
- Sin claves foráneas
- Columnas de período: `periodo_inicio DATE`, `periodo_fin DATE`
- `sucursal_id INT NOT NULL DEFAULT 0` (0 = todas)
- UNIQUE KEY en `(periodo_inicio, periodo_fin, sucursal_id, <id_grain>)`
- Columna `fecha_actualizacion DATETIME` con ON UPDATE CURRENT_TIMESTAMP
- Índices en período, sucursal y dimensiones principales

### 5. Crear script de fill — desnormalizada

Archivo: `scripts/fill_<nombre>.py`
- Lee de `comercial`, escribe en `comercialdesnormalized`
- Soporta `--full` y `--desde`/`--hasta`
- Procesa en batches de 500
- Usa `ON DUPLICATE KEY UPDATE`
- Incluye `sys.stdout.reconfigure(encoding="utf-8")` al inicio

### 6. Crear script de fill — agregada

Archivo: `scripts/fill_resumen_<nombre>.py`
- Lee de `comercialdesnormalized.<tabla>`, escribe en `comercialaggregated`
- Soporta `--desde`/`--hasta`, `--sucursal`, `--todos`
- Usa `ON DUPLICATE KEY UPDATE`
- Incluye `sys.stdout.reconfigure(encoding="utf-8")` al inicio

### 7. Crear script individual `<nombre>_all.py`

Archivo: `scripts/<nombre>_all.py`

Este script gestiona el ciclo completo del reporte de forma aislada, sin tocar
los demás reportes. Permite probar y recargar un único reporte.

```python
"""
scripts/<nombre>_all.py
Gestiona el ciclo completo del reporte <nombre> de forma aislada.

Uso:
    python scripts/<nombre>_all.py                # drop + create + fill (default)
    python scripts/<nombre>_all.py --fill-only    # solo recarga datos (tablas deben existir)
    python scripts/<nombre>_all.py --drop         # solo drop tablas
    python scripts/<nombre>_all.py --create       # solo crear tablas
    python scripts/<nombre>_all.py --desde 2025-01-01 --hasta 2025-12-31
"""

import os, sys, argparse, subprocess
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from utils.db_setup import drop_tables, run_sql_file

load_dotenv()

PYTHON = sys.executable
ROOT   = os.path.dirname(os.path.dirname(__file__))

TABLAS_DESNORM = ["<tabla_desnorm>"]
TABLAS_AGG     = ["<tabla_agg>"]

SQL_DESNORM    = "scripts/create_<nombre>.sql"
SQL_AGG        = "scripts/create_resumen_<nombre>.sql"

FILL_DESNORM   = ["scripts/fill_<nombre>.py", "--full"]
# FILL_AGG se arma en main() para incluir --desde y --hasta


def do_drop():
    db_desnorm = os.getenv("DB_NAME_DESNORM")
    db_agg     = os.getenv("DB_NAME_AGG")
    print(f"\nDrop en {db_desnorm}")
    drop_tables(TABLAS_DESNORM, db_name=db_desnorm)
    print(f"Drop en {db_agg}")
    drop_tables(TABLAS_AGG, db_name=db_agg)


def do_create():
    db_desnorm = os.getenv("DB_NAME_DESNORM")
    db_agg     = os.getenv("DB_NAME_AGG")
    print(f"\nCreate en {db_desnorm}")
    run_sql_file(SQL_DESNORM, db_name=db_desnorm)
    print(f"Create en {db_agg}")
    run_sql_file(SQL_AGG, db_name=db_agg)


def do_fill(desde: str, hasta: str):
    def run(label, cmd):
        print(f"\n── {label}")
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            sys.exit(r.returncode)

    run("fill desnorm", [PYTHON] + FILL_DESNORM)
    run("fill agg",     [PYTHON, "scripts/fill_resumen_<nombre>.py",
                         "--desde", desde, "--hasta", hasta])


def main():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Ciclo completo reporte <nombre>")
    p.add_argument("--fill-only", action="store_true", help="Solo recarga datos (tablas deben existir)")
    p.add_argument("--drop",      action="store_true", help="Solo drop tablas")
    p.add_argument("--create",    action="store_true", help="Solo crear tablas")
    p.add_argument("--desde", default=(hoy.replace(year=hoy.year-2)).isoformat(), metavar="YYYY-MM-DD")
    p.add_argument("--hasta", default=hoy.isoformat(), metavar="YYYY-MM-DD")
    args = p.parse_args()

    if args.drop:
        do_drop()
    elif args.create:
        do_create()
    elif args.fill_only:
        do_fill(args.desde, args.hasta)
    else:
        do_drop()
        do_create()
        do_fill(args.desde, args.hasta)

    print("\n✓ Completado")


if __name__ == "__main__":
    main()
```

Sustituir `<nombre>`, `<tabla_desnorm>` y `<tabla_agg>` con los valores reales del reporte.

### 8. Actualizar scripts `_all`

**`scripts/drop_all.py`** — agregar las nuevas tablas al dict `TABLAS`:
```python
os.getenv("DB_NAME_DESNORM"): ["linea_venta", "<nueva_tabla>"],
os.getenv("DB_NAME_AGG"):     ["resumen_ventas", "resumen_<nombre>"],
```

**`scripts/create_all.py`** — agregar los nuevos scripts SQL a la lista `SCRIPTS`:
```python
("scripts/create_<nombre>.sql",         os.getenv("DB_NAME_DESNORM")),
("scripts/create_resumen_<nombre>.sql",  os.getenv("DB_NAME_AGG")),
```

**`scripts/fill_all.py`** — agregar los nuevos pasos después de los existentes:
```python
run("fill_<nombre> (comercialdesnormalized)",
    [PYTHON, "scripts/fill_<nombre>.py", "--full"])

run("fill_resumen_<nombre> (comercialaggregated)",
    [PYTHON, "scripts/fill_resumen_<nombre>.py",
     "--desde", args.desde, "--hasta", args.hasta])
```

### 8. Crear modelos Pydantic

En `api/models.py` agregar:
- Un modelo `<Nombre>Item` con todos los campos del response y `Field(description=...)`
- Un modelo `Resumen<Nombre>` con los totales
- Un modelo `Respuesta<Nombre>` que agrupa filtros + resumen + datos

### 9. Crear endpoint FastAPI con documentación completa

Archivo: `api/routes/<nombre>.py`
- Importa `get_conn_agg` de `api.db`
- Importa los modelos desde `api.models`
- Query SQL sobre la tabla `resumen_<nombre>` en `comercialaggregated`

El decorador `@router.get` debe incluir:
```python
@router.get(
    "/<ruta>",
    response_model=Respuesta<Nombre>,
    summary="Título corto visible en /docs",
    description=(
        "Descripción completa en Markdown. Explicar:\n\n"
        "- Qué devuelve el endpoint\n"
        "- De qué tabla lee (`comercialaggregated.<tabla>`)\n"
        "- Qué hacer si el resultado viene vacío (indicar el fill script)\n"
        "- Criterio de ordenamiento\n"
    ),
    responses={
        200: {"description": "Descripción del caso exitoso"},
        400: {"description": "Descripción del caso de error"},
    },
)
```

Cada parámetro `Query` debe incluir `description` y `examples`:
```python
fecha_desde: Optional[date] = Query(
    default=None,
    description="Descripción del parámetro y su default.",
    examples={"ejemplo": {"value": "2025-01-01"}},
)
```

Registrar el router en `api/main.py`:
- Agregar `from api.routes import <nombre>` 
- Agregar `app.include_router(<nombre>.router)`
- Agregar entrada en la lista `TAGS` con nombre y descripción del grupo

### 10. Agregar a Postman

- Verificar si el workspace **Pruebas Comercial** y la colección **ERP Comercial API** ya existen
- Agregar la nueva request dentro de la carpeta del tag correspondiente
- URL base: `{{base_url}}/reportes/<nombre>`
- Incluir query params documentados

### 11. Marcar como implementado en el catálogo

En `api/data/catalogo.json`, localizar el reporte por número o nombre y actualizar:
```json
{
  "numero": "X.X",
  "nombre": "...",
  "estado": "implementado",
  "endpoint": "/ruta/del/endpoint"
}
```

Guardar el archivo. La página `/catalogo` reflejará el cambio automáticamente al recargar.

### 12. Actualizar USAGE.md

Agregar sección para:
- Los dos scripts SQL (create)
- Los dos scripts de fill con todos sus modos
- El nuevo endpoint con tabla de parámetros y ejemplos de URL

---

## Convenciones del proyecto

- DB transaccional: `comercial` (var: `DB_NAME`)
- DB desnormalizada: `comercialdesnormalized` (var: `DB_NAME_DESNORM`)
- DB agregada: `comercialaggregated` (var: `DB_NAME_AGG`)
- Conexiones: usar `_BASE` de `utils/` o los pools de `api/db.py`
- Variables de entorno: siempre vía `os.getenv()` con `load_dotenv()`
- Encoding: `sys.stdout.reconfigure(encoding="utf-8")` en todo script CLI
- Sin claves foráneas en las DBs desnormalizada y agregada
- `sucursal_id = 0` como sentinel para "todas las sucursales"
- Siempre usar `ON DUPLICATE KEY UPDATE` en inserts masivos
