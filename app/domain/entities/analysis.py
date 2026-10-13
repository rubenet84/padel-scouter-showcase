"""
Entidad de dominio para el resultado de un análisis IA.

AnalysisResult es el objeto de valor que retorna el caso de uso
AnalyzePlayerUseCase después de calcular el power level y consultar
a Gemini. Los datos se persisten en AnalysisModel (infraestructura).
"""
from dataclasses import dataclass
from uuid import UUID
from app.domain.value_objects.category import PlayerCategory


@dataclass
class AnalysisResult:
    """Resultado completo del análisis de un jugador.

    Incluye tanto métricas calculadas localmente (power_level, golpe_definitivo)
    como contenido generado por IA (descripción, fortalezas, debilidades, plan).
    """
    player_id:        UUID
    power_level:      int          # 0 - 9999 (escala Dragon Ball)
    category:         PlayerCategory
    ai_description:   str          # Narrativa generada por Gemini
    strengths:        list[str]    # Fortalezas detectadas
    weaknesses:       list[str]    # Debilidades detectadas
    improvement_plan: str          # Plan de mejora personalizado
    golpe_definitivo: str = "Por determinar"   # Nombre épico del golpe más fuerte
    golpe_descripcion: str = ""                 # Descripción cinematográfica
    golpe_puntuacion:  int = 0                  # Puntuación del golpe (0-100)
    nivel_amenaza:    str = "MEDIO"             # Nivel de amenaza: BAJO, MEDIO, ALTO, MUY ALTO