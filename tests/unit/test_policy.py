"""
Tests unitarios de la política de autorización (app/domain/authorization/policy.py).

Verifican la fuente única de verdad de roles, permisos, alcance y límites:
- Parseo fail-safe de roles.
- Matriz rol → permisos (admin / entrenador / jugador).
- Límites de jugadores por rol.
- Alcance por rol.
- Comportamiento fail-closed ante roles inválidos.
"""
from app.domain.authorization.policy import (
    Permission,
    Role,
    Scope,
    has_permission,
    has_unlimited_players,
    is_admin,
    is_within_player_limit,
    permissions_for,
    player_limit,
    resolve_scope,
    role_from_value,
)


class TestRoleFromValue:

    def test_parsea_roles_validos(self):
        assert role_from_value("admin") is Role.ADMIN
        assert role_from_value("entrenador") is Role.ENTRENADOR
        assert role_from_value("jugador") is Role.JUGADOR

    def test_acepta_mayusculas_yespacios(self):
        assert role_from_value("  ADMIN ") is Role.ADMIN
        assert role_from_value("Jugador") is Role.JUGADOR

    def test_pasa_enum_directamente(self):
        assert role_from_value(Role.ENTRENADOR) is Role.ENTRENADOR

    def test_rol_desconocido_devuelve_none(self):
        assert role_from_value("viewer") is None
        assert role_from_value("superuser") is None
        assert role_from_value("") is None

    def test_valor_no_string_devuelve_none(self):
        assert role_from_value(None) is None
        assert role_from_value(123) is None


class TestHasPermissionAdmin:

    def test_admin_tiene_todos_los_permisos(self):
        for permiso in Permission:
            assert has_permission(Role.ADMIN, permiso) is True

    def test_admin_gestiona_usuarios_y_auditoria(self):
        assert has_permission(Role.ADMIN, Permission.USERS_CHANGE_ROLE)
        assert has_permission(Role.ADMIN, Permission.USERS_SUSPEND)
        assert has_permission(Role.ADMIN, Permission.AUDIT_READ)
        assert has_permission(Role.ADMIN, Permission.SYSTEM_MANAGE)


class TestHasPermissionEntrenador:

    def test_entrenador_gestiona_jugadores(self):
        assert has_permission(Role.ENTRENADOR, Permission.PLAYERS_CREATE)
        assert has_permission(Role.ENTRENADOR, Permission.PLAYERS_READ)
        assert has_permission(Role.ENTRENADOR, Permission.PLAYERS_UPDATE)
        assert has_permission(Role.ENTRENADOR, Permission.PLAYERS_DELETE)

    def test_entrenador_puede_restaurar_y_comparar(self):
        assert has_permission(Role.ENTRENADOR, Permission.PLAYERS_RESTORE)
        assert has_permission(Role.ENTRENADOR, Permission.STATS_COMPARE)

    def test_entrenador_no_gestiona_usuarios(self):
        assert has_permission(Role.ENTRENADOR, Permission.USERS_READ) is False
        assert has_permission(Role.ENTRENADOR, Permission.USERS_CHANGE_ROLE) is False
        assert has_permission(Role.ENTRENADOR, Permission.AUDIT_READ) is False
        assert has_permission(Role.ENTRENADOR, Permission.SYSTEM_MANAGE) is False


