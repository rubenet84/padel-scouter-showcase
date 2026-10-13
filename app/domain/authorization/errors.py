"""Excepciones de autorización del dominio.

Son puras (no dependen de FastAPI ni SQLAlchemy). La capa API las traducirá a
los códigos HTTP correspondientes en fases posteriores:

- PermissionDeniedError      -> 403
- ResourceNotFoundError      -> 404 (recurso ajeno o inexistente; no revela existencia)
- PlayerLimitExceededError   -> 409 (o 403) según decida la capa API
"""


class AuthorizationError(Exception):
    """Error base de autorización."""


class PermissionDeniedError(AuthorizationError):
    """El usuario no posee el permiso requerido."""


class ResourceNotFoundError(AuthorizationError):
    """El recurso no existe o no es accesible para el usuario.

    Se usa tanto para recursos inexistentes como para recursos de otro usuario,
    de modo que la capa API responda 404 sin revelar la existencia de recursos
    ajenos (anti-IDOR/BOLA).
    """


class PlayerLimitExceededError(AuthorizationError):
    """El usuario alcanzó el límite de jugadores de su rol/plan."""
