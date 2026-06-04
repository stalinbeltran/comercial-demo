import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Body
from fastapi.responses import FileResponse, HTMLResponse

ROOT = Path(__file__).parent.parent.parent
SCAN_DIRS = ["api", "reportes", "scripts", "utils"]
OUTPUT_FILE = ROOT / "output" / "sql_extracted.json"

router = APIRouter(tags=["SQL Explorer"])


def _get_files() -> dict[str, list[str]]:
    from utils.helpers import walk_files

    groups: dict[str, list[str]] = {}
    for folder in SCAN_DIRS:
        path = ROOT / folder
        if not path.is_dir():
            continue
        files = [
            str(f.relative_to(ROOT)).replace("\\", "/")
            for f in walk_files(path, ".py")
            if "__pycache__" not in str(f)
        ]
        if files:
            groups[folder] = files
    return groups


def _build_html() -> str:
    groups = _get_files()
    total = sum(len(v) for v in groups.values())

    # Cargar datos ya extraídos para marcar archivos y pre-poblar el panel
    if OUTPUT_FILE.exists():
        try:
            extracted = json.loads(OUTPUT_FILE.read_text(encoding="utf-8")).get("files", {})
        except Exception:
            extracted = {}
    else:
        extracted = {}
    extracted_js = json.dumps(extracted, ensure_ascii=False)

    groups_html = ""
    for folder, files in groups.items():
        items = "".join(
            f"""<li data-has-data="{'true' if f in extracted else 'false'}">
                  <label title="{f}">
                    <input type="checkbox" class="file-cb" value="{f}">
                    <span class="fname">{Path(f).name}</span>
                    <span class="fpath">{f}</span>
                  </label>
                </li>"""
            for f in files
        )
        groups_html += f"""
        <div class="group">
          <div class="group-header">
            <label class="group-label">
              <input type="checkbox" class="group-cb"> {folder}/
            </label>
            <span class="group-count">{len(files)} archivos</span>
          </div>
          <ul>{items}</ul>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SQL Explorer — ERP Comercial</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
       background:#f5f6fa;color:#2d3436;padding:2rem}}
  header{{max-width:960px;margin:0 auto 1.5rem}}
  header h1{{font-size:1.6rem;font-weight:700;margin-bottom:.25rem}}
  header p{{color:#636e72;font-size:.95rem}}
  .layout{{display:flex;gap:0;align-items:start}}
  #leftPanel{{width:340px;min-width:180px;max-width:680px;flex-shrink:0}}
  .resizer{{width:10px;flex-shrink:0;cursor:col-resize;position:relative;
            align-self:stretch;display:flex;align-items:center;justify-content:center}}
  .resizer::after{{content:"";display:block;width:3px;height:40px;
                   border-radius:2px;background:#e0e0e0;transition:background .15s}}
  .resizer:hover::after,.resizer.dragging::after{{background:#0984e3}}
  .right-panel{{flex:1;min-width:0}}
  .card{{background:#fff;border-radius:10px;padding:1.25rem;
         box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .panel-header{{display:flex;justify-content:space-between;
                 align-items:center;margin-bottom:.75rem}}
  .panel-header h2{{font-size:1rem;font-weight:600}}
  .sel-btns button{{background:none;border:none;color:#0984e3;
                    cursor:pointer;font-size:.82rem;padding:0 4px}}
  .sel-btns button:hover{{text-decoration:underline}}
  .file-list{{max-height:540px;overflow-y:auto}}
  .group{{margin-bottom:.5rem}}
  .group-header{{display:flex;justify-content:space-between;
                 align-items:center;padding:.35rem .5rem;
                 background:#f0f3f8;border-radius:6px;margin-bottom:2px}}
  .group-label{{font-weight:600;font-size:.85rem;cursor:pointer;
                display:flex;align-items:center;gap:.4rem}}
  .group-count{{font-size:.75rem;color:#b2bec3}}
  ul{{list-style:none;padding-left:.5rem}}
  li label{{display:flex;align-items:baseline;gap:.4rem;padding:.3rem .5rem;
            border-radius:4px;cursor:pointer;font-size:.85rem}}
  li label:hover{{background:#f8f9fa}}
  .fname{{font-weight:500;white-space:nowrap}}
  .fpath{{color:#b2bec3;font-size:.75rem;font-family:monospace;
          overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  input[type=checkbox]{{accent-color:#0984e3;flex-shrink:0}}
  li[data-has-data="true"] .fname::after{{content:"";display:inline-block;
    width:7px;height:7px;border-radius:50%;background:#00b894;
    margin-left:5px;vertical-align:middle;}}
  .result-ts{{font-size:.72rem;color:#b2bec3;font-style:italic;margin-left:.4rem;}}
  .btn{{display:inline-flex;align-items:center;gap:.4rem;padding:.55rem 1.2rem;
        border:none;border-radius:6px;font-size:.9rem;font-weight:600;
        cursor:pointer;transition:opacity .15s}}
  .btn-primary{{background:#0984e3;color:#fff}}
  .btn-primary:disabled{{opacity:.5;cursor:not-allowed}}
  .btn-dl{{background:#00b894;color:#fff;font-size:.82rem;
           padding:.4rem .9rem;margin-left:.5rem}}
  .btn:hover:not(:disabled){{opacity:.85}}
  .actions{{margin-top:1rem;display:flex;align-items:center}}
  .counter{{font-size:.82rem;color:#636e72;margin-left:auto}}
  .results-header{{display:flex;justify-content:space-between;
                   align-items:center;margin-bottom:1rem}}
  .results-header h2{{font-size:1rem;font-weight:600}}
  .empty{{color:#b2bec3;font-size:.9rem;text-align:center;padding:2rem}}
  .file-block{{margin-bottom:1.25rem;border:1px solid #f0f0f0;border-radius:8px;overflow:hidden}}
  .file-block-header{{background:#f8f9fa;padding:.5rem .85rem;
                      font-size:.82rem;font-family:monospace;color:#636e72;
                      display:flex;justify-content:space-between}}
  .file-block-header span{{font-weight:600;color:#2d3436}}
  .no-sql{{padding:.75rem .85rem;font-size:.85rem;color:#b2bec3}}
  .query-block{{padding:.75rem .85rem;border-top:1px solid #f0f0f0}}
  .query-meta{{font-size:.75rem;color:#b2bec3;margin-bottom:.4rem}}
  .query-meta b{{color:#636e72}}
  .query-actions{{display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem}}
  .db-select{{border:1px solid #dfe6e9;border-radius:4px;padding:.2rem .4rem;
              font-size:.78rem;color:#636e72;background:#fff;cursor:pointer}}
  .run-btn{{display:inline-flex;align-items:center;gap:.3rem;padding:.25rem .75rem;
            background:#6c5ce7;color:#fff;border:none;border-radius:4px;
            font-size:.78rem;font-weight:600;cursor:pointer}}
  .run-btn:hover{{opacity:.85}} .run-btn:disabled{{opacity:.5;cursor:not-allowed}}
  .query-result{{margin-top:.6rem}}
  .result-table-wrap{{overflow:auto;max-height:280px;border:1px solid #f0f0f0;border-radius:6px}}
  .result-table{{width:100%;border-collapse:collapse;font-size:.78rem}}
  .result-table th{{position:sticky;top:0;background:#f0f3f8;padding:.35rem .6rem;
                    text-align:left;font-weight:600;color:#636e72;
                    white-space:nowrap;border-bottom:1px solid #dfe6e9}}
  .result-table td{{padding:.35rem .6rem;border-bottom:1px solid #f8f8f8;white-space:nowrap}}
  .result-table tr:last-child td{{border-bottom:none}}
  .result-table td.null{{color:#b2bec3;font-style:italic}}
  .run-error{{padding:.5rem .75rem;background:#fff5f5;border-left:3px solid #ff7675;
              font-size:.82rem;color:#d63031;border-radius:4px}}
  .run-info{{padding:.4rem .75rem;font-size:.82rem;color:#636e72;
             background:#f8f9fa;border-radius:4px}}
  pre{{background:#2d3436;color:#dfe6e9;border-radius:6px;
       padding:.75rem 1rem;font-size:.78rem;overflow-x:auto;
       line-height:1.5;white-space:pre-wrap;word-break:break-word}}
  .spinner{{display:none;width:16px;height:16px;border:2px solid #fff;
            border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite}}
  @keyframes spin{{to{{transform:rotate(360deg)}}}}
  .toast{{position:fixed;bottom:1.5rem;right:1.5rem;background:#2d3436;color:#fff;
          padding:.6rem 1rem;border-radius:8px;font-size:.85rem;
          opacity:0;transition:opacity .3s;pointer-events:none}}
  .toast.show{{opacity:1}}
</style>
</head>
<body>
<header>
  <h1>SQL Explorer</h1>
  <p>Seleccioná los archivos Python del proyecto, extraé sus queries SQL y exportalos a JSON.</p>
</header>

<div class="layout">
  <!-- Panel izquierdo: selector de archivos -->
  <div class="card" id="leftPanel">
    <div class="panel-header">
      <h2>Archivos del proyecto <small style="color:#b2bec3;font-weight:400">({total})</small></h2>
      <div class="sel-btns">
        <button onclick="selectAll(true)">Todos</button>·
        <button onclick="selectAll(false)">Ninguno</button>
      </div>
    </div>
    <div class="file-list">
      {groups_html}
    </div>
    <div class="actions">
      <button class="btn btn-primary" id="btnExtract" onclick="extract()">
        <span class="spinner" id="spinner"></span>
        Extraer SQL
      </button>
      <span class="counter" id="counter">0 seleccionados</span>
    </div>
  </div>

  <div class="resizer" id="resizer"></div>

  <!-- Panel derecho: resultados -->
  <div class="card right-panel">
    <div class="results-header">
      <h2>Queries extraídos</h2>
      <button class="btn btn-dl" id="btnDl" style="display:none"
              onclick="window.location='/sql-explorer/download'">
        ⬇ Descargar JSON
      </button>
    </div>
    <div id="results">
      <p class="empty">Seleccioná archivos y presioná <b>Extraer SQL</b>.</p>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const EXTRACTED = {extracted_js};

const checkboxes = () => document.querySelectorAll('.file-cb');
const groupCbs   = () => document.querySelectorAll('.group-cb');

function updateCounter() {{
  const n = [...checkboxes()].filter(c => c.checked).length;
  document.getElementById('counter').textContent = n + ' seleccionado' + (n===1?'':'s');
  document.getElementById('btnExtract').disabled = n === 0;
  previewSelected();
}}

function previewSelected() {{
  const checked = [...checkboxes()].filter(c => c.checked);
  if (!checked.length) {{
    document.getElementById('results').innerHTML =
      '<p class="empty">Seleccioná archivos y presioná <b>Extraer SQL</b>.</p>';
    return;
  }}
  const items = checked.map(c => {{
    const d = EXTRACTED[c.value];
    return {{ file: c.value, queries: d ? d.queries : [], last_extracted: d ? d.last_extracted : null }};
  }});
  renderResults(items);
}}

function selectAll(v) {{
  checkboxes().forEach(c => c.checked = v);
  groupCbs().forEach(c => c.checked = v);
  updateCounter();
}}

// Checkbox de grupo sincroniza hijos
groupCbs().forEach(gcb => {{
  gcb.addEventListener('change', () => {{
    const ul = gcb.closest('.group').querySelector('ul');
    ul.querySelectorAll('.file-cb').forEach(c => c.checked = gcb.checked);
    updateCounter();
  }});
}});
checkboxes().forEach(c => c.addEventListener('change', updateCounter));
updateCounter();

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}}

async function extract() {{
  const selected = [...checkboxes()].filter(c=>c.checked).map(c=>c.value);
  if (!selected.length) return;

  const btn = document.getElementById('btnExtract');
  const sp  = document.getElementById('spinner');
  btn.disabled = true; sp.style.display = 'block';

  try {{
    const res  = await fetch('/sql-explorer/extract', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{files: selected}}),
    }});
    const data = await res.json();
    // Sincronizar EXTRACTED en memoria y actualizar puntos indicadores
    const ts = new Date().toISOString().slice(0, 19);
    data.results.forEach(r => {{
      EXTRACTED[r.file] = {{ last_extracted: ts, queries: r.queries }};
      const cb = [...checkboxes()].find(c => c.value === r.file);
      if (cb) cb.closest('li').dataset.hasData = 'true';
    }});
    document.getElementById('btnDl').style.display = 'inline-flex';
    const total = data.results.reduce((s,r)=>s+r.queries.length,0);
    showToast(`${{total}} quer${{total===1?'y':'ies'}} extraído${{total===1?'':'s'}} — JSON guardado`);
  }} catch(e) {{
    showToast('Error al extraer: ' + e.message);
  }} finally {{
    btn.disabled = false; sp.style.display = 'none';
    updateCounter();
  }}
}}

function renderResults(results) {{
  const div = document.getElementById('results');
  if (!results.length) {{ div.innerHTML = '<p class="empty">Sin resultados.</p>'; return; }}

  div.innerHTML = results.map(r => {{
    const queries = r.queries.length
      ? r.queries.map(q => `
          <div class="query-block">
            <div class="query-meta">
              línea <b>${{q.line}}</b>
              ${{q.variable ? '&nbsp;|&nbsp; variable <b>'+q.variable+'</b>' : ''}}
            </div>
            <div class="query-actions">
              <select class="db-select">
                <option value="main">main</option>
                <option value="agg">agg</option>
                <option value="desnorm">desnorm</option>
              </select>
              <button class="run-btn" onclick="runQuery(this)">&#9654; Ejecutar</button>
            </div>
            <pre>${{escHtml(q.sql.trim())}}</pre>
            <div class="query-result"></div>
          </div>`).join('')
      : `<div class="no-sql">${{r.last_extracted ? 'Sin queries SQL en este archivo' : 'Aún no extraído'}}</div>`;

    const ts = r.last_extracted
      ? `<span class="result-ts">${{r.last_extracted}}</span>` : '';

    return `<div class="file-block">
      <div class="file-block-header">
        <span>${{r.file}}</span>
        <span style="color:#b2bec3">${{r.queries.length}} quer${{r.queries.length===1?'y':'ies'}}${{ts}}</span>
      </div>
      ${{queries}}
    </div>`;
  }}).join('');
}}

async function runQuery(btn) {{
  const block     = btn.closest('.query-block');
  const sql       = block.querySelector('pre').textContent;
  const db        = block.querySelector('.db-select').value;
  const resultDiv = block.querySelector('.query-result');

  btn.disabled = true; btn.textContent = '…';
  resultDiv.innerHTML = '';

  try {{
    const res  = await fetch('/sql-explorer/run', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{sql, db}}),
    }});
    const data = await res.json();

    if (data.error) {{
      resultDiv.innerHTML = `<div class="run-error">${{escHtml(data.error)}}</div>`;
    }} else if (data.affected_rows !== undefined) {{
      resultDiv.innerHTML = `<div class="run-info">&#10003; ${{data.affected_rows}} fila(s) afectadas</div>`;
    }} else if (!data.rows.length) {{
      resultDiv.innerHTML = '<div class="run-info">(sin resultados)</div>';
    }} else {{
      const heads = data.columns.map(c => `<th>${{escHtml(c)}}</th>`).join('');
      const rows  = data.rows.map(r =>
        '<tr>' + r.map(v => v === null
          ? '<td class="null">NULL</td>'
          : `<td>${{escHtml(String(v))}}</td>`
        ).join('') + '</tr>'
      ).join('');
      resultDiv.innerHTML = `
        <div class="result-table-wrap">
          <table class="result-table">
            <thead><tr>${{heads}}</tr></thead>
            <tbody>${{rows}}</tbody>
          </table>
        </div>
        <div style="font-size:.72rem;color:#b2bec3;margin-top:.3rem;">${{data.rows.length}} fila(s)</div>`;
    }}
  }} catch(e) {{
    resultDiv.innerHTML = `<div class="run-error">${{escHtml(e.message)}}</div>`;
  }} finally {{
    btn.disabled = false; btn.innerHTML = '&#9654; Ejecutar';
  }}
}}

function escHtml(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

// ── Resizer ──────────────────────────────────────────────────────────────────
(function() {{
  const resizer   = document.getElementById('resizer');
  const leftPanel = document.getElementById('leftPanel');
  let dragging = false, startX = 0, startW = 0;

  resizer.addEventListener('mousedown', e => {{
    dragging = true;
    startX = e.clientX;
    startW = leftPanel.getBoundingClientRect().width;
    resizer.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  }});

  document.addEventListener('mousemove', e => {{
    if (!dragging) return;
    const w = Math.min(680, Math.max(180, startW + e.clientX - startX));
    leftPanel.style.width = w + 'px';
  }});

  document.addEventListener('mouseup', () => {{
    if (!dragging) return;
    dragging = false;
    resizer.classList.remove('dragging');
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }});
}})();
</script>
</body>
</html>"""


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.get(
    "/sql-explorer",
    response_class=HTMLResponse,
    summary="SQL Explorer",
    description="Página interactiva para extraer queries SQL de los archivos Python del proyecto.",
    responses={200: {"content": {"text/html": {}}}},
)
def sql_explorer_html():
    return HTMLResponse(content=_build_html())


