import json
import os
import requests
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime, timedelta

CONFIG_FILE = "oauth2_config.json"
TOKEN_DIR = "tokens"

os.makedirs(TOKEN_DIR, exist_ok=True)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_token_file(service_name):
    return os.path.join(TOKEN_DIR, f"token_{service_name}.json")

def save_token(service_name, data):
    data["timestamp"] = datetime.utcnow().isoformat()
    with open(get_token_file(service_name), "w") as f:
        json.dump(data, f)

def load_token(service_name):
    token_path = get_token_file(service_name)
    if not os.path.exists(token_path):
        return None
    with open(token_path, "r") as f:
        data = json.load(f)
    return data

def is_token_expired(token_data):
    if "expires_in" not in token_data or "timestamp" not in token_data:
        return True
    issued_at = datetime.fromisoformat(token_data["timestamp"])
    expires_in = int(token_data["expires_in"])
    return datetime.utcnow() >= issued_at + timedelta(seconds=expires_in - 60)

def client_credentials_flow(config, service_name):
    print(f"[{service_name}] Using Client Credentials Flow")
    data = {
        "grant_type": "client_credentials",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "scope": config.get("scope", "")
    }
    response = requests.post(config["token_url"], data=data)
    response.raise_for_status()
    token_data = response.json()
    save_token(service_name, token_data)
    return token_data["access_token"]

def authorization_code_flow(config, service_name):
    token_data = load_token(service_name)

    if token_data and "refresh_token" in token_data and not is_token_expired(token_data):
        print(f"[{service_name}] Using cached access token.")
        return token_data["access_token"]

    if token_data and "refresh_token" in token_data:
        print(f"[{service_name}] Using Refresh Token")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
        }
        response = requests.post(config["token_url"], data=data)
        if response.ok:
            new_token_data = response.json()
            new_token_data["refresh_token"] = token_data["refresh_token"]
            save_token(service_name, new_token_data)
            return new_token_data["access_token"]
        else:
            print(f"[{service_name}] Refresh failed, re-authenticating.")

    print(f"[{service_name}] Starting Authorization Code Flow")
    params = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "scope": config.get("scope", ""),
    }
    url = f"{config['auth_url']}?{urlencode(params)}"
    print(f"[{service_name}] Open this URL in your browser to authorize:
{url}")
    webbrowser.open(url)

    redirect_response = input("Paste the full redirect URL after authorization:\n")
    code = parse_qs(urlparse(redirect_response).query)["code"][0]

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config["redirect_uri"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
    }
    response = requests.post(config["token_url"], data=data)
    response.raise_for_status()
    token_data = response.json()
    save_token(service_name, token_data)
    return token_data["access_token"]

def get_access_token(service_name, config):
    flow = config["flow"]
    if flow == "client_credentials":
        return client_credentials_flow(config, service_name)
    elif flow == "authorization_code":
        return authorization_code_flow(config, service_name)
    else:
        raise ValueError(f"[{service_name}] Unsupported flow type: {flow}")

def main():
    config_data = load_config()
    for service_name, service_config in config_data.items():
        print(f"\n=== Handling {service_name} ===")
        try:
            token = get_access_token(service_name, service_config)
            print(f"[{service_name}] Access Token: {token[:30]}... (truncated)")
        except Exception as e:
            print(f"[{service_name}] Error: {e}")

if __name__ == "__main__":
    main()