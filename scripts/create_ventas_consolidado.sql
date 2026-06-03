-- ============================================================
-- create_ventas_consolidado.sql
-- Tabla desnormalizada para reporte 1.1 — Resumen de ventas consolidado
-- DB destino: comercialdesnormalized
-- Grain: un registro por linea_pedido, con pais aplanado
-- Sin claves foráneas — DB separada
-- ============================================================

CREATE TABLE ventas_consolidado (

    linea_id        INT UNSIGNED      NOT NULL,   -- linea_pedido.id de origen
    pedido_id       INT UNSIGNED      NOT NULL,
    numero_pedido   VARCHAR(30)       NOT NULL,
    fecha_pedido    DATETIME          NOT NULL,
    estado_pedido   VARCHAR(30)       NOT NULL,
    moneda          CHAR(3)           NOT NULL,

    -- Dimensiones
    cliente_id      INT UNSIGNED      NOT NULL,
    sucursal_id     INT UNSIGNED      NOT NULL,
    sucursal_nombre VARCHAR(150)      NOT NULL,
    pais_id         SMALLINT UNSIGNED NOT NULL,
    pais_nombre     VARCHAR(100)      NOT NULL,

    -- Métrica
    subtotal_linea  DECIMAL(14, 4)    NOT NULL,

    -- Auditoría
    fecha_carga     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_vc PRIMARY KEY (linea_id)
);

CREATE INDEX idx_vc_pedido    ON ventas_consolidado (pedido_id);
CREATE INDEX idx_vc_fecha     ON ventas_consolidado (fecha_pedido);
CREATE INDEX idx_vc_sucursal  ON ventas_consolidado (sucursal_id);
CREATE INDEX idx_vc_pais      ON ventas_consolidado (pais_id);
CREATE INDEX idx_vc_estado    ON ventas_consolidado (estado_pedido);
CREATE INDEX idx_vc_cliente   ON ventas_consolidado (cliente_id);
