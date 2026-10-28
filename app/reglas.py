"""Modos de partida y catálogo de reglas (ideas 2 + 6, catálogo cerrado el 28 oct.).

Es la única fuente de las reglas: la API lo publica en GET /rules y la web pinta las casillas a partir de él.
Las reglas de una partida se guardan en runs.rules (JSONB) como {clave: valor}; si una clave no está,
la regla está desactivada. El valor es `true` (casilla) o el parámetro (número, lista de especies, tipo, texto).
El código consulta siempre runs.rules, nunca el modo: el modo solo decide qué plantilla se copia al crear.
"""
from dataclasses import asdict, dataclass

MODOS = ("normal", "nuzlocke", "randomlocke", "personalizada")

GRUPOS = {
    "A": "Básicas",
    "B": "Cláusulas",
    "C": "Vidas y segundas oportunidades",
    "D": "Nivel y equipo",
    "E": "Objetos y curación",
    "F": "Combate y ataques",
    "G": "Restricciones de Pokémon",
    "H": "Aleatorizado por el randomizer",
}


@dataclass(frozen=True)
class Regla:
    clave: str
    grupo: str
    nombre: str
    control: str = "casilla"   # casilla | numero | especies | tipo | texto
    minimo: int | None = None
    maximo: int | None = None
    sin_limite: bool = False   # número opcional: `true` significa «sin límite»
    web: str = "honor"         # comprueba | parcial | honor | informativo (lo que hará la web)


