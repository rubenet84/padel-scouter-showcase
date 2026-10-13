"""Cálculo de puntos FEP (Federación Española de Pádel).

Fuente única de verdad para el cálculo de puntos FEP en toda la aplicación.
Los puntos se distribuyen según la mejor ronda alcanzada en cada torneo,
no se suman planos.

Regla FEP: puntos_torneo × peso_ronda = puntos_obtenidos.
- Ganar la Final → 100% de los puntos del torneo.
- Semifinal → 56.25%.
- Cuartos → 42.18%.
- Fase de grupos → 0%.
"""

from collections import defaultdict
from uuid import UUID

from app.domain.value_objects.rounds import best_round_info


def compute_fep_points(
    match_rows: list,
    player_ids: list[UUID],
) -> dict[UUID, int]:
    """Calcula los puntos FEP por jugador a partir de partidos de torneo.

    Para cada jugador, agrupa los partidos por torneo, determina la mejor
    ronda alcanzada mediante best_round_info() y aplica el peso correspondiente
    sobre los puntos base del torneo.

    Solo los partidos de torneo (tournament_id IS NOT NULL) contribuyen al FEP.
    Los partidos amistosos se excluyen del cálculo.

    Args:
        match_rows: Lista de objetos Row de SQLAlchemy con atributos:
                    tournament_id, fep_points, ronda, ganado, player1_id, partner_id.
        player_ids: Lista de UUIDs de jugadores para los que calcular FEP.

    Returns:
        Dict mapeando cada player_id a sus puntos FEP totales (int).
    """
    # Agrupar partidos de torneo por jugador → torneo
    pt_groups: dict[UUID, dict[UUID, list]] = defaultdict(lambda: defaultdict(list))
    for m in match_rows:
        if not m.tournament_id:
            continue
        for pid in player_ids:
            if m.player1_id == pid or m.partner_id == pid:
                pt_groups[pid][m.tournament_id].append(m)

    result: dict[UUID, int] = {}
    for pid in player_ids:
        total_fep = 0
        for tid, tms in pt_groups.get(pid, {}).items():
            fep_total = tms[0].fep_points or 0   # puntos base del torneo
            if fep_total == 0:
                continue
            # Peso según mejor ronda: final=1.0, semi=0.5625, cuartos=0.4218...
            weight = best_round_info(tms)[2]
            total_fep += int(fep_total * weight)
        result[pid] = total_fep
    return result
