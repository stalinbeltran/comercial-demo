# CLAUDE.md — ERP Comercial Multi-sucursal

## Descripción del Proyecto
Sistema ERP para empresa comercial con presencia en múltiples países y sucursales.
Maneja miles de productos, promociones individuales por producto, precios especiales
por cliente, bodegas (locales e independientes), flota de camiones con control de
rutas y recorridos, pedidos, entregas y facturación.

## Stack
- **Motor:** MySQL 8.x
- **Convención de queries:** SQL directo, sin ORM
- **Collation:** utf8mb4_unicode_ci (recomendado)
- **Motor de tablas:** InnoDB (todas)

## Arquitectura de Datos

### Capa 1 — Tablas Primarias (transaccionales, normalizadas)
| Tabla | Descripción |
|---|---|
| `pais` | Países con moneda por defecto |
| `ciudad` | Ciudades vinculadas a país |
| `sucursal` | Locales comerciales por ciudad |
| `bodega` | Bodegas en sucursal o independientes (`sucursal_id` nullable) |
| `grupo_cliente` | Segmentos de clientes para precios especiales |
| `cliente` | Clientes persona o empresa |
| `direccion_entrega` | Direcciones de despacho por cliente |
| `categoria` | Árbol de categorías (autorreferencial via `padre_id`) |
| `producto` | Catálogo con precio oficial y datos logísticos |
| `precio_especial` | Precios por cliente específico O por grupo de cliente |
| `promocion` | Descuentos por producto (%, monto fijo, 2x1, etc.) |
| `stock` | Cantidad actual por bodega+producto (con columna virtual `cantidad_disponible`) |
| `movimiento_stock` | Log de todas las entradas/salidas/ajustes/traslados |
| `conductor` | Conductores de la flota |
| `camion` | Vehículos con capacidad kg y m³ |
| `ruta` | Rutas entre ciudades con distancia y tiempo estimado |
| `recorrido` | Viaje concreto camion+conductor+ruta con estado |
| `parada_recorrido` | Paradas ordenadas dentro de un recorrido (con GPS lat/lon) |
| `pedido` | Cabecera del pedido con totales |
| `linea_pedido` | Detalle de productos por pedido (guarda precio histórico) |
| `entrega` | Entrega asociada al pedido (retiro local, domicilio o camión) |
| `factura` | Factura fiscal vinculada a pedido y entrega |

### Capa 2 — Tablas Secundarias (desnormalizadas, para reportes)
| Tabla | Granularidad | Reportes |
|---|---|---|
| `sec_ventas_detalle` | Línea de pedido | Ventas por país/sucursal/producto/cliente/categoría |
| `sec_facturas_cartera` | Factura | Cobranza, vencimientos, límites de crédito |
| `sec_clientes_resumen` | Cliente × mes | Actividad, retención, churn, segmentación |
| `sec_inventario_snapshot` | Producto × bodega × día | Stock crítico, rotación, cobertura |
| `sec_movimientos_stock` | Movimiento | Trazabilidad, ajustes, traslados |
| `sec_logistica_entregas` | Entrega | Puntualidad, entregas fallidas, costo logístico |
| `sec_rendimiento_flota` | Recorrido | KPIs de camiones y conductores |
| `sec_resumen_sucursal_dia` | Sucursal × día | Dashboard operativo, comparativos |
| `sec_promociones_precios` | Producto × promo × mes | Efectividad promocional, dispersión de precios |

### Capa 3 — Tablas Analíticas (valores precalculados, granularidad diaria)
| Tabla | Granularidad | Descripción |
|---|---|---|
| `sec_promo_precios_diario` | Producto × día | Métricas precalculadas de promociones, ventanas móviles, uplift, comparativas |

## Convenciones de Nomenclatura
```
PKs:          id INT UNSIGNED NOT NULL AUTO_INCREMENT
Tablas sec:   prefijo sec_
Tablas anal:  prefijo sec_ + sufijo _diario / _mensual / _semanal
Índices:      idx_{tabla_corta}_{campo(s)}
FKs:          fk_{tabla}_{tabla_referenciada}
Unique:       uq_{tabla}_{campo(s)}
```

## Decisiones de Diseño Importantes
- `precio_especial` acepta `cliente_id` OR `grupo_cliente_id` (validar en app que al menos uno esté presente)
- `bodega.sucursal_id` es nullable → permite bodegas independientes sin local
- `stock.cantidad_disponible` es columna VIRTUAL GENERATED → siempre consistente, sin lógica extra
- `linea_pedido` guarda `precio_unitario` en el momento de la venta → precio histórico inmutable
- `movimiento_stock.referencia_tipo/id` → trazabilidad polimórfica sin FK rígida
- `entrega.tipo` ENUM con columnas nullable → evita herencia de tablas compleja
- `parada_recorrido` tiene lat/lon → soporte GPS y tracking en tiempo real
- Tablas secundarias NO tienen FK a primarias → desacoplamiento total para rendimiento

## Frecuencia de Carga de Tablas Secundarias
| Frecuencia | Tablas |
|---|---|
| Tiempo real / cada hora | `sec_ventas_detalle`, `sec_facturas_cartera`, `sec_logistica_entregas` |
| Una vez al día (nocturno) | `sec_inventario_snapshot`, `sec_resumen_sucursal_dia`, `sec_rendimiento_flota`, `sec_movimientos_stock`, `sec_promo_precios_diario` |
| Una vez al mes (cierre) | `sec_clientes_resumen`, `sec_promociones_precios` |

## Estructura de Archivos SQL
```
sql/
├── 01_primarias.sql              -- Tablas transaccionales (bloques 1-6)
├── 02_secundarias.sql            -- 9 tablas sec_ de reportes
└── 03_analitica_promo_precios.sql -- sec_promo_precios_diario con métricas precalculadas
```

## Reportes Disponibles
Ver `docs/reportes.md` para el listado completo de 40+ reportes con sus queries base.
Ver `docs/graficos.md` para los tipos de visualización recomendados por reporte.

## Granularidades Disponibles en sec_promo_precios_diario
Todas las consultas temporales se resuelven cambiando el GROUP BY:
```sql
-- Diario
GROUP BY fecha
-- Semanal
GROUP BY anio_semana        -- '2025-W12'
-- Mensual
GROUP BY anio_mes           -- '2025-03'
-- Trimestral
GROUP BY anio_trimestre     -- '2025-Q1'
-- Anual
GROUP BY anio
-- Día de la semana (estacionalidad)
GROUP BY dia_semana
-- Fin de semana vs semana
GROUP BY es_fin_de_semana
```