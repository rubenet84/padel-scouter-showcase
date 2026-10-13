"""
Política de autorización de Padel Scouter — fuente única de verdad.

Este módulo concentra TODAS las decisiones de autorización del sistema:
qué roles existen, qué permisos tiene cada uno, cuál es su alcance sobre los
datos y qué límites aplican. Ningún endpoint ni servicio debe comparar roles
manualmente: todos deben consumir las funciones de aquí.

Restricciones de la capa de dominio:
- No importa SQLAlchemy, FastAPI ni ninguna dependencia de infraestructura.
- Es puro y testeable de forma aislada.
- El sistema es "fail-closed": un rol desconocido no obtiene ningún permiso.

Nota: los permisos de torneos se definirán en una fase posterior, una vez
confirmado el modelo de propiedad (compartido vs. por dueño) de los torneos.
"""
from enum import Enum


class Role(str, Enum):
    """Roles disponibles en Padel Scouter.

    - ADMIN: administración global, sin límites.
    - ENTRENADOR: gestiona su propio roster de jugadores (máx. 25).
    - JUGADOR: gestiona sus propios jugadores (máx. 2).
    """

    ADMIN = "admin"
    ENTRENADOR = "entrenador"
    JUGADOR = "jugador"


class Permission(str, Enum):
    """Permisos granulares del sistema (acción concreta sobre un recurso)."""

    # ── Usuarios (exclusivo de administración) ──────────────────
    USERS_READ = "users.read"
    USERS_UPDATE = "users.update"
    USERS_SUSPEND = "users.suspend"
    USERS_CHANGE_ROLE = "users.change_role"

    # ── Jugadores ───────────────────────────────────────────────
    PLAYERS_CREATE = "players.create"
    PLAYERS_READ = "players.read"
    PLAYERS_UPDATE = "players.update"
    PLAYERS_DELETE = "players.delete"
    PLAYERS_RESTORE = "players.restore"

    # ── Partidos ────────────────────────────────────────────────
    MATCHES_CREATE = "matches.create"
    MATCHES_READ = "matches.read"
    MATCHES_UPDATE = "matches.update"
    MATCHES_DELETE = "matches.delete"

    # ── Estadísticas ────────────────────────────────────────────
    STATS_READ = "stats.read"
    STATS_COMPARE = "stats.compare"

    # ── Inteligencia Artificial ─────────────────────────────────
    AI_ANALYZE = "ai.analyze"
    AI_CHAT = "ai.chat"

    # ── Informes ────────────────────────────────────────────────
    REPORTS_GENERATE = "reports.generate"
    REPORTS_DOWNLOAD = "reports.download"

    # ── Torneos ─────────────────────────────────────────────────
    TOURNAMENTS_CREATE = "tournaments.create"
    TOURNAMENTS_READ = "tournaments.read"
    TOURNAMENTS_UPDATE = "tournaments.update"
    TOURNAMENTS_DELETE = "tournaments.delete"

    # ── Notificaciones ──────────────────────────────────────────
    NOTIFICATIONS_READ = "notifications.read"
    NOTIFICATIONS_UPDATE = "notifications.update"

    # ── Administración ──────────────────────────────────────────
    AUDIT_READ = "audit.read"
    SYSTEM_MANAGE = "system.manage"


class Scope(str, Enum):
    """Alcance de los datos sobre los que un rol puede operar.

    - OWN: solo recursos cuyo owner_id es el propio usuario.
    - ROSTER: su ámbito de responsabilidad (hoy equivalente a OWN vía owner_id;
      queda explicitado para futuras extensiones sin romper la política).
    - GLOBAL: todos los recursos del sistema (administración).
    """

    OWN = "own"
    ROSTER = "roster"
    GLOBAL = "global"


# ── Matriz rol → permisos (fuente única de verdad) ──────────────

_PLAYER_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.PLAYERS_CREATE,
    Permission.PLAYERS_READ,
    Permission.PLAYERS_UPDATE,
    Permission.PLAYERS_DELETE,
    Permission.MATCHES_CREATE,
    Permission.MATCHES_READ,
    Permission.MATCHES_UPDATE,
    Permission.MATCHES_DELETE,
    Permission.STATS_READ,
    Permission.AI_ANALYZE,
    Permission.AI_CHAT,
    Permission.TOURNAMENTS_CREATE,
    Permission.TOURNAMENTS_READ,
    Permission.TOURNAMENTS_UPDATE,
    Permission.TOURNAMENTS_DELETE,
    Permission.NOTIFICATIONS_READ,
    Permission.NOTIFICATIONS_UPDATE,
})

