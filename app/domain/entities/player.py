"""
Entidades de dominio para jugadores.

Define Player (agregado raíz) y PlayerStats (value object) como
dataclasses puras sin dependencias de infraestructura.

Arquitectura: Capa de dominio — entidades sin lógica de persistencia.
Los modelos de base de datos (PlayerModel) son independientes y viven
en app.infrastructure.database.models.
"""
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from app.domain.value_objects.category import PlayerCategory


@dataclass
class PlayerStats:
    """Estadísticas base de un jugador de pádel (0-100).

    Divididas en tres grupos:
    - Técnica: golpes y fundamentos (derecha, revés, volea, remate, etc.).
    - Físico: velocidad, resistencia, reflejos.
    - Mental/Táctico: táctica, presión, trabajo en pareja.

    Cada stat se inicializa en 50 (nivel medio) y se sobreescribe con
    los valores reales al crear el jugador.
    """
    # Técnica (0-100)
    derecha:       int = 50
    reves:         int = 50
    volea_derecha: int = 50
    volea_reves:   int = 50
    bandeja:       int = 50
    vibora:        int = 50
    remate:        int = 50
    globo:         int = 50
    saque:         int = 50
    bajada_pared:  int = 50

    # Físico (0-100)
    velocidad:     int = 50
    resistencia:   int = 50
    reflejos:      int = 50

    # Mental/Táctico (0-100)
    tactica:             int = 50
    presion:             int = 50
    trabajo_en_pareja:   int = 50


@dataclass
class Player:
    """Entidad jugador — agregado raíz del dominio de jugadores.

    Contiene la identidad (UUID), nombre, categoría FEP y estadísticas.
    El power_level no es un atributo persistente — se calcula bajo demanda
    desde las estadísticas y el historial de partidos.
    """
    name:     str
    category: PlayerCategory
    stats:    PlayerStats
    id:       UUID = field(default_factory=uuid4)