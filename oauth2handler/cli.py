"""
Command-line interface for OAuth2 Handler
"""
import argparse
import json
import logging
import sys
from typing import Dict, Any

from .oauth2_client import OAuth2Client
from .exceptions import OAuth2Error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("oauth2handler")


def setup_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(description="OAuth2 Handler CLI")
    
    # Main arguments
    parser.add_argument("-c", "--config", default="oauth2_config.json",
                        help="Path to configuration file (default: oauth2_config.json)")
    parser.add_argument("-s", "--service", help="Name of the service to authenticate with")
    parser.add_argument("--list", action="store_true", help="List available services")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-persist", action="store_true", 
                        help="Don't persist tokens to disk")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Get token command
    token_parser = subparsers.add_parser("token", help="Get an access token")
    token_parser.add_argument("--force", action="store_true", 
                             help="Force token refresh")
    token_parser.add_argument("--full", action="store_true",
                             help="Display full token response")
    
    # Revoke token command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke a token")
    revoke_parser.add_argument("--type", choices=["access_token", "refresh_token"],
                              default="access_token", help="Type of token to revoke")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show token information")
    
    return parser


def display_services(clients: Dict[str, OAuth2Client]) -> None:
    """Display available services."""
    print("\nAvailable services:")
    for name, client in clients.items():
        print(f"  - {name} ({client.config.flow})")


def get_token_command(args, client: OAuth2Client) -> None:
    """Execute the token command."""
    try:
        token = client.get_access_token(force_refresh=args.force)
        
        if args.full:
            token_data = {}
            if client.token_persistence:
                from .utils import load_token
                token_data = load_token(client.service_name) or {}
            
            print(json.dumps(token_data, indent=2))
        else:
            print(f"Access Token: {token[:30]}... (truncated)")
    except OAuth2Error as e:
        logger.error(f"Failed to get token: {e}")
        sys.exit(1)


def revoke_token_command(args, client: OAuth2Client) -> None:
    """Execute the revoke command."""
    if client.revoke_token(token_type=args.type):
        print(f"Successfully revoked {args.type}")
    else:
        print(f"Failed to revoke {args.type}")
        sys.exit(1)


def info_command(args, client: OAuth2Client) -> None:
    """Execute the info command."""
    from .utils import load_token, is_token_expired
    
    token_data = load_token(client.service_name)
    
    if not token_data:
        print("No token data found")
        return
        
    is_expired = is_token_expired(token_data)
    has_refresh = "refresh_token" in token_data
    
    print("\nToken Information:")
    print(f"  Service:       {client.service_name}")
    print(f"  Flow:          {client.config.flow}")
    print(f"  Expired:       {'Yes' if is_expired else 'No'}")
    print(f"  Refresh Token: {'Yes' if has_refresh else 'No'}")
    
    if "scope" in token_data:
        print(f"  Scope:         {token_data['scope']}")
        
    if "expires_in" in token_data:
        print(f"  Expires In:    {token_data['expires_in']} seconds")


def main():
    """Main entry point for the CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        clients = OAuth2Client.from_config_file(
            args.config, 
            token_persistence=not args.no_persist
        )
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
        
    if args.list:
        display_services(clients)
        return
        
    if not args.service:
        if len(clients) == 1:
            args.service = list(clients.keys())[0]
        else:
            logger.error("Please specify a service with --service")
            display_services(clients)
            sys.exit(1)
            
    if args.service not in clients:
        logger.error(f"Service '{args.service}' not found in configuration")
        display_services(clients)
        sys.exit(1)
        
    client = clients[args.service]
    
    # Execute commands
    if args.command == "token":
        get_token_command(args, client)
    elif args.command == "revoke":
        revoke_token_command(args, client)
    elif args.command == "info":
        info_command(args, client)
    else:
        # Default to getting a token
        get_token_command(argparse.Namespace(force=False, full=False), client)


if __name__ == "__main__":
    main()
