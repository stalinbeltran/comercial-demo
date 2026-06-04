import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from api.data.catalogo import load as load_catalogo

CATALOGO_JSON = Path(__file__).parent.parent / "data" / "catalogo.json"

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
            creates  = r.get("creates") or {}
            db_keys  = r.get("db_keys") or {}
            chips = "".join(
                f'<span class="tbl-chip">{t}'
                + (f'<span class="db-badge db-{db_keys[t]}">{db_keys[t]}</span>' if t in db_keys else "")
                + "</span>"
                for t in creates
            )
            tables_td = f'<div class="tables">{chips}</div>' if chips else '<span style="color:#dfe6e9">—</span>'
            filas += (
                f'<tr class="{r["estado"]}">'
                f'<td class="num">{r["numero"]}</td>'
                f'<td>{r["nombre"]}</td>'
                f'<td>{_badge(r["estado"], r["endpoint"])}</td>'
                f'<td>{tables_td}</td>'
                f'</tr>'
            )
        modulos_html += f"""
        <div class="modulo">
            <h2>{mod["modulo_id"]}. {mod["modulo"]}</h2>
            <table>
                <thead><tr><th>#</th><th>Reporte</th><th>Estado</th><th>Tablas</th></tr></thead>
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
  .tables {{ display: flex; flex-wrap: wrap; gap: .3rem; }}
  .tbl-chip {{ font-family: monospace; font-size: .72rem; background: #f0f3f8;
               color: #636e72; border-radius: 4px; padding: .15rem .45rem;
               white-space: nowrap; display:inline-flex; align-items:center; gap:.25rem; }}
  .db-badge {{ font-size:.65rem; font-weight:700; padding:.05rem .3rem;
               border-radius:3px; font-family:sans-serif; }}
  .db-main    {{ background:#dbeafe; color:#1e40af; }}
  .db-agg     {{ background:#d1fae5; color:#065f46; }}
  .db-desnorm {{ background:#ede9fe; color:#5b21b6; }}
  .btn-detect {{ margin-top:.75rem; padding:.35rem .9rem; background:#0984e3;
                 color:#fff; border:none; border-radius:6px; font-size:.82rem;
                 font-weight:600; cursor:pointer; }}
  .btn-detect:hover {{ opacity:.85; }}
  .btn-detect:disabled {{ opacity:.5; cursor:not-allowed; }}
</style>
</head>
<body>
<header>
  <h1>Catálogo de Reportes — ERP Comercial</h1>
  <p>Inventario completo de reportes ejecutivos por módulo.</p>
  <div class="progress-bar"><div style="width:{pct}%"></div></div>
  <p class="progress-label">{implementados} de {total} reportes implementados ({pct}%)</p>
  <button class="btn-detect" id="btnDetect" onclick="detectDbs()">Detectar DBs</button>
</header>
<script>
async function detectDbs() {{
  const btn = document.getElementById('btnDetect');
  btn.disabled = true; btn.textContent = 'Consultando…';
  try {{
    const res  = await fetch('/catalogo/detect-dbs', {{ method: 'POST' }});
    const data = await res.json();
    btn.textContent = `✓ ${{data.updated}} reporte(s) actualizados`;
    setTimeout(() => location.reload(), 900);
  }} catch(e) {{
    btn.textContent = 'Error — reintentá';
    btn.disabled = false;
  }}
}}
</script>
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


@router.post(
    "/catalogo/detect-dbs",
    summary="Detectar DB de cada tabla",
    description=(
        "Consulta INFORMATION_SCHEMA en las tres bases del proyecto para determinar "
        "en qué DB existe cada tabla del catálogo. Guarda el resultado en `catalogo.json`."
    ),
)
def catalogo_detect_dbs():
    from utils.schema_reader import detect_table_dbs

    raw = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))

    all_tables = {
        tabla
        for modulo in raw["modulos"]
        for reporte in modulo["reportes"]
        for tabla in reporte.get("creates", {})
    }

    db_keys = detect_table_dbs(list(all_tables))

    updated = 0
    for modulo in raw["modulos"]:
        for reporte in modulo["reportes"]:
            creates = reporte.get("creates", {})
            if not creates:
                continue
            reporte_keys = {t: db_keys[t] for t in creates if t in db_keys}
            if reporte_keys:
                reporte["db_keys"] = reporte_keys
                updated += 1

    CATALOGO_JSON.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {"updated": updated, "db_keys": db_keys}


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
