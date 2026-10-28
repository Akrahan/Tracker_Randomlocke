"""Genera los ataques y habilidades de cada especie a partir de los CSV de PokéAPI (nombres en español).

Crea en la carpeta de destino:
  - moves.csv            (id, name): los ataques que aparecen en alguna lista.
  - species_moves.csv    (species_id, move_id, method, level): lo que puede aprender cada especie.
  - abilities.csv        (id, name)
  - species_abilities.csv (species_id, ability_id, slot, hidden)

Qué juego se usa: para cada especie, el juego principal MÁS RECIENTE en que aparece (decisión del 28 oct.).
Los DLC cuentan como su juego base. Se descartan los juegos con un sistema de ataques distinto
(Colosseum, XD, Let's Go, Leyendas, Champions...). Si una especie aprende un ataque de varias formas,
se queda la más útil: por nivel (el más bajo) > MT > tutor > huevo.

Uso (desde la raíz del proyecto):
    1. Descargar en una carpeta vacía, por ejemplo descargas/:
       https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/{moves,move_names,pokemon_moves,
       abilities,ability_names,pokemon_abilities}.csv
    2. python -I scripts/generar_ataques.py descargas app
Necesita app/species.csv (solo se guardan las especies que hay en la lista).
"""
import csv, sys
from pathlib import Path

origen, destino = Path(sys.argv[1]), Path(sys.argv[2])
ESPANOL = "7"

# version_group_id de PokéAPI -> juego principal, del más antiguo al más reciente
JUEGOS = {
    1: 1, 2: 2,                 # Rojo/Azul, Amarillo
    3: 3, 4: 4,                 # Oro/Plata, Cristal
    5: 5, 6: 6, 7: 7,           # Rubí/Zafiro, Esmeralda, Rojo Fuego/Verde Hoja
    8: 8, 9: 9, 10: 10,         # Diamante/Perla, Platino, Oro HeartGold/Plata SoulSilver
    11: 11, 14: 12,             # Negro/Blanco, Negro 2/Blanco 2
    15: 13, 16: 14,             # X/Y, Rubí Omega/Zafiro Alfa
    17: 15, 18: 16,             # Sol/Luna, Ultrasol/Ultraluna
    20: 17, 21: 17, 22: 17,     # Espada/Escudo y sus DLC
    23: 18,                     # Diamante Brillante/Perla Reluciente
    25: 19, 26: 19, 27: 19,     # Escarlata/Púrpura y sus DLC
}
METODOS = {"1": "level-up", "4": "machine", "3": "tutor", "2": "egg"}
PRIORIDAD = {"level-up": 0, "machine": 1, "tutor": 2, "egg": 3}


def leer(nombre):
    with open(origen / nombre, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def nombres_es(nombre, columna):
    return {int(r[columna]): r["name"] for r in leer(nombre) if r["local_language_id"] == ESPANOL}


with open(destino / "species.csv", encoding="utf-8", newline="") as f:
    especies = {int(r["id"]) for r in csv.DictReader(f)}

# Todas las formas de aprender cada ataque, agrupadas por especie y juego
por_juego = {}
for r in leer("pokemon_moves.csv"):
    pid, vg, metodo = int(r["pokemon_id"]), int(r["version_group_id"]), METODOS.get(r["pokemon_move_method_id"])
    # pokemon_id = species_id en la forma por defecto (1-1025); los >= 10001 son formas alternativas.
    if pid not in especies or vg not in JUEGOS or metodo is None:
        continue
    nivel = int(r["level"] or 0) if metodo == "level-up" else None
    por_juego.setdefault(pid, {}).setdefault(JUEGOS[vg], []).append((int(r["move_id"]), metodo, nivel))

aprende = []
for pid in sorted(por_juego):
    juegos = por_juego[pid]
    mejor = {}
    for move_id, metodo, nivel in juegos[max(juegos)]:
        clave = (PRIORIDAD[metodo], nivel if nivel is not None else 0)
        if move_id not in mejor or clave < mejor[move_id][0]:
            mejor[move_id] = (clave, metodo, nivel)
    aprende += [(pid, m, metodo, "" if nivel is None else nivel) for m, (_, metodo, nivel) in sorted(mejor.items())]

nombres_ataques = nombres_es("move_names.csv", "move_id")
usados = sorted({m for _, m, _, _ in aprende})
sin_nombre = [m for m in usados if m not in nombres_ataques]
assert not sin_nombre, f"ataques sin nombre en español: {sin_nombre[:10]}"

habilidades = []
for r in leer("pokemon_abilities.csv"):
    pid = int(r["pokemon_id"])
    if pid in especies:
        habilidades.append((pid, int(r["ability_id"]), int(r["slot"]), r["is_hidden"] == "1"))
habilidades.sort()
nombres_habilidades = nombres_es("ability_names.csv", "ability_id")
usadas = sorted({a for _, a, _, _ in habilidades})
assert all(a in nombres_habilidades for a in usadas), "hay habilidades sin nombre en español"


def escribir(nombre, cabecera, filas):
    with open(destino / nombre, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cabecera)
        w.writerows(filas)


escribir("moves.csv", ["id", "name"], [(m, nombres_ataques[m]) for m in usados])
escribir("species_moves.csv", ["species_id", "move_id", "method", "level"], aprende)
escribir("abilities.csv", ["id", "name"], [(a, nombres_habilidades[a]) for a in usadas])
escribir("species_abilities.csv", ["species_id", "ability_id", "slot", "hidden"],
         [(p, a, s, "true" if h else "false") for p, a, s, h in habilidades])

print(f"ataques: {len(usados)}; filas especie-ataque: {len(aprende)}; especies con ataques: {len(por_juego)} de {len(especies)}")
print(f"habilidades: {len(usadas)}; filas especie-habilidad: {len(habilidades)}")
print("sin ataques:", sorted(especies - set(por_juego))[:10])
