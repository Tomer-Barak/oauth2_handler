# OAuth2 Handler

[![PyPI version](https://badge.fury.io/py/oauth2handler.svg)](https://badge.fury.io/py/oauth2handler)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, flexible OAuth2 client library for developers.

## Installation

```bash
pip install oauth2handler
```

## Features

- Supports multiple OAuth2 flows:
  - Client Credentials
  - Authorization Code (with automatic token refresh)
  - PKCE extension for public clients
- Token management with persistent storage
- Command-line interface
- Simple API for integration into applications
- Error handling and logging
- Token revocation support
- Configurable via JSON or programmatically

## Why Use OAuth2 Handler?

- **Simple Interface**: Easy to use in your applications with minimal boilerplate
- **Automatic Token Management**: Handles token refresh and persistence automatically
- **CLI Tool**: Use it in scripts or from the command line
- **Support for Multiple Services**: Configure once, use everywhere
- **PKCE Support**: Secure authentication for public clients

## Installation

```bash
pip install oauth2handler
```

Or install from source:

```bash
git clone https://github.com/username/oauth2handler.git
cd oauth2handler
pip install -e .
```

## Quick Start

### Configuration

Create a configuration file named `oauth2_config.json`:

```json
{
  "github": {
    "flow": "authorization_code",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "redirect_uri": "http://localhost",
    "scope": "repo user"
  },
  "api_service": {
    "flow": "client_credentials",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "token_url": "https://api.example.com/oauth2/token",
    "scope": "read write"
  }
}
```

### Command Line Usage

Get a token for a service:

```bash
oauth2 --service github token
```

Force token refresh:

```bash
oauth2 --service github token --force
```

Display full token information:

```bash
oauth2 --service github token --full
```

Show token information:

```bash
oauth2 --service github info
```

List available services:

```bash
oauth2 --list
```

### Python API

```python
from oauth2handler import OAuth2Client, OAuth2Config

# Create a client directly
config = OAuth2Config(
    flow="authorization_code",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    auth_url="https://github.com/login/oauth/authorize",
    token_url="https://github.com/login/oauth/access_token",
    redirect_uri="http://localhost",
    scope="repo user"
)

client = OAuth2Client("github", config)
token = client.get_access_token()

# Or load from config file
clients = OAuth2Client.from_config_file("oauth2_config.json")
github_client = clients["github"]
token = github_client.get_access_token()

# Use the token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.github.com/user", headers=headers)
```

## PKCE Support

For public clients (e.g., mobile apps, SPAs), you should use PKCE:

```json
{
  "spotify": {
    "flow": "authorization_code",
    "client_id": "YOUR_CLIENT_ID",
    "auth_url": "https://accounts.spotify.com/authorize",
    "token_url": "https://accounts.spotify.com/api/token",
    "redirect_uri": "http://localhost",
    "scope": "user-read-private user-read-email",
    "use_pkce": true
  }
}
```

## Custom Authorization Callback

For better integration in GUI applications, you can provide a custom authorization callback:

```python
def auth_callback(auth_url):
    # Show the URL in your app's UI
    # Wait for the user to authorize
    # Return the redirect URL
    return redirect_url

client = OAuth2Client(
    "github", 
    config, 
    auth_callback=auth_callback
)
token = client.get_access_token()
```

## Error Handling

```python
from oauth2handler import OAuth2Error, TokenError, AuthorizationError

try:
    token = client.get_access_token()
except TokenError as e:
    print(f"Token error: {e}")
except AuthorizationError as e:
    print(f"Authorization error: {e}")
except OAuth2Error as e:
    print(f"OAuth2 error: {e}")
```

## Project Structure

```
oauth2handler/
├── __init__.py          # Package exports and version
├── cli.py               # Command-line interface
├── exceptions.py        # OAuth2-specific exceptions
├── oauth2_client.py     # Main client implementation
└── utils.py             # Helper utilities for token management
tests/
├── test_oauth2handler.py # Main package tests
└── test_cli.py          # CLI tests
setup.py                 # Package installation script
oauth2_cli.py            # CLI entry point
example.py               # Usage examples
oauth2_config.json       # Your service configurations
oauth2_config_example.json # Example configurations
README.md                # Documentation
LICENSE                  # MIT License file
CHANGELOG.md             # Version history and changes
CONTRIBUTING.md          # Guide for contributors
.gitignore               # Git ignore patterns
```

## Usage Examples

### Example 1: GitHub Profile with Authorization Code Flow

This example demonstrates how to authenticate with GitHub and fetch your profile information:

```python
import requests
from oauth2handler import OAuth2Client, OAuth2Config

# Create configuration for GitHub
config = OAuth2Config(
    flow="authorization_code",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    auth_url="https://github.com/login/oauth/authorize",
    token_url="https://github.com/login/oauth/access_token",
    redirect_uri="http://localhost",
    scope="repo user"
)

# Create client and get token
client = OAuth2Client("github", config)
token = client.get_access_token()

# Use the token to access GitHub API
headers = {"Authorization": f"token {token}"}
response = requests.get("https://api.github.com/user", headers=headers)
user_data = response.json()

print(f"Hello, {user_data.get('name')}!")
print(f"You have {user_data.get('public_repos')} public repositories.")
```

### Example 2: Spotify API with PKCE

This example shows how to use PKCE flow with Spotify API (useful for public clients):

```python
import requests
from oauth2handler import OAuth2Client, OAuth2Config

# Create config with PKCE enabled
config = OAuth2Config(
    flow="authorization_code",
    client_id="YOUR_SPOTIFY_CLIENT_ID",
    auth_url="https://accounts.spotify.com/authorize",
    token_url="https://accounts.spotify.com/api/token",
    redirect_uri="http://localhost",
    scope="user-read-private user-read-email",
    use_pkce=True  # Enable PKCE
)

client = OAuth2Client("spotify", config)
token = client.get_access_token()

# Use the token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.spotify.com/v1/me", headers=headers)
profile = response.json()

print(f"Logged in as: {profile.get('display_name')}")
```

### Example 3: Client Credentials Flow for API Access

For service-to-service authentication without user involvement:

```python
from oauth2handler import OAuth2Client, OAuth2Config

# Create config for a service using client credentials
config = OAuth2Config(
    flow="client_credentials",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    token_url="https://api.example.com/oauth2/token",
    scope="read write"
)

client = OAuth2Client("api_service", config)
token = client.get_access_token()

# Use the token for API access
# ...
```

### Example 4: Loading Multiple Clients from Config File

Manage multiple OAuth2 services from a single config file:

```python
from oauth2handler import OAuth2Client

# Load all clients from config
clients = OAuth2Client.from_config_file("oauth2_config.json")

# Get tokens for specific services
github_token = clients["github"].get_access_token()
api_token = clients["api_service"].get_access_token()

# Use the tokens as needed
# ...
```

### Example 5: Custom Authorization Callback for GUI Apps

For better integration with GUI applications:

```python
from oauth2handler import OAuth2Client, OAuth2Config
import tkinter as tk
from tkinter import simpledialog

def gui_auth_callback(auth_url):
    """Show auth URL in a dialog and get redirect URL from user"""
    root = tk.Tk()
    root.withdraw()
    
    # Show instructions with the auth URL
    tk.messagebox.showinfo(
        "Authorization Required",
        f"Please open this URL in your browser:\n\n{auth_url}\n\n"
        "After authorization, copy the redirect URL from your browser."
    )
    
    # Get the redirect URL from user
    redirect_url = simpledialog.askstring(
        "Enter Redirect URL", 
        "Paste the redirect URL from your browser:"
    )
    
    root.destroy()
    return redirect_url

# Create client with custom callback
client = OAuth2Client(
    "github", 
    config, 
    auth_callback=gui_auth_callback
)
token = client.get_access_token()
# Use the token...
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 OAuth2 Handler Contributors

The MIT License is a permissive license that allows for reuse with few restrictions. It permits use, modification, distribution, and private or commercial use while providing only minimal liability protection for the author.
