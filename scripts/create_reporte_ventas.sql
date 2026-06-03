-- ============================================================
-- create_reporte_ventas.sql
-- Tabla desnormalizada de líneas de venta
-- DB destino: comercialdesnormalizada
-- Grain: un registro por linea_pedido (sin agregación)
-- Sin claves foráneas — DB separada del esquema transaccional
-- ============================================================

CREATE TABLE linea_venta (

    -- Identificadores de origen
    linea_id                INT UNSIGNED      NOT NULL,
    pedido_id               INT UNSIGNED      NOT NULL,

    -- Pedido
    numero_pedido           VARCHAR(30)       NOT NULL,
    fecha_pedido            DATETIME          NOT NULL,
    fecha_requerida         DATE                       DEFAULT NULL,
    estado_pedido           VARCHAR(30)       NOT NULL,
    moneda                  CHAR(3)           NOT NULL,

    -- Cliente
    cliente_id              INT UNSIGNED      NOT NULL,
    cliente_nombre          VARCHAR(200)      NOT NULL,
    cliente_tipo            VARCHAR(20)       NOT NULL,
    cliente_identificacion  VARCHAR(50)                DEFAULT NULL,
    grupo_cliente           VARCHAR(100)               DEFAULT NULL,

    -- Sucursal y ciudad
    sucursal_id             INT UNSIGNED      NOT NULL,
    sucursal_nombre         VARCHAR(150)      NOT NULL,
    ciudad_sucursal         VARCHAR(100)               DEFAULT NULL,

    -- Categoría (jerarquía aplanada)
    categoria               VARCHAR(150)               DEFAULT NULL,
    subcategoria            VARCHAR(150)               DEFAULT NULL,

    -- Producto
    producto_id             INT UNSIGNED      NOT NULL,
    sku                     VARCHAR(60)       NOT NULL,
    producto                VARCHAR(200)      NOT NULL,
    unidad_medida           VARCHAR(30)       NOT NULL,
    precio_oficial          DECIMAL(14, 4)             DEFAULT NULL,

    -- Bodega
    bodega_id               INT UNSIGNED      NOT NULL,
    bodega_nombre           VARCHAR(150)      NOT NULL,
    tipo_bodega             VARCHAR(30)                DEFAULT NULL,

    -- Línea (métricas de venta)
    cantidad                DECIMAL(14, 4)    NOT NULL,
    precio_unitario         DECIMAL(14, 4)    NOT NULL,
    descuento_pct           DECIMAL(6, 4)     NOT NULL DEFAULT 0,
    descuento_monto         DECIMAL(14, 4)    NOT NULL DEFAULT 0,
    subtotal                DECIMAL(14, 4)    NOT NULL,
    con_promocion           TINYINT(1)        NOT NULL DEFAULT 0,

    -- Factura
    factura_id              INT UNSIGNED               DEFAULT NULL,
    numero_fiscal           VARCHAR(60)                DEFAULT NULL,
    estado_factura          VARCHAR(20)                DEFAULT NULL,
    fecha_emision           DATETIME                   DEFAULT NULL,
    impuesto_pct            DECIMAL(6, 4)              DEFAULT NULL,

    -- Auditoría de carga
    fecha_carga             DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_lv PRIMARY KEY (linea_id)
);

CREATE INDEX idx_lv_pedido       ON linea_venta (pedido_id);
CREATE INDEX idx_lv_fecha        ON linea_venta (fecha_pedido);
CREATE INDEX idx_lv_cliente      ON linea_venta (cliente_id);
CREATE INDEX idx_lv_producto     ON linea_venta (producto_id);
CREATE INDEX idx_lv_sucursal     ON linea_venta (sucursal_id);
CREATE INDEX idx_lv_categoria    ON linea_venta (categoria);
CREATE INDEX idx_lv_estado       ON linea_venta (estado_pedido);
