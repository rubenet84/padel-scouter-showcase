from app.domain.value_objects.category import ScoringMethod


class MatchScore:
    """
    Implementa los 3 métodos de puntuación FIP 2026.
    - Método 1: Con Ventaja (clásico)
    - Método 2: Star Point  (NUEVO 2026 — tercer deuce = punto decisivo)
    - Método 3: Punto de Oro (deuce directo a punto decisivo)
    """

    def __init__(self, method: ScoringMethod = ScoringMethod.CON_VENTAJA):
        self.method = method

    # ── Juego ────────────────────────────────────────────────────
    def is_game_won(
        self, p1: int, p2: int, deuce_count: int = 0
    ) -> bool | None:
        """
        Devuelve True si p1 gana, False si p2 gana, None si sigue.
        deuce_count: cuántas veces se ha llegado a iguales en este juego.
        """
        if self.method == ScoringMethod.CON_VENTAJA:
            if p1 >= 4 and p1 - p2 >= 2:
                return True
            if p2 >= 4 and p2 - p1 >= 2:
                return False
            return None

        if self.method == ScoringMethod.PUNTO_ORO:
            if p1 >= 4 and p1 > p2:
                return True
            if p2 >= 4 and p2 > p1:
                return False
            if p1 == 3 and p2 == 3:
                return None  # → punto de oro
            return None

        if self.method == ScoringMethod.STAR_POINT:
            # Igual que con_ventaja pero al 3er deuce → star point
            if p1 >= 4 and p1 - p2 >= 2:
                return True
            if p2 >= 4 and p2 - p1 >= 2:
                return False
            if p1 == p2 and p1 >= 3 and deuce_count >= 3:
                return None  # → star point obligatorio
            return None

    def requires_star_point(self, deuce_count: int) -> bool:
        return (
            self.method == ScoringMethod.STAR_POINT
            and deuce_count >= 3
        )

    # ── Set ──────────────────────────────────────────────────────
    def is_set_won(self, g1: int, g2: int) -> bool | None:
        """Regla FIP: ganar 6 juegos con 2 de ventaja. Tie-break a 6-6."""
        if g1 >= 6 and g1 - g2 >= 2:
            return True
        if g2 >= 6 and g2 - g1 >= 2:
            return False
        if g1 == 7 and g2 == 6:
            return True
        if g2 == 7 and g1 == 6:
            return False
        return None

    def requires_tiebreak(self, g1: int, g2: int) -> bool:
        return g1 == 6 and g2 == 6

    # ── Tie-break ────────────────────────────────────────────────
    def is_tiebreak_won(self, p1: int, p2: int) -> bool | None:
        """Tie-break FIP: primero en 7 con 2 de ventaja."""
        if p1 >= 7 and p1 - p2 >= 2:
            return True
        if p2 >= 7 and p2 - p1 >= 2:
            return False
        return None