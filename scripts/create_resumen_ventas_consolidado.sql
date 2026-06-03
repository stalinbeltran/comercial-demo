-- ============================================================
-- create_resumen_ventas_consolidado.sql
-- Tabla agregada para reporte 1.1 — Resumen de ventas consolidado
-- DB destino: comercialaggregated
-- Grain: un registro por (periodo, sucursal)
-- sucursal_id = 0 → total de todas las sucursales
-- Sin claves foráneas — DB separada
-- ============================================================

CREATE TABLE resumen_ventas_consolidado (

    id              BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,

    -- Período
    periodo_inicio  DATE              NOT NULL,
    periodo_fin     DATE              NOT NULL,

    -- Sucursal (0 = todas)
    sucursal_id     INT UNSIGNED      NOT NULL DEFAULT 0,
    sucursal_nombre VARCHAR(150)               DEFAULT NULL,
    pais_nombre     VARCHAR(100)               DEFAULT NULL,

    -- Métricas
    total_ventas    DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    total_pedidos   INT UNSIGNED      NOT NULL DEFAULT 0,
    clientes_activos INT UNSIGNED     NOT NULL DEFAULT 0,

    -- Auditoría
    fecha_actualizacion DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rvc  PRIMARY KEY (id),
    CONSTRAINT uq_rvc  UNIQUE (periodo_inicio, periodo_fin, sucursal_id)
);

CREATE INDEX idx_rvc_periodo   ON resumen_ventas_consolidado (periodo_inicio, periodo_fin);
CREATE INDEX idx_rvc_sucursal  ON resumen_ventas_consolidado (sucursal_id);
CREATE INDEX idx_rvc_pais      ON resumen_ventas_consolidado (pais_nombre);
