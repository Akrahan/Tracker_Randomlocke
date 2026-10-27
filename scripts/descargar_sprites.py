"""Descarga los dibujos de los Pokémon, les recorta el margen transparente y los guarda en una carpeta.

Se ejecuta dentro de un contenedor de un solo uso (servicio «sprites» de Compose, `make sprites-dev` o
`make sprites-prod`), que escribe en el volumen «sprites»; la web lo monta en /app/static/sprites.

Fuente: repositorio público PokeAPI/sprites.
  - 1-649: pixel art de 5.ª generación (Blanco/Negro).
  - 650-1025: no existen en ese estilo; se usa el dibujo por defecto como respaldo.
Es idempotente: si un fichero ya existe, no se vuelve a descargar.
"""
import io
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

BASE = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
ULTIMA_ESPECIE = 1025
ULTIMA_QUINTA_GEN = 649


def url(numero: int) -> str:
    if numero <= ULTIMA_QUINTA_GEN:
        return f"{BASE}/versions/generation-v/black-white/{numero}.png"
    return f"{BASE}/{numero}.png"


def preparar(numero: int, destino: Path) -> str:
    fichero = destino / f"{numero}.png"
    if fichero.exists():
        return "existía"
    try:
        with urllib.request.urlopen(url(numero), timeout=20) as respuesta:
            datos = respuesta.read()
        imagen = Image.open(io.BytesIO(datos)).convert("RGBA")
        caja = imagen.getchannel("A").getbbox()
        if caja:
            imagen = imagen.crop(caja)
        temporal = fichero.with_suffix(".tmp")
        imagen.save(temporal, "PNG", optimize=True)
        temporal.replace(fichero)
        return "descargado"
    except Exception as error:  # una especie que falle no debe parar el resto
        return f"error: {error}"


def main() -> None:
    destino = Path(sys.argv[1] if len(sys.argv) > 1 else "/sprites")
    destino.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as hilos:
        resultados = list(hilos.map(lambda n: (n, preparar(n, destino)), range(1, ULTIMA_ESPECIE + 1)))

    descargados = sum(r == "descargado" for _, r in resultados)
    existian = sum(r == "existía" for _, r in resultados)
    errores = [(n, r) for n, r in resultados if r.startswith("error")]
    print(f"descargados: {descargados} · ya existían: {existian} · errores: {len(errores)}")
    for numero, motivo in errores[:10]:
        print(f"  {numero}: {motivo}")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
