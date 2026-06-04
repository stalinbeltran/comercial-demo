from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()


def get_env(key: str, default: str = None) -> str:
    return os.getenv(key, default)


def walk_files(folder: str | Path, ext: str) -> list[Path]:
    """Devuelve todos los archivos con la extensión dada dentro de folder (recursivo).

    Args:
        folder: directorio raíz desde donde buscar
        ext:    extensión a filtrar, con o sin punto (ej. ".py" o "py")

    Returns:
        Lista de Path ordenada por ruta relativa al folder.
    """
    root = Path(folder)
    if not root.is_dir():
        raise NotADirectoryError(f"No es un directorio: {root}")

    suffix = ext if ext.startswith(".") else f".{ext}"
    return sorted(root.rglob(f"*{suffix}"))

