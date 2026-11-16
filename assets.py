import base64
from functools import lru_cache
from pathlib import Path

STATIC = Path(__file__).parent / "static"


@lru_cache(maxsize=None)
def svg_uri(folder, name):
    data = (STATIC / folder / f"{name}.svg").read_bytes()
    return "data:image/svg+xml;base64," + base64.b64encode(data).decode()