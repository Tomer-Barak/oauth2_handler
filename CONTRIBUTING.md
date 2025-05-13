# Contributing to OAuth2 Handler

Thank you for your interest in contributing to the OAuth2 Handler project! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/oauth2handler.git
   cd oauth2handler
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   ```
4. Install development dependencies:
   ```bash
   pip install pytest pytest-cov
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-or-bugfix-name
   ```
2. Make your changes
3. Run tests to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```
4. Add or update tests to cover your changes
5. Update documentation if needed
6. Commit your changes with descriptive commit messages
7. Push your branch to GitHub
8. Create a pull request against the main branch

## Code Style

This project follows PEP 8 style guidelines. Please ensure your code conforms to these guidelines before submitting a PR.

## Running Tests

```bash
pytest
```

For coverage report:
```bash
pytest --cov=oauth2handler tests/
```

## Adding Support for New OAuth2 Providers

When adding support for a new OAuth2 provider, please:

1. Add example config to `oauth2_config_example.json`
2. Add documentation in the README
3. Add a test case if specific provider behavior is implemented

## Release Process

1. Update version in `oauth2handler/__init__.py` and `setup.py`
2. Update CHANGELOG.md
3. Tag the release commit with the version number
4. Build and upload to PyPI

## Code of Conduct

Please be respectful and considerate of others when contributing to the project.

Thank you for your contributions!