CATALOGO = (
    # A. Básicas
    Regla("primer_encuentro", "A", "Solo el primer encuentro de cada zona", web="comprueba"),
    Regla("muerte_definitiva", "A", "Debilitado = muerto", web="comprueba"),
    Regla("motes_obligatorios", "A", "Motes obligatorios", web="comprueba"),
    Regla("derrota_total_fin", "A", "Derrota total = fin de la partida", web="parcial"),
    Regla("sin_muertes", "A", "Sin muertes: la primera muerte termina la partida", web="comprueba"),
    # B. Cláusulas
    Regla("clausula_duplicados", "B", "Duplicados: una especie ya capturada permite repetir el encuentro",
          "numero", 1, 99, sin_limite=True, web="comprueba"),
    Regla("duplicados_linea_evolutiva", "B", "…contando la línea evolutiva", web="comprueba"),
    Regla("clausula_variocolor", "B", "Variocolor: se puede capturar fuera de turno", web="comprueba"),
    Regla("regalos_no_cuentan", "B", "Los regalos no gastan el encuentro", web="comprueba"),
    Regla("estaticos_no_cuentan", "B", "Los estáticos no gastan el encuentro", web="comprueba"),
    Regla("huida_repite", "B", "Si el primer encuentro huye, se repite"),
    Regla("capturas_mo", "B", "Capturas solo para MO", "numero", 1, 20, web="comprueba"),
    Regla("pokemon_elegidos", "B", "Pokémon elegidos al inicio, fuera de las normas", "numero", 1, 20, web="comprueba"),
    # C. Vidas y segundas oportunidades
    Regla("vidas", "C", "Vidas por Pokémon", "numero", 1, 99, web="comprueba"),
    Regla("resurrecciones", "C", "Resurrecciones en toda la partida", "numero", 1, 99, web="comprueba"),
    Regla("revivir_sacrificando", "C", "Revivir sacrificando a otros (cuántos)", "numero", 1, 6, web="comprueba"),
    Regla("seguir_con_caja", "C", "Tras una derrota total, seguir con la caja", web="comprueba"),
    # D. Nivel y equipo
    Regla("limite_nivel", "D", "Límite de nivel (nivel máximo actual)", "numero", 1, 100, web="comprueba"),
    Regla("margen_nivel", "D", "Margen sobre el límite de nivel (niveles)", "numero", 1, 99, web="comprueba"),
    Regla("tamano_equipo", "D", "Tamaño máximo del equipo", "numero", 1, 6, web="comprueba"),
    Regla("caja_retirado", "D", "Caja = retirado para siempre", web="comprueba"),
    Regla("orden_sustitucion", "D", "Orden fijo de sustitución (por captura)", web="comprueba"),
    Regla("encerrado_gimnasio", "D", "No salir de un gimnasio hasta ganar"),
    Regla("todos_entrenadores", "D", "Combatir contra todos los entrenadores"),
    Regla("sin_volver_atras", "D", "Sin volver atrás"),
    # E. Objetos y curación
    Regla("sin_curativos_combate", "E", "Sin objetos curativos en combate"),
    Regla("max_curativos_combate", "E", "Máximo de objetos curativos por combate", "numero", 1, 99),
    Regla("solo_objetos_encontrados", "E", "Solo objetos encontrados"),
    Regla("sin_objetos_equipados", "E", "Sin objetos equipados", web="comprueba"),
    Regla("sin_centros", "E", "Sin Centros Pokémon"),
    Regla("usos_centro", "E", "Usos de cada Centro Pokémon", "numero", 1, 99),
    Regla("limite_pokeballs", "E", "Límite de Poké Balls compradas", "numero", 1, 999),
    # F. Combate y ataques
    Regla("modo_fijo", "F", "Estilo de combate «Fijo»"),
    Regla("sin_mt", "F", "Sin MT (solo ataques por nivel)", web="comprueba"),
    Regla("sin_ataques_mejora", "F", "Sin ataques de mejora"),
    Regla("potencia_maxima", "F", "Potencia máxima de los ataques", "numero", 1, 250, web="comprueba"),
    Regla("sin_stab", "F", "Sin ataques de su mismo tipo (sin STAB)", web="comprueba"),
    Regla("solo_stab", "F", "Solo ataques de su mismo tipo (solo STAB)", web="comprueba"),
    Regla("a_ciegas", "F", "A ciegas (sin guías ni calculadoras)"),
    # G. Restricciones de Pokémon
    Regla("sin_inicial", "G", "Sin el Pokémon inicial", web="comprueba"),
    Regla("sin_regalos", "G", "Sin Pokémon regalados", web="comprueba"),
    Regla("especies_prohibidas", "G", "Especies prohibidas", "especies", 1, 100, web="comprueba"),
    Regla("monotipo", "G", "Monolocke: todos de un tipo", "tipo", web="comprueba"),
    Regla("tipo_prohibido", "G", "Tipo prohibido", "tipo", web="comprueba"),
    Regla("sin_doble_tipo", "G", "Sin Pokémon de doble tipo", web="comprueba"),
    Regla("solo_doble_tipo", "G", "Solo Pokémon de doble tipo", web="comprueba"),
    Regla("max_mismo_tipo", "G", "Máximo de Pokémon del mismo tipo en el equipo", "numero", 1, 6, web="comprueba"),
    Regla("max_evoluciones", "G", "Máximo de evoluciones (0 = sin evolucionar)", "numero", 0, 2, web="comprueba"),
    Regla("solo_generacion", "G", "Solo Pokémon de la generación del juego", web="comprueba"),
    Regla("limite_estadisticas_base", "G", "Límite de estadísticas base totales", "numero", 100, 800, web="comprueba"),
    Regla("tematico", "G", "Temático (color o letra inicial)", "texto", 1, 50, web="comprueba"),
    # H. Aleatorizado por el randomizer
    Regla("aleatorio_encuentros", "H", "Encuentros salvajes", web="informativo"),
    Regla("aleatorio_iniciales", "H", "Pokémon iniciales", web="informativo"),
    Regla("aleatorio_fijos", "H", "Pokémon fijos y regalados", web="informativo"),
    Regla("aleatorio_entrenadores", "H", "Equipos de los entrenadores", web="informativo"),
    Regla("aleatorio_ataques", "H", "Ataques que aprende cada especie", web="informativo"),
    Regla("aleatorio_mt", "H", "Compatibilidad con MT y tutores", web="informativo"),
    Regla("aleatorio_contenido_mt", "H", "Contenido de las MT", web="informativo"),
    Regla("aleatorio_habilidades", "H", "Habilidades", web="informativo"),
    Regla("aleatorio_tipos", "H", "Tipos", web="informativo"),
    Regla("aleatorio_estadisticas", "H", "Estadísticas base", web="informativo"),
    Regla("aleatorio_evoluciones", "H", "Evoluciones", web="informativo"),
    Regla("aleatorio_objetos", "H", "Objetos del suelo y de las tiendas", web="informativo"),
    Regla("aleatorio_datos_ataques", "H", "Datos de los ataques (potencia, tipo)", web="informativo"),
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

# Reglas que se contradicen y reglas que necesitan otra
INCOMPATIBLES = (
    ("sin_stab", "solo_stab"),
    ("sin_doble_tipo", "solo_doble_tipo"),
    ("sin_curativos_combate", "max_curativos_combate"),
    ("sin_centros", "usos_centro"),
    ("sin_regalos", "regalos_no_cuentan"),
)
REQUIERE = {
    "duplicados_linea_evolutiva": "clausula_duplicados",
    "margen_nivel": "limite_nivel",
}


def es_entero(valor) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)  # en Python, True también es un int


