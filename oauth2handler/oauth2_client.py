"""
OAuth2 Client implementation
"""
import json
import logging
import requests
import webbrowser
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable
from urllib.parse import urlencode, urlparse, parse_qs

from .exceptions import TokenError, ConfigurationError, AuthorizationError
from .utils import (
    save_token, load_token, is_token_expired, 
    generate_pkce_challenge, load_config_file
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class OAuth2Config:
    """OAuth2 Configuration dataclass."""
    flow: str
    client_id: str
    client_secret: Optional[str] = None
    auth_url: Optional[str] = None
    token_url: str = None
    redirect_uri: Optional[str] = None
    scope: Optional[str] = None
    use_pkce: bool = False
    extra_params: Dict[str, str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.flow not in ["client_credentials", "authorization_code"]:
            raise ConfigurationError(f"Unsupported flow: {self.flow}")
            
        if self.flow == "authorization_code" and not self.auth_url:
            raise ConfigurationError("Authorization URL required for authorization_code flow")
            
        if self.flow == "authorization_code" and not self.redirect_uri:
            raise ConfigurationError("Redirect URI required for authorization_code flow")
            
        if not self.token_url:
            raise ConfigurationError("Token URL is required")
            
        if not self.client_id:
            raise ConfigurationError("Client ID is required")
            
        # Client secret is optional for PKCE flows
        if not self.client_secret and not self.use_pkce and self.flow != "implicit":
            raise ConfigurationError("Client secret is required for non-PKCE flows")

        # Initialize extra params if not provided
        if self.extra_params is None:
            self.extra_params = {}


class OAuth2Client:
    """OAuth2 Client for handling authentication flows."""
    
    def __init__(
        self, 
        service_name: str, 
        config: OAuth2Config,
        token_persistence: bool = True,
        auth_callback: Optional[Callable[[str], str]] = None
    ):
        """Initialize the OAuth2 client.
        
        Args:
            service_name: Name of the service (used for token storage)
            config: OAuth2Config object with the configuration
            token_persistence: Whether to save tokens to disk
            auth_callback: Optional callback function to handle authorization
                           If not provided, will use input() to get the redirect URL
        """
        self.service_name = service_name
        self.config = config
        self.token_persistence = token_persistence
        self.auth_callback = auth_callback
        self._pkce_verifier = None

    def get_access_token(self, force_refresh: bool = False) -> str:
        """Get an access token using the configured flow.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Access token string
        """
        if self.config.flow == "client_credentials":
            return self._client_credentials_flow()
        elif self.config.flow == "authorization_code":
            return self._authorization_code_flow(force_refresh)
        else:
            raise ConfigurationError(f"Unsupported flow: {self.config.flow}")
            
    def _client_credentials_flow(self) -> str:
        """Execute client credentials flow.
        
        Returns:
            Access token string
        """
        logger.info(f"[{self.service_name}] Using Client Credentials Flow")
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        
        if self.config.scope:
            data["scope"] = self.config.scope
            
        # Add any extra parameters
        data.update(self.config.extra_params)
        
        try:
            response = requests.post(self.config.token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            if self.token_persistence:
                save_token(self.service_name, token_data)
                
            return token_data["access_token"]
        except requests.RequestException as e:
            raise TokenError(f"Failed to get access token: {e}")

    def _authorization_code_flow(self, force_refresh: bool = False) -> str:
        """Execute authorization code flow with automatic token refresh.
        
        Args:
            force_refresh: Force token refresh even if current token is valid
            
        Returns:
            Access token string
        """
        if not force_refresh and self.token_persistence:
            token_data = load_token(self.service_name)
            
            if token_data and "refresh_token" in token_data and not is_token_expired(token_data):
                logger.info(f"[{self.service_name}] Using cached access token")
                return token_data["access_token"]
                
            if token_data and "refresh_token" in token_data:
                try:
                    return self._refresh_token(token_data["refresh_token"])
                except TokenError as e:
                    logger.warning(f"[{self.service_name}] Refresh failed: {e}")
                    # Continue with full auth flow
        
        # Generate PKCE challenge if needed
        pkce_data = None
        if self.config.use_pkce:
            pkce_data = generate_pkce_challenge()
            self._pkce_verifier = pkce_data["code_verifier"]
            
        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
        }
        
        if self.config.scope:
            auth_params["scope"] = self.config.scope
            
        # Add PKCE challenge if present
        if pkce_data:
            auth_params["code_challenge"] = pkce_data["code_challenge"]
            auth_params["code_challenge_method"] = "S256"
            
        # Add any extra parameters
        auth_params.update(self.config.extra_params)
        
        auth_url = f"{self.config.auth_url}?{urlencode(auth_params)}"
        
        logger.info(f"[{self.service_name}] Starting Authorization Code Flow")
        logger.info(f"[{self.service_name}] Authorization URL: {auth_url}")
        
        # Open browser or provide URL for authorization
        webbrowser.open(auth_url)
        
        # Get authorization code from redirect
        if self.auth_callback:
            redirect_response = self.auth_callback(auth_url)
        else:
            redirect_response = input("Paste the full redirect URL after authorization: ")
            
        try:
            parsed_url = urlparse(redirect_response)
            query_params = parse_qs(parsed_url.query)
            
            if "error" in query_params:
                error = query_params["error"][0]
                error_description = query_params.get("error_description", [""])[0]
                raise AuthorizationError(
                    f"Authorization error: {error} - {error_description}"
                )
                
            if "code" not in query_params:
                raise AuthorizationError("No authorization code found in redirect URL")
                
            code = query_params["code"][0]
        except Exception as e:
            raise AuthorizationError(f"Failed to parse redirect URL: {e}")
        
        # Exchange code for tokens
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
        }
        
        # Add client secret if not using PKCE
        if not self.config.use_pkce:
            token_data["client_secret"] = self.config.client_secret
        elif self._pkce_verifier:
            token_data["code_verifier"] = self._pkce_verifier
            
        try:
            response = requests.post(self.config.token_url, data=token_data)
            response.raise_for_status()
            token_data = response.json()
            
            if self.token_persistence:
                save_token(self.service_name, token_data)
                
            return token_data["access_token"]
        except requests.RequestException as e:
            raise TokenError(f"Failed to exchange code for token: {e}")
            
    def _refresh_token(self, refresh_token: str) -> str:
        """Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New access token
            
        Raises:
            TokenError: If token refresh fails
        """
        logger.info(f"[{self.service_name}] Using Refresh Token")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
        }
        
        # Add client secret if not using PKCE
        if not self.config.use_pkce:
            data["client_secret"] = self.config.client_secret
              try:
            response = requests.post(self.config.token_url, data=data)
            
            # Handle common error responses with more detailed information
            if not response.ok:
                error_data = {}
                try:
                    error_data = response.json()
                except Exception:
                    pass
                
                error_desc = error_data.get("error_description", "")
                error_type = error_data.get("error", "")
                status_code = response.status_code
                
                if error_type == "invalid_grant":
                    raise TokenError(f"Refresh token expired or revoked: {error_desc}")
                elif status_code == 429:
                    raise TokenError(f"Rate limit exceeded: {error_desc}")
                else:
                    raise TokenError(f"Token refresh failed: {status_code} - {error_type} {error_desc}")
            
            token_data = response.json()
            
            # Most services don't return a new refresh token, so keep the old one
            if "refresh_token" not in token_data:
                token_data["refresh_token"] = refresh_token
                
            if self.token_persistence:
                save_token(self.service_name, token_data)
                
            return token_data["access_token"]
        except requests.RequestException as e:
            logger.error(f"[{self.service_name}] Network error during token refresh: {e}")
            raise TokenError(f"Token refresh network error: {e}")
            
    def revoke_token(self, token_type: str = "access_token") -> bool:
        """Revoke a token if the service supports token revocation.
        
        Args:
            token_type: Type of token to revoke ('access_token' or 'refresh_token')
            
        Returns:
            True if successful, False otherwise
        """
        if not hasattr(self.config, "revocation_url") or not self.config.revocation_url:
            logger.warning(f"[{self.service_name}] No revocation URL configured")
            return False
            
        token_data = load_token(self.service_name)
        if not token_data or token_type not in token_data:
            logger.warning(f"[{self.service_name}] No {token_type} to revoke")
            return False
            
        data = {
            "token": token_data[token_type],
            "client_id": self.config.client_id,
            "token_type_hint": token_type,
        }
        
        if self.config.client_secret:
            data["client_secret"] = self.config.client_secret
            
        try:
            response = requests.post(self.config.revocation_url, data=data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"[{self.service_name}] Token revocation failed: {e}")
            return False
            
    @staticmethod
    def from_dict(service_name: str, config_dict: Dict[str, Any], **kwargs) -> 'OAuth2Client':
        """Create an OAuth2Client from a configuration dictionary.
        
        Args:
            service_name: Name of the service
            config_dict: Dictionary with configuration
            **kwargs: Additional arguments to pass to OAuth2Client constructor
            
        Returns:
            OAuth2Client instance
        """
        config = OAuth2Config(
            flow=config_dict.get("flow"),
            client_id=config_dict.get("client_id"),
            client_secret=config_dict.get("client_secret"),
            auth_url=config_dict.get("auth_url"),
            token_url=config_dict.get("token_url"),
            redirect_uri=config_dict.get("redirect_uri"),
            scope=config_dict.get("scope"),
            use_pkce=config_dict.get("use_pkce", False),
            extra_params=config_dict.get("extra_params", {})
        )
        return OAuth2Client(service_name, config, **kwargs)
    
    @classmethod
    def from_config_file(cls, config_file: str, **kwargs) -> Dict[str, 'OAuth2Client']:
        """Create OAuth2Client instances from a configuration file.
        
        Args:
            config_file: Path to the configuration file
            **kwargs: Additional arguments to pass to OAuth2Client constructor
            
        Returns:
            Dictionary mapping service names to OAuth2Client instances
        """
        config_data = load_config_file(config_file)
        clients = {}
        
        for service_name, service_config in config_data.items():
            try:
                clients[service_name] = cls.from_dict(service_name, service_config, **kwargs)
            except ConfigurationError as e:
                logger.error(f"Failed to create client for {service_name}: {e}")
                
        return clients
