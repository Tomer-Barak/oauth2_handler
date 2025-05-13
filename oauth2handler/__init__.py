"""
OAuth2 Handler - A simple OAuth2 client library for developers

This library provides a simple interface for handling OAuth2 authentication flows
including client credentials and authorization code flows with automatic token refresh.

MIT License
Copyright (c) 2025 OAuth2 Handler Contributors
See LICENSE file for details.
"""

from .oauth2_client import OAuth2Client, OAuth2Config
from .exceptions import OAuth2Error

__version__ = "0.1.0"
__all__ = ["OAuth2Client", "OAuth2Config", "OAuth2Error"]
