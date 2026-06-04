import json
import os

_JSON_PATH = os.path.join(os.path.dirname(__file__), "catalogo.json")


def load() -> list:
    """Lee el JSON en cada llamada — sin caché, siempre actualizado."""
    with open(_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)["modulos"]


# Alias de compatibilidad para código que ya importa CATALOGO directamente
CATALOGO = load()
