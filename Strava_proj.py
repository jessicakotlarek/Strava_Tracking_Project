import requests
import os
import pandas as pd
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
CODE = os.getenv("STRAVA_CODE")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

def exchange_code_for_tokens(code: str):
    """Exchange one-time code for access and refresh tokens."""
    r = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()

def refresh_access_token(refresh_token: str):
    """Refresh access token using a stored refresh token."""
    r = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()

# Step 1 — Get tokens
tokens = None
if REFRESH_TOKEN:  # Use refresh flow
    print("Refreshing access token...")
    tokens = refresh_access_token(REFRESH_TOKEN)
elif CODE:  # First-time code exchange
    print("Exchanging code for tokens...")
    tokens = exchange_code_for_tokens(CODE)
    print("\n✅ Save this refresh token to your .env file for future runs:")
    print(f"STRAVA_REFRESH_TOKEN={tokens['refresh_token']}")
    print("Then remove STRAVA_CODE from your .env.\n")
else:
    raise RuntimeError("No STRAVA_REFRESH_TOKEN or STRAVA_CODE in .env")

access_token = tokens["access_token"]


# Step 2 — Call the Strava API
headers = {"Authorization": f"Bearer {access_token}"}
resp = requests.get(
    "https://www.strava.com/api/v3/athlete/activities",
    headers=headers,
    params={"per_page": 200, "page": 1},
    timeout=30
)
resp.raise_for_status()
activities = resp.json()


# Step 3 — Print activity summaries
for activity in activities:
    name = activity['name']
    miles = activity['distance'] / 1609.34
    minutes = activity['moving_time'] / 60
    print(f"{name}: {miles:.2f} miles, {minutes:.1f} minutes")

# Step 4 — Put into DataFrame
df = pd.DataFrame(activities)
print(df.columns)
print(f"\nTotal activities fetched: {len(df)}")