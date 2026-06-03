Vas a implementar un nuevo reporte en el ERP Comercial siguiendo el procedimiento estándar del proyecto.

## Entrada

El usuario te dará una de estas dos cosas:
- El **nombre** del reporte (ej. "ventas por cliente", "stock por bodega")
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

### 7. Actualizar scripts `_all`

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

### 9. Crear endpoint FastAPI

Archivo: `api/routes/<nombre>.py`
- Importa `get_conn_agg` de `api.db`
- Importa los modelos desde `api.models`
- Query SQL sobre la tabla `resumen_<nombre>` en `comercialaggregated`
- Filtros: `fecha_desde`, `fecha_hasta`, `sucursal_id`
- `response_model`, `summary`, `description`, `responses` documentados
- Registrar el router en `api/main.py` con su tag

### 10. Agregar a Postman

- Verificar si el workspace **Pruebas Comercial** y la colección **ERP Comercial API** ya existen
- Agregar la nueva request dentro de la carpeta del tag correspondiente
- URL base: `{{base_url}}/reportes/<nombre>`
- Incluir query params documentados

### 11. Actualizar USAGE.md

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
