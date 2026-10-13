"""Value object ComputedStats — estadísticas competitivas desde datos reales.

Dataclass puro de dominio. La función get_computed_stats() que lo construye
fue movida a app.services.computed_stats_service durante el refactor de
Clean Architecture (Fase 2).
"""

from dataclasses import dataclass


@dataclass
class ComputedStats:
    """Estadísticas competitivas calculadas desde partidos y torneos reales.

    Atributos:
        torneos (int): Número de torneos distintos en los que participó.
        win_rate (float): Porcentaje de victorias (0-100).
        fep_points (int): Puntos FEP totales ponderados por mejor ronda alcanzada.
    """

    torneos: int = 0
    win_rate: float = 0.0  # 0–100 percentage
    fep_points: int = 0
