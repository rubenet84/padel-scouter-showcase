import pytest

from app.domain.entities.player import PlayerStats
from app.domain.value_objects.golpe_definitivo import (
    find_strongest_stat,
    nivel_amenaza_from_score,
    dragon_balls_for_level,
)


class TestGolpeDefinitivo:

    def test_find_strongest_stat(self):
        stats = PlayerStats(remate=95, derecha=80, velocidad=70)
        key, label, cat, value = find_strongest_stat(stats)
        assert key == "remate"
        assert label == "Remate"
        assert cat == "técnica"
        assert value == 95

    @pytest.mark.parametrize("score,expected", [
        (0, "BAJO"), (49, "BAJO"),
        (50, "MEDIO"), (69, "MEDIO"),
        (70, "ALTO"), (89, "ALTO"),
        (90, "MUY ALTO"), (100, "MUY ALTO"),
    ])
    def test_nivel_amenaza_from_score(self, score, expected):
        assert nivel_amenaza_from_score(score) == expected

    @pytest.mark.parametrize("nivel,count", [
        ("BAJO", 1), ("MEDIO", 3), ("ALTO", 5), ("MUY ALTO", 7),
    ])
    def test_dragon_balls_for_level(self, nivel, count):
        assert dragon_balls_for_level(nivel) == count
