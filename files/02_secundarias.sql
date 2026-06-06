-- ============================================================
-- 02_secundarias.sql
-- Tablas desnormalizadas para reportes (capa 2)
-- ERP Comercial Multi-sucursal
-- Sin FK a tablas primarias (desacoplamiento intencional)
-- ============================================================

-- ============================================================
-- sec_ventas_detalle
-- Granularidad: línea de pedido
-- Reportes: 1.1,1.2,1.3,1.4,1.5,1.6,1.7,6.1,6.2,6.5,7.1,7.2,7.3,7.6
-- Carga: tiempo real / cada hora
-- ============================================================

CREATE TABLE sec_ventas_detalle (
    id                     BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    -- Tiempo
    fecha_pedido           DATE              NOT NULL,
    anio                   SMALLINT UNSIGNED NOT NULL,
    mes                    TINYINT UNSIGNED  NOT NULL,
    semana                 TINYINT UNSIGNED  NOT NULL,
    dia_semana             TINYINT UNSIGNED  NOT NULL,
    -- Pedido
    pedido_id              INT UNSIGNED      NOT NULL,
    numero_pedido          VARCHAR(30)       NOT NULL,
    estado_pedido          VARCHAR(30)       NOT NULL,
    linea_pedido_id        INT UNSIGNED      NOT NULL,
    -- Geografía
    pais_id                SMALLINT UNSIGNED NOT NULL,
    pais_nombre            VARCHAR(100)      NOT NULL,
    pais_moneda            CHAR(3)           NOT NULL,
    ciudad_id              INT UNSIGNED      NOT NULL,
    ciudad_nombre          VARCHAR(100)      NOT NULL,
    sucursal_id            INT UNSIGNED      NOT NULL,
    sucursal_nombre        VARCHAR(150)      NOT NULL,
    -- Cliente
    cliente_id             INT UNSIGNED      NOT NULL,
    cliente_nombre         VARCHAR(200)      NOT NULL,
    cliente_tipo           VARCHAR(20)       NOT NULL,
    grupo_cliente_id       INT UNSIGNED               DEFAULT NULL,
    grupo_cliente_nombre   VARCHAR(100)               DEFAULT NULL,
    -- Producto
    producto_id            INT UNSIGNED      NOT NULL,
    producto_sku           VARCHAR(60)       NOT NULL,
    producto_nombre        VARCHAR(200)      NOT NULL,
    categoria_id           INT UNSIGNED               DEFAULT NULL,
    categoria_nombre       VARCHAR(150)               DEFAULT NULL,
    categoria_padre_nombre VARCHAR(150)               DEFAULT NULL,
    -- Bodega
    bodega_id              INT UNSIGNED      NOT NULL,
    bodega_nombre          VARCHAR(150)      NOT NULL,
    -- Promoción
    promocion_id           INT UNSIGNED               DEFAULT NULL,
    promocion_nombre       VARCHAR(150)               DEFAULT NULL,
    tiene_precio_especial  TINYINT(1)        NOT NULL DEFAULT 0,
    -- Valores
    moneda                 CHAR(3)           NOT NULL,
    cantidad               DECIMAL(14,4)     NOT NULL,
    precio_oficial         DECIMAL(14,4)     NOT NULL,
    precio_unitario_venta  DECIMAL(14,4)     NOT NULL,
    descuento_pct          DECIMAL(6,4)      NOT NULL DEFAULT 0,
    descuento_monto        DECIMAL(14,4)     NOT NULL DEFAULT 0,
    subtotal_linea         DECIMAL(14,4)     NOT NULL,
    margen_bruto_estimado  DECIMAL(14,4)              DEFAULT NULL,
    -- Auditoría
    fecha_carga            DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion    DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                           ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_svd PRIMARY KEY (id),
    CONSTRAINT uq_svd_linea UNIQUE (linea_pedido_id)
);
CREATE INDEX idx_svd_fecha         ON sec_ventas_detalle (fecha_pedido);
CREATE INDEX idx_svd_anio_mes      ON sec_ventas_detalle (anio, mes);
CREATE INDEX idx_svd_pais          ON sec_ventas_detalle (pais_id, fecha_pedido);
CREATE INDEX idx_svd_sucursal      ON sec_ventas_detalle (sucursal_id, fecha_pedido);
CREATE INDEX idx_svd_cliente       ON sec_ventas_detalle (cliente_id, fecha_pedido);
CREATE INDEX idx_svd_producto      ON sec_ventas_detalle (producto_id, fecha_pedido);
CREATE INDEX idx_svd_categoria     ON sec_ventas_detalle (categoria_id, fecha_pedido);
CREATE INDEX idx_svd_grupo_cliente ON sec_ventas_detalle (grupo_cliente_id);
CREATE INDEX idx_svd_estado_pedido ON sec_ventas_detalle (estado_pedido, fecha_pedido);
CREATE INDEX idx_svd_promocion     ON sec_ventas_detalle (promocion_id);
CREATE INDEX idx_svd_precio_esp    ON sec_ventas_detalle (tiene_precio_especial, fecha_pedido);


