# Import libraries
import requests
import json
from prometheus_client import start_http_server, Gauge
import time

# Defining metrics for Prometheus ... These are containers
home_goals_metric = Gauge(
    "football_home_goals",              # Defined by me
    "Goals scored by home team",        # Defined by me
    ["match_id", "home_team", "away_team"]  # Defined by me, football_home_goals{home_team="Liverpool", match_id="123"} = 4
)

away_goals_metric = Gauge(
    "football_away_goals",
    "Goals scored by away team",
    ["match_id", "home_team", "away_team"]
)

# API set-up
API_KEY = "aa5c9232acdc45c0955c38f9dd629599"
HEADERS = {"X-Auth-Token": API_KEY}             # How the API key is sent
BASE_URL = "https://api.football-data.org/v4"

# Declaring functions here
def fetch_matches():                            # Function to get match data
    url = f"{BASE_URL}/competitions/PL/matches" # The full URL for our match data, combined with our base URL
    response = requests.get(url, headers=HEADERS) # This sends a GET request for our API

    if response.status_code == 200:             # This checks if our request worked, 200 means success
        return response.json()                  # This convert the response into Python data, JSON dictionary
    else:                                       # If something fails, this prints the error
        print("Error:", response.status_code, response.text)
        return None                             # Meaning no data

def parse_match(match):                         # Takes one match from the API and simplifies it
    return {                                    # match is entire raw object from API
        "match_id": match["id"],                # Gets the match ID
        "home_team": match["homeTeam"]["name"],             # Gets the home team name
        "away_team": match["awayTeam"]["name"],             # Gets the away team name
        "home_goals": match["score"]["fullTime"]["home"],   # Gets the final score for the home team
        "away_goals": match["score"]["fullTime"]["away"],   # Gets the final score for the away team
        "status": match["status"]                           # Gets the match status, like 'finished' or 'live' etc.
    }

def get_parsed_matches():
    data = fetch_matches()

    if not data:
        return []

    return [parse_match(match) for match in data["matches"]]

def update_metrics(matches):
    for match in matches:
        labels = {
            "match_id": str(match["match_id"]),
            "home_team": match["home_team"],
            "away_team": match["away_team"]
        }

        home_goals.labels(**labels).set(match["home_goals"])
        away_goals.labels(**labels).set(match["away_goals"])

# API sends a list of items, we write a for loop that assigns each item to a 'match'


# This is where we actually start calling the script

if __name__ == "__main__":

    start_http_server(8000)
    print("Prometheus metrics running at http://localhost:8000/metrics")

    while True:
        matches = get_parsed_matches()

        # Clear old metric values (important cleanup step)
        home_goals_metric.clear()
        away_goals_metric.clear()

        for match in matches:
            labels = {
                "match_id": str(match["match_id"]),
                "home_team": match["home_team"],
                "away_team": match["away_team"]
            }

            home_goals_metric.labels(**labels).set(match["home_goals"] or 0) # Prometheus cannot accept empty values
            away_goals_metric.labels(**labels).set(match["away_goals"] or 0) # so we convert to 0

        time.sleep(30)

# if __name__ == "__main__":
#     parsed_matches = get_parsed_matches()
#
#     print("=== PARSED MATCHES ===")
#
#     for match in parsed_matches[:5]:
#         print(match)

# if __name__ == "__main__":                      # This means the code will only be run if it is executed here directly, it is a python feature
#     data = fetch_matches()                      # Calls the API and stores the results in data
#
#     if data:                         # Checks if data exists, so basically makes sure we haven't returned 'none' above
#         # 🔍 Step 1: Inspect raw JSON structure (first match)
#         print("=== RAW JSON SAMPLE ===")    # This is just for learning purposes, to see the raw data printed out
#         print(json.dumps(data["matches"][0], indent=2)) # Prints first match in full details, the 2 indent makes it readable
#
#         # 🔍 Step 2: Parsed output
#         print("\n=== PARSED MATCHES ===")
#         parsed_matches = [parse_match(match) for match in data["matches"]]  # Loop through all matches, apply parse_match to all
#
#         for match in parsed_matches[:5]:        #Prints the first 5 matches in clean format
#             print(match)


# "matches" comes directly from the API call and includes all that data for each game, has to be in quotes. match is my
# defined function for one item in "matches". parse_match(match) cleans the item to only include data I want.