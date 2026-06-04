-- ============================================================
-- create_resumen_ventas_sucursal_dia.sql
-- Tabla agregada para reporte 1.2 — Ventas por sucursal comparativo
-- DB destino: comercialaggregated
-- Grain: un registro por (fecha, sucursal_id)
-- sucursal_id = 0 → total de todas las sucursales
-- Granularidad DIARIA — el endpoint agrega sobre cualquier rango sumando días
-- Fuente: comercialdesnormalized.ventas_consolidado
-- Sin claves foráneas — DB separada
-- ============================================================

CREATE TABLE resumen_ventas_sucursal_dia (

    id               BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,

    -- Día (granularidad diaria)
    fecha            DATE              NOT NULL,

    -- Sucursal (0 = todas)
    sucursal_id      INT UNSIGNED      NOT NULL DEFAULT 0,
    sucursal_nombre  VARCHAR(150)               DEFAULT NULL,
    pais_nombre      VARCHAR(100)               DEFAULT NULL,

    -- Métricas del día
    total_ventas     DECIMAL(14, 2)    NOT NULL DEFAULT 0,
    total_pedidos    INT UNSIGNED      NOT NULL DEFAULT 0,
    clientes_activos INT UNSIGNED      NOT NULL DEFAULT 0,

    -- Auditoría
    fecha_actualizacion DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rvsd  PRIMARY KEY (id),
    CONSTRAINT uq_rvsd  UNIQUE (fecha, sucursal_id)
);

CREATE INDEX idx_rvsd_fecha     ON resumen_ventas_sucursal_dia (fecha);
CREATE INDEX idx_rvsd_sucursal  ON resumen_ventas_sucursal_dia (sucursal_id);
CREATE INDEX idx_rvsd_pais      ON resumen_ventas_sucursal_dia (pais_nombre);
