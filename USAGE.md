# ERP Comercial — Guía de uso

## Entorno virtual

```powershell
# Crear (solo la primera vez)
python -m venv venv

# Activar
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

> Sin activar el venv, usar siempre `.\venv\Scripts\python` en lugar de `python`.

---

## Configuración (.env)

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=...
DB_NAME=comercial               # DB transaccional
DB_NAME_DESNORM=comercialdesnormalized   # DB con detalle plano
DB_NAME_AGG=comercialaggregated          # DB con datos agregados
```

---

## Scripts SQL — crear tablas

### linea_venta (comercialdesnormalized)
Detalle plano de linea_pedido con todas las dimensiones aplanadas.
```sql
-- Ejecutar en comercialdesnormalized
source scripts/create_reporte_ventas.sql
```

### resumen_ventas (comercialaggregated)
Métricas agregadas por período / sucursal / producto.
```sql
-- Ejecutar en comercialaggregated
source scripts/create_resumen_ventas.sql
```

---

## seed_db.py — poblar DB transaccional (comercial)

Genera datos de prueba con Faker para todas las tablas del ERP.

```powershell
# Insertar datos (primera vez)
python scripts/seed_db.py

# Borrar todo y reinsertar
python scripts/seed_db.py --reset

# Cambiar volumen de registros
python scripts/seed_db.py --counts pedidos=300 clientes=200

# Combinar reset con volumen
python scripts/seed_db.py --reset --counts pedidos=500 clientes=300
```

Parámetros disponibles para `--counts`:

| Clave | Default |
|---|---|
| `sucursales` | 5 |
| `bodegas_por_sucursal` | 2 |
| `clientes` | 100 |
| `conductores` | 10 |
| `camiones` | 8 |
| `rutas` | 6 |
| `recorridos` | 20 |
| `pedidos` | 150 |
| `lineas_max` | 6 |

---

## fill_reporte_ventas.py — poblar linea_venta (comercialdesnormalized)

Lee de `comercial` y escribe en `comercialdesnormalized.linea_venta`.
Un registro por cada `linea_pedido` con todas las dimensiones desnormalizadas.

```powershell
# Carga completa
python scripts/fill_reporte_ventas.py --full

# Incremental por fecha de pedido
python scripts/fill_reporte_ventas.py --desde 2025-01-01
python scripts/fill_reporte_ventas.py --desde 2025-01-01 --hasta 2025-06-30
```

---

## fill_resumen_ventas.py — poblar resumen_ventas (comercialaggregated)

Lee de `comercialdesnormalized.linea_venta` y escribe en `comercialaggregated.resumen_ventas`.
Requiere que `linea_venta` ya esté poblada (`fill_reporte_ventas.py` primero).
Métricas agregadas (SUM, AVG, COUNT) por período / sucursal / producto.

```powershell
# Total de todas las sucursales, mes actual (sucursal_id = 0)
python scripts/fill_resumen_ventas.py

# Rango de fechas explícito
python scripts/fill_resumen_ventas.py --desde 2025-01-01 --hasta 2025-12-31

# Solo una sucursal
python scripts/fill_resumen_ventas.py --sucursal 3

# Todas las sucursales individualmente (una fila por sucursal)
python scripts/fill_resumen_ventas.py --todos

# Combinar modo con fechas
python scripts/fill_resumen_ventas.py --todos --desde 2025-01-01 --hasta 2025-12-31
```

> Todos los scripts usan `ON DUPLICATE KEY UPDATE` — correrlos dos veces sobre
> el mismo período actualiza los valores en lugar de duplicar registros.

---

## API — FastAPI

```powershell
# Levantar servidor (con recarga automática en desarrollo)
uvicorn api.main:app --reload
```

La raíz `http://localhost:8000` redirige automáticamente a `/docs`.

Para detener el servidor: **`Ctrl + C`** en la terminal donde corre uvicorn.

### Documentación interactiva — /docs (Swagger UI)

La interfaz principal para explorar y probar la API.

- En la parte superior aparece la descripción general: diagrama de flujo de carga y tabla de bases de datos.
- Los endpoints se agrupan por tag (ej. **Reportes**). Al agregar nuevos endpoints con el mismo tag aparecen aquí automáticamente.
- Para probar un endpoint:
  1. Click en el endpoint
  2. Click en **Try it out**
  3. Completar los parámetros
  4. Click en **Execute**
  5. Ver el `curl` equivalente, la URL completa y el JSON de respuesta
- Al fondo de cada endpoint hay una sección **Schemas** con la estructura exacta del JSON de respuesta y descripción de cada campo.

### Documentación de solo lectura — /redoc

```
http://localhost:8000/redoc
```

Mejor presentación para compartir con clientes o equipo. No permite ejecutar llamadas.

### Spec OpenAPI — /openapi.json

```
http://localhost:8000/openapi.json
```

El contrato completo de la API en JSON. Útil para importar en Postman u otras herramientas.

### GET /reportes/ventas-por-categoria

Ventas agrupadas por categoría, subcategoría y producto.

| Parámetro | Tipo | Default | Ejemplo |
|---|---|---|---|
| `fecha_desde` | date | 1° del mes actual | `2025-01-01` |
| `fecha_hasta` | date | hoy | `2025-12-31` |
| `sucursal_id` | int | todas | `3` |

```
GET http://localhost:8000/reportes/ventas-por-categoria?fecha_desde=2025-01-01&fecha_hasta=2025-12-31
GET http://localhost:8000/reportes/ventas-por-categoria?sucursal_id=2
```

> Si el resultado viene vacío, verificar que `resumen_ventas` tenga datos para el rango
> solicitado. Correr `fill_resumen_ventas.py --desde ... --hasta ...` si es necesario.

---

## Postman

Workspace: **Pruebas Comercial**
Colección: **ERP Comercial API**
Variable de colección: `base_url = http://localhost:8000`