-- ============================================================
-- sec_facturas_cartera
-- Granularidad: factura
-- Reportes: 1.7,1.8,4.4,4.5,7.3,7.5
-- Carga: tiempo real / cada hora
-- ============================================================

CREATE TABLE sec_facturas_cartera (
    id                      INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    -- Tiempo
    fecha_emision           DATE              NOT NULL,
    fecha_vencimiento       DATE                        DEFAULT NULL,
    anio                    SMALLINT UNSIGNED NOT NULL,
    mes                     TINYINT UNSIGNED  NOT NULL,
    dias_mora               SMALLINT          NOT NULL DEFAULT 0,
    esta_vencida            TINYINT(1)        NOT NULL DEFAULT 0,
    -- Identificadores
    factura_id              INT UNSIGNED      NOT NULL,
    numero_fiscal           VARCHAR(60)       NOT NULL,
    pedido_id               INT UNSIGNED      NOT NULL,
    numero_pedido           VARCHAR(30)       NOT NULL,
    estado_factura          VARCHAR(20)       NOT NULL,
    estado_pedido           VARCHAR(30)       NOT NULL,
    -- Geografía
    pais_id                 SMALLINT UNSIGNED NOT NULL,
    pais_nombre             VARCHAR(100)      NOT NULL,
    sucursal_id             INT UNSIGNED      NOT NULL,
    sucursal_nombre         VARCHAR(150)      NOT NULL,
    -- Cliente
    cliente_id              INT UNSIGNED      NOT NULL,
    cliente_nombre          VARCHAR(200)      NOT NULL,
    grupo_cliente_id        INT UNSIGNED               DEFAULT NULL,
    grupo_cliente_nombre    VARCHAR(100)               DEFAULT NULL,
    limite_credito          DECIMAL(14,2)     NOT NULL DEFAULT 0,
    credito_usado_acumulado DECIMAL(14,2)     NOT NULL DEFAULT 0,
    pct_credito_usado       DECIMAL(6,2)      NOT NULL DEFAULT 0,
    -- Importes
    moneda                  CHAR(3)           NOT NULL,
    subtotal                DECIMAL(14,2)     NOT NULL,
    descuento_total         DECIMAL(14,2)     NOT NULL DEFAULT 0,
    base_imponible          DECIMAL(14,2)     NOT NULL,
    impuesto_monto          DECIMAL(14,2)     NOT NULL DEFAULT 0,
    total                   DECIMAL(14,2)     NOT NULL,
    monto_pagado            DECIMAL(14,2)     NOT NULL DEFAULT 0,
    saldo_pendiente         DECIMAL(14,2)     NOT NULL DEFAULT 0,
    tipo_entrega            VARCHAR(30)                DEFAULT NULL,
    -- Auditoría
    fecha_carga             DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_sfc PRIMARY KEY (id),
    CONSTRAINT uq_sfc_factura UNIQUE (factura_id)
);
CREATE INDEX idx_sfc_fecha        ON sec_facturas_cartera (fecha_emision);
CREATE INDEX idx_sfc_anio_mes     ON sec_facturas_cartera (anio, mes);
CREATE INDEX idx_sfc_vencimiento  ON sec_facturas_cartera (fecha_vencimiento, estado_factura);
CREATE INDEX idx_sfc_esta_vencida ON sec_facturas_cartera (esta_vencida, dias_mora);
CREATE INDEX idx_sfc_cliente      ON sec_facturas_cartera (cliente_id, esta_vencida);
CREATE INDEX idx_sfc_pais         ON sec_facturas_cartera (pais_id, fecha_emision);
CREATE INDEX idx_sfc_sucursal     ON sec_facturas_cartera (sucursal_id, fecha_emision);
CREATE INDEX idx_sfc_estado       ON sec_facturas_cartera (estado_factura);
CREATE INDEX idx_sfc_credito      ON sec_facturas_cartera (pct_credito_usado);


-- ============================================================
-- sec_clientes_resumen
-- Granularidad: cliente × mes
-- Reportes: 4.1,4.2,4.3,4.6,4.7,7.1
-- Carga: una vez al mes (cierre)
-- ============================================================

