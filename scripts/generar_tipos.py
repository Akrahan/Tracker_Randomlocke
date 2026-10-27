"""Genera app/types.csv y app/species_types.csv a partir de los CSV de PokéAPI (solo los 18 tipos de combate, en español).

Uso (desde la raíz del proyecto):
    1. Descargar en una carpeta vacía, por ejemplo descargas/:
       https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/{types,type_names,pokemon_types}.csv
    2. python -I scripts/generar_tipos.py descargas app
Necesita app/species.csv (solo se guardan los tipos de las especies que hay en la lista).
"""
import csv, sys
from pathlib import Path

origen, destino = Path(sys.argv[1]), Path(sys.argv[2])

ident = {}
with open(origen / "types.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        if int(r["id"]) <= 18:
            ident[int(r["id"])] = r["identifier"]

nombres = {}
with open(origen / "type_names.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        if r["local_language_id"] == "7" and int(r["type_id"]) in ident:
            nombres[int(r["type_id"])] = r["name"]
assert len(nombres) == 18, nombres

with open(destino / "types.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["id", "identifier", "name"])
    for i in sorted(ident):
        w.writerow([i, ident[i], nombres[i]])

especies = set()
with open(destino / "species.csv", encoding="utf-8", newline="") as f:
    especies = {int(r["id"]) for r in csv.DictReader(f)}

filas = []
with open(origen / "pokemon_types.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        pid, tid = int(r["pokemon_id"]), int(r["type_id"])
        # pokemon_id = species_id en la forma por defecto (1-1025); los >= 10001 son formas alternativas.
        if pid in especies and tid in ident:
            filas.append((pid, tid, int(r["slot"])))
filas.sort()

with open(destino / "species_types.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["species_id", "type_id", "slot"])
    w.writerows(filas)

con_tipo = {p for p, _, _ in filas}
print(f"tipos: {len(ident)}; filas especie-tipo: {len(filas)}; especies con tipo: {len(con_tipo)} de {len(especies)}")
print("sin tipo:", sorted(especies - con_tipo)[:10])
