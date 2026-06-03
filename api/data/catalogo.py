import json
import os

_JSON_PATH = os.path.join(os.path.dirname(__file__), "catalogo.json")


def _load() -> list:
    with open(_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)["modulos"]


# Lista de módulos — leída en cada import (se recarga con uvicorn --reload)
CATALOGO = _load()
