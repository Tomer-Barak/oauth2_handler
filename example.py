#!/usr/bin/env python
"""
Example usage of OAuth2Handler
"""
import json
import requests
from oauth2handler import OAuth2Client, OAuth2Config

def example_github_profile():
    """Example: Get GitHub profile with OAuth2"""
    # Load configuration
    with open("oauth2_config.json", "r") as f:
        config_data = json.load(f)
        
    if "github" not in config_data:
        print("No 'github' configuration found in oauth2_config.json")
        print("Please add GitHub OAuth2 configuration first")
        return
        
    # Create client from config
    github_config = config_data["github"]
    config = OAuth2Config(
        flow=github_config["flow"],
        client_id=github_config["client_id"],
        client_secret=github_config["client_secret"],
        auth_url=github_config["auth_url"],
        token_url=github_config["token_url"],
        redirect_uri=github_config["redirect_uri"],
        scope=github_config.get("scope")
    )
    
    # Alternative: use from_dict method
    # client = OAuth2Client.from_dict("github", github_config)
    
    client = OAuth2Client("github", config)
    
    try:
        # Get an access token
        token = client.get_access_token()
        print(f"Got access token: {token[:10]}... (truncated)")
        
        # Use the token to access GitHub API
        headers = {"Authorization": f"token {token}"}
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        print("\nGitHub Profile:")
        print(f"  Username: {user_data.get('login')}")
        print(f"  Name: {user_data.get('name')}")
        print(f"  Email: {user_data.get('email')}")
        print(f"  Location: {user_data.get('location')}")
        print(f"  Public repos: {user_data.get('public_repos')}")
        
    except Exception as e:
        print(f"Error: {e}")
        
def example_spotify_with_pkce():
    """Example: Get Spotify profile with PKCE"""
    # Create config directly
    config = OAuth2Config(
        flow="authorization_code",
        client_id="YOUR_SPOTIFY_CLIENT_ID",  # Replace with your client ID
        auth_url="https://accounts.spotify.com/authorize",
        token_url="https://accounts.spotify.com/api/token",
        redirect_uri="http://localhost",
        scope="user-read-private user-read-email",
        use_pkce=True  # Enable PKCE
    )
    
    client = OAuth2Client("spotify", config)
    
    try:
        # Get an access token
        token = client.get_access_token()
        print(f"Got Spotify access token: {token[:10]}... (truncated)")
        
        # Use the token to access Spotify API
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        print("\nSpotify Profile:")
        print(f"  Username: {user_data.get('id')}")
        print(f"  Display Name: {user_data.get('display_name')}")
        print(f"  Email: {user_data.get('email')}")
        print(f"  Country: {user_data.get('country')}")
        print(f"  Product: {user_data.get('product')}")
        
    except Exception as e:
        print(f"Error: {e}")

def example_load_all_clients():
    """Example: Load all clients from config file"""
    clients = OAuth2Client.from_config_file("oauth2_config.json")
    
    print("Available services:")
    for name, client in clients.items():
        print(f"  - {name} ({client.config.flow})")
        
    # Get token for a specific service
    if "api_service" in clients:
        try:
            token = clients["api_service"].get_access_token()
            print(f"Got API service token: {token[:10]}... (truncated)")
        except Exception as e:
            print(f"Error getting API service token: {e}")

if __name__ == "__main__":
    print("OAuth2Handler Example")
    print("=====================\n")
    
    # Uncomment the example you want to run
    example_github_profile()
    # example_spotify_with_pkce()
    # example_load_all_clients()
