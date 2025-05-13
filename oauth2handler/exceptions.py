"""
OAuth2 Handler Exceptions
"""

class OAuth2Error(Exception):
    """Base exception for OAuth2 Handler errors."""
    pass


class TokenError(OAuth2Error):
    """Raised when there's an issue with token retrieval or refresh."""
    pass


class ConfigurationError(OAuth2Error):
    """Raised when there's an issue with the configuration."""
    pass


class AuthorizationError(OAuth2Error):
    """Raised when there's an issue with the authorization process."""
    pass
