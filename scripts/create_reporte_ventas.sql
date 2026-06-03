-- ============================================================
-- create_reporte_ventas.sql
-- Tabla desnormalizada para reporte de ventas por producto / categoría
-- Grain: un registro por (periodo, sucursal, producto)
-- sucursal_id = 0 → agregado de todas las sucursales
-- ============================================================

CREATE TABLE reporte_ventas_producto (
    id                  BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,

    -- Período del reporte
    periodo_inicio      DATE              NOT NULL,
    periodo_fin         DATE              NOT NULL,

    -- Sucursal (0 = todas)
    sucursal_id         INT UNSIGNED      NOT NULL DEFAULT 0,
    sucursal_nombre     VARCHAR(150)               DEFAULT NULL,

    -- Categoría (desnormalizada desde la jerarquía de categoria)
    categoria           VARCHAR(150)               DEFAULT NULL,
    subcategoria        VARCHAR(150)               DEFAULT NULL,

    -- Producto
    producto_id         INT UNSIGNED      NOT NULL,
    sku                 VARCHAR(60)       NOT NULL,
    producto            VARCHAR(200)      NOT NULL,

    -- Métricas
    unidades_vendidas   DECIMAL(14, 4)    NOT NULL DEFAULT 0,
    precio_promedio     DECIMAL(14, 4)    NOT NULL DEFAULT 0,
    total_descuentos    DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    ingresos_netos      DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    num_pedidos         INT UNSIGNED      NOT NULL DEFAULT 0,

    -- Auditoría
    fecha_actualizacion DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rvp PRIMARY KEY (id),
    CONSTRAINT uq_rvp UNIQUE (periodo_inicio, periodo_fin, sucursal_id, producto_id)
);

CREATE INDEX idx_rvp_periodo   ON reporte_ventas_producto (periodo_inicio, periodo_fin);
CREATE INDEX idx_rvp_sucursal  ON reporte_ventas_producto (sucursal_id);
CREATE INDEX idx_rvp_categoria ON reporte_ventas_producto (categoria);
CREATE INDEX idx_rvp_producto  ON reporte_ventas_producto (producto_id);
