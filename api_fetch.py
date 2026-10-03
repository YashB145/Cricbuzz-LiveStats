import os
import requests
import sqlite3

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
api_key = os.getenv("RAPIDAPI_KEY", "")

if not api_key:
    raise SystemExit("Set RAPIDAPI_KEY before running api_fetch.py")

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers, timeout=15)
response.raise_for_status()
data = response.json()

# connect to DB
conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

if 'typeMatches' in data:
    for type_match in data['typeMatches']:
        for series in type_match['seriesMatches']:
            if 'seriesAdWrapper' in series:
                for match in series['seriesAdWrapper']['matches']:
                    info = match['matchInfo']
                    score = match.get('matchScore', {})

                    team1 = info['team1']['teamName']
                    team2 = info['team2']['teamName']
                    status = info['status']

                    t1 = score.get('team1Score', {}).get('inngs1', {})
                    t2 = score.get('team2Score', {}).get('inngs1', {})

                    score_str = f"{t1.get('runs', '0')}/{t1.get('wickets', '0')} vs {t2.get('runs', '0')}/{t2.get('wickets', '0')}"

                    # INSERT into DB
                    cursor.execute("""
                        INSERT INTO matches (team1, team2, status, score)
                        VALUES (?, ?, ?, ?)
                    """, (team1, team2, status, score_str))

conn.commit()
conn.close()

print("✅ Data stored in database")
