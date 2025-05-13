# Changelog

All notable changes to the OAuth2 Handler project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-05-13

### Fixed
- Fixed datetime.utcnow() deprecation warning by using timezone-aware objects
- Improved error handling for token refresh failures

### Added
- Additional documentation for setup and configuration
- GitHub Actions workflows for CI/CD

## [0.1.0] - 2025-05-13

### Added
- Initial release of OAuth2 Handler
- Support for Client Credentials flow
- Support for Authorization Code flow with automatic refresh
- PKCE extension support for public clients
- Token persistence with file storage
- Command-line interface
- Token revocation support
- Error handling and logging
- Example configurations for popular services (GitHub, Google, Spotify)
