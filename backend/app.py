import requests

API_KEY = "aa5c9232acdc45c0955c38f9dd629599"  # replace with your real API key
HEADERS = {"X-Auth-Token": API_KEY}
BASE_URL = "https://api.football-data.org/v4"

response = requests.get(f"{BASE_URL}/competitions/PL/matches", headers=HEADERS)

if response.status_code == 200:
    data = response.json()
    if response.status_code == 200:
        data = response.json()

        for match in data["matches"][:5]:  # first 5 matches
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            goals = match["score"]["fullTime"]
            print(f"{home} vs {away} -> Full-time: {goals['home']} - {goals['away']}")
else:
    print("Error:", response.status_code, response.text)