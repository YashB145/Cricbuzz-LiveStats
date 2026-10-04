import os
import requests

def get_live_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    api_key = os.getenv("RAPIDAPI_KEY", "")

    if not api_key:
        return []

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 429:
            return []
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
                state = info.get("state", "").lower()

                # ONLY LIVE FILTER
                if "live" in state or "in progress" in state or "Live" in status or "In Progress" in status:
                    t1_info = info.get("team1", {})
                    t2_info = info.get("team2", {})
                    t1_img = t1_info.get("imageId")
                    t2_img = t2_info.get("imageId")

                    live_matches.append({
                        "match_id": info.get("matchId"),
                        "team1": t1_info.get("teamName"),
                        "team2": t2_info.get("teamName"),
                        "team1_id": t1_info.get("teamId"),
                        "team2_id": t2_info.get("teamId"),
                        "team1_sname": t1_info.get("teamSName"),
                        "team2_sname": t2_info.get("teamSName"),
                        "team1_logo": f"https://static.cricbuzz.com/a/img/v1/i1/c{t1_img}/i.jpg" if t1_img else None,
                        "team2_logo": f"https://static.cricbuzz.com/a/img/v1/i1/c{t2_img}/i.jpg" if t2_img else None,
                        "status": status,
                        "score": score
                    })

    return live_matches

