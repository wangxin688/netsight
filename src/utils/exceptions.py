__all__ = (
    "TokenNotProvidedError",
    "TokenInvalidError",
    "TokenExpiredError",
    "TokenInvalidForRefreshError",
    "PermissionDenyError",
    "ResourceNotFoundError",
)


class TokenNotProvidedError(Exception):
    pass


class TokenInvalidError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


class TokenInvalidForRefreshError(Exception):
    pass


class PermissionDenyError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass
