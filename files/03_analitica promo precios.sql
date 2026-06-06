-- ============================================================
-- 03_analitica_promo_precios.sql
-- Tabla analítica con valores precalculados
-- Granularidad: producto × día (con todas las agrupaciones temporales)
-- Reportes: 1.5,1.6,6.3,6.4 + análisis de tendencias y alertas
-- Carga: una vez al día (proceso nocturno)
-- ============================================================

CREATE TABLE sec_promo_precios_diario (
    id                               INT UNSIGNED        NOT NULL AUTO_INCREMENT,

    -- ─────────────────────────────────────────────
    -- DIMENSIÓN TIEMPO
    -- Todas las granularidades precalculadas → cambiar GROUP BY para cada vista
    -- ─────────────────────────────────────────────
    fecha                            DATE                NOT NULL,
    anio                             SMALLINT UNSIGNED   NOT NULL,
    trimestre                        TINYINT UNSIGNED    NOT NULL,   -- 1-4
    mes                              TINYINT UNSIGNED    NOT NULL,   -- 1-12
    semana_anio                      TINYINT UNSIGNED    NOT NULL,   -- 1-53 (ISO week)
    dia_mes                          TINYINT UNSIGNED    NOT NULL,   -- 1-31
    dia_semana                       TINYINT UNSIGNED    NOT NULL,   -- 1=Dom…7=Sab
    es_fin_de_semana                 TINYINT(1)          NOT NULL DEFAULT 0,
    anio_mes                         CHAR(7)             NOT NULL,   -- '2025-03'
    anio_semana                      CHAR(8)             NOT NULL,   -- '2025-W12'
    anio_trimestre                   CHAR(7)             NOT NULL,   -- '2025-Q1'

    -- ─────────────────────────────────────────────
    -- DIMENSIÓN PRODUCTO
    -- ─────────────────────────────────────────────
    producto_id                      INT UNSIGNED        NOT NULL,
    producto_sku                     VARCHAR(60)         NOT NULL,
    producto_nombre                  VARCHAR(200)        NOT NULL,
    categoria_id                     INT UNSIGNED                    DEFAULT NULL,
    categoria_nombre                 VARCHAR(150)                    DEFAULT NULL,
    categoria_padre_id               INT UNSIGNED                    DEFAULT NULL,
    categoria_padre_nombre           VARCHAR(150)                    DEFAULT NULL,

    -- ─────────────────────────────────────────────
    -- PRECIOS BASE Y SU EVOLUCIÓN
    -- ─────────────────────────────────────────────
    moneda                           CHAR(3)             NOT NULL,
    precio_oficial                   DECIMAL(14,4)       NOT NULL,
    precio_oficial_7d_ant            DECIMAL(14,4)                   DEFAULT NULL,
    precio_oficial_30d_ant           DECIMAL(14,4)                   DEFAULT NULL,
    variacion_precio_oficial_7d_pct  DECIMAL(8,4)                    DEFAULT NULL,
    variacion_precio_oficial_30d_pct DECIMAL(8,4)                    DEFAULT NULL,

    -- ─────────────────────────────────────────────
    -- PROMOCIÓN VIGENTE EN ESTA FECHA
    -- ─────────────────────────────────────────────
    tiene_promocion_activa           TINYINT(1)          NOT NULL DEFAULT 0,
    promocion_id                     INT UNSIGNED                    DEFAULT NULL,
    promocion_nombre                 VARCHAR(150)                    DEFAULT NULL,
    promocion_tipo                   VARCHAR(30)                     DEFAULT NULL,
    promocion_descuento_pct          DECIMAL(6,4)                    DEFAULT NULL,
    promocion_precio_final           DECIMAL(14,4)                   DEFAULT NULL,
    ahorro_absoluto_promo            DECIMAL(14,4)                   DEFAULT NULL,   -- precio_oficial - promo_precio
    promocion_fecha_inicio           DATE                            DEFAULT NULL,
    promocion_fecha_fin              DATE                            DEFAULT NULL,
    dia_de_promo                     SMALLINT UNSIGNED               DEFAULT NULL,   -- nro de día dentro de la promo
    dias_restantes_promo             SMALLINT                        DEFAULT NULL,   -- negativo = ya venció
    pct_vida_promo_transcurrido      DECIMAL(6,2)                    DEFAULT NULL,   -- 0-100%

    -- ─────────────────────────────────────────────
    -- PRECIOS ESPECIALES (agregados del día)
    -- ─────────────────────────────────────────────
    cantidad_precios_especiales      INT UNSIGNED        NOT NULL DEFAULT 0,
    precio_especial_minimo           DECIMAL(14,4)                   DEFAULT NULL,
    precio_especial_maximo           DECIMAL(14,4)                   DEFAULT NULL,
    precio_especial_promedio         DECIMAL(14,4)                   DEFAULT NULL,
    descuento_especial_min_pct       DECIMAL(6,4)                    DEFAULT NULL,
    descuento_especial_max_pct       DECIMAL(6,4)                    DEFAULT NULL,
    descuento_especial_avg_pct       DECIMAL(6,4)                    DEFAULT NULL,
    delta_precio_esp_vs_promo        DECIMAL(14,4)                   DEFAULT NULL,   -- precio_esp_min - promo_precio

    -- ─────────────────────────────────────────────
    -- VENTAS DEL DÍA
    -- ─────────────────────────────────────────────
    pedidos_con_producto             INT UNSIGNED        NOT NULL DEFAULT 0,
    unidades_vendidas                DECIMAL(14,4)       NOT NULL DEFAULT 0,
    monto_vendido                    DECIMAL(14,2)       NOT NULL DEFAULT 0,
    monto_descuentos_otorgados       DECIMAL(14,2)       NOT NULL DEFAULT 0,

    unidades_bajo_promo              DECIMAL(14,4)       NOT NULL DEFAULT 0,
    monto_bajo_promo                 DECIMAL(14,2)       NOT NULL DEFAULT 0,
    pct_unidades_bajo_promo          DECIMAL(6,2)                    DEFAULT NULL,

    unidades_bajo_precio_especial    DECIMAL(14,4)       NOT NULL DEFAULT 0,
    monto_bajo_precio_especial       DECIMAL(14,2)       NOT NULL DEFAULT 0,
    pct_unidades_bajo_precio_esp     DECIMAL(6,2)                    DEFAULT NULL,

    unidades_a_precio_oficial        DECIMAL(14,4)       NOT NULL DEFAULT 0,
    pct_unidades_precio_oficial      DECIMAL(6,2)                    DEFAULT NULL,

    -- ─────────────────────────────────────────────
    -- VENTANAS MÓVILES PRECALCULADAS
    -- Evitan GROUP BY + SUM sobre rangos de fechas en tiempo de consulta
    -- ─────────────────────────────────────────────

    -- Últimos 7 días (incluye fecha actual)
    unidades_7d                      DECIMAL(14,4)                   DEFAULT NULL,
    monto_7d                         DECIMAL(14,2)                   DEFAULT NULL,
    unidades_bajo_promo_7d           DECIMAL(14,4)                   DEFAULT NULL,
    pct_promo_7d                     DECIMAL(6,2)                    DEFAULT NULL,

    -- Últimos 30 días
    unidades_30d                     DECIMAL(14,4)                   DEFAULT NULL,
    monto_30d                        DECIMAL(14,2)                   DEFAULT NULL,
    unidades_bajo_promo_30d          DECIMAL(14,4)                   DEFAULT NULL,
    pct_promo_30d                    DECIMAL(6,2)                    DEFAULT NULL,
    descuentos_otorgados_30d         DECIMAL(14,2)                   DEFAULT NULL,

    -- Acumulado mes calendario en curso (desde día 1 del mes)
    unidades_mes_actual              DECIMAL(14,4)                   DEFAULT NULL,
    monto_mes_actual                 DECIMAL(14,2)                   DEFAULT NULL,
    descuentos_mes_actual            DECIMAL(14,2)                   DEFAULT NULL,
    pct_promo_mes_actual             DECIMAL(6,2)                    DEFAULT NULL,

    -- Mismo día del mes anterior (comparativa día a día)
    monto_mismo_dia_mes_ant          DECIMAL(14,2)                   DEFAULT NULL,
    variacion_dia_vs_mes_ant_pct     DECIMAL(8,2)                    DEFAULT NULL,

    -- Mes anterior completo (benchmark)
    unidades_mes_anterior            DECIMAL(14,4)                   DEFAULT NULL,
    monto_mes_anterior               DECIMAL(14,2)                   DEFAULT NULL,
    pct_promo_mes_anterior           DECIMAL(6,2)                    DEFAULT NULL,

    -- ─────────────────────────────────────────────
    -- MÉTRICAS DE EFECTIVIDAD PROMOCIONAL
    -- ─────────────────────────────────────────────
    baseline_unidades_30d_pre_promo  DECIMAL(14,4)                   DEFAULT NULL,   -- promedio diario 30d antes de iniciar promo
    uplift_unidades_pct              DECIMAL(8,2)                    DEFAULT NULL,   -- (ventas_dia/baseline - 1) × 100
    costo_descuento_dia              DECIMAL(14,2)                   DEFAULT NULL,   -- unidades_bajo_promo × ahorro_absoluto
    ingreso_incremental_estimado     DECIMAL(14,2)                   DEFAULT NULL,   -- uplift × precio_oficial × baseline

    -- ─────────────────────────────────────────────
    -- AUDITORÍA
    -- ─────────────────────────────────────────────
    fecha_carga                      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_sppd PRIMARY KEY (id),
    CONSTRAINT uq_sppd_prod_fecha UNIQUE (producto_id, fecha, promocion_id)
);

