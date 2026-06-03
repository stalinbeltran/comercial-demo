from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.routes import reportes

# Metadatos de tags — agregar una entrada por cada nuevo grupo de endpoints
TAGS = [
    {
        "name": "Reportes",
        "description": (
            "Consultas analíticas pre-agregadas. "
            "Los datos provienen de **comercialaggregated** y se actualizan "
            "con el script `fill_resumen_ventas.py`."
        ),
    },
]

app = FastAPI(
    title="ERP Comercial API",
    description=(
        "API de reportes del ERP Comercial Multi-sucursal — Panamá.\n\n"
        "## Bases de datos\n"
        "| Variable | DB | Uso |\n"
        "|---|---|---|\n"
        "| `DB_NAME` | `comercial` | Datos transaccionales normalizados |\n"
        "| `DB_NAME_DESNORM` | `comercialdesnormalized` | Detalle plano (`linea_venta`) |\n"
        "| `DB_NAME_AGG` | `comercialaggregated` | Agregados (`resumen_ventas`) |\n\n"
        "## Flujo de carga\n"
        "```\n"
        "comercial → fill_reporte_ventas.py → comercialdesnormalized\n"
        "                                              ↓\n"
        "                          fill_resumen_ventas.py\n"
        "                                              ↓\n"
        "                          comercialaggregated  ← esta API\n"
        "```\n\n"
        "## Notas\n"
        "- Los endpoints de reportes aplican defaults de fecha si no se pasan parámetros "
        "(inicio del mes actual → hoy).\n"
        "- `sucursal_id = null` devuelve el agregado de todas las sucursales.\n"
    ),
    version="1.0.0",
    openapi_tags=TAGS,
    contact={
        "name": "ERP Comercial",
        "email": "stalin.beltran2006@gmail.com",
    },
)

app.include_router(reportes.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