def validar(reglas: dict) -> dict:
    """Comprueba el formato de unas reglas y las devuelve limpias (sin las desactivadas).

    Lanza ValueError con un mensaje para el usuario. Que las especies y los tipos existan lo comprueba
    la API, porque necesita la base de datos."""
    limpias = {}
    for clave, valor in reglas.items():
        regla = POR_CLAVE.get(clave)
        if regla is None:
            raise ValueError(f"«{clave}» no es una regla")
        if valor is False or valor is None:
            continue  # desactivada: no se guarda
        if regla.control == "casilla":
            if valor is not True:
                raise ValueError(f"«{regla.nombre}» solo se activa o se desactiva")
        elif regla.control == "numero":
            if valor is True and regla.sin_limite:
                pass
            elif not es_entero(valor) or not regla.minimo <= valor <= regla.maximo:
                raise ValueError(f"«{regla.nombre}» necesita un número entre {regla.minimo} y {regla.maximo}")
        elif regla.control == "especies":
            if (not isinstance(valor, list) or not regla.minimo <= len(valor) <= regla.maximo
                    or not all(isinstance(e, str) and 0 < len(e.strip()) <= 100 for e in valor)):
                raise ValueError(f"«{regla.nombre}» necesita una lista de especies")
            valor = list(dict.fromkeys(e.strip() for e in valor))  # sin repetidas, en el mismo orden
        elif regla.control == "tipo":
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"«{regla.nombre}» necesita un tipo")
            valor = valor.strip().lower()
        elif regla.control == "texto":
            if not isinstance(valor, str) or not regla.minimo <= len(valor.strip()) <= regla.maximo:
                raise ValueError(f"«{regla.nombre}» necesita un texto de {regla.minimo} a {regla.maximo} caracteres")
            valor = valor.strip()
        limpias[clave] = valor

    for a, b in INCOMPATIBLES:
        if a in limpias and b in limpias:
            raise ValueError(f"«{POR_CLAVE[a].nombre}» y «{POR_CLAVE[b].nombre}» no se pueden activar a la vez")
    for regla, necesita in REQUIERE.items():
        if regla in limpias and necesita not in limpias:
            raise ValueError(f"«{POR_CLAVE[regla].nombre}» necesita «{POR_CLAVE[necesita].nombre}»")
    return limpias


def catalogo_publico() -> dict:
    return {
        "modes": MODOS,
        "groups": GRUPOS,
        "rules": [asdict(r) for r in CATALOGO],
        "templates": PLANTILLAS,
    }
