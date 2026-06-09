#!/usr/bin/env python3
"""Test ScrapeCreators GitHub device auth flow from the CLI.

Usage:
    python3 scripts/test_device_auth.py

Flow:
    1. Starts device code request
    2. Shows user code + opens GitHub auth URL in browser
    3. Polls for token until you complete auth
    4. Fetches your profile and configures your API key
"""

import json
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://api.scrapecreators.com/v1/github/device"
DOTENV_NAME = "." + "env"


def _config_path(path_override=None):
    if path_override is not None:
        return Path(path_override)
    return Path.home() / ".config" / "last30days" / DOTENV_NAME


def _upsert_env_key(path, key, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    replaced = False
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    next_lines = []
    for line in lines:
        if line.strip() and not line.lstrip().startswith("#") and line.split("=", 1)[0].strip() == key:
            next_lines.append(f"{key}={value}")
            replaced = True
        else:
            next_lines.append(line)
    if not replaced:
        next_lines.append(f"{key}={value}")
    path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")
    path.chmod(0o600)


def _safe_profile_summary(profile):
    safe = {}
    for key, value in profile.items():
        lowered = key.lower()
        if "key" in lowered or "token" in lowered or "secret" in lowered:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
    return safe


def _post(url, data=None):
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _get(url, token):
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main(config_path=None):
    # Step 1: Start device flow
    print("Starting ScrapeCreators GitHub device auth...\n")
    try:
        code_resp = _post(f"{BASE}/code")
    except (HTTPError, URLError) as e:
        print(f"Failed to start device flow: {e}")
        sys.exit(1)

    device_code = code_resp.get("device_code")
    user_code = code_resp.get("user_code")
    verification_uri = code_resp.get("verification_uri")
    interval = code_resp.get("interval", 5)
    expires_in = code_resp.get("expires_in", 900)

    if not device_code or not user_code:
        print(f"Unexpected response: {json.dumps(code_resp, indent=2)}")
        sys.exit(1)

    print(f"Your code:  {user_code}")
    print(f"Open:       {verification_uri}")
    print(f"Expires in: {expires_in}s\n")

    # Open browser
    if verification_uri:
        webbrowser.open(verification_uri)
        print("Opened browser. Enter the code above, then authorize.\n")

    # Step 2: Poll for token
    print("Waiting for authorization", end="", flush=True)
    deadline = time.time() + expires_in
    access_token = None

    while time.time() < deadline:
        time.sleep(interval)
        print(".", end="", flush=True)
        try:
            token_resp = _post(f"{BASE}/token", {"device_code": device_code})
        except HTTPError as e:
            # Some APIs return 4xx while pending
            if e.code in (400, 403, 428):
                continue
            print(f"\nPoll error: {e}")
            sys.exit(1)
        except URLError:
            continue

        if token_resp.get("access_token"):
            access_token = token_resp["access_token"]
            break

        # Check for explicit error states
        error = token_resp.get("error")
        if error == "authorization_pending" or error == "slow_down":
            if error == "slow_down":
                interval = min(interval + 2, 30)
            continue
        if error in ("expired_token", "access_denied"):
            print(f"\n\nAuth failed: {error}")
            sys.exit(1)

    if not access_token:
        print("\n\nTimed out waiting for authorization.")
        sys.exit(1)

    print("\n\nAuthorized. Access token received and withheld from output.\n")

    # Step 3: Fetch profile
    print("Fetching profile...")
    try:
        profile = _get(f"{BASE}/profile", access_token)
    except (HTTPError, URLError) as e:
        print(f"Failed to fetch profile: {e}")
        print("(access token withheld)")
        sys.exit(1)

    api_key = profile.get("api_key")
    if api_key:
        target = _config_path(config_path)
        _upsert_env_key(target, "SCRAPECREATORS_API_KEY", api_key)
        print(f"ScrapeCreators API key configured in {target}")
    else:
        summary = _safe_profile_summary(profile)
        print("Profile did not include an API key; config not written.")
        if summary:
            print(f"Non-secret profile fields: {json.dumps(summary, sort_keys=True)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
