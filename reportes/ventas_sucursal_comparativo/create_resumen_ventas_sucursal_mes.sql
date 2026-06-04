-- ============================================================
-- create_resumen_ventas_sucursal_mes.sql
-- Tabla agregada para reporte 1.2 — Ventas por sucursal comparativo
-- DB destino: comercialaggregated
-- Grain: un registro por (mes, sucursal_id)
-- sucursal_id = 0 → total de todas las sucursales
-- Fuente: comercialdesnormalized.ventas_consolidado
-- Sin claves foráneas — DB separada
-- ============================================================

CREATE TABLE resumen_ventas_sucursal_mes (

    id               BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,

    -- Período (primer día del mes)
    mes              DATE              NOT NULL,

    -- Sucursal (0 = todas)
    sucursal_id      INT UNSIGNED      NOT NULL DEFAULT 0,
    sucursal_nombre  VARCHAR(150)               DEFAULT NULL,
    pais_nombre      VARCHAR(100)               DEFAULT NULL,

    -- Métricas del mes
    total_ventas     DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    total_pedidos    INT UNSIGNED      NOT NULL DEFAULT 0,
    clientes_activos INT UNSIGNED      NOT NULL DEFAULT 0,

    -- Auditoría
    fecha_actualizacion DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rvsm  PRIMARY KEY (id),
    CONSTRAINT uq_rvsm  UNIQUE (mes, sucursal_id)
);

CREATE INDEX idx_rvsm_mes      ON resumen_ventas_sucursal_mes (mes);
CREATE INDEX idx_rvsm_sucursal ON resumen_ventas_sucursal_mes (sucursal_id);
CREATE INDEX idx_rvsm_pais     ON resumen_ventas_sucursal_mes (pais_nombre);