CREATE TABLE sec_clientes_resumen (
    id                          INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    anio                        SMALLINT UNSIGNED NOT NULL,
    mes                         TINYINT UNSIGNED  NOT NULL,
    -- Cliente
    cliente_id                  INT UNSIGNED      NOT NULL,
    cliente_nombre              VARCHAR(200)      NOT NULL,
    cliente_tipo                VARCHAR(20)       NOT NULL,
    identificacion              VARCHAR(50)                 DEFAULT NULL,
    fecha_registro              DATE              NOT NULL,
    grupo_cliente_id            INT UNSIGNED               DEFAULT NULL,
    grupo_cliente_nombre        VARCHAR(100)               DEFAULT NULL,
    pais_id                     SMALLINT UNSIGNED NOT NULL,
    pais_nombre                 VARCHAR(100)      NOT NULL,
    -- Actividad acumulada histórica
    total_pedidos_historico     INT UNSIGNED      NOT NULL DEFAULT 0,
    total_facturado_historico   DECIMAL(16,2)     NOT NULL DEFAULT 0,
    ticket_promedio_historico   DECIMAL(14,2)     NOT NULL DEFAULT 0,
    primera_compra_fecha        DATE                        DEFAULT NULL,
    ultima_compra_fecha         DATE                        DEFAULT NULL,
    dias_desde_ultima_compra    INT                         DEFAULT NULL,
    -- Actividad período actual
    pedidos_periodo             INT UNSIGNED      NOT NULL DEFAULT 0,
    facturado_periodo           DECIMAL(14,2)     NOT NULL DEFAULT 0,
    unidades_periodo            DECIMAL(14,4)     NOT NULL DEFAULT 0,
    -- Actividad período anterior
    pedidos_periodo_anterior    INT UNSIGNED      NOT NULL DEFAULT 0,
    facturado_periodo_anterior  DECIMAL(14,2)     NOT NULL DEFAULT 0,
    variacion_pct               DECIMAL(8,2)               DEFAULT NULL,
    -- Segmentación
    segmento_actividad          ENUM('activo_30','activo_60','activo_90',
                                     'inactivo_90_plus','nuevo','recuperado','perdido')
                                                  NOT NULL DEFAULT 'activo_30',
    es_nuevo_periodo            TINYINT(1)        NOT NULL DEFAULT 0,
    es_recuperado               TINYINT(1)        NOT NULL DEFAULT 0,
    es_perdido                  TINYINT(1)        NOT NULL DEFAULT 0,
    -- Crédito
    limite_credito              DECIMAL(14,2)     NOT NULL DEFAULT 0,
    saldo_pendiente             DECIMAL(14,2)     NOT NULL DEFAULT 0,
    facturas_vencidas_cantidad  INT UNSIGNED      NOT NULL DEFAULT 0,
    monto_vencido               DECIMAL(14,2)     NOT NULL DEFAULT 0,
    dias_mora_promedio          DECIMAL(6,2)               DEFAULT NULL,
    tiene_precio_especial       TINYINT(1)        NOT NULL DEFAULT 0,
    fecha_carga                 DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_scr PRIMARY KEY (id),
    CONSTRAINT uq_scr_cliente_periodo UNIQUE (cliente_id, anio, mes)
);
CREATE INDEX idx_scr_anio_mes  ON sec_clientes_resumen (anio, mes);
CREATE INDEX idx_scr_pais      ON sec_clientes_resumen (pais_id, anio, mes);
CREATE INDEX idx_scr_grupo     ON sec_clientes_resumen (grupo_cliente_id, anio, mes);
CREATE INDEX idx_scr_segmento  ON sec_clientes_resumen (segmento_actividad, anio, mes);
CREATE INDEX idx_scr_facturado ON sec_clientes_resumen (facturado_periodo DESC);
CREATE INDEX idx_scr_mora      ON sec_clientes_resumen (monto_vencido, dias_mora_promedio);
CREATE INDEX idx_scr_nuevos    ON sec_clientes_resumen (es_nuevo_periodo, anio, mes);
CREATE INDEX idx_scr_perdidos  ON sec_clientes_resumen (es_perdido, anio, mes);


-- ============================================================
-- sec_inventario_snapshot
-- Granularidad: producto × bodega × día
-- Reportes: 2.1,2.2,2.3,2.4,2.5,2.7,5.4,7.5
-- Carga: una vez al día (nocturno)
-- ============================================================

