"""
Entidad de dominio para torneos.

Tournament es una entidad simple con identidad (UUID), nombre, fecha,
puntos FEP y owner. Se usa como referencia desde los partidos para
calcular estadísticas competitivas y distribuir puntos FEP.

Arquitectura: Capa de dominio — entidad pura sin lógica de persistencia.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Tournament:
    """Entidad torneo con datos mínimos para el dominio."""
    id: UUID = field(default_factory=uuid4)
    name: str
    date: date
    fep_points: int | None = 0
    owner_id: UUID
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
