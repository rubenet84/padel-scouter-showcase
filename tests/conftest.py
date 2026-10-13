import pytest
from app.domain.entities.player import Player, PlayerStats
from app.domain.value_objects.category import PlayerCategory


@pytest.fixture
def stats_iniciacion() -> PlayerStats:
    return PlayerStats(
        derecha=20, reves=15, volea_derecha=10, volea_reves=10, bandeja=5,
        vibora=0,  remate=10, globo=10,  saque=20,
        bajada_pared=5, velocidad=40, resistencia=35,
        reflejos=30, tactica=15, presion=10,
        trabajo_en_pareja=15,
    )


@pytest.fixture
def stats_tercera() -> PlayerStats:
    return PlayerStats(
        derecha=60, reves=55, volea_derecha=58, volea_reves=58, bandeja=52,
        vibora=45, remate=60, globo=55,  saque=62,
        bajada_pared=50, velocidad=65, resistencia=60,
        reflejos=62, tactica=58, presion=55,
        trabajo_en_pareja=60,
    )


@pytest.fixture
def stats_pro() -> PlayerStats:
    return PlayerStats(
        derecha=95, reves=92, volea_derecha=90, volea_reves=90, bandeja=93,
        vibora=88, remate=94, globo=85,  saque=91,
        bajada_pared=89, velocidad=95, resistencia=92,
        reflejos=94, tactica=95, presion=90,
        trabajo_en_pareja=95,
    )