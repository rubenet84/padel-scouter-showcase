"""Cálculo de métricas por jugador desde datos de partidos.

Fuente única de verdad para la agregación de métricas por jugador en
toda la aplicación. Procesa lotes de partidos y devuelve estadísticas
normalizadas para rankings, comparadores y visualizaciones.
"""

from collections import defaultdict
from uuid import UUID


def compute_player_match_metrics(
    match_rows: list,
    player_ids: list[UUID],
) -> dict[UUID, dict]:
    """Métricas base derivadas de partidos para un lote de jugadores.

    Calcula victorias, derrotas, % victorias, sets ganados, juegos ganados
    y mejor racha de victorias consecutivas a partir de los partidos.

    Los partidos se asignan al jugador si este aparece como player1 o partner.
    El resultado (resultado) se parsea asumiendo el formato "6-4 6-3" donde el
    primer número de cada set corresponde al jugador.

    Args:
        match_rows: Lista de objetos Row con atributos:
                    ganado, resultado, player1_id, partner_id.
        player_ids: Lista de UUIDs de jugadores a evaluar.

    Returns:
        Dict[UUID, dict] con claves: wins, losses, matches, win_pct,
        sets_won, games_won, streak.
    """
    # Agrupar partidos por jugador
    player_matches: dict[UUID, list] = defaultdict(list)
    for m in match_rows:
        for pid in player_ids:
            if m.player1_id == pid or m.partner_id == pid:
                player_matches[pid].append(m)

    result: dict[UUID, dict] = {}
    for pid in player_ids:
        pms = player_matches.get(pid, [])

        wins = sum(1 for m in pms if m.ganado)
        losses = sum(1 for m in pms if not m.ganado)
        total = len(pms)
        win_pct = round(wins / total * 100, 1) if total > 0 else 0.0

        # Parsear resultado para contar sets y juegos ganados
        # Formato esperado: "6-4 6-3" (juegos del set 1, juegos del set 2)
        sets_won = 0
        games_won = 0
        for m in pms:
            if not m.resultado:
                continue
            for s in m.resultado.split():
                parts = s.split("-")
                if len(parts) != 2:
                    continue
                try:
                    ps, rs = int(parts[0]), int(parts[1])
                    games_won += ps                    # ps = juegos del jugador
                    if ps > rs:
                        sets_won += 1                  # ganó el set
                except ValueError:
                    continue

        # Mejor racha de victorias consecutivas
        best_streak = 0
        current = 0
        for m in pms:  # ordenados por played_at DESC (más reciente primero)
            if m.ganado:
                current += 1
                if current > best_streak:
                    best_streak = current
            else:
                current = 0
        streak = best_streak

        result[pid] = {
            "wins": wins,
            "losses": losses,
            "matches": total,
            "win_pct": win_pct,
            "sets_won": sets_won,
            "games_won": games_won,
            "streak": streak,
        }
    return result


def _compute_player_metrics(
    match_rows: list,
    player_ids: list[UUID],
    fep_points: dict[UUID, int],
) -> dict[UUID, dict]:
    """Métricas completas por jugador: base + torneos ganados + finales + semis.

    Extiende compute_player_match_metrics() añadiendo datos específicos de
    torneo (torneos ganados, finales alcanzadas, semifinales) y puntos FEP.

    Args:
        match_rows: Lista de objetos Row con atributos de partido.
        player_ids: Lista de UUIDs de jugadores.
        fep_points: Dict precalculado de puntos FEP por jugador.

    Returns:
        Dict[UUID, dict] con todas las métricas incluido "points", "tournaments_won",
        "finals", "semis".
    """
    # 1. Métricas base desde partidos (victorias, derrotas, sets, juegos, racha)
    base = compute_player_match_metrics(match_rows, player_ids)

    # 2. Inicializar resultado con defaults para TODOS los player_ids
    result: dict[UUID, dict] = {}
    for pid in player_ids:
        entry = dict(
            base.get(
                pid,
                {
                    "wins": 0,
                    "losses": 0,
                    "matches": 0,
                    "win_pct": 0.0,
                    "sets_won": 0,
                    "games_won": 0,
                    "streak": 0,
                },
            )
        )
        entry["tournaments_won"] = 0
        entry["finals"] = 0
        entry["semis"] = 0
        result[pid] = entry

    # 3. Enriquecer con datos de torneo (ligero — sin parsear resultado de nuevo)
    for m in match_rows:
        for pid in player_ids:
            if not (m.player1_id == pid or m.partner_id == pid):
                continue
            # Una victoria en un partido de torneo cuenta como "torneo ganado"
            # (representa ganar UN partido en ese torneo, no el torneo entero)
            if m.ganado and m.tournament_id:
                result[pid]["tournaments_won"] += 1
            ronda = (getattr(m, "ronda", None) or "").strip()
            if ronda == "Final":
                result[pid]["finals"] += 1
            elif ronda == "Semifinal":
                result[pid]["semis"] += 1

    # 4. Adjuntar puntos FEP precalculados
    for pid in player_ids:
        result[pid]["points"] = fep_points.get(pid, 0)

    return result