CREATE TABLE sec_inventario_snapshot (
    id                   BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    fecha_snapshot       DATE              NOT NULL,
    anio                 SMALLINT UNSIGNED NOT NULL,
    mes                  TINYINT UNSIGNED  NOT NULL,
    -- Bodega
    bodega_id            INT UNSIGNED      NOT NULL,
    bodega_nombre        VARCHAR(150)      NOT NULL,
    bodega_tipo          VARCHAR(30)       NOT NULL,
    sucursal_id          INT UNSIGNED               DEFAULT NULL,
    sucursal_nombre      VARCHAR(150)               DEFAULT NULL,
    pais_id              SMALLINT UNSIGNED          DEFAULT NULL,
    pais_nombre          VARCHAR(100)               DEFAULT NULL,
    capacidad_m3         DECIMAL(10,2)              DEFAULT NULL,
    -- Producto
    producto_id          INT UNSIGNED      NOT NULL,
    producto_sku         VARCHAR(60)       NOT NULL,
    producto_nombre      VARCHAR(200)      NOT NULL,
    categoria_id         INT UNSIGNED               DEFAULT NULL,
    categoria_nombre     VARCHAR(150)               DEFAULT NULL,
    -- Stock
    cantidad_total       DECIMAL(14,4)     NOT NULL DEFAULT 0,
    cantidad_reservada   DECIMAL(14,4)     NOT NULL DEFAULT 0,
    cantidad_disponible  DECIMAL(14,4)     NOT NULL DEFAULT 0,
    valor_stock_oficial  DECIMAL(16,2)     NOT NULL DEFAULT 0,
    -- Rotación
    ventas_unidades_30d  DECIMAL(14,4)     NOT NULL DEFAULT 0,
    ventas_unidades_60d  DECIMAL(14,4)     NOT NULL DEFAULT 0,
    ventas_unidades_90d  DECIMAL(14,4)     NOT NULL DEFAULT 0,
    dias_cobertura       DECIMAL(8,2)               DEFAULT NULL,
    indice_rotacion_90d  DECIMAL(8,4)               DEFAULT NULL,
    -- Alertas
    stock_critico        TINYINT(1)        NOT NULL DEFAULT 0,
    sin_movimiento_30d   TINYINT(1)        NOT NULL DEFAULT 0,
    sin_movimiento_60d   TINYINT(1)        NOT NULL DEFAULT 0,
    sin_movimiento_90d   TINYINT(1)        NOT NULL DEFAULT 0,
    ajustes_cantidad_mes DECIMAL(14,4)     NOT NULL DEFAULT 0,
    fecha_carga          DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_sis PRIMARY KEY (id),
    CONSTRAINT uq_sis_snap UNIQUE (bodega_id, producto_id, fecha_snapshot)
);
CREATE INDEX idx_sis_fecha          ON sec_inventario_snapshot (fecha_snapshot);
CREATE INDEX idx_sis_pais           ON sec_inventario_snapshot (pais_id, fecha_snapshot);
CREATE INDEX idx_sis_sucursal       ON sec_inventario_snapshot (sucursal_id, fecha_snapshot);
CREATE INDEX idx_sis_bodega         ON sec_inventario_snapshot (bodega_id, fecha_snapshot);
CREATE INDEX idx_sis_producto       ON sec_inventario_snapshot (producto_id, fecha_snapshot);
CREATE INDEX idx_sis_critico        ON sec_inventario_snapshot (stock_critico, fecha_snapshot);
CREATE INDEX idx_sis_sin_movimiento ON sec_inventario_snapshot (sin_movimiento_90d, fecha_snapshot);
CREATE INDEX idx_sis_rotacion       ON sec_inventario_snapshot (indice_rotacion_90d);


-- ============================================================
-- sec_movimientos_stock
-- Granularidad: movimiento
-- Reportes: 2.6,2.7,2.8
-- Carga: una vez al día (nocturno)
-- ============================================================