-- Filtros temporales
CREATE INDEX idx_sppd_fecha          ON sec_promo_precios_diario (fecha);
CREATE INDEX idx_sppd_anio_mes       ON sec_promo_precios_diario (anio_mes);
CREATE INDEX idx_sppd_anio_semana    ON sec_promo_precios_diario (anio_semana);
CREATE INDEX idx_sppd_anio_trimestre ON sec_promo_precios_diario (anio_trimestre);
CREATE INDEX idx_sppd_anio           ON sec_promo_precios_diario (anio);

-- Dimensión producto
CREATE INDEX idx_sppd_producto       ON sec_promo_precios_diario (producto_id, fecha);
CREATE INDEX idx_sppd_categoria      ON sec_promo_precios_diario (categoria_id, fecha);
CREATE INDEX idx_sppd_cat_padre      ON sec_promo_precios_diario (categoria_padre_id, fecha);

-- Filtros de negocio
CREATE INDEX idx_sppd_promo_activa   ON sec_promo_precios_diario (tiene_promocion_activa, fecha);
CREATE INDEX idx_sppd_promocion      ON sec_promo_precios_diario (promocion_id, fecha);
CREATE INDEX idx_sppd_descuento_max  ON sec_promo_precios_diario (descuento_especial_max_pct, fecha);
CREATE INDEX idx_sppd_pct_promo_30d  ON sec_promo_precios_diario (pct_promo_30d DESC);
CREATE INDEX idx_sppd_uplift         ON sec_promo_precios_diario (uplift_unidades_pct DESC);
CREATE INDEX idx_sppd_costo_desc     ON sec_promo_precios_diario (costo_descuento_dia DESC);
CREATE INDEX idx_sppd_fin_semana     ON sec_promo_precios_diario (es_fin_de_semana, fecha);