# El entrenador amplía al jugador con: restaurar jugadores, comparar estadísticas
# y generar/descargar informes PDF (reports.* queda fuera de 'jugador').
_COACH_PERMISSIONS: frozenset[Permission] = _PLAYER_PERMISSIONS | frozenset({
    Permission.PLAYERS_RESTORE,
    Permission.STATS_COMPARE,
    Permission.REPORTS_GENERATE,
    Permission.REPORTS_DOWNLOAD,
})

# El administrador tiene todos los permisos del sistema.
_ADMIN_PERMISSIONS: frozenset[Permission] = frozenset(Permission)

ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: _ADMIN_PERMISSIONS,
    Role.ENTRENADOR: _COACH_PERMISSIONS,
    Role.JUGADOR: _PLAYER_PERMISSIONS,
}


# ── Límites por rol ─────────────────────────────────────────────
# None significa "ilimitado".
PLAYER_LIMITS: dict[Role, int | None] = {
    Role.ADMIN: None,
    Role.ENTRENADOR: 25,
    Role.JUGADOR: 2,
}


# ── Alcance por rol ─────────────────────────────────────────────
_ROLE_SCOPE: dict[Role, Scope] = {
    Role.ADMIN: Scope.GLOBAL,
    Role.ENTRENADOR: Scope.ROSTER,
    Role.JUGADOR: Scope.OWN,
}


# ── Funciones de consulta (API pública de la política) ──────────

def role_from_value(value: object) -> Role | None:
    """Convierte un valor crudo (str) en Role, o None si no es un rol válido.

    Es "fail-safe": un valor inesperado devuelve None en lugar de asumir un rol
    por defecto. La migración de datos es la responsable de no dejar roles
    inválidos en la base de datos; esta función evita que valores corruptos
    obtengan permisos accidentalmente.
    """
    if isinstance(value, Role):
        return value
    if not isinstance(value, str):
        return None
    try:
        return Role(value.strip().lower())
    except ValueError:
        return None


def has_permission(role: Role | None, permission: Permission) -> bool:
    """Indica si un rol posee el permiso dado (fail-closed si el rol es inválido)."""
    if role is None:
        return False
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def has_all_permissions(role: Role | None, *permissions: Permission) -> bool:
    """Indica si el rol posee TODOS los permisos indicados (semántica AND).

    Fail-closed: sin permisos indicados devuelve False (no se concede acceso
    por una lista vacía — un error de programación nunca debe ampliar permisos).
    """
    if not permissions:
        return False
    return all(has_permission(role, p) for p in permissions)


def has_any_permission(role: Role | None, *permissions: Permission) -> bool:
    """Indica si el rol posee AL MENOS UNO de los permisos (semántica OR).

    Fail-closed: sin permisos indicados devuelve False.
    """
    if not permissions:
        return False
    return any(has_permission(role, p) for p in permissions)


def permissions_for(role: Role | None) -> frozenset[Permission]:
    """Devuelve el conjunto completo de permisos de un rol (vacío si es inválido)."""
    if role is None:
        return frozenset()
    return ROLE_PERMISSIONS.get(role, frozenset())


def resolve_scope(role: Role | None) -> Scope:
    """Devuelve el alcance de datos de un rol (fail-closed: sin rol ⇒ OWN)."""
    if role is None:
        return Scope.OWN
    return _ROLE_SCOPE.get(role, Scope.OWN)


def player_limit(role: Role | None) -> int | None:
    """Límite de jugadores del rol (None = ilimitado; rol inválido ⇒ 0)."""
    if role is None:
        return 0
    return PLAYER_LIMITS.get(role, 0)


def has_unlimited_players(role: Role | None) -> bool:
    """Indica si el rol no tiene límite de jugadores."""
    return player_limit(role) is None


def is_within_player_limit(role: Role | None, current_count: int) -> bool:
    """Comprueba si el rol puede crear un jugador más dado el conteo actual.

    Un límite None (admin) siempre permite. Un rol inválido (límite 0) nunca
    permite crear jugadores.
    """
    limit = player_limit(role)
    if limit is None:
        return True
    return current_count < limit


def is_admin(role: Role | None) -> bool:
    """Indica si el rol es administrador (acceso global)."""
    return role is Role.ADMIN