CREATE TABLE sec_movimientos_stock (
    id                  BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    fecha               DATETIME          NOT NULL,
    fecha_dia           DATE              NOT NULL,
    anio                SMALLINT UNSIGNED NOT NULL,
    mes                 TINYINT UNSIGNED  NOT NULL,
    -- Movimiento
    movimiento_id       BIGINT UNSIGNED   NOT NULL,
    tipo_movimiento     VARCHAR(40)       NOT NULL,
    es_ajuste           TINYINT(1)        NOT NULL DEFAULT 0,
    es_traslado         TINYINT(1)        NOT NULL DEFAULT 0,
    referencia_tipo     VARCHAR(50)                DEFAULT NULL,
    referencia_id       INT UNSIGNED               DEFAULT NULL,
    -- Bodega origen
    bodega_id           INT UNSIGNED      NOT NULL,
    bodega_nombre       VARCHAR(150)      NOT NULL,
    bodega_tipo         VARCHAR(30)       NOT NULL,
    sucursal_id         INT UNSIGNED               DEFAULT NULL,
    sucursal_nombre     VARCHAR(150)               DEFAULT NULL,
    pais_id             SMALLINT UNSIGNED          DEFAULT NULL,
    pais_nombre         VARCHAR(100)               DEFAULT NULL,
    -- Bodega destino (traslados)
    bodega_destino_id   INT UNSIGNED               DEFAULT NULL,
    bodega_destino_nombre VARCHAR(150)             DEFAULT NULL,
    -- Producto
    producto_id         INT UNSIGNED      NOT NULL,
    producto_sku        VARCHAR(60)       NOT NULL,
    producto_nombre     VARCHAR(200)      NOT NULL,
    categoria_id        INT UNSIGNED               DEFAULT NULL,
    categoria_nombre    VARCHAR(150)               DEFAULT NULL,
    -- Cantidades
    cantidad            DECIMAL(14,4)     NOT NULL,
    stock_antes         DECIMAL(14,4)     NOT NULL,
    stock_despues       DECIMAL(14,4)     NOT NULL,
    valor_movimiento    DECIMAL(16,2)              DEFAULT NULL,
    fecha_carga         DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_sms PRIMARY KEY (id),
    CONSTRAINT uq_sms_mov UNIQUE (movimiento_id)
);
CREATE INDEX idx_sms_fecha      ON sec_movimientos_stock (fecha_dia);
CREATE INDEX idx_sms_anio_mes   ON sec_movimientos_stock (anio, mes);
CREATE INDEX idx_sms_bodega     ON sec_movimientos_stock (bodega_id, fecha_dia);
CREATE INDEX idx_sms_producto   ON sec_movimientos_stock (producto_id, fecha_dia);
CREATE INDEX idx_sms_tipo       ON sec_movimientos_stock (tipo_movimiento, fecha_dia);
CREATE INDEX idx_sms_ajuste     ON sec_movimientos_stock (es_ajuste, fecha_dia);
CREATE INDEX idx_sms_traslado   ON sec_movimientos_stock (es_traslado, fecha_dia);
CREATE INDEX idx_sms_referencia ON sec_movimientos_stock (referencia_tipo, referencia_id);


-- ============================================================
-- sec_logistica_entregas
-- Granularidad: entrega
-- Reportes: 3.1,3.2,3.5,3.6,3.7,3.8,7.5
-- Carga: tiempo real / cada hora
-- ============================================================

CREATE TABLE sec_logistica_entregas (
    id                       INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    -- Tiempo
    fecha_entrega_estimada   DATE                        DEFAULT NULL,
    fecha_entrega_real       DATE                        DEFAULT NULL,
    anio                     SMALLINT UNSIGNED          DEFAULT NULL,
    mes                      TINYINT UNSIGNED           DEFAULT NULL,
    dias_retraso             SMALLINT          NOT NULL DEFAULT 0,
    entrega_a_tiempo         TINYINT(1)        NOT NULL DEFAULT 0,
    -- Identificadores
    entrega_id               INT UNSIGNED      NOT NULL,
    pedido_id                INT UNSIGNED      NOT NULL,
    numero_pedido            VARCHAR(30)       NOT NULL,
    tipo_entrega             VARCHAR(30)       NOT NULL,
    estado_entrega           VARCHAR(30)       NOT NULL,
    -- Cliente y destino
    cliente_id               INT UNSIGNED      NOT NULL,
    cliente_nombre           VARCHAR(200)      NOT NULL,
    pais_id                  SMALLINT UNSIGNED NOT NULL,
    pais_nombre              VARCHAR(100)      NOT NULL,
    ciudad_id                INT UNSIGNED               DEFAULT NULL,
    ciudad_nombre            VARCHAR(100)               DEFAULT NULL,
    sucursal_retiro_id       INT UNSIGNED               DEFAULT NULL,
    sucursal_retiro_nombre   VARCHAR(150)               DEFAULT NULL,
    -- Transporte
    recorrido_id             INT UNSIGNED               DEFAULT NULL,
    camion_id                INT UNSIGNED               DEFAULT NULL,
    camion_patente           VARCHAR(20)                DEFAULT NULL,
    conductor_id             INT UNSIGNED               DEFAULT NULL,
    conductor_nombre         VARCHAR(200)               DEFAULT NULL,
    ruta_id                  INT UNSIGNED               DEFAULT NULL,
    ruta_nombre              VARCHAR(150)               DEFAULT NULL,
    parada_orden             SMALLINT UNSIGNED          DEFAULT NULL,
    -- Métricas
    peso_total_kg            DECIMAL(10,2)              DEFAULT NULL,
    volumen_total_m3         DECIMAL(8,4)               DEFAULT NULL,
    valor_pedido             DECIMAL(14,2)     NOT NULL DEFAULT 0,
    costo_entrega_estimado   DECIMAL(10,2)              DEFAULT NULL,
    -- Resultado
    fue_exitosa              TINYINT(1)        NOT NULL DEFAULT 0,
    motivo_fallo             VARCHAR(200)               DEFAULT NULL,
    requirio_reintento       TINYINT(1)        NOT NULL DEFAULT 0,
    fecha_carga              DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion      DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP
                             ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_sle PRIMARY KEY (id),
    CONSTRAINT uq_sle_entrega UNIQUE (entrega_id)
);
CREATE INDEX idx_sle_fecha      ON sec_logistica_entregas (fecha_entrega_real);
CREATE INDEX idx_sle_anio_mes   ON sec_logistica_entregas (anio, mes);
CREATE INDEX idx_sle_pais       ON sec_logistica_entregas (pais_id, fecha_entrega_real);
CREATE INDEX idx_sle_cliente    ON sec_logistica_entregas (cliente_id);
CREATE INDEX idx_sle_camion     ON sec_logistica_entregas (camion_id, fecha_entrega_real);
CREATE INDEX idx_sle_conductor  ON sec_logistica_entregas (conductor_id, fecha_entrega_real);
CREATE INDEX idx_sle_recorrido  ON sec_logistica_entregas (recorrido_id);
CREATE INDEX idx_sle_estado     ON sec_logistica_entregas (estado_entrega, fecha_entrega_real);
CREATE INDEX idx_sle_a_tiempo   ON sec_logistica_entregas (entrega_a_tiempo, anio, mes);
CREATE INDEX idx_sle_fallidas   ON sec_logistica_entregas (fue_exitosa, fecha_entrega_real);


