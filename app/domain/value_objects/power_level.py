"""
Cálculo del Power Level (poder de combate padelístico).

Implementa el algoritmo core del sistema: transforma las estadísticas
del jugador (técnica, físico, mental) y sus datos competitivos (win rate,
puntos FEP) en un valor único de 0 a 9999, estilo Dragon Ball Scouter.

La fórmula pondera:
- 45% técnica (10 golpes con pesos diferenciados, normalizados a 0-100).
- 25% físico (velocidad, resistencia, reflejos).
- 20% mental (táctica, presión, trabajo en pareja).
- 10% competitivo (puntos FEP y win rate de partidos reales).

La categoría FEP del jugador NO influye en el cálculo del power level.
En su lugar, classify_by_power() sugiere una categoría basada en el
power level resultante.
"""
from app.domain.entities.player import PlayerStats
from app.domain.value_objects.category import PlayerCategory
from app.domain.value_objects.computed_stats import ComputedStats


def calculate_power_level(
    stats: PlayerStats,
    computed_stats: ComputedStats | None = None,
) -> int:
    """
    Calcula el poder de combate padelístico (0 - 9999).

    Solo usa stats reales del jugador (técnica + físico + mental) y
    datos de partidos (competitivo). La categoría NO influye en el
    cálculo — la categoría sugerida se deriva del power level vía
    `classify_by_power()`.

    Cuando `computed_stats` se proporciona, el componente competitivo
    se calcula desde datos reales de partidos.

    Args:
        stats: Estadísticas base del jugador (0-100 en cada atributo).
        computed_stats: Estadísticas computadas desde partidos reales.
                       Si es None, el componente competitivo es 0.

    Returns:
        Power level entre 0 y 9999.
    """
    # Componente técnica: 10 golpes con pesos según importancia en pádel
    # Los pesos suman 0.80, se divide entre 0.80 para normalizar a 0-100
    tecnica = (
        stats.derecha      * 0.12 +
        stats.reves        * 0.10 +
        ((stats.volea_derecha + stats.volea_reves) / 2) * 0.10 +
        stats.bandeja      * 0.10 +
        stats.vibora       * 0.08 +
        stats.remate       * 0.08 +
        stats.globo         * 0.06 +
        stats.saque        * 0.08 +
        stats.bajada_pared * 0.08
    ) / 0.80  # escalar a 0-100 (pesos suman 80%)

    # Componente físico: velocidad, resistencia y reflejos
    fisico = (
        stats.velocidad   * 0.35 +
        stats.resistencia * 0.35 +
        stats.reflejos    * 0.30
    )

    # Componente mental: táctica, presión y trabajo en pareja
    mental = (
        stats.tactica           * 0.40 +
        stats.presion           * 0.30 +
        stats.trabajo_en_pareja * 0.30
    )

    # Componente competitivo desde datos reales de partidos
    if computed_stats:
        win_rate = computed_stats.win_rate / 100   # normalizar a 0-1
        fep_pts = computed_stats.fep_points
    else:
        win_rate = 0.0
        fep_pts = 0

    # FEP contribuye hasta ~500 pts, win rate hasta ~15 pts
    competitive = (fep_pts / 10) + (win_rate * 15)

    # Fórmula final: suma ponderada de los 4 componentes
    raw_score = (
        tecnica   * 0.45 +
        fisico    * 0.25 +
        mental    * 0.20 +
        competitive * 0.10
    )

    # Mapeo directo 0-9999, sin anclaje por categoría
    return min(int(raw_score * 100), 9999)


def classify_by_power(power_level: int) -> PlayerCategory:
    """Clasifica un jugador por su poder de combate.

    Los umbrales están calibrados para una progresión natural:
    - Iniciación: 0-1499
    - 5ª: 1500-2999
    - 4ª: 3000-4499
    - 3ª: 4500-5999
    - 2ª: 6000-7499
    - 1ª: 7500-8999
    - Profesional: 9000+

    Args:
        power_level: Poder de combate calculado (0-9999).

    Returns:
        PlayerCategory correspondiente al nivel de poder.
    """
    if power_level < 1500:
        return PlayerCategory.INICIACION
    elif power_level < 3000:
        return PlayerCategory.QUINTA
    elif power_level < 4500:
        return PlayerCategory.CUARTA
    elif power_level < 6000:
        return PlayerCategory.TERCERA
    elif power_level < 7500:
        return PlayerCategory.SEGUNDA
    elif power_level < 9000:
        return PlayerCategory.PRIMERA
    return PlayerCategory.PRO
