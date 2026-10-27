"""Genera app/natures.csv (las 25 naturalezas, en español) a partir de los CSV de PokéAPI.

Uso (desde la raíz del proyecto):
    1. Descargar en una carpeta vacía, por ejemplo descargas/:
       https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/{natures,nature_names}.csv
    2. python -I scripts/generar_naturalezas.py descargas app
Columnas: id, name, increased, decreased. increased/decreased es la estadística que sube y la que baja
(attack, defense, special-attack, special-defense, speed); en las 5 naturalezas neutras van vacías.
"""
import csv
import sys
from pathlib import Path

ESTADISTICA = {2: "attack", 3: "defense", 4: "special-attack", 5: "special-defense", 6: "speed"}

origen, destino = Path(sys.argv[1]), Path(sys.argv[2])

nombres = {}
with open(origen / "nature_names.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        if r["local_language_id"] == "7":
            nombres[int(r["nature_id"])] = r["name"]

filas = []
with open(origen / "natures.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        i, sube, baja = int(r["id"]), int(r["increased_stat_id"]), int(r["decreased_stat_id"])
        neutra = sube == baja
        filas.append((i, nombres[i], "" if neutra else ESTADISTICA[sube], "" if neutra else ESTADISTICA[baja]))

assert len(filas) == 25, len(filas)
with open(destino / "natures.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "name", "increased", "decreased"])
    w.writerows(sorted(filas))
print(f"naturalezas: {len(filas)}; neutras: {sum(1 for f in filas if not f[2])}")