-- ============================================================
-- sec_rendimiento_flota
-- Granularidad: recorrido
-- Reportes: 3.3,3.4,3.7,3.8
-- Carga: una vez al día (nocturno)
-- ============================================================

CREATE TABLE sec_rendimiento_flota (
    id                    INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    fecha_salida          DATE              NOT NULL,
    fecha_llegada         DATE                        DEFAULT NULL,
    anio                  SMALLINT UNSIGNED NOT NULL,
    mes                   TINYINT UNSIGNED  NOT NULL,
    duracion_minutos      INT UNSIGNED               DEFAULT NULL,
    -- Recorrido
    recorrido_id          INT UNSIGNED      NOT NULL,
    estado_recorrido      VARCHAR(30)       NOT NULL,
    -- Camión
    camion_id             INT UNSIGNED      NOT NULL,
    camion_patente        VARCHAR(20)       NOT NULL,
    camion_marca          VARCHAR(80)                DEFAULT NULL,
    camion_modelo         VARCHAR(80)                DEFAULT NULL,
    capacidad_kg          DECIMAL(10,2)              DEFAULT NULL,
    capacidad_m3          DECIMAL(8,2)               DEFAULT NULL,
    sucursal_base_id      INT UNSIGNED               DEFAULT NULL,
    sucursal_base_nombre  VARCHAR(150)               DEFAULT NULL,
    -- Conductor
    conductor_id          INT UNSIGNED      NOT NULL,
    conductor_nombre      VARCHAR(200)      NOT NULL,
    -- Ruta
    ruta_id               INT UNSIGNED               DEFAULT NULL,
    ruta_nombre           VARCHAR(150)               DEFAULT NULL,
    distancia_ruta_km     DECIMAL(8,2)               DEFAULT NULL,
    -- Métricas
    km_recorridos         DECIMAL(10,2)              DEFAULT NULL,
    paradas_totales       SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    paradas_completadas   SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    paradas_fallidas      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    pct_completado        DECIMAL(6,2)               DEFAULT NULL,
    -- Carga
    peso_cargado_kg       DECIMAL(10,2)              DEFAULT NULL,
    volumen_cargado_m3    DECIMAL(8,4)               DEFAULT NULL,
    pct_ocupacion_kg      DECIMAL(6,2)               DEFAULT NULL,
    pct_ocupacion_m3      DECIMAL(6,2)               DEFAULT NULL,
    valor_carga_total     DECIMAL(16,2)              DEFAULT NULL,
    -- Puntualidad
    tiempo_estimado_min   INT UNSIGNED               DEFAULT NULL,
    tiempo_real_min       INT UNSIGNED               DEFAULT NULL,
    desviacion_tiempo_min INT                        DEFAULT NULL,
    recorrido_a_tiempo    TINYINT(1)        NOT NULL DEFAULT 0,
    fecha_carga           DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_srf PRIMARY KEY (id),
    CONSTRAINT uq_srf_recorrido UNIQUE (recorrido_id)
);
CREATE INDEX idx_srf_fecha      ON sec_rendimiento_flota (fecha_salida);
CREATE INDEX idx_srf_anio_mes   ON sec_rendimiento_flota (anio, mes);
CREATE INDEX idx_srf_camion     ON sec_rendimiento_flota (camion_id, fecha_salida);
CREATE INDEX idx_srf_conductor  ON sec_rendimiento_flota (conductor_id, fecha_salida);
CREATE INDEX idx_srf_ruta       ON sec_rendimiento_flota (ruta_id, fecha_salida);
CREATE INDEX idx_srf_ocupacion  ON sec_rendimiento_flota (pct_ocupacion_kg);
CREATE INDEX idx_srf_estado     ON sec_rendimiento_flota (estado_recorrido);


