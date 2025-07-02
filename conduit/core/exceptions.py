class ConduitError(Exception):
    """Base exception for all Conduit errors."""

    pass


class ConfigurationError(ConduitError):
    """Raised when there is a configuration error."""

    pass


class PlatformError(ConduitError):
    """Raised when there is a platform-specific error."""

    pass
