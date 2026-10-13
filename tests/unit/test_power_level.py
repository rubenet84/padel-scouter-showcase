import pytest
from app.domain.value_objects.power_level import (
    calculate_power_level,
    classify_by_power,
)
from app.domain.value_objects.category import PlayerCategory


class TestCalculatePowerLevel:

    def test_iniciacion_stats_produce_low_power(self, stats_iniciacion):
        power = calculate_power_level(stats_iniciacion)
        assert 1000 <= power <= 2000, f"Esperado 1000-2000, obtenido {power}"

    def test_tercera_stats_produce_mid_power(self, stats_tercera):
        power = calculate_power_level(stats_tercera)
        assert 4000 <= power <= 6000, f"Esperado 4000-6000, obtenido {power}"

    def test_pro_stats_produce_high_power(self, stats_pro):
        power = calculate_power_level(stats_pro)
        assert 7000 <= power <= 9000, f"Esperado 7000-9000, obtenido {power}"

    def test_power_level_nunca_supera_9999(self, stats_pro):
        power = calculate_power_level(stats_pro)
        assert power <= 9999

    def test_power_level_siempre_positivo(self, stats_iniciacion):
        power = calculate_power_level(stats_iniciacion)
        assert power > 0

    def test_mejor_jugador_tiene_mayor_poder(self, stats_iniciacion, stats_pro):
        power_ini = calculate_power_level(stats_iniciacion)
        power_pro = calculate_power_level(stats_pro)
        assert power_pro > power_ini

    def test_power_level_es_entero(self, stats_tercera):
        power = calculate_power_level(stats_tercera)
        assert isinstance(power, int)


class TestClassifyByPower:

    def test_power_bajo_es_iniciacion(self):
        assert classify_by_power(500) == PlayerCategory.INICIACION

    def test_power_medio_es_tercera(self):
        assert classify_by_power(5000) == PlayerCategory.TERCERA

    def test_power_alto_es_pro(self):
        assert classify_by_power(9500) == PlayerCategory.PRO

    def test_limites_exactos(self):
        assert classify_by_power(1500) == PlayerCategory.QUINTA
        assert classify_by_power(3000) == PlayerCategory.CUARTA
        assert classify_by_power(4500) == PlayerCategory.TERCERA
        assert classify_by_power(6000) == PlayerCategory.SEGUNDA
        assert classify_by_power(7500) == PlayerCategory.PRIMERA
        assert classify_by_power(9000) == PlayerCategory.PRO