-- ============================================================
-- sec_resumen_sucursal_dia
-- Granularidad: sucursal × día
-- Reportes: 5.1,5.2,5.3,5.5,7.1,7.2,7.6
-- Carga: una vez al día (nocturno)
-- ============================================================

CREATE TABLE sec_resumen_sucursal_dia (
    id                         INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    fecha                      DATE              NOT NULL,
    anio                       SMALLINT UNSIGNED NOT NULL,
    mes                        TINYINT UNSIGNED  NOT NULL,
    semana                     TINYINT UNSIGNED  NOT NULL,
    -- Sucursal
    sucursal_id                INT UNSIGNED      NOT NULL,
    sucursal_nombre            VARCHAR(150)      NOT NULL,
    ciudad_id                  INT UNSIGNED      NOT NULL,
    ciudad_nombre              VARCHAR(100)      NOT NULL,
    pais_id                    SMALLINT UNSIGNED NOT NULL,
    pais_nombre                VARCHAR(100)      NOT NULL,
    moneda_pais                CHAR(3)           NOT NULL,
    -- Pedidos
    pedidos_total              INT UNSIGNED      NOT NULL DEFAULT 0,
    pedidos_confirmados        INT UNSIGNED      NOT NULL DEFAULT 0,
    pedidos_en_preparacion     INT UNSIGNED      NOT NULL DEFAULT 0,
    pedidos_listos             INT UNSIGNED      NOT NULL DEFAULT 0,
    pedidos_entregados         INT UNSIGNED      NOT NULL DEFAULT 0,
    pedidos_cancelados         INT UNSIGNED      NOT NULL DEFAULT 0,
    pedidos_anulados           INT UNSIGNED      NOT NULL DEFAULT 0,
    -- Ventas
    monto_pedidos_confirmados  DECIMAL(14,2)     NOT NULL DEFAULT 0,
    monto_entregado            DECIMAL(14,2)     NOT NULL DEFAULT 0,
    monto_cancelado            DECIMAL(14,2)     NOT NULL DEFAULT 0,
    ticket_promedio_dia        DECIMAL(14,2)              DEFAULT NULL,
    -- Facturación
    facturas_emitidas          INT UNSIGNED      NOT NULL DEFAULT 0,
    monto_facturado            DECIMAL(14,2)     NOT NULL DEFAULT 0,
    facturas_vencidas_acum     INT UNSIGNED      NOT NULL DEFAULT 0,
    monto_vencido_acum         DECIMAL(14,2)     NOT NULL DEFAULT 0,
    -- Entregas
    entregas_programadas       INT UNSIGNED      NOT NULL DEFAULT 0,
    entregas_completadas       INT UNSIGNED      NOT NULL DEFAULT 0,
    entregas_fallidas          INT UNSIGNED      NOT NULL DEFAULT 0,
    pct_entregas_exitosas      DECIMAL(6,2)               DEFAULT NULL,
    -- Inventario
    productos_stock_critico    INT UNSIGNED      NOT NULL DEFAULT 0,
    productos_sin_stock        INT UNSIGNED      NOT NULL DEFAULT 0,
    bodegas_ocupacion_pct_avg  DECIMAL(6,2)               DEFAULT NULL,
    -- Comparativas
    monto_facturado_mes_ant    DECIMAL(14,2)              DEFAULT NULL,
    variacion_vs_mes_ant_pct   DECIMAL(8,2)               DEFAULT NULL,
    monto_facturado_anio_ant   DECIMAL(14,2)              DEFAULT NULL,
    variacion_vs_anio_ant_pct  DECIMAL(8,2)               DEFAULT NULL,
    fecha_carga                DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_srsd PRIMARY KEY (id),
    CONSTRAINT uq_srsd_suc_fecha UNIQUE (sucursal_id, fecha)
);
CREATE INDEX idx_srsd_fecha     ON sec_resumen_sucursal_dia (fecha);
CREATE INDEX idx_srsd_anio_mes  ON sec_resumen_sucursal_dia (anio, mes);
CREATE INDEX idx_srsd_pais      ON sec_resumen_sucursal_dia (pais_id, fecha);
CREATE INDEX idx_srsd_sucursal  ON sec_resumen_sucursal_dia (sucursal_id, fecha);
CREATE INDEX idx_srsd_facturado ON sec_resumen_sucursal_dia (monto_facturado DESC);
CREATE INDEX idx_srsd_critico   ON sec_resumen_sucursal_dia (productos_stock_critico);


