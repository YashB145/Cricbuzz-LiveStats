import os
import requests

def get_live_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/hscard"
    api_key = os.getenv("RAPIDAPI_KEY", "")

    if not api_key:
        return []

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return []

    live_matches = []

    for match in data.get("typeMatches", []):
        for series in match.get("seriesMatches", []):
            for game in series.get("seriesAdWrapper", {}).get("matches", []):

                info = game.get("matchInfo", {})
                score = game.get("matchScore", {})

                status = info.get("status", "")

                # 🔥 ONLY LIVE FILTER
                if "Live" in status or "In Progress" in status:

                    live_matches.append({
                        "team1": info.get("team1", {}).get("teamName"),
                        "team2": info.get("team2", {}).get("teamName"),
                        "status": status,
                        "score": score
                    })

    return live_matches
