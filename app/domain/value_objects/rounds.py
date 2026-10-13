"""Constantes y utilidades compartidas para cálculo de rondas de torneo.

Fuente única de verdad para ROUND_ORDER, ROUND_WEIGHTS y funciones auxiliares
de rondas usadas en las capas de dominio y API.

Jerarquía de rondas (single-elimination): Fase de grupos → 32avos → ... → Final.
Cada ronda tiene un peso FEP que determina el % de puntos del torneo que se
otorgan al jugador según la mejor ronda alcanzada.
"""

# Jerarquía de rondas: índice más bajo = ronda más temprana
ROUND_ORDER: list[str] = [
    "Fase de grupos",
    "32avos",
    "16avos",
    "Octavos",
    "Cuartos",
    "Semifinal",
    "Final",
]

# Pesos FEP por ronda: porcentaje de los puntos del torneo que se otorgan.
# Ganar la Final no otorga el 100% automáticamente (best_round_info asigna 1.0).
# Fuente: reglamento FEP oficial.
ROUND_WEIGHTS: dict[str, float] = {
    "Fase de grupos": 0.0,
    "32avos":         0.1780,
    "16avos":         0.2373,
    "Octavos":        0.3164,
    "Cuartos":        0.4218,
    "Semifinal":      0.5625,
    "Final":          0.75,
}


def get_round_index(round_name: str) -> int:
    """Devuelve el índice jerárquico de una ronda. -1 si no es reconocida."""
    try:
        return ROUND_ORDER.index(round_name)
    except ValueError:
        return -1


def best_round_info(matches: list) -> tuple[str | None, int, float]:
    """Determina la mejor ronda alcanzada por un jugador en un torneo.

    Algoritmo:
    1. Busca la ronda más alta donde el jugador tuvo una VICTORIA.
    2. Si ganó la Final → campeón (índice 6, peso 1.0 = 100% puntos).
    3. Si no hay victorias → ronda más alta donde participó (aunque perdiera).

    Returns:
        Tupla (nombre_ronda, índice_ronda, peso_FEP).
        Si no se encuentra ninguna ronda: (None, -1, 0.0).
    """
    win_idx = -1      # mejor ronda con victoria
    reach_idx = -1    # mejor ronda alcanzada (con o sin victoria)

    for m in matches:
        ronda = (getattr(m, "ronda", None) or "").strip()
        if ronda in ROUND_ORDER:
            idx = ROUND_ORDER.index(ronda)
            if idx > reach_idx:
                reach_idx = idx
            if getattr(m, "ganado", False) and idx > win_idx:
                win_idx = idx

    # Caso especial: ganó la Final → peso completo
    if win_idx >= 0 and ROUND_ORDER[win_idx] == "Final":
        return ("Final", 6, 1.0)

    # Mejor ronda con victoria (sin contar Final ya procesada)
    if win_idx >= 0:
        name = ROUND_ORDER[win_idx]
        return (name, win_idx, ROUND_WEIGHTS.get(name, 0.0))

    # Sin victorias: ronda más alta alcanzada
    if reach_idx >= 0:
        name = ROUND_ORDER[reach_idx]
        return (name, reach_idx, ROUND_WEIGHTS.get(name, 0.0))

    return (None, -1, 0.0)
