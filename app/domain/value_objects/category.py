"""
Value objects de categorías de jugador y métodos de puntuación.

Define los enumerados oficiales usados en toda la aplicación:
- PlayerCategory: categorías FEP (Iniciación a Profesional) con pesos.
- ScoringMethod: métodos de puntuación FIP 2026.
"""
from enum import Enum


class PlayerCategory(Enum):
    """Categorías de la Federación Española de Pádel (FEP).

    Cada categoría tiene un peso numérico usado para ordenar y comparar niveles.
    """
    INICIACION = "Iniciación"
    QUINTA     = "5ª Categoría"
    CUARTA     = "4ª Categoría"
    TERCERA    = "3ª Categoría"
    SEGUNDA    = "2ª Categoría"
    PRIMERA    = "1ª Categoría"
    PRO        = "Profesional"

    def weight(self) -> int:
        """Peso numérico de la categoría para ordenamiento (1-7)."""
        weights = {
            "Iniciación":   1,
            "5ª Categoría": 2,
            "4ª Categoría": 3,
            "3ª Categoría": 4,
            "2ª Categoría": 5,
            "1ª Categoría": 6,
            "Profesional":  7,
        }
        return weights[self.value]


class ScoringMethod(Enum):
    """Métodos de puntuación según reglamento FIP 2026.

    - CON_VENTAJA: clásico, ventaja después de deuce.
    - STAR_POINT: nuevo 2026, tercer deuce = punto decisivo.
    - PUNTO_ORO: deuce directo a punto decisivo.
    """
    CON_VENTAJA = "con_ventaja"
    STAR_POINT  = "star_point"
    PUNTO_ORO   = "punto_oro"