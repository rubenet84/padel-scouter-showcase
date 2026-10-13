import pytest
from app.domain.value_objects.score import MatchScore
from app.domain.value_objects.category import ScoringMethod


class TestConVentaja:

    def setup_method(self):
        self.score = MatchScore(ScoringMethod.CON_VENTAJA)

    def test_gana_juego_con_4_0(self):
        assert self.score.is_game_won(4, 0) is True

    def test_gana_juego_con_ventaja(self):
        assert self.score.is_game_won(5, 3) is True

    def test_no_gana_sin_dos_diferencia(self):
        assert self.score.is_game_won(4, 3) is None

    def test_iguales_a_3(self):
        assert self.score.is_game_won(3, 3) is None

    def test_gana_set_6_3(self):
        assert self.score.is_set_won(6, 3) is True

    def test_no_gana_set_6_5(self):
        assert self.score.is_set_won(6, 5) is None

    def test_gana_set_7_5(self):
        assert self.score.is_set_won(7, 5) is True

    def test_tiebreak_a_6_6(self):
        assert self.score.requires_tiebreak(6, 6) is True
        assert self.score.requires_tiebreak(6, 5) is False

    def test_tiebreak_gana_7_5(self):
        assert self.score.is_tiebreak_won(7, 5) is True

    def test_tiebreak_no_gana_7_6(self):
        assert self.score.is_tiebreak_won(7, 6) is None


class TestStarPoint:
    """Nuevo sistema FIP 2026"""

    def setup_method(self):
        self.score = MatchScore(ScoringMethod.STAR_POINT)

    def test_star_point_al_tercer_deuce(self):
        assert self.score.requires_star_point(deuce_count=3) is True

    def test_sin_star_point_antes_del_tercer_deuce(self):
        assert self.score.requires_star_point(deuce_count=2) is False

    def test_gana_normalmente_antes_del_star_point(self):
        assert self.score.is_game_won(4, 2, deuce_count=0) is True


class TestPuntoOro:

    def setup_method(self):
        self.score = MatchScore(ScoringMethod.PUNTO_ORO)

    def test_iguales_requiere_punto_decisivo(self):
        assert self.score.is_game_won(3, 3) is None

    def test_gana_con_4_puntos_sin_ventaja(self):
        assert self.score.is_game_won(4, 2) is True