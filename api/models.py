from pydantic import BaseModel, Field
from typing import Optional


# ─── COMUNES ──────────────────────────────────────────────────────────────────

class FiltrosFecha(BaseModel):
    fecha_desde: str = Field(description="Inicio del período aplicado (YYYY-MM-DD)")
    fecha_hasta: str = Field(description="Fin del período aplicado (YYYY-MM-DD)")
    sucursal_id: Optional[int] = Field(
        default=None,
        description="ID de sucursal filtrada. null = todas las sucursales",
    )


# ─── REPORTE: VENTAS POR CATEGORÍA ────────────────────────────────────────────

class VentaProductoItem(BaseModel):
    categoria:         Optional[str]   = Field(description="Categoría raíz del producto")
    subcategoria:      Optional[str]   = Field(description="Subcategoría. null si el producto está en la raíz")
    sku:               str             = Field(description="Código SKU del producto")
    producto:          str             = Field(description="Nombre del producto")
    unidades_vendidas: float           = Field(description="Total de unidades vendidas en el período")
    precio_promedio:   float           = Field(description="Precio unitario promedio de venta")
    total_descuentos:  float           = Field(description="Suma de descuentos aplicados en el período")
    ingresos_netos:    float           = Field(description="Subtotal neto (sin impuestos) del período")
    num_pedidos:       float           = Field(description="Cantidad de pedidos distintos que incluyen el producto")


class ResumenVentasCategoria(BaseModel):
    total_registros: int   = Field(description="Cantidad de productos en el resultado")
    total_ingresos:  float = Field(description="Suma de ingresos_netos de todos los productos")
    total_unidades:  float = Field(description="Suma de unidades_vendidas de todos los productos")


class RespuestaVentasCategoria(BaseModel):
    filtros: FiltrosFecha
    resumen: ResumenVentasCategoria
    datos:   list[VentaProductoItem]


# ─── REPORTE 1.1: RESUMEN DE VENTAS CONSOLIDADO ───────────────────────────────

class VentasConsolidadoItem(BaseModel):
    sucursal_id:      int            = Field(description="ID de sucursal. 0 = total de todas")
    sucursal_nombre:  Optional[str]  = Field(description="Nombre de la sucursal. null si es total global")
    pais_nombre:      Optional[str]  = Field(description="País de la sucursal. null si es total global")
    total_ventas:     float          = Field(description="Suma de subtotales de líneas de pedido (excluye cancelados/anulados)")
    total_pedidos:    int            = Field(description="Cantidad de pedidos distintos en el período")
    clientes_activos: int            = Field(description="Cantidad de clientes distintos que realizaron pedidos")


class ResumenVentasConsolidado(BaseModel):
    total_registros:  int   = Field(description="Cantidad de filas en el resultado")
    total_ventas:     float = Field(description="Suma global de total_ventas")
    total_pedidos:    int   = Field(description="Suma global de total_pedidos")
    clientes_activos: int   = Field(description="Suma global de clientes_activos")


class RespuestaVentasConsolidado(BaseModel):
    filtros: FiltrosFecha
    resumen: ResumenVentasConsolidado
    datos:   list[VentasConsolidadoItem]