-- ============================================================
-- sec_promociones_precios
-- Granularidad: producto × promoción × mes
-- Reportes: 1.5,1.6,6.3,6.4
-- Carga: una vez al mes (cierre)
-- ============================================================

CREATE TABLE sec_promociones_precios (
    id                           INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    fecha_snapshot               DATE              NOT NULL,
    anio                         SMALLINT UNSIGNED NOT NULL,
    mes                          TINYINT UNSIGNED  NOT NULL,
    -- Producto
    producto_id                  INT UNSIGNED      NOT NULL,
    producto_sku                 VARCHAR(60)       NOT NULL,
    producto_nombre              VARCHAR(200)      NOT NULL,
    categoria_id                 INT UNSIGNED               DEFAULT NULL,
    categoria_nombre             VARCHAR(150)               DEFAULT NULL,
    precio_oficial               DECIMAL(14,4)     NOT NULL,
    moneda                       CHAR(3)           NOT NULL,
    -- Promoción
    promocion_id                 INT UNSIGNED               DEFAULT NULL,
    promocion_nombre             VARCHAR(150)               DEFAULT NULL,
    promocion_tipo               VARCHAR(30)                DEFAULT NULL,
    promocion_descuento_pct      DECIMAL(6,4)               DEFAULT NULL,
    promocion_precio_final       DECIMAL(14,4)              DEFAULT NULL,
    promocion_vigente            TINYINT(1)        NOT NULL DEFAULT 0,
    promocion_fecha_inicio       DATE                        DEFAULT NULL,
    promocion_fecha_fin          DATE                        DEFAULT NULL,
    dias_restantes_promo         INT                         DEFAULT NULL,
    -- Precios especiales (resumen)
    cantidad_precios_especiales  INT UNSIGNED      NOT NULL DEFAULT 0,
    precio_especial_minimo       DECIMAL(14,4)              DEFAULT NULL,
    precio_especial_maximo       DECIMAL(14,4)              DEFAULT NULL,
    precio_especial_promedio     DECIMAL(14,4)              DEFAULT NULL,
    descuento_especial_max_pct   DECIMAL(6,4)               DEFAULT NULL,
    -- Ventas del mes
    unidades_vendidas_mes        DECIMAL(14,4)     NOT NULL DEFAULT 0,
    unidades_bajo_promo_mes      DECIMAL(14,4)     NOT NULL DEFAULT 0,
    unidades_bajo_precio_esp_mes DECIMAL(14,4)     NOT NULL DEFAULT 0,
    monto_vendido_mes            DECIMAL(14,2)     NOT NULL DEFAULT 0,
    monto_descuentos_mes         DECIMAL(14,2)     NOT NULL DEFAULT 0,
    pct_ventas_bajo_promo        DECIMAL(6,2)               DEFAULT NULL,
    fecha_carga                  DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_spp PRIMARY KEY (id),
    CONSTRAINT uq_spp_prod_fecha UNIQUE (producto_id, promocion_id, fecha_snapshot)
);
CREATE INDEX idx_spp_fecha        ON sec_promociones_precios (fecha_snapshot);
CREATE INDEX idx_spp_anio_mes     ON sec_promociones_precios (anio, mes);
CREATE INDEX idx_spp_producto     ON sec_promociones_precios (producto_id, fecha_snapshot);
CREATE INDEX idx_spp_categoria    ON sec_promociones_precios (categoria_id, fecha_snapshot);
CREATE INDEX idx_spp_vigente      ON sec_promociones_precios (promocion_vigente, dias_restantes_promo);
CREATE INDEX idx_spp_descuento    ON sec_promociones_precios (descuento_especial_max_pct);
CREATE INDEX idx_spp_ventas_promo ON sec_promociones_precios (pct_ventas_bajo_promo DESC);