import requests
from scripts.utils.env import write_env_var

def get_access_token(username, password, env_path, api_base_url) -> str:
    if not username or not password:
        raise RuntimeError("[ERROR] Missing DADOSFERA_USERNAME or DADOSFERA_PASSWORD")

    print("[INFO] Signing in to Dadosfera")

    response = requests.post(
        f"{api_base_url}/auth/sign-in",
        headers={
            "accept": "application/json",
            "content-type": "application/json"
        },
        json={
            "username": username,
            "password": password
        }
    )

    if response.status_code != 200:
        print("[ERROR] Authentication failed")
        print(response.status_code, response.text)
        raise SystemExit(1)

    data = response.json()
    token = data["tokens"]["accessToken"]

    if not token:
        raise RuntimeError("[ERROR] accessToken not found in response")

    write_env_var("DADOSFERA_ACCESS_TOKEN", token, env_path)

    print("[INFO] Access token obtained and saved to .env")

    return token