# Chat: 9c6db7fa-5397-4717-aee0-ae5223b4fbeb
**Proyecto:** c--Desarrollo-interferometer-fringe-analysis  
**Fecha:** 2026-06-02  
**Archivo:** 9c6db7fa-5397-4717-aee0-ae5223b4fbeb.jsonl  

---

### **Usuario** [2026-05-31T17:16:07]

busca en esta carpeta archivos py que no se estan usando

---

### **Asistente** [2026-05-31T17:16:11]

Voy a explorar la estructura del proyecto y buscar qué archivos .py existen y cuáles se importan entre sí.

---

### **Asistente** [2026-05-31T17:16:11]

[Tool: Glob]

---

### **Asistente** [2026-05-31T17:16:21]

[Tool: Agent]

---

### **Asistente** [2026-05-31T17:17:28]

El resultado es interesante: este proyecto tiene un patrón de **scripts independientes**, no de módulos reutilizables. Solo 4 archivos se importan entre sí:

---

### Archivos usados como módulos (importados por otros)
| Archivo | Importado por |
|---|---|
| [globals.py](globals.py) | 22+ archivos |
| [phaseProcessing.py](phaseProcessing.py) | 6 archivos |
| [histogram.py](histogram.py) | 5 archivos |
| [publisher.py](publisher.py) | `captureVideo.py`, `photoSaving.py` |

---

### Los otros 44 archivos no son importados por nadie

Eso no significa necesariamente que estén "sin usar" — son **scripts de entrada** que se ejecutan directamente (`python getCSV.py`, etc.). Sin embargo, puede haber algunos que ya no se usen en ningún flujo de trabajo.

Para identificar cuáles podrían estar realmente obsoletos, ¿quieres que revise si alguno de esos scripts tiene funcionalidad duplicada o si hay algún grupo en particular que sospechas que ya no se usa?

---

