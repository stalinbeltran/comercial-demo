from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from api.data.catalogo import load as load_catalogo

router = APIRouter(tags=["Catálogo"])

# ─── HTML ─────────────────────────────────────────────────────────────────────

def _badge(estado: str, endpoint: str | None) -> str:
    if estado == "implementado":
        link = f'<a href="{endpoint}" style="color:inherit;text-decoration:none;">{endpoint}</a>'
        return (
            f'<span class="badge done">&#10003; Implementado</span>'
            f'<span class="ep">{link}</span>'
        )
    return '<span class="badge pending">Pendiente</span>'


def _build_html() -> str:
    CATALOGO = load_catalogo()
    total = sum(len(m["reportes"]) for m in CATALOGO)
    implementados = sum(
        1 for m in CATALOGO for r in m["reportes"] if r["estado"] == "implementado"
    )
    pct = round(implementados / total * 100) if total else 0

    modulos_html = ""
    for mod in CATALOGO:
        filas = ""
        for r in mod["reportes"]:
            filas += (
                f'<tr class="{r["estado"]}">'
                f'<td class="num">{r["numero"]}</td>'
                f'<td>{r["nombre"]}</td>'
                f'<td>{_badge(r["estado"], r["endpoint"])}</td>'
                f'</tr>'
            )
        modulos_html += f"""
        <div class="modulo">
            <h2>{mod["modulo_id"]}. {mod["modulo"]}</h2>
            <table>
                <thead><tr><th>#</th><th>Reporte</th><th>Estado</th></tr></thead>
                <tbody>{filas}</tbody>
            </table>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo de Reportes — ERP Comercial</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background: #f5f6fa; color: #2d3436; padding: 2rem; }}
  header {{ max-width: 900px; margin: 0 auto 2rem; }}
  header h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: .25rem; }}
  header p {{ color: #636e72; font-size: .95rem; }}
  .progress-bar {{ background: #dfe6e9; border-radius: 6px;
                   height: 10px; margin: 1rem 0 .4rem; max-width: 340px; }}
  .progress-bar div {{ background: #00b894; border-radius: 6px; height: 100%; }}
  .progress-label {{ font-size: .85rem; color: #636e72; }}
  .modulo {{ background: #fff; border-radius: 10px; padding: 1.5rem;
             margin: 0 auto 1.5rem; max-width: 900px;
             box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .modulo h2 {{ font-size: 1.05rem; font-weight: 600; margin-bottom: 1rem;
                color: #2d3436; border-left: 4px solid #0984e3;
                padding-left: .6rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
  th {{ text-align: left; padding: .5rem .75rem; background: #f0f3f8;
        font-weight: 600; color: #636e72; font-size: .8rem;
        text-transform: uppercase; letter-spacing: .04em; }}
  td {{ padding: .55rem .75rem; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }}
  tr:last-child td {{ border-bottom: none; }}
  tr.implementado td:first-child {{ font-weight: 600; }}
  td.num {{ color: #b2bec3; font-size: .85rem; width: 50px; }}
  .badge {{ display: inline-block; padding: .2rem .6rem; border-radius: 20px;
            font-size: .78rem; font-weight: 600; }}
  .badge.done {{ background: #d4edda; color: #1a6b32; }}
  .badge.pending {{ background: #f0f0f0; color: #999; }}
  .ep {{ margin-left: .6rem; font-size: .82rem; color: #0984e3;
         font-family: monospace; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<header>
  <h1>Catálogo de Reportes — ERP Comercial</h1>
  <p>Inventario completo de reportes ejecutivos por módulo.</p>
  <div class="progress-bar"><div style="width:{pct}%"></div></div>
  <p class="progress-label">{implementados} de {total} reportes implementados ({pct}%)</p>
</header>
{modulos_html}
</body>
</html>"""


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.get(
    "/catalogo",
    response_class=HTMLResponse,
    summary="Catálogo de reportes",
    description=(
        "Página HTML con el inventario completo de reportes del ERP, "
        "organizados por módulo. Indica cuáles están implementados y el "
        "endpoint correspondiente."
    ),
    responses={200: {"content": {"text/html": {}}}},
)
def catalogo_html():
    return HTMLResponse(content=_build_html())


@router.get(
    "/catalogo/json",
    summary="Catálogo de reportes (JSON)",
    description="Mismos datos que `/catalogo` pero en formato JSON.",
)
def catalogo_json():
    modulos = load_catalogo()
    total = sum(len(m["reportes"]) for m in modulos)
    implementados = sum(
        1 for m in modulos for r in m["reportes"] if r["estado"] == "implementado"
    )
    return {
        "resumen": {"total": total, "implementados": implementados, "pendientes": total - implementados},
        "modulos": modulos,
    }