class TestHasPermissionJugador:

    def test_jugador_gestiona_sus_jugadores(self):
        assert has_permission(Role.JUGADOR, Permission.PLAYERS_CREATE)
        assert has_permission(Role.JUGADOR, Permission.PLAYERS_READ)
        assert has_permission(Role.JUGADOR, Permission.PLAYERS_UPDATE)
        assert has_permission(Role.JUGADOR, Permission.PLAYERS_DELETE)

    def test_jugador_gestiona_partidos_e_ia(self):
        assert has_permission(Role.JUGADOR, Permission.MATCHES_CREATE)
        assert has_permission(Role.JUGADOR, Permission.AI_ANALYZE)
        assert has_permission(Role.JUGADOR, Permission.AI_CHAT)

    def test_reportes_solo_admin_y_entrenador(self):
        # jugador NO tiene reports.* (generar/descargar PDF); admin y entrenador SÍ.
        assert has_permission(Role.JUGADOR, Permission.REPORTS_GENERATE) is False
        assert has_permission(Role.JUGADOR, Permission.REPORTS_DOWNLOAD) is False
        assert has_permission(Role.ENTRENADOR, Permission.REPORTS_GENERATE) is True
        assert has_permission(Role.ENTRENADOR, Permission.REPORTS_DOWNLOAD) is True
        assert has_permission(Role.ADMIN, Permission.REPORTS_GENERATE) is True
        assert has_permission(Role.ADMIN, Permission.REPORTS_DOWNLOAD) is True

    def test_jugador_no_restaura_ni_compara(self):
        assert has_permission(Role.JUGADOR, Permission.PLAYERS_RESTORE) is False
        assert has_permission(Role.JUGADOR, Permission.STATS_COMPARE) is False

    def test_jugador_no_gestiona_usuarios_ni_sistema(self):
        assert has_permission(Role.JUGADOR, Permission.USERS_READ) is False
        assert has_permission(Role.JUGADOR, Permission.USERS_CHANGE_ROLE) is False
        assert has_permission(Role.JUGADOR, Permission.AUDIT_READ) is False
        assert has_permission(Role.JUGADOR, Permission.SYSTEM_MANAGE) is False


class TestPermisosPorRol:

    def test_conjunto_admin_es_todos(self):
        assert permissions_for(Role.ADMIN) == frozenset(Permission)

    def test_entrenador_superconjunto_de_jugador(self):
        jugador = permissions_for(Role.JUGADOR)
        entrenador = permissions_for(Role.ENTRENADOR)
        assert jugador < entrenador  # subconjunto estricto
        assert Permission.PLAYERS_RESTORE in entrenador
        assert Permission.PLAYERS_RESTORE not in jugador

    def test_rol_invalido_sin_permisos(self):
        assert permissions_for(None) == frozenset()


class TestLimitesDeJugadores:

    def test_admin_ilimitado(self):
        assert player_limit(Role.ADMIN) is None
        assert has_unlimited_players(Role.ADMIN) is True

    def test_entrenador_25(self):
        assert player_limit(Role.ENTRENADOR) == 25
        assert has_unlimited_players(Role.ENTRENADOR) is False

    def test_jugador_2(self):
        assert player_limit(Role.JUGADOR) == 2

    def test_rol_invalido_limite_cero(self):
        assert player_limit(None) == 0


class TestIsWithinPlayerLimit:

    def test_admin_siempre_puede(self):
        assert is_within_player_limit(Role.ADMIN, 0) is True
        assert is_within_player_limit(Role.ADMIN, 9999) is True

    def test_jugador_limite_2(self):
        assert is_within_player_limit(Role.JUGADOR, 0) is True
        assert is_within_player_limit(Role.JUGADOR, 1) is True
        assert is_within_player_limit(Role.JUGADOR, 2) is False
        assert is_within_player_limit(Role.JUGADOR, 3) is False

    def test_entrenador_limite_25(self):
        assert is_within_player_limit(Role.ENTRENADOR, 24) is True
        assert is_within_player_limit(Role.ENTRENADOR, 25) is False

    def test_rol_invalido_no_puede_crear(self):
        assert is_within_player_limit(None, 0) is False


class TestAlcance:

    def test_admin_global(self):
        assert resolve_scope(Role.ADMIN) is Scope.GLOBAL
        assert is_admin(Role.ADMIN) is True

    def test_entrenador_roster(self):
        assert resolve_scope(Role.ENTRENADOR) is Scope.ROSTER

    def test_jugador_own(self):
        assert resolve_scope(Role.JUGADOR) is Scope.OWN

    def test_rol_invalido_own(self):
        assert resolve_scope(None) is Scope.OWN
        assert is_admin(None) is False


class TestFailClosed:

    def test_rol_invalido_no_tiene_ningun_permiso(self):
        assert has_permission(None, Permission.PLAYERS_READ) is False
        assert has_permission(None, Permission.USERS_READ) is False
        assert has_permission(None, Permission.AI_CHAT) is False

    def test_viewer_legacy_no_tiene_permisos(self):
        # 'viewer' ya no existe: si apareciera, debe quedar sin permisos.
        rol = role_from_value("viewer")
        assert rol is None
        assert has_permission(rol, Permission.PLAYERS_READ) is False
