-- =============================================================
-- BASE DE DATOS: comercial_db
-- Empresa comercial con sucursales, inventario, bodegas,
-- facturación, compras y cuentas por cobrar/pagar.
-- Compatible con MySQL Community 8.0+
-- Codificación: utf8mb4 / utf8mb4_unicode_ci
-- =============================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP DATABASE IF EXISTS comercial_db;
CREATE DATABASE comercial_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE comercial_db;

-- =============================================================
-- MÓDULO: CATÁLOGOS BASE
-- =============================================================

CREATE TABLE paises (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo_iso CHAR(3)      NOT NULL,
    nombre     VARCHAR(100) NOT NULL,
    activo     TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_paises_codigo (codigo_iso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE departamentos (
    id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_pais INT UNSIGNED NOT NULL,
    codigo  VARCHAR(10)  NOT NULL,
    nombre  VARCHAR(100) NOT NULL,
    activo  TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_dep_pais FOREIGN KEY (id_pais) REFERENCES paises (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE municipios (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_departamento INT UNSIGNED NOT NULL,
    codigo          VARCHAR(10)  NOT NULL,
    nombre          VARCHAR(100) NOT NULL,
    activo          TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_mun_dep FOREIGN KEY (id_departamento) REFERENCES departamentos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE unidades_medida (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo      VARCHAR(10)  NOT NULL,
    nombre      VARCHAR(50)  NOT NULL,
    abreviatura VARCHAR(10)  NOT NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_um_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tipos_documento_identidad (
    id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(50)  NOT NULL,
    activo TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tipos_documento_fiscal (
    id               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo           VARCHAR(10)  NOT NULL,
    nombre           VARCHAR(100) NOT NULL,
    genera_movimiento TINYINT(1)  NOT NULL DEFAULT 0,
    tipo_movimiento  ENUM('entrada','salida','neutro') NOT NULL DEFAULT 'neutro',
    activo           TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_tdf_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE impuestos (
    id     INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(50)   NOT NULL,
    tasa   DECIMAL(5,4)  NOT NULL COMMENT '0.12 = 12%',
    activo TINYINT(1)    NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE monedas (
    id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo  CHAR(3)      NOT NULL,
    nombre  VARCHAR(50)  NOT NULL,
    simbolo VARCHAR(5)   NOT NULL,
    activo  TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_mon_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE marcas (
    id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    activo TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE listas_precio (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tipos_movimiento (
    id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(100) NOT NULL,
    tipo         ENUM('entrada','salida','traslado','ajuste') NOT NULL,
    afecta_costo TINYINT(1)   NOT NULL DEFAULT 0,
    activo       TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE formas_pago (
    id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(50)  NOT NULL,
    tipo   ENUM('efectivo','tarjeta','transferencia','cheque','credito') NOT NULL,
    activo TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE roles (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(50)  NOT NULL,
    descripcion VARCHAR(255) NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: EMPRESA Y SUCURSALES
-- =============================================================

CREATE TABLE empresa (
    id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
    razon_social   VARCHAR(200) NOT NULL,
    nit            VARCHAR(20)  NOT NULL,
    direccion      VARCHAR(255) NULL,
    telefono       VARCHAR(20)  NULL,
    email          VARCHAR(150) NULL,
    logo           VARCHAR(500) NULL COMMENT 'Ruta o URL del logo',
    id_moneda_base INT UNSIGNED NOT NULL,
    activo         TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_empresa_nit (nit),
    CONSTRAINT fk_empresa_moneda FOREIGN KEY (id_moneda_base) REFERENCES monedas (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE sucursales (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_empresa  INT UNSIGNED NOT NULL,
    codigo      VARCHAR(10)  NOT NULL,
    nombre      VARCHAR(150) NOT NULL,
    direccion   VARCHAR(255) NULL,
    telefono    VARCHAR(20)  NULL,
    email       VARCHAR(150) NULL,
    id_municipio INT UNSIGNED NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_suc_codigo (codigo),
    CONSTRAINT fk_suc_empresa   FOREIGN KEY (id_empresa)   REFERENCES empresa    (id),
    CONSTRAINT fk_suc_municipio FOREIGN KEY (id_municipio) REFERENCES municipios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE bodegas (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_sucursal INT UNSIGNED NOT NULL,
    codigo      VARCHAR(10)  NOT NULL,
    nombre      VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255) NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_bod_codigo (codigo),
    CONSTRAINT fk_bod_sucursal FOREIGN KEY (id_sucursal) REFERENCES sucursales (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ubicaciones_bodega (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_bodega   INT UNSIGNED NOT NULL,
    codigo      VARCHAR(20)  NOT NULL,
    descripcion VARCHAR(100) NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_ubod_bodega FOREIGN KEY (id_bodega) REFERENCES bodegas (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cuentas_bancarias (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_sucursal   INT UNSIGNED NOT NULL,
    id_moneda     INT UNSIGNED NOT NULL,
    banco         VARCHAR(100) NOT NULL,
    numero_cuenta VARCHAR(50)  NOT NULL,
    nombre_cuenta VARCHAR(150) NOT NULL,
    tipo          ENUM('monetaria','ahorro') NOT NULL DEFAULT 'monetaria',
    activo        TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_cban_sucursal FOREIGN KEY (id_sucursal) REFERENCES sucursales (id),
    CONSTRAINT fk_cban_moneda   FOREIGN KEY (id_moneda)   REFERENCES monedas    (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: PERSONAS Y USUARIOS
-- =============================================================

CREATE TABLE empleados (
    id                    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_sucursal           INT UNSIGNED NOT NULL,
    codigo                VARCHAR(20)  NOT NULL,
    nombres               VARCHAR(100) NOT NULL,
    apellidos             VARCHAR(100) NOT NULL,
    id_tipo_doc_identidad INT UNSIGNED NULL,
    numero_doc            VARCHAR(30)  NULL,
    telefono              VARCHAR(20)  NULL,
    email                 VARCHAR(150) NULL,
    cargo                 VARCHAR(100) NULL,
    fecha_ingreso         DATE         NULL,
    activo                TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_emp_codigo (codigo),
    CONSTRAINT fk_emp_sucursal FOREIGN KEY (id_sucursal)           REFERENCES sucursales              (id),
    CONSTRAINT fk_emp_tipo_doc FOREIGN KEY (id_tipo_doc_identidad) REFERENCES tipos_documento_identidad (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE usuarios (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_empleado   INT UNSIGNED NULL,
    username      VARCHAR(50)  NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email         VARCHAR(150) NOT NULL,
    activo        TINYINT(1)   NOT NULL DEFAULT 1,
    ultimo_acceso DATETIME     NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usr_username (username),
    UNIQUE KEY uq_usr_email    (email),
    CONSTRAINT fk_usr_empleado FOREIGN KEY (id_empleado) REFERENCES empleados (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE usuarios_roles (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_usuario INT UNSIGNED NOT NULL,
    id_rol     INT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usr_rol (id_usuario, id_rol),
    CONSTRAINT fk_usrrol_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
    CONSTRAINT fk_usrrol_rol     FOREIGN KEY (id_rol)     REFERENCES roles    (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE clientes (
    id                    INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    codigo                VARCHAR(20)   NOT NULL,
    tipo                  ENUM('individual','empresa') NOT NULL DEFAULT 'empresa',
    razon_social          VARCHAR(200)  NOT NULL,
    nombre_comercial      VARCHAR(200)  NULL,
    id_tipo_doc_identidad INT UNSIGNED  NULL,
    numero_doc            VARCHAR(30)   NULL,
    telefono              VARCHAR(20)   NULL,
    email                 VARCHAR(150)  NULL,
    id_lista_precio_def   INT UNSIGNED  NULL,
    id_moneda_defecto     INT UNSIGNED  NULL,
    limite_credito        DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    dias_credito          INT UNSIGNED  NOT NULL DEFAULT 0,
    activo                TINYINT(1)    NOT NULL DEFAULT 1,
    created_at            DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cli_codigo (codigo),
    CONSTRAINT fk_cli_tipo_doc   FOREIGN KEY (id_tipo_doc_identidad) REFERENCES tipos_documento_identidad (id),
    CONSTRAINT fk_cli_lista_prec FOREIGN KEY (id_lista_precio_def)   REFERENCES listas_precio             (id),
    CONSTRAINT fk_cli_moneda     FOREIGN KEY (id_moneda_defecto)     REFERENCES monedas                   (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE clientes_direcciones (
    id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_cliente   INT UNSIGNED NOT NULL,
    descripcion  VARCHAR(100) NOT NULL,
    direccion    VARCHAR(255) NOT NULL,
    id_municipio INT UNSIGNED NULL,
    telefono     VARCHAR(20)  NULL,
    es_principal TINYINT(1)   NOT NULL DEFAULT 0,
    activo       TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_cdir_cliente   FOREIGN KEY (id_cliente)  REFERENCES clientes   (id),
    CONSTRAINT fk_cdir_municipio FOREIGN KEY (id_municipio) REFERENCES municipios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE proveedores (
    id                    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo                VARCHAR(20)  NOT NULL,
    razon_social          VARCHAR(200) NOT NULL,
    nombre_comercial      VARCHAR(200) NULL,
    id_tipo_doc_identidad INT UNSIGNED NULL,
    numero_doc            VARCHAR(30)  NULL,
    telefono              VARCHAR(20)  NULL,
    email                 VARCHAR(150) NULL,
    direccion             VARCHAR(255) NULL,
    id_municipio          INT UNSIGNED NULL,
    plazo_pago_dias       INT UNSIGNED NOT NULL DEFAULT 0,
    activo                TINYINT(1)   NOT NULL DEFAULT 1,
    created_at            DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_prov_codigo (codigo),
    CONSTRAINT fk_prov_tipo_doc  FOREIGN KEY (id_tipo_doc_identidad) REFERENCES tipos_documento_identidad (id),
    CONSTRAINT fk_prov_municipio FOREIGN KEY (id_municipio)          REFERENCES municipios                (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE proveedores_contactos (
    id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_proveedor INT UNSIGNED NOT NULL,
    nombre       VARCHAR(150) NOT NULL,
    cargo        VARCHAR(100) NULL,
    telefono     VARCHAR(20)  NULL,
    email        VARCHAR(150) NULL,
    es_principal TINYINT(1)   NOT NULL DEFAULT 0,
    activo       TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    CONSTRAINT fk_pcon_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: CATÁLOGO DE PRODUCTOS
-- =============================================================

CREATE TABLE categorias (
    id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_categoria_padre INT UNSIGNED NULL,
    codigo             VARCHAR(20)  NOT NULL,
    nombre             VARCHAR(100) NOT NULL,
    activo             TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cat_codigo (codigo),
    CONSTRAINT fk_cat_padre FOREIGN KEY (id_categoria_padre) REFERENCES categorias (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE productos (
    id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_categoria       INT UNSIGNED NULL,
    id_marca           INT UNSIGNED NULL,
    id_unidad_medida   INT UNSIGNED NOT NULL,
    codigo             VARCHAR(50)  NOT NULL,
    descripcion        VARCHAR(255) NOT NULL,
    descripcion_larga  TEXT         NULL,
    tipo               ENUM('producto','servicio','kit') NOT NULL DEFAULT 'producto',
    maneja_inventario  TINYINT(1)   NOT NULL DEFAULT 1,
    maneja_lotes       TINYINT(1)   NOT NULL DEFAULT 0,
    maneja_vencimiento TINYINT(1)   NOT NULL DEFAULT 0,
    activo             TINYINT(1)   NOT NULL DEFAULT 1,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_prod_codigo (codigo),
    CONSTRAINT fk_prod_categoria FOREIGN KEY (id_categoria)     REFERENCES categorias     (id),
    CONSTRAINT fk_prod_marca     FOREIGN KEY (id_marca)         REFERENCES marcas          (id),
    CONSTRAINT fk_prod_um        FOREIGN KEY (id_unidad_medida) REFERENCES unidades_medida (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE codigos_barra (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_producto INT UNSIGNED NOT NULL,
    codigo      VARCHAR(100) NOT NULL,
    tipo        VARCHAR(20)  NULL COMMENT 'EAN13, UPC, QR, etc.',
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cb_codigo (codigo),
    CONSTRAINT fk_cb_producto FOREIGN KEY (id_producto) REFERENCES productos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE productos_precios (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_producto     INT UNSIGNED  NOT NULL,
    id_lista_precio INT UNSIGNED  NOT NULL,
    id_moneda       INT UNSIGNED  NOT NULL,
    precio          DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    activo          TINYINT(1)    NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pp_prod_lista (id_producto, id_lista_precio),
    CONSTRAINT fk_pp_producto     FOREIGN KEY (id_producto)     REFERENCES productos     (id),
    CONSTRAINT fk_pp_lista_precio FOREIGN KEY (id_lista_precio) REFERENCES listas_precio (id),
    CONSTRAINT fk_pp_moneda       FOREIGN KEY (id_moneda)       REFERENCES monedas       (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE productos_impuestos (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_producto INT UNSIGNED NOT NULL,
    id_impuesto INT UNSIGNED NOT NULL,
    activo      TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pi_prod_imp (id_producto, id_impuesto),
    CONSTRAINT fk_pi_producto FOREIGN KEY (id_producto) REFERENCES productos (id),
    CONSTRAINT fk_pi_impuesto FOREIGN KEY (id_impuesto) REFERENCES impuestos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: INVENTARIO
-- =============================================================

CREATE TABLE lotes (
    id                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_producto       INT UNSIGNED NOT NULL,
    numero_lote       VARCHAR(50)  NOT NULL,
    fecha_fabricacion DATE         NULL,
    fecha_vencimiento DATE         NULL,
    activo            TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_lote_prod_num (id_producto, numero_lote),
    CONSTRAINT fk_lot_producto FOREIGN KEY (id_producto) REFERENCES productos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE inventario (
    id                 INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_producto        INT UNSIGNED  NOT NULL,
    id_bodega          INT UNSIGNED  NOT NULL,
    id_ubicacion       INT UNSIGNED  NULL,
    id_lote            INT UNSIGNED  NULL,
    cantidad           DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    cantidad_reservada DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    costo_promedio     DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    PRIMARY KEY (id),
    UNIQUE KEY uq_inv_prod_bod_ub_lot (id_producto, id_bodega, id_ubicacion, id_lote),
    CONSTRAINT fk_inv_producto  FOREIGN KEY (id_producto)  REFERENCES productos         (id),
    CONSTRAINT fk_inv_bodega    FOREIGN KEY (id_bodega)    REFERENCES bodegas            (id),
    CONSTRAINT fk_inv_ubicacion FOREIGN KEY (id_ubicacion) REFERENCES ubicaciones_bodega (id),
    CONSTRAINT fk_inv_lote      FOREIGN KEY (id_lote)      REFERENCES lotes              (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE traslados (
    id                INT UNSIGNED NOT NULL AUTO_INCREMENT,
    numero            VARCHAR(20)  NOT NULL,
    id_sucursal       INT UNSIGNED NOT NULL,
    id_bodega_origen  INT UNSIGNED NOT NULL,
    id_bodega_destino INT UNSIGNED NOT NULL,
    fecha             DATE         NOT NULL,
    estado            ENUM('borrador','confirmado','anulado') NOT NULL DEFAULT 'borrador',
    id_usuario        INT UNSIGNED NOT NULL,
    observaciones     TEXT         NULL,
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_tras_numero (numero),
    CONSTRAINT fk_tras_sucursal FOREIGN KEY (id_sucursal)       REFERENCES sucursales (id),
    CONSTRAINT fk_tras_origen   FOREIGN KEY (id_bodega_origen)  REFERENCES bodegas    (id),
    CONSTRAINT fk_tras_destino  FOREIGN KEY (id_bodega_destino) REFERENCES bodegas    (id),
    CONSTRAINT fk_tras_usuario  FOREIGN KEY (id_usuario)        REFERENCES usuarios   (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE traslados_detalle (
    id             INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_traslado    INT UNSIGNED  NOT NULL,
    id_producto    INT UNSIGNED  NOT NULL,
    id_lote        INT UNSIGNED  NULL,
    cantidad       DECIMAL(15,4) NOT NULL,
    costo_unitario DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    PRIMARY KEY (id),
    CONSTRAINT fk_tdet_traslado FOREIGN KEY (id_traslado) REFERENCES traslados (id),
    CONSTRAINT fk_tdet_producto FOREIGN KEY (id_producto) REFERENCES productos  (id),
    CONSTRAINT fk_tdet_lote     FOREIGN KEY (id_lote)     REFERENCES lotes      (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ajustes_inventario (
    id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    numero     VARCHAR(20)  NOT NULL,
    id_bodega  INT UNSIGNED NOT NULL,
    fecha      DATE         NOT NULL,
    tipo       ENUM('entrada','salida','ajuste_fisico') NOT NULL,
    motivo     VARCHAR(255) NULL,
    estado     ENUM('borrador','confirmado','anulado') NOT NULL DEFAULT 'borrador',
    id_usuario INT UNSIGNED NOT NULL,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_ajuste_numero (numero),
    CONSTRAINT fk_aj_bodega  FOREIGN KEY (id_bodega)  REFERENCES bodegas  (id),
    CONSTRAINT fk_aj_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ajustes_inventario_detalle (
    id               INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_ajuste        INT UNSIGNED  NOT NULL,
    id_producto      INT UNSIGNED  NOT NULL,
    id_lote          INT UNSIGNED  NULL,
    cantidad_sistema DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    cantidad_fisica  DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    diferencia       DECIMAL(15,4) GENERATED ALWAYS AS (cantidad_fisica - cantidad_sistema) STORED,
    costo_unitario   DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    PRIMARY KEY (id),
    CONSTRAINT fk_ajdet_ajuste   FOREIGN KEY (id_ajuste)   REFERENCES ajustes_inventario (id),
    CONSTRAINT fk_ajdet_producto FOREIGN KEY (id_producto) REFERENCES productos           (id),
    CONSTRAINT fk_ajdet_lote     FOREIGN KEY (id_lote)     REFERENCES lotes               (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE movimientos_inventario (
    id                 INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_producto        INT UNSIGNED  NOT NULL,
    id_bodega          INT UNSIGNED  NOT NULL,
    id_lote            INT UNSIGNED  NULL,
    id_tipo_movimiento INT UNSIGNED  NOT NULL,
    cantidad           DECIMAL(15,4) NOT NULL,
    costo_unitario     DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    costo_total        DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    documento_tipo     VARCHAR(50)   NULL COMMENT 'factura | recepcion | traslado | ajuste',
    documento_id       INT UNSIGNED  NULL,
    fecha              DATE          NOT NULL,
    id_usuario         INT UNSIGNED  NOT NULL,
    observaciones      VARCHAR(255)  NULL,
    created_at         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_mov_producto FOREIGN KEY (id_producto)        REFERENCES productos        (id),
    CONSTRAINT fk_mov_bodega   FOREIGN KEY (id_bodega)          REFERENCES bodegas          (id),
    CONSTRAINT fk_mov_lote     FOREIGN KEY (id_lote)            REFERENCES lotes            (id),
    CONSTRAINT fk_mov_tipo     FOREIGN KEY (id_tipo_movimiento) REFERENCES tipos_movimiento (id),
    CONSTRAINT fk_mov_usuario  FOREIGN KEY (id_usuario)         REFERENCES usuarios         (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: COMPRAS
-- =============================================================

CREATE TABLE ordenes_compra (
    id                     INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    numero                 VARCHAR(20)   NOT NULL,
    id_proveedor           INT UNSIGNED  NOT NULL,
    id_sucursal            INT UNSIGNED  NOT NULL,
    id_moneda              INT UNSIGNED  NOT NULL,
    fecha                  DATE          NOT NULL,
    fecha_entrega_esperada DATE          NULL,
    estado                 ENUM('borrador','enviada','parcial','recibida','anulada') NOT NULL DEFAULT 'borrador',
    subtotal               DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_impuestos        DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total                  DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    id_usuario             INT UNSIGNED  NOT NULL,
    observaciones          TEXT          NULL,
    created_at             DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_oc_numero (numero),
    CONSTRAINT fk_oc_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores (id),
    CONSTRAINT fk_oc_sucursal  FOREIGN KEY (id_sucursal)  REFERENCES sucursales  (id),
    CONSTRAINT fk_oc_moneda    FOREIGN KEY (id_moneda)    REFERENCES monedas     (id),
    CONSTRAINT fk_oc_usuario   FOREIGN KEY (id_usuario)   REFERENCES usuarios    (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ordenes_compra_detalle (
    id               INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_orden_compra  INT UNSIGNED  NOT NULL,
    id_producto      INT UNSIGNED  NOT NULL,
    id_unidad_medida INT UNSIGNED  NOT NULL,
    cantidad         DECIMAL(15,4) NOT NULL,
    cantidad_recibida DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    precio_unitario  DECIMAL(15,4) NOT NULL,
    subtotal         DECIMAL(15,2) NOT NULL,
    id_impuesto      INT UNSIGNED  NULL,
    impuesto_monto   DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total            DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_ocdet_oc       FOREIGN KEY (id_orden_compra)  REFERENCES ordenes_compra  (id),
    CONSTRAINT fk_ocdet_producto FOREIGN KEY (id_producto)      REFERENCES productos        (id),
    CONSTRAINT fk_ocdet_um       FOREIGN KEY (id_unidad_medida) REFERENCES unidades_medida  (id),
    CONSTRAINT fk_ocdet_impuesto FOREIGN KEY (id_impuesto)      REFERENCES impuestos        (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE recepciones (
    id                   INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    numero               VARCHAR(20)   NOT NULL,
    id_proveedor         INT UNSIGNED  NOT NULL,
    id_bodega            INT UNSIGNED  NOT NULL,
    id_orden_compra      INT UNSIGNED  NULL,
    numero_doc_proveedor VARCHAR(50)   NULL COMMENT 'Número de factura del proveedor',
    fecha                DATE          NOT NULL,
    estado               ENUM('borrador','confirmada','anulada') NOT NULL DEFAULT 'borrador',
    subtotal             DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_impuestos      DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total                DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    id_usuario           INT UNSIGNED  NOT NULL,
    observaciones        TEXT          NULL,
    created_at           DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_rec_numero (numero),
    CONSTRAINT fk_rec_proveedor FOREIGN KEY (id_proveedor)   REFERENCES proveedores    (id),
    CONSTRAINT fk_rec_bodega    FOREIGN KEY (id_bodega)       REFERENCES bodegas        (id),
    CONSTRAINT fk_rec_oc        FOREIGN KEY (id_orden_compra) REFERENCES ordenes_compra (id),
    CONSTRAINT fk_rec_usuario   FOREIGN KEY (id_usuario)      REFERENCES usuarios       (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE recepciones_detalle (
    id             INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_recepcion   INT UNSIGNED  NOT NULL,
    id_producto    INT UNSIGNED  NOT NULL,
    id_lote        INT UNSIGNED  NULL,
    cantidad       DECIMAL(15,4) NOT NULL,
    costo_unitario DECIMAL(15,4) NOT NULL,
    id_impuesto    INT UNSIGNED  NULL,
    impuesto_monto DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    costo_total    DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_rdet_recepcion FOREIGN KEY (id_recepcion) REFERENCES recepciones (id),
    CONSTRAINT fk_rdet_producto  FOREIGN KEY (id_producto)  REFERENCES productos   (id),
    CONSTRAINT fk_rdet_lote      FOREIGN KEY (id_lote)      REFERENCES lotes       (id),
    CONSTRAINT fk_rdet_impuesto  FOREIGN KEY (id_impuesto)  REFERENCES impuestos   (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: VENTAS Y FACTURACIÓN
-- =============================================================

CREATE TABLE cotizaciones (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    numero          VARCHAR(20)   NOT NULL,
    id_cliente      INT UNSIGNED  NOT NULL,
    id_sucursal     INT UNSIGNED  NOT NULL,
    id_lista_precio INT UNSIGNED  NULL,
    id_moneda       INT UNSIGNED  NOT NULL,
    fecha           DATE          NOT NULL,
    fecha_vencimiento DATE        NULL,
    estado          ENUM('borrador','enviada','aprobada','rechazada','vencida','facturada') NOT NULL DEFAULT 'borrador',
    subtotal        DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_impuestos DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    descuento       DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    id_usuario      INT UNSIGNED  NOT NULL,
    observaciones   TEXT          NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_cot_numero (numero),
    CONSTRAINT fk_cot_cliente    FOREIGN KEY (id_cliente)      REFERENCES clientes      (id),
    CONSTRAINT fk_cot_sucursal   FOREIGN KEY (id_sucursal)     REFERENCES sucursales    (id),
    CONSTRAINT fk_cot_lista_prec FOREIGN KEY (id_lista_precio) REFERENCES listas_precio (id),
    CONSTRAINT fk_cot_moneda     FOREIGN KEY (id_moneda)       REFERENCES monedas       (id),
    CONSTRAINT fk_cot_usuario    FOREIGN KEY (id_usuario)      REFERENCES usuarios      (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cotizaciones_detalle (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_cotizacion   INT UNSIGNED  NOT NULL,
    id_producto     INT UNSIGNED  NOT NULL,
    descripcion     VARCHAR(255)  NULL COMMENT 'Override de descripción si se requiere',
    cantidad        DECIMAL(15,4) NOT NULL,
    precio_unitario DECIMAL(15,4) NOT NULL,
    descuento_pct   DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    descuento_monto DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    subtotal        DECIMAL(15,2) NOT NULL,
    id_impuesto     INT UNSIGNED  NULL,
    impuesto_monto  DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_cdet_cotizacion FOREIGN KEY (id_cotizacion) REFERENCES cotizaciones (id),
    CONSTRAINT fk_cdet_producto   FOREIGN KEY (id_producto)   REFERENCES productos    (id),
    CONSTRAINT fk_cdet_impuesto   FOREIGN KEY (id_impuesto)   REFERENCES impuestos    (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pedidos (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    numero          VARCHAR(20)   NOT NULL,
    id_cliente      INT UNSIGNED  NOT NULL,
    id_cotizacion   INT UNSIGNED  NULL,
    id_sucursal     INT UNSIGNED  NOT NULL,
    id_moneda       INT UNSIGNED  NOT NULL,
    fecha           DATE          NOT NULL,
    estado          ENUM('borrador','confirmado','parcial','despachado','anulado') NOT NULL DEFAULT 'borrador',
    subtotal        DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_impuestos DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    descuento       DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    id_usuario      INT UNSIGNED  NOT NULL,
    observaciones   TEXT          NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_ped_numero (numero),
    CONSTRAINT fk_ped_cliente    FOREIGN KEY (id_cliente)    REFERENCES clientes    (id),
    CONSTRAINT fk_ped_cotizacion FOREIGN KEY (id_cotizacion) REFERENCES cotizaciones (id),
    CONSTRAINT fk_ped_sucursal   FOREIGN KEY (id_sucursal)   REFERENCES sucursales  (id),
    CONSTRAINT fk_ped_moneda     FOREIGN KEY (id_moneda)     REFERENCES monedas     (id),
    CONSTRAINT fk_ped_usuario    FOREIGN KEY (id_usuario)    REFERENCES usuarios    (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pedidos_detalle (
    id                  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_pedido           INT UNSIGNED  NOT NULL,
    id_producto         INT UNSIGNED  NOT NULL,
    descripcion         VARCHAR(255)  NULL,
    cantidad            DECIMAL(15,4) NOT NULL,
    cantidad_despachada DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    precio_unitario     DECIMAL(15,4) NOT NULL,
    descuento_pct       DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    descuento_monto     DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    subtotal            DECIMAL(15,2) NOT NULL,
    id_impuesto         INT UNSIGNED  NULL,
    impuesto_monto      DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total               DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_pdet_pedido   FOREIGN KEY (id_pedido)   REFERENCES pedidos   (id),
    CONSTRAINT fk_pdet_producto FOREIGN KEY (id_producto) REFERENCES productos (id),
    CONSTRAINT fk_pdet_impuesto FOREIGN KEY (id_impuesto) REFERENCES impuestos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE facturas (
    id                INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    numero            VARCHAR(20)   NOT NULL,
    serie             VARCHAR(10)   NULL,
    id_cliente        INT UNSIGNED  NOT NULL,
    id_pedido         INT UNSIGNED  NULL,
    id_cotizacion     INT UNSIGNED  NULL,
    id_sucursal       INT UNSIGNED  NOT NULL,
    id_moneda         INT UNSIGNED  NOT NULL,
    id_lista_precio   INT UNSIGNED  NULL,
    fecha             DATE          NOT NULL,
    fecha_vencimiento DATE          NULL,
    estado            ENUM('pendiente','parcial','pagada','anulada') NOT NULL DEFAULT 'pendiente',
    subtotal          DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_impuestos   DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    descuento         DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total             DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    saldo             DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    id_usuario        INT UNSIGNED  NOT NULL,
    observaciones     TEXT          NULL,
    created_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_fac_serie_numero (serie, numero),
    CONSTRAINT fk_fac_cliente    FOREIGN KEY (id_cliente)     REFERENCES clientes      (id),
    CONSTRAINT fk_fac_pedido     FOREIGN KEY (id_pedido)      REFERENCES pedidos       (id),
    CONSTRAINT fk_fac_cotizacion FOREIGN KEY (id_cotizacion)  REFERENCES cotizaciones  (id),
    CONSTRAINT fk_fac_sucursal   FOREIGN KEY (id_sucursal)    REFERENCES sucursales    (id),
    CONSTRAINT fk_fac_moneda     FOREIGN KEY (id_moneda)      REFERENCES monedas       (id),
    CONSTRAINT fk_fac_lista_prec FOREIGN KEY (id_lista_precio) REFERENCES listas_precio (id),
    CONSTRAINT fk_fac_usuario    FOREIGN KEY (id_usuario)     REFERENCES usuarios      (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE facturas_detalle (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_factura      INT UNSIGNED  NOT NULL,
    id_producto     INT UNSIGNED  NOT NULL,
    descripcion     VARCHAR(255)  NULL,
    id_bodega       INT UNSIGNED  NULL,
    cantidad        DECIMAL(15,4) NOT NULL,
    precio_unitario DECIMAL(15,4) NOT NULL,
    descuento_pct   DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    descuento_monto DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    subtotal        DECIMAL(15,2) NOT NULL,
    id_impuesto     INT UNSIGNED  NULL,
    impuesto_monto  DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_fdet_factura  FOREIGN KEY (id_factura)  REFERENCES facturas  (id),
    CONSTRAINT fk_fdet_producto FOREIGN KEY (id_producto) REFERENCES productos (id),
    CONSTRAINT fk_fdet_bodega   FOREIGN KEY (id_bodega)   REFERENCES bodegas   (id),
    CONSTRAINT fk_fdet_impuesto FOREIGN KEY (id_impuesto) REFERENCES impuestos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE notas_credito (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    numero          VARCHAR(20)   NOT NULL,
    serie           VARCHAR(10)   NULL,
    id_factura      INT UNSIGNED  NOT NULL,
    id_cliente      INT UNSIGNED  NOT NULL,
    id_sucursal     INT UNSIGNED  NOT NULL,
    fecha           DATE          NOT NULL,
    motivo          VARCHAR(255)  NULL,
    estado          ENUM('activa','aplicada','anulada') NOT NULL DEFAULT 'activa',
    subtotal        DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_impuestos DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    saldo           DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    id_usuario      INT UNSIGNED  NOT NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_nc_serie_numero (serie, numero),
    CONSTRAINT fk_nc_factura  FOREIGN KEY (id_factura)  REFERENCES facturas   (id),
    CONSTRAINT fk_nc_cliente  FOREIGN KEY (id_cliente)  REFERENCES clientes   (id),
    CONSTRAINT fk_nc_sucursal FOREIGN KEY (id_sucursal) REFERENCES sucursales (id),
    CONSTRAINT fk_nc_usuario  FOREIGN KEY (id_usuario)  REFERENCES usuarios   (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE notas_credito_detalle (
    id              INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_nota_credito INT UNSIGNED  NOT NULL,
    id_producto     INT UNSIGNED  NULL,
    descripcion     VARCHAR(255)  NOT NULL,
    cantidad        DECIMAL(15,4) NOT NULL DEFAULT 1.0000,
    precio_unitario DECIMAL(15,4) NOT NULL DEFAULT 0.0000,
    subtotal        DECIMAL(15,2) NOT NULL,
    id_impuesto     INT UNSIGNED  NULL,
    impuesto_monto  DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total           DECIMAL(15,2) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_ncdet_nc       FOREIGN KEY (id_nota_credito) REFERENCES notas_credito (id),
    CONSTRAINT fk_ncdet_producto FOREIGN KEY (id_producto)     REFERENCES productos     (id),
    CONSTRAINT fk_ncdet_impuesto FOREIGN KEY (id_impuesto)     REFERENCES impuestos     (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
-- MÓDULO: CUENTAS POR COBRAR Y PAGOS
-- =============================================================

CREATE TABLE cxc (
    id                INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_factura        INT UNSIGNED  NOT NULL,
    id_cliente        INT UNSIGNED  NOT NULL,
    fecha_emision     DATE          NOT NULL,
    fecha_vencimiento DATE          NOT NULL,
    monto_total       DECIMAL(15,2) NOT NULL,
    monto_pagado      DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    saldo             DECIMAL(15,2) NOT NULL,
    estado            ENUM('pendiente','parcial','pagada','vencida') NOT NULL DEFAULT 'pendiente',
    PRIMARY KEY (id),
    UNIQUE KEY uq_cxc_factura (id_factura),
    CONSTRAINT fk_cxc_factura FOREIGN KEY (id_factura) REFERENCES facturas (id),
    CONSTRAINT fk_cxc_cliente FOREIGN KEY (id_cliente) REFERENCES clientes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cxc_pagos (
    id            INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_cxc        INT UNSIGNED  NOT NULL,
    id_forma_pago INT UNSIGNED  NOT NULL,
    id_usuario    INT UNSIGNED  NOT NULL,
    fecha         DATE          NOT NULL,
    monto         DECIMAL(15,2) NOT NULL,
    referencia    VARCHAR(100)  NULL,
    observaciones VARCHAR(255)  NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_cxcp_cxc        FOREIGN KEY (id_cxc)        REFERENCES cxc        (id),
    CONSTRAINT fk_cxcp_forma_pago FOREIGN KEY (id_forma_pago) REFERENCES formas_pago (id),
    CONSTRAINT fk_cxcp_usuario    FOREIGN KEY (id_usuario)    REFERENCES usuarios    (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cxp (
    id                       INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_recepcion             INT UNSIGNED  NULL,
    id_proveedor             INT UNSIGNED  NOT NULL,
    numero_factura_proveedor VARCHAR(50)   NULL,
    fecha_emision            DATE          NOT NULL,
    fecha_vencimiento        DATE          NOT NULL,
    monto_total              DECIMAL(15,2) NOT NULL,
    monto_pagado             DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    saldo                    DECIMAL(15,2) NOT NULL,
    estado                   ENUM('pendiente','parcial','pagada','vencida') NOT NULL DEFAULT 'pendiente',
    PRIMARY KEY (id),
    CONSTRAINT fk_cxp_recepcion FOREIGN KEY (id_recepcion) REFERENCES recepciones (id),
    CONSTRAINT fk_cxp_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cxp_pagos (
    id                 INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_cxp             INT UNSIGNED  NOT NULL,
    id_forma_pago      INT UNSIGNED  NOT NULL,
    id_cuenta_bancaria INT UNSIGNED  NULL,
    id_usuario         INT UNSIGNED  NOT NULL,
    fecha              DATE          NOT NULL,
    monto              DECIMAL(15,2) NOT NULL,
    referencia         VARCHAR(100)  NULL,
    observaciones      VARCHAR(255)  NULL,
    created_at         DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_cxpp_cxp         FOREIGN KEY (id_cxp)             REFERENCES cxp               (id),
    CONSTRAINT fk_cxpp_forma_pago  FOREIGN KEY (id_forma_pago)      REFERENCES formas_pago       (id),
    CONSTRAINT fk_cxpp_cuenta_banc FOREIGN KEY (id_cuenta_bancaria) REFERENCES cuentas_bancarias (id),
    CONSTRAINT fk_cxpp_usuario     FOREIGN KEY (id_usuario)         REFERENCES usuarios          (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================
SET FOREIGN_KEY_CHECKS = 1;
