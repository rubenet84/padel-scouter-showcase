"""
Detección del Golpe Definitivo (signature ability) del jugador.

Inspirado en el Scouter de Dragon Ball, identifica la estadística más
alta del jugador como su "golpe definitivo" y le asigna un nivel de
amenaza (BAJO, MEDIO, ALTO, MUY ALTO) y una cantidad de Dragon Balls.

Las estadísticas se evalúan en orden, priorizando técnica > físico > mental.
"""
from app.domain.entities.player import PlayerStats

# Estadísticas evaluadas para el golpe definitivo (excluye historial competitivo)
# Formato: (clave_atributo, etiqueta_legible, categoría)
SCOUTER_STATS: list[tuple[str, str, str]] = [
    ("derecha", "Derecha", "técnica"),
    ("reves", "Revés", "técnica"),
    ("volea_derecha", "Volea de Derecha", "técnica"),
    ("volea_reves", "Volea de Revés", "técnica"),
    ("bandeja", "Bandeja", "técnica"),
    ("vibora", "Víbora", "técnica"),
    ("remate", "Remate", "técnica"),
    ("globo", "Globo", "técnica"),
    ("saque", "Saque", "técnica"),
    ("bajada_pared", "Bajada de pared", "técnica"),
    ("velocidad", "Velocidad", "físico"),
    ("resistencia", "Resistencia", "físico"),
    ("reflejos", "Reflejos", "físico"),
    ("tactica", "Táctica", "mental"),
    ("presion", "Presión", "mental"),
    ("trabajo_en_pareja", "Trabajo en pareja", "mental"),
]


def find_strongest_stat(stats: PlayerStats) -> tuple[str, str, str, int]:
    """Encuentra la estadística más alta del jugador.

    Recorre todas las estadísticas del scouter y devuelve la de mayor valor.
    En caso de empate, gana la primera encontrada (orden de SCOUTER_STATS).

    Returns:
        Tupla (clave, etiqueta, categoría, puntuación) de la mejor estadística.
    """
    best_key, best_label, best_cat = SCOUTER_STATS[0]
    best_value = getattr(stats, best_key)

    for key, label, cat in SCOUTER_STATS[1:]:
        value = getattr(stats, key)
        if value > best_value:
            best_key, best_label, best_cat, best_value = key, label, cat, value

    return best_key, best_label, best_cat, best_value


def nivel_amenaza_from_score(score: int) -> str:
    """Convierte una puntuación (0-100) en nivel de amenaza.

    Umbrales:
    - 90+: MUY ALTO — poder devastador.
    - 70-89: ALTO — amenaza seria.
    - 50-69: MEDIO — competente.
    - <50: BAJO — en desarrollo.
    """
    if score >= 90:
        return "MUY ALTO"
    if score >= 70:
        return "ALTO"
    if score >= 50:
        return "MEDIO"
    return "BAJO"


def dragon_balls_for_level(nivel: str) -> int:
    """Asigna Dragon Balls según el nivel de amenaza.

    Referencia Dragon Ball:
    - BAJO: 1 estrella.
    - MEDIO: 3 estrellas.
    - ALTO: 5 estrellas.
    - MUY ALTO: 7 estrellas (las 7 esferas).
    """
    return {
        "BAJO": 1,
        "MEDIO": 3,
        "ALTO": 5,
        "MUY ALTO": 7,
    }.get(nivel, 1)
