# Chat: e71cf128-8aa7-493c-bb5b-832213bd4108
**Proyecto:** c--Desarrollo-comercial  
**Fecha:** 2026-06-04  
**Archivo:** e71cf128-8aa7-493c-bb5b-832213bd4108.jsonl  

---

### **Usuario** [2026-06-05T00:12:25]

busca el archivo donde se genera sql_extracted.json y además de extraer los queries de los archivos crea y usa una función para obtener las tablas consultadas en cada query. Agrega estas tablas al json, de modo que cada query tenga una lista de las tablas consultadas en él

---

### **Asistente** [2026-06-05T00:12:30]

Buscando el archivo que genera `sql_extracted.json`.

---

### **Asistente** [2026-06-05T00:12:30]

[Tool: Grep]

---

### **Asistente** [2026-06-05T00:12:32]

[Tool: Read]

---

### **Asistente** [2026-06-05T00:12:35]

Ahora veo el archivo `utils/sql_extract.py` que hace la extracción real.

---

### **Asistente** [2026-06-05T00:12:35]

[Tool: Glob]

---

### **Asistente** [2026-06-05T00:12:38]

[Tool: Read]

---

### **Asistente** [2026-06-05T00:12:47]

Veo la estructura completa. Ahora voy a agregar la función `extract_tables_from_sql` en `utils/sql_extract.py` y actualizar `extract_sql_strings` para incluir las tablas en cada query.

---

### **Asistente** [2026-06-05T00:12:47]

[Tool: Grep]

---

### **Asistente** [2026-06-05T00:12:50]

Usaré regex puro ya que `sqlparse` no está en el proyecto.

---

### **Asistente** [2026-06-05T00:13:07]

[Tool: Edit]

---

### **Asistente** [2026-06-05T00:13:12]

Listo. Ahora verifico que el archivo quedó bien:

---

### **Asistente** [2026-06-05T00:13:12]

[Tool: Read]

---

### **Asistente** [2026-06-05T00:13:19]

El cambio quedó correcto. Lo que hice:

**En [utils/sql_extract.py](utils/sql_extract.py):**

1. **Nueva función `extract_tables_from_sql(sql)`** — usa regex para detectar tablas después de `FROM`, `JOIN` (todas las variantes), `UPDATE` e `INSERT INTO`. Filtra palabras reservadas SQL y maneja nombres con backticks y prefijos de schema (`db.tabla` → toma solo `tabla`). Devuelve una lista sin duplicados en orden de aparición.

2. **`extract_sql_strings` actualizado** — ahora incluye el campo `"tables"` en cada entrada del resultado, llamando a `extract_tables_from_sql` sobre el SQL encontrado.

El JSON resultante tendrá esta forma por query:
```json
{
  "line": 42,
  "variable": "sql",
  "sql": "SELECT * FROM pedidos JOIN clientes ON ...",
  "tables": ["pedidos", "clientes"]
}
```

---

