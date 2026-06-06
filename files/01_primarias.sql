-- ============================================================
-- 01_primarias.sql
-- Tablas transaccionales normalizadas
-- ERP Comercial Multi-sucursal
-- ============================================================

-- ============================================================
-- BLOQUE 1: GEOGRAFÍA Y ESTRUCTURA CORPORATIVA
-- ============================================================

CREATE TABLE pais (
    id             SMALLINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nombre         VARCHAR(100)       NOT NULL,
    codigo_iso     CHAR(3)            NOT NULL,           -- ISO 3166-1 alpha-3
    moneda_defecto CHAR(3)            NOT NULL,           -- ISO 4217
    activo         TINYINT(1)         NOT NULL DEFAULT 1,
    CONSTRAINT pk_pais PRIMARY KEY (id),
    CONSTRAINT uq_pais_iso UNIQUE (codigo_iso)
);

CREATE TABLE ciudad (
    id            INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    pais_id       SMALLINT UNSIGNED   NOT NULL,
    nombre        VARCHAR(100)        NOT NULL,
    codigo_postal VARCHAR(20)                  DEFAULT NULL,
    CONSTRAINT pk_ciudad PRIMARY KEY (id),
    CONSTRAINT fk_ciudad_pais FOREIGN KEY (pais_id)
        REFERENCES pais(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_ciudad_pais ON ciudad(pais_id);

CREATE TABLE sucursal (
    id             INT UNSIGNED       NOT NULL AUTO_INCREMENT,
    ciudad_id      INT UNSIGNED       NOT NULL,
    nombre         VARCHAR(150)       NOT NULL,
    direccion      VARCHAR(255)       NOT NULL,
    telefono       VARCHAR(30)                 DEFAULT NULL,
    email          VARCHAR(150)                DEFAULT NULL,
    activa         TINYINT(1)         NOT NULL DEFAULT 1,
    fecha_apertura DATE                        DEFAULT NULL,
    CONSTRAINT pk_sucursal PRIMARY KEY (id),
    CONSTRAINT fk_sucursal_ciudad FOREIGN KEY (ciudad_id)
        REFERENCES ciudad(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_sucursal_ciudad ON sucursal(ciudad_id);

CREATE TABLE bodega (
    id           INT UNSIGNED         NOT NULL AUTO_INCREMENT,
    sucursal_id  INT UNSIGNED                  DEFAULT NULL,   -- NULL = bodega independiente
    nombre       VARCHAR(150)         NOT NULL,
    tipo         ENUM('local','central','transito','externa') NOT NULL DEFAULT 'local',
    capacidad_m3 DECIMAL(10,2)                 DEFAULT NULL,
    activa       TINYINT(1)           NOT NULL DEFAULT 1,
    CONSTRAINT pk_bodega PRIMARY KEY (id),
    CONSTRAINT fk_bodega_sucursal FOREIGN KEY (sucursal_id)
        REFERENCES sucursal(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_bodega_sucursal ON bodega(sucursal_id);


-- ============================================================
-- BLOQUE 2: CLIENTES
-- ============================================================

CREATE TABLE grupo_cliente (
    id          INT UNSIGNED          NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100)          NOT NULL,
    descripcion TEXT                           DEFAULT NULL,
    activo      TINYINT(1)            NOT NULL DEFAULT 1,
    CONSTRAINT pk_grupo_cliente PRIMARY KEY (id)
);

CREATE TABLE cliente (
    id               INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    grupo_cliente_id INT UNSIGNED               DEFAULT NULL,
    tipo             ENUM('persona','empresa')  NOT NULL DEFAULT 'persona',
    nombre           VARCHAR(200)      NOT NULL,
    identificacion   VARCHAR(50)                DEFAULT NULL,   -- RUT, NIT, DNI, etc.
    pais_id          SMALLINT UNSIGNED NOT NULL,
    email            VARCHAR(150)               DEFAULT NULL,
    telefono         VARCHAR(30)                DEFAULT NULL,
    limite_credito   DECIMAL(14,2)              DEFAULT 0.00,
    activo           TINYINT(1)        NOT NULL DEFAULT 1,
    fecha_registro   DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_cliente PRIMARY KEY (id),
    CONSTRAINT fk_cliente_grupo FOREIGN KEY (grupo_cliente_id)
        REFERENCES grupo_cliente(id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_cliente_pais FOREIGN KEY (pais_id)
        REFERENCES pais(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_cliente_grupo   ON cliente(grupo_cliente_id);
CREATE INDEX idx_cliente_pais    ON cliente(pais_id);
CREATE INDEX idx_cliente_identif ON cliente(identificacion);

CREATE TABLE direccion_entrega (
    id           INT UNSIGNED         NOT NULL AUTO_INCREMENT,
    cliente_id   INT UNSIGNED         NOT NULL,
    ciudad_id    INT UNSIGNED         NOT NULL,
    direccion    VARCHAR(255)         NOT NULL,
    referencia   VARCHAR(255)                  DEFAULT NULL,
    contacto     VARCHAR(150)                  DEFAULT NULL,
    telefono     VARCHAR(30)                   DEFAULT NULL,
    es_principal TINYINT(1)           NOT NULL DEFAULT 0,
    activa       TINYINT(1)           NOT NULL DEFAULT 1,
    CONSTRAINT pk_dir_entrega PRIMARY KEY (id),
    CONSTRAINT fk_dir_cliente FOREIGN KEY (cliente_id)
        REFERENCES cliente(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_dir_ciudad FOREIGN KEY (ciudad_id)
        REFERENCES ciudad(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_dir_cliente ON direccion_entrega(cliente_id);
CREATE INDEX idx_dir_ciudad  ON direccion_entrega(ciudad_id);


-- ============================================================
-- BLOQUE 3: CATÁLOGO DE PRODUCTOS
-- ============================================================

CREATE TABLE categoria (
    id          INT UNSIGNED          NOT NULL AUTO_INCREMENT,
    padre_id    INT UNSIGNED                   DEFAULT NULL,   -- autorreferencial
    nombre      VARCHAR(150)          NOT NULL,
    descripcion TEXT                           DEFAULT NULL,
    activa      TINYINT(1)            NOT NULL DEFAULT 1,
    CONSTRAINT pk_categoria PRIMARY KEY (id),
    CONSTRAINT fk_categoria_padre FOREIGN KEY (padre_id)
        REFERENCES categoria(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_categoria_padre ON categoria(padre_id);

CREATE TABLE producto (
    id             INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    categoria_id   INT UNSIGNED                 DEFAULT NULL,
    codigo_sku     VARCHAR(60)         NOT NULL,
    nombre         VARCHAR(200)        NOT NULL,
    descripcion    TEXT                         DEFAULT NULL,
    unidad_medida  VARCHAR(30)         NOT NULL DEFAULT 'unidad',
    precio_oficial DECIMAL(14,4)       NOT NULL,
    moneda         CHAR(3)             NOT NULL DEFAULT 'USD',
    peso_kg        DECIMAL(8,3)                 DEFAULT NULL,
    volumen_m3     DECIMAL(8,4)                 DEFAULT NULL,
    activo         TINYINT(1)          NOT NULL DEFAULT 1,
    fecha_creacion DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_producto PRIMARY KEY (id),
    CONSTRAINT uq_producto_sku UNIQUE (codigo_sku),
    CONSTRAINT fk_producto_cat FOREIGN KEY (categoria_id)
        REFERENCES categoria(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX idx_producto_cat    ON producto(categoria_id);
CREATE INDEX idx_producto_activo ON producto(activo);

CREATE TABLE precio_especial (
    id               INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    producto_id      INT UNSIGNED      NOT NULL,
    cliente_id       INT UNSIGNED               DEFAULT NULL,   -- precio para cliente específico
    grupo_cliente_id INT UNSIGNED               DEFAULT NULL,   -- precio para grupo
    precio           DECIMAL(14,4)     NOT NULL,
    moneda           CHAR(3)           NOT NULL DEFAULT 'USD',
    fecha_inicio     DATE              NOT NULL,
    fecha_fin        DATE                        DEFAULT NULL,   -- NULL = sin vencimiento
    activo           TINYINT(1)        NOT NULL DEFAULT 1,
    -- Al menos uno de cliente_id o grupo_cliente_id debe estar presente (validar en app)
    CONSTRAINT pk_precio_especial PRIMARY KEY (id),
    CONSTRAINT fk_pe_producto FOREIGN KEY (producto_id)
        REFERENCES producto(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_pe_cliente FOREIGN KEY (cliente_id)
        REFERENCES cliente(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_pe_grupo FOREIGN KEY (grupo_cliente_id)
        REFERENCES grupo_cliente(id) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE INDEX idx_pe_producto ON precio_especial(producto_id);
CREATE INDEX idx_pe_cliente  ON precio_especial(cliente_id);
CREATE INDEX idx_pe_grupo    ON precio_especial(grupo_cliente_id);
CREATE INDEX idx_pe_vigencia ON precio_especial(fecha_inicio, fecha_fin);

CREATE TABLE promocion (
    id                 INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    producto_id        INT UNSIGNED     NOT NULL,
    nombre             VARCHAR(150)     NOT NULL,
    descripcion        TEXT                      DEFAULT NULL,
    tipo               ENUM('porcentaje','monto_fijo','precio_especial','2x1','otro')
                                        NOT NULL DEFAULT 'porcentaje',
    valor_descuento    DECIMAL(10,4)             DEFAULT NULL,   -- % o monto según tipo
    precio_promocional DECIMAL(14,4)             DEFAULT NULL,   -- para tipo precio_especial
    cantidad_minima    INT UNSIGNED               DEFAULT 1,
    fecha_inicio       DATE             NOT NULL,
    fecha_fin          DATE                       DEFAULT NULL,
    activa             TINYINT(1)       NOT NULL DEFAULT 1,
    CONSTRAINT pk_promocion PRIMARY KEY (id),
    CONSTRAINT fk_promo_producto FOREIGN KEY (producto_id)
        REFERENCES producto(id) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE INDEX idx_promo_producto ON promocion(producto_id);
CREATE INDEX idx_promo_vigencia ON promocion(fecha_inicio, fecha_fin, activa);


-- ============================================================
-- BLOQUE 4: INVENTARIO
-- ============================================================

CREATE TABLE stock (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    bodega_id           INT UNSIGNED    NOT NULL,
    producto_id         INT UNSIGNED    NOT NULL,
    cantidad            DECIMAL(14,4)   NOT NULL DEFAULT 0,
    cantidad_reservada  DECIMAL(14,4)   NOT NULL DEFAULT 0,  -- reservado por pedidos pendientes
    cantidad_disponible DECIMAL(14,4)   GENERATED ALWAYS AS
                        (cantidad - cantidad_reservada) VIRTUAL,
    fecha_actualizacion DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_stock PRIMARY KEY (id),
    CONSTRAINT uq_stock_bodega_prod UNIQUE (bodega_id, producto_id),
    CONSTRAINT fk_stock_bodega FOREIGN KEY (bodega_id)
        REFERENCES bodega(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_stock_producto FOREIGN KEY (producto_id)
        REFERENCES producto(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_stock_producto ON stock(producto_id);

CREATE TABLE movimiento_stock (
    id               BIGINT UNSIGNED    NOT NULL AUTO_INCREMENT,
    bodega_id        INT UNSIGNED       NOT NULL,
    producto_id      INT UNSIGNED       NOT NULL,
    tipo             ENUM('entrada','salida','traslado_entrada','traslado_salida',
                         'ajuste_positivo','ajuste_negativo','reserva','liberacion')
                                        NOT NULL,
    cantidad         DECIMAL(14,4)      NOT NULL,
    stock_resultante DECIMAL(14,4)      NOT NULL,
    referencia_tipo  VARCHAR(50)                 DEFAULT NULL,   -- 'pedido','traslado','ajuste'
    referencia_id    INT UNSIGNED                DEFAULT NULL,
    usuario_id       INT UNSIGNED                DEFAULT NULL,   -- FK a tabla usuarios (futura)
    notas            TEXT                        DEFAULT NULL,
    fecha            DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_mov_stock PRIMARY KEY (id),
    CONSTRAINT fk_mov_bodega FOREIGN KEY (bodega_id)
        REFERENCES bodega(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_mov_producto FOREIGN KEY (producto_id)
        REFERENCES producto(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_mov_bodega     ON movimiento_stock(bodega_id);
CREATE INDEX idx_mov_producto   ON movimiento_stock(producto_id);
CREATE INDEX idx_mov_fecha      ON movimiento_stock(fecha);
CREATE INDEX idx_mov_referencia ON movimiento_stock(referencia_tipo, referencia_id);


-- ============================================================
-- BLOQUE 5: TRANSPORTE
-- ============================================================

CREATE TABLE conductor (
    id            INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(200)        NOT NULL,
    num_licencia  VARCHAR(50)         NOT NULL,
    tipo_licencia VARCHAR(20)                  DEFAULT NULL,
    telefono      VARCHAR(30)                  DEFAULT NULL,
    email         VARCHAR(150)                 DEFAULT NULL,
    activo        TINYINT(1)          NOT NULL DEFAULT 1,
    CONSTRAINT pk_conductor PRIMARY KEY (id),
    CONSTRAINT uq_conductor_licencia UNIQUE (num_licencia)
);

CREATE TABLE camion (
    id           INT UNSIGNED         NOT NULL AUTO_INCREMENT,
    patente      VARCHAR(20)          NOT NULL,
    marca        VARCHAR(80)                   DEFAULT NULL,
    modelo       VARCHAR(80)                   DEFAULT NULL,
    anio         YEAR                          DEFAULT NULL,
    capacidad_kg DECIMAL(10,2)                 DEFAULT NULL,
    capacidad_m3 DECIMAL(8,2)                  DEFAULT NULL,
    sucursal_id  INT UNSIGNED                  DEFAULT NULL,   -- base del camión
    activo       TINYINT(1)           NOT NULL DEFAULT 1,
    CONSTRAINT pk_camion PRIMARY KEY (id),
    CONSTRAINT uq_camion_patente UNIQUE (patente),
    CONSTRAINT fk_camion_sucursal FOREIGN KEY (sucursal_id)
        REFERENCES sucursal(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX idx_camion_sucursal ON camion(sucursal_id);

CREATE TABLE ruta (
    id                  INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nombre              VARCHAR(150)    NOT NULL,
    ciudad_origen_id    INT UNSIGNED             DEFAULT NULL,
    ciudad_destino_id   INT UNSIGNED             DEFAULT NULL,
    distancia_km        DECIMAL(8,2)             DEFAULT NULL,
    tiempo_estimado_min INT UNSIGNED             DEFAULT NULL,
    activa              TINYINT(1)      NOT NULL DEFAULT 1,
    CONSTRAINT pk_ruta PRIMARY KEY (id),
    CONSTRAINT fk_ruta_origen  FOREIGN KEY (ciudad_origen_id)
        REFERENCES ciudad(id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_ruta_destino FOREIGN KEY (ciudad_destino_id)
        REFERENCES ciudad(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX idx_ruta_origen  ON ruta(ciudad_origen_id);
CREATE INDEX idx_ruta_destino ON ruta(ciudad_destino_id);

CREATE TABLE recorrido (
    id           INT UNSIGNED         NOT NULL AUTO_INCREMENT,
    camion_id    INT UNSIGNED         NOT NULL,
    conductor_id INT UNSIGNED         NOT NULL,
    ruta_id      INT UNSIGNED                  DEFAULT NULL,
    fecha_salida DATETIME                       DEFAULT NULL,
    fecha_llegada DATETIME                      DEFAULT NULL,
    km_inicial   DECIMAL(10,2)                  DEFAULT NULL,
    km_final     DECIMAL(10,2)                  DEFAULT NULL,
    estado       ENUM('programado','en_curso','completado','cancelado')
                                      NOT NULL DEFAULT 'programado',
    notas        TEXT                           DEFAULT NULL,
    CONSTRAINT pk_recorrido PRIMARY KEY (id),
    CONSTRAINT fk_recorrido_camion FOREIGN KEY (camion_id)
        REFERENCES camion(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_recorrido_conductor FOREIGN KEY (conductor_id)
        REFERENCES conductor(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_recorrido_ruta FOREIGN KEY (ruta_id)
        REFERENCES ruta(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX idx_recorrido_camion    ON recorrido(camion_id);
CREATE INDEX idx_recorrido_conductor ON recorrido(conductor_id);
CREATE INDEX idx_recorrido_estado    ON recorrido(estado);
CREATE INDEX idx_recorrido_fecha     ON recorrido(fecha_salida);

CREATE TABLE parada_recorrido (
    id                   INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    recorrido_id         INT UNSIGNED   NOT NULL,
    orden                SMALLINT UNSIGNED NOT NULL,
    direccion_entrega_id INT UNSIGNED            DEFAULT NULL,   -- entrega a domicilio
    sucursal_id          INT UNSIGNED            DEFAULT NULL,   -- recogida en sucursal
    latitud              DECIMAL(10,7)           DEFAULT NULL,
    longitud             DECIMAL(10,7)           DEFAULT NULL,
    hora_estimada        DATETIME                DEFAULT NULL,
    hora_llegada         DATETIME                DEFAULT NULL,
    hora_salida          DATETIME                DEFAULT NULL,
    estado               ENUM('pendiente','en_camino','completada','no_entregada')
                                        NOT NULL DEFAULT 'pendiente',
    notas                TEXT                    DEFAULT NULL,
    CONSTRAINT pk_parada PRIMARY KEY (id),
    CONSTRAINT fk_parada_recorrido FOREIGN KEY (recorrido_id)
        REFERENCES recorrido(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_parada_dir FOREIGN KEY (direccion_entrega_id)
        REFERENCES direccion_entrega(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_parada_sucursal FOREIGN KEY (sucursal_id)
        REFERENCES sucursal(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_parada_recorrido ON parada_recorrido(recorrido_id);
CREATE INDEX idx_parada_orden     ON parada_recorrido(recorrido_id, orden);


-- ============================================================
-- BLOQUE 6: PEDIDOS, ENTREGAS Y FACTURACIÓN
-- ============================================================

CREATE TABLE pedido (
    id             INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    cliente_id     INT UNSIGNED        NOT NULL,
    sucursal_id    INT UNSIGNED        NOT NULL,   -- sucursal que procesa el pedido
    numero_pedido  VARCHAR(30)         NOT NULL,
    fecha_pedido   DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_requerida DATE                         DEFAULT NULL,
    estado         ENUM('borrador','confirmado','en_preparacion',
                        'listo','entregado','cancelado','anulado')
                                       NOT NULL DEFAULT 'borrador',
    moneda         CHAR(3)             NOT NULL DEFAULT 'USD',
    subtotal       DECIMAL(14,2)       NOT NULL DEFAULT 0,
    descuento_total DECIMAL(14,2)      NOT NULL DEFAULT 0,
    impuesto_total DECIMAL(14,2)       NOT NULL DEFAULT 0,
    total          DECIMAL(14,2)       NOT NULL DEFAULT 0,
    notas          TEXT                         DEFAULT NULL,
    CONSTRAINT pk_pedido PRIMARY KEY (id),
    CONSTRAINT uq_pedido_numero UNIQUE (numero_pedido),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id)
        REFERENCES cliente(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_sucursal FOREIGN KEY (sucursal_id)
        REFERENCES sucursal(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_pedido_cliente  ON pedido(cliente_id);
CREATE INDEX idx_pedido_sucursal ON pedido(sucursal_id);
CREATE INDEX idx_pedido_estado   ON pedido(estado);
CREATE INDEX idx_pedido_fecha    ON pedido(fecha_pedido);

CREATE TABLE linea_pedido (
    id              INT UNSIGNED        NOT NULL AUTO_INCREMENT,
    pedido_id       INT UNSIGNED        NOT NULL,
    producto_id     INT UNSIGNED        NOT NULL,
    bodega_id       INT UNSIGNED        NOT NULL,   -- desde qué bodega se despacha
    promocion_id    INT UNSIGNED                 DEFAULT NULL,
    cantidad        DECIMAL(14,4)       NOT NULL,
    precio_unitario DECIMAL(14,4)       NOT NULL,  -- precio histórico al momento de venta
    descuento_pct   DECIMAL(6,4)        NOT NULL DEFAULT 0,
    descuento_monto DECIMAL(14,4)       NOT NULL DEFAULT 0,
    subtotal        DECIMAL(14,4)       NOT NULL,
    CONSTRAINT pk_linea_pedido PRIMARY KEY (id),
    CONSTRAINT fk_lp_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedido(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_lp_producto FOREIGN KEY (producto_id)
        REFERENCES producto(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_lp_bodega FOREIGN KEY (bodega_id)
        REFERENCES bodega(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_lp_promocion FOREIGN KEY (promocion_id)
        REFERENCES promocion(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX idx_lp_pedido   ON linea_pedido(pedido_id);
CREATE INDEX idx_lp_producto ON linea_pedido(producto_id);
CREATE INDEX idx_lp_bodega   ON linea_pedido(bodega_id);

CREATE TABLE entrega (
    id                   INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    pedido_id            INT UNSIGNED   NOT NULL,
    tipo                 ENUM('retiro_local','envio_domicilio','envio_camion') NOT NULL,
    -- Para retiro en sucursal:
    sucursal_retiro_id   INT UNSIGNED            DEFAULT NULL,
    -- Para envío en camión:
    recorrido_id         INT UNSIGNED            DEFAULT NULL,
    parada_id            INT UNSIGNED            DEFAULT NULL,
    -- Para envío a domicilio directo:
    direccion_entrega_id INT UNSIGNED            DEFAULT NULL,
    fecha_estimada       DATETIME                DEFAULT NULL,
    fecha_real           DATETIME                DEFAULT NULL,
    estado               ENUM('pendiente','en_camino','entregada',
                              'no_entregada','devuelta') NOT NULL DEFAULT 'pendiente',
    receptor_nombre      VARCHAR(200)            DEFAULT NULL,
    notas                TEXT                    DEFAULT NULL,
    CONSTRAINT pk_entrega PRIMARY KEY (id),
    CONSTRAINT uq_entrega_pedido UNIQUE (pedido_id),   -- 1 entrega por pedido
    CONSTRAINT fk_entrega_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedido(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_entrega_sucursal FOREIGN KEY (sucursal_retiro_id)
        REFERENCES sucursal(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_entrega_recorrido FOREIGN KEY (recorrido_id)
        REFERENCES recorrido(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_entrega_parada FOREIGN KEY (parada_id)
        REFERENCES parada_recorrido(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_entrega_dir FOREIGN KEY (direccion_entrega_id)
        REFERENCES direccion_entrega(id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX idx_entrega_recorrido ON entrega(recorrido_id);
CREATE INDEX idx_entrega_estado    ON entrega(estado);

CREATE TABLE factura (
    id                INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    pedido_id         INT UNSIGNED     NOT NULL,
    entrega_id        INT UNSIGNED              DEFAULT NULL,
    numero_fiscal     VARCHAR(60)      NOT NULL,
    serie             VARCHAR(10)               DEFAULT NULL,
    fecha_emision     DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE                       DEFAULT NULL,
    moneda            CHAR(3)          NOT NULL DEFAULT 'USD',
    subtotal          DECIMAL(14,2)    NOT NULL,
    descuento_total   DECIMAL(14,2)    NOT NULL DEFAULT 0,
    base_imponible    DECIMAL(14,2)    NOT NULL,
    impuesto_pct      DECIMAL(6,4)     NOT NULL DEFAULT 0,
    impuesto_monto    DECIMAL(14,2)    NOT NULL DEFAULT 0,
    total             DECIMAL(14,2)    NOT NULL,
    estado            ENUM('emitida','pagada','anulada','vencida') NOT NULL DEFAULT 'emitida',
    notas             TEXT                       DEFAULT NULL,
    CONSTRAINT pk_factura PRIMARY KEY (id),
    CONSTRAINT uq_factura_numero UNIQUE (numero_fiscal, serie),
    CONSTRAINT uq_factura_pedido UNIQUE (pedido_id),   -- 1 factura por pedido
    CONSTRAINT fk_factura_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedido(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_factura_entrega FOREIGN KEY (entrega_id)
        REFERENCES entrega(id) ON UPDATE CASCADE ON DELETE SET NULL
);
CREATE INDEX idx_factura_fecha  ON factura(fecha_emision);
CREATE INDEX idx_factura_estado ON factura(estado);