"""Modos de partida y catálogo de reglas (ideas 2 + 6, catálogo reducido el 28 oct. a las reglas habituales).

Es la única fuente de las reglas: la API lo publica en GET /rules y la web muestra a partir de él qué trae
cada modo. Las reglas de una partida se guardan en runs.rules (JSONB) como {clave: valor}; si una clave no
está, la regla está desactivada. El valor es `true` (casilla) o el parámetro (número, lista de especies, tipo).
El código consulta siempre runs.rules, nunca el modo: el modo solo decide qué plantilla se copia al crear.

El modo «personalizada» (elegir las reglas una a una) está aplazado desde el 28 oct.; el catálogo, con sus
parámetros y dependencias, ya está preparado para él.
"""
from dataclasses import asdict, dataclass

MODOS = ("normal", "nuzlocke", "randomlocke")

GRUPOS = {
    "basicas": "Básicas",
    "clausulas": "Cláusulas",
    "segundas": "Segundas oportunidades",
    "dificultad": "Dificultad",
    "restricciones": "Restricciones de Pokémon",
    "aleatorizado": "Aleatorizado por el randomizer",
}


@dataclass(frozen=True)
class Regla:
    clave: str
    grupo: str
    nombre: str
    control: str = "casilla"   # casilla | numero | especies | tipo
    minimo: int | None = None
    maximo: int | None = None
    sin_limite: bool = False   # número opcional: `true` significa «sin límite»
    web: str = "honor"         # comprueba | parcial | honor | informativo (lo que hará la web)
    depende: str | None = None  # solo se puede activar si esta otra regla está activa


CATALOGO = (
    # Básicas
    Regla("primer_encuentro", "basicas", "Solo el primer encuentro de cada zona", web="comprueba"),
    Regla("muerte_definitiva", "basicas", "Debilitado = muerto", web="comprueba"),
    Regla("motes_obligatorios", "basicas", "Motes obligatorios", web="comprueba"),
    Regla("derrota_total_fin", "basicas", "Derrota total = fin de la partida", web="parcial"),
    # Cláusulas: son excepciones a «solo el primer encuentro», así que dependen de ella
    Regla("clausula_duplicados", "clausulas", "Duplicados: una especie ya capturada permite repetir el encuentro",
          "numero", 1, 99, sin_limite=True, web="comprueba", depende="primer_encuentro"),
    Regla("duplicados_linea_evolutiva", "clausulas", "Contar también su línea evolutiva",
          web="comprueba", depende="clausula_duplicados"),
    Regla("clausula_variocolor", "clausulas", "Variocolor: se puede capturar fuera de turno",
          web="comprueba", depende="primer_encuentro"),
    Regla("regalos_no_cuentan", "clausulas", "Regalos y estáticos no gastan el encuentro",
          web="comprueba", depende="primer_encuentro"),
    # Segundas oportunidades: suavizan «debilitado = muerto»
    Regla("vidas", "segundas", "Vidas por Pokémon", "numero", 1, 99, web="comprueba", depende="muerte_definitiva"),
    Regla("resurrecciones", "segundas", "Resurrecciones en toda la partida", "numero", 1, 99,
          web="comprueba", depende="muerte_definitiva"),
    # Dificultad
    Regla("limite_nivel", "dificultad", "Límite de nivel (nivel máximo actual)", "numero", 1, 100, web="comprueba"),
    Regla("max_curativos_combate", "dificultad", "Objetos curativos por combate (0 = prohibidos)", "numero", 0, 99),
    Regla("modo_fijo", "dificultad", "Estilo de combate «Fijo»"),
    # Restricciones de Pokémon
    Regla("especies_prohibidas", "restricciones", "Especies prohibidas", "especies", 1, 100, web="comprueba"),
    Regla("monotipo", "restricciones", "Monolocke: todos de un tipo", "tipo", web="comprueba"),
    # Aleatorizado por el randomizer
    Regla("aleatorio_encuentros", "aleatorizado", "Encuentros salvajes", web="informativo"),
    Regla("aleatorio_iniciales", "aleatorizado", "Pokémon iniciales", web="informativo"),
    Regla("aleatorio_fijos", "aleatorizado", "Pokémon fijos y regalados", web="informativo"),
    Regla("aleatorio_entrenadores", "aleatorizado", "Equipos de los entrenadores", web="informativo"),
    Regla("aleatorio_ataques", "aleatorizado", "Ataques que aprende cada especie", web="informativo"),
    Regla("aleatorio_mt", "aleatorizado", "Compatibilidad con MT y tutores", web="informativo"),
    Regla("aleatorio_habilidades", "aleatorizado", "Habilidades", web="informativo"),
    Regla("aleatorio_tipos", "aleatorizado", "Tipos", web="informativo"),
)
POR_CLAVE = {r.clave: r for r in CATALOGO}

_NUZLOCKE = {
    "primer_encuentro": True, "muerte_definitiva": True, "motes_obligatorios": True,
    "derrota_total_fin": True, "clausula_duplicados": True, "clausula_variocolor": True,
}
PLANTILLAS = {
    "normal": {},
    "nuzlocke": _NUZLOCKE,
    "randomlocke": {
        **_NUZLOCKE,
        "aleatorio_encuentros": True, "aleatorio_iniciales": True, "aleatorio_fijos": True,
        "aleatorio_entrenadores": True, "aleatorio_ataques": True, "aleatorio_mt": True,
        "aleatorio_habilidades": True,
    },
}


def catalogo_publico() -> dict:
    return {
        "modes": MODOS,
        "groups": GRUPOS,
        "rules": [asdict(r) for r in CATALOGO],
        "templates": PLANTILLAS,
    }
