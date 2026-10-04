import os
import requests
import sqlite3

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
api_key = os.getenv("RAPIDAPI_KEY", "")

if not api_key:
    print("ℹ️ Set RAPIDAPI_KEY before running api_fetch.py")
    raise SystemExit(0)

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code == 429:
        print("⚠️ RapidAPI quota exceeded (HTTP 429).")
        raise SystemExit(0)
    response.raise_for_status()
    data = response.json()
except (requests.RequestException, ValueError) as err:
    print(f"❌ API fetch error: {err}")
    raise SystemExit(0)

# connect to DB
conn = sqlite3.connect("cricket.db")
cursor = conn.cursor()

inserted = 0
if 'typeMatches' in data:
    for type_match in data.get('typeMatches', []):
        for series in type_match.get('seriesMatches', []):
            wrapper = series.get('seriesAdWrapper', {})
            for match in wrapper.get('matches', []):
                info = match.get('matchInfo', {})
                score = match.get('matchScore', {})

                team1 = info.get('team1', {}).get('teamName', 'Team 1')
                team2 = info.get('team2', {}).get('teamName', 'Team 2')
                status = info.get('status', 'Scheduled')

                t1 = score.get('team1Score', {}).get('inngs1', {})
                t2 = score.get('team2Score', {}).get('inngs1', {})

                score_str = f"{t1.get('runs', '0')}/{t1.get('wickets', '0')} vs {t2.get('runs', '0')}/{t2.get('wickets', '0')}"

                # INSERT into DB
                cursor.execute("""
                    INSERT INTO matches (team1, team2, status, score)
                    VALUES (?, ?, ?, ?)
                """, (team1, team2, status, score_str))
                inserted += 1

conn.commit()
conn.close()

print(f"✅ Stored {inserted} matches in database")

