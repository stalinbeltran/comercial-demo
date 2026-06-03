-- ============================================================
-- create_resumen_ventas.sql
-- Tabla agregada de ventas por producto / categoría / período
-- DB destino: comercialaggregated
-- Grain: un registro por (periodo_inicio, periodo_fin, sucursal_id, producto_id)
-- sucursal_id = 0 → agregado de todas las sucursales
-- Sin claves foráneas — DB separada del esquema transaccional
-- ============================================================

CREATE TABLE resumen_ventas (

    id                  BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,

    -- Período
    periodo_inicio      DATE              NOT NULL,
    periodo_fin         DATE              NOT NULL,

    -- Sucursal (0 = todas las sucursales agregadas)
    sucursal_id         INT UNSIGNED      NOT NULL DEFAULT 0,
    sucursal_nombre     VARCHAR(150)               DEFAULT NULL,

    -- Categoría (jerarquía aplanada)
    categoria           VARCHAR(150)               DEFAULT NULL,
    subcategoria        VARCHAR(150)               DEFAULT NULL,

    -- Producto
    producto_id         INT UNSIGNED      NOT NULL,
    sku                 VARCHAR(60)       NOT NULL,
    producto            VARCHAR(200)      NOT NULL,

    -- Métricas agregadas
    unidades_vendidas   DECIMAL(14, 4)    NOT NULL DEFAULT 0,
    precio_promedio     DECIMAL(14, 4)    NOT NULL DEFAULT 0,
    total_descuentos    DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    ingresos_netos      DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    num_pedidos         INT UNSIGNED      NOT NULL DEFAULT 0,

    -- Auditoría de carga
    fecha_actualizacion DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rv  PRIMARY KEY (id),
    CONSTRAINT uq_rv  UNIQUE (periodo_inicio, periodo_fin, sucursal_id, producto_id)
);

CREATE INDEX idx_rv_periodo    ON resumen_ventas (periodo_inicio, periodo_fin);
CREATE INDEX idx_rv_sucursal   ON resumen_ventas (sucursal_id);
CREATE INDEX idx_rv_producto   ON resumen_ventas (producto_id);
CREATE INDEX idx_rv_categoria  ON resumen_ventas (categoria);
