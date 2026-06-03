from fastapi import FastAPI
from api.routes import reportes

app = FastAPI(
    title="ERP Comercial API",
    description="API de reportes — ERP Multi-sucursal Panamá",
    version="1.0.0",
)

app.include_router(reportes.router)


@app.get("/", include_in_schema=False)
def root():
    return {"status": "ok", "docs": "/docs"}