@router.post(
    "/sql-explorer/extract",
    summary="Extraer SQL de archivos seleccionados",
    description="Recibe una lista de rutas de archivos .py y devuelve los queries SQL encontrados. Guarda el resultado en `output/sql_extracted.json`.",
)
def sql_explorer_extract(payload: dict = Body(...)):
    from utils.sql_extract import extract_sql_strings

    files: list[str] = payload.get("files", [])
    results = []

    for rel_path in files:
        abs_path = (ROOT / rel_path).resolve()
        if not abs_path.is_relative_to(ROOT) or not abs_path.exists() or not abs_path.is_file():
            continue
        try:
            source = abs_path.read_text(encoding="utf-8")
            queries = extract_sql_strings(source)
        except Exception:
            queries = []

        results.append({"file": rel_path, "queries": queries})

    # Cargar acumulado existente o iniciar vacío
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    if OUTPUT_FILE.exists():
        try:
            accumulated = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        except Exception:
            accumulated = {"files": {}}
    else:
        accumulated = {"files": {}}

    # Fusionar: actualizar los archivos de esta extracción, preservar el resto
    ts = datetime.now().isoformat(timespec="seconds")
    for entry in results:
        accumulated["files"][entry["file"]] = {
            "last_extracted": ts,
            "queries": entry["queries"],
        }

    OUTPUT_FILE.write_text(
        json.dumps(accumulated, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {"results": results, "saved_to": str(OUTPUT_FILE.relative_to(ROOT))}


@router.post(
    "/sql-explorer/run",
    summary="Ejecutar un query SQL",
    description="Ejecuta un query SQL contra la base de datos indicada y devuelve los resultados.",
)
def sql_explorer_run(payload: dict = Body(...)):
    from utils.sql_runner import run_query
    import mysql.connector

    sql    = payload.get("sql", "").strip()
    db_key = payload.get("db", "main")

    if not sql:
        return {"error": "El query está vacío"}

    try:
        rows = run_query(sql, db_key)
    except mysql.connector.Error as e:
        return {"error": f"MySQL [{e.errno}]: {e.msg}"}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

    if rows and "affected_rows" in rows[0]:
        return {"affected_rows": rows[0]["affected_rows"]}

    columns = list(rows[0].keys()) if rows else []
    serialized = [
        [str(row[c]) if row[c] is not None else None for c in columns]
        for row in rows
    ]
    return {"columns": columns, "rows": serialized}


@router.get(
    "/sql-explorer/download",
    summary="Descargar JSON con queries extraídos",
    description="Descarga el archivo `output/sql_extracted.json` generado por la última extracción.",
)
def sql_explorer_download():
    if not OUTPUT_FILE.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Aún no se ha realizado ninguna extracción.")
    return FileResponse(
        path=str(OUTPUT_FILE),
        media_type="application/json",
        filename="sql_extracted.json",
    )
