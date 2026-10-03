"""Download real Cricsheet international matches into ml_international_matches.

Does not modify or delete the existing matches table or other project data.
"""
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import zipfile
from collections import Counter
from datetime import datetime
from typing import Any

import requests

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cricket.db")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cricsheet")
CRICSHEET_BASE = "https://cricsheet.org/downloads"

DATASETS = [
    "tests_json.zip",
    "odis_json.zip",
    "t20s_json.zip",
]

ALLOWED_FORMATS = {"Test", "ODI", "T20I"}
ALLOWED_TEAM_TYPE = "international"

# Official national sides as named in Cricsheet (ICC full members + associates).
NATIONAL_TEAMS = frozenset({
    "Afghanistan", "Australia", "Bangladesh", "England", "India", "Ireland",
    "New Zealand", "Pakistan", "South Africa", "Sri Lanka", "West Indies",
    "Zimbabwe", "Scotland", "Netherlands", "Namibia", "Nepal", "Oman",
    "United Arab Emirates", "U.A.E.", "UAE", "United States of America",
    "U.S.A.", "USA", "Papua New Guinea", "P.N.G.", "PNG", "Canada", "Kenya",
    "Hong Kong", "Jersey", "Guernsey", "Bermuda", "Italy", "Uganda",
    "Tanzania", "Malaysia", "Singapore", "Qatar", "Kuwait", "Bahrain",
    "Saudi Arabia", "Germany", "Austria", "Belgium", "France", "Spain",
    "Portugal", "Denmark", "Norway", "Sweden", "Finland", "Romania",
    "Czech Republic", "Czechia", "Thailand", "Japan", "Indonesia",
    "Philippines", "Vanuatu", "Fiji", "Samoa", "Cook Islands", "Argentina",
    "Brazil", "Chile", "Mexico", "Cayman Islands", "Botswana", "Nigeria",
    "Ghana", "Rwanda", "Malawi", "Mozambique", "Sierra Leone", "Cameroon",
    "Bhutan", "Maldives", "Isle of Man", "Malta", "Gibraltar", "Luxembourg",
    "Switzerland", "Greece", "Bulgaria", "Serbia", "Croatia", "Hungary",
    "Poland", "Estonia", "Slovenia", "Cyprus", "Turkey", "Iran", "China",
    "South Korea", "Korea", "Myanmar", "Cambodia", "Panama", "Bahamas",
    "Eswatini", "Lesotho", "Gambia", "Mali", "Seychelles", "East Africa",
    "Wales", "Nigeria", "Rwanda", "Serbia", "Belgium", "Austria",
    "United States", "Papua New Guinea", "ICC Members XI",
})

REJECT_NAME_RE = re.compile(
    r"("
    r"\bunder[-\s]?19s?\b|\bu[-]?19s?\b|\byouth\b|\bacademy\b|"
    r"\blions\b|\binvit(?:ation|ational)\b|\bpresident'?s\b|"
    r"\bboard\s+xi\b|\bworld\s+xi\b|\bafrica\s+xi\b|\basia\s+xi\b|"
    r"\brest of\b|\bcombined\b|\bclub\b|\bcounty\b|"
    r"\broyal challengers\b|\bsuper kings\b|\bknight riders\b|"
    r"\bsunrisers\b|\bcapitals\b|\bindians\b|\bsultan\b|"
    r"\bstrikers\b|\bheat\b|\bstars\b|\bscorchers\b|"
    r"\bA\b$"
    r")",
    re.IGNORECASE,
)

FRANCHISE_EXACT = frozenset({
    "RCB", "MI", "CSK", "KKR", "RR", "DC", "GT", "LSG", "PBKS", "SRH",
    "Mumbai Indians", "Chennai Super Kings", "Kolkata Knight Riders",
    "Royal Challengers Bengaluru", "Royal Challengers Bangalore",
    "Rajasthan Royals", "Delhi Capitals", "Delhi Daredevils",
    "Gujarat Titans", "Lucknow Super Giants", "Punjab Kings",
    "Kings XI Punjab", "Sunrisers Hyderabad", "Gujarat Lions",
    "Deccan Chargers", "Pune Warriors", "Rising Pune Supergiant",
    "Rising Pune Supergiants", "Kochi Tuskers Kerala",
    "Chennai Super Kings", "Rajsthan",
})

COUNTY_EXACT = frozenset({
    "Warwickshire", "Essex", "Hampshire", "Somerset", "Gloucestershire",
    "Lancashire", "Middlesex", "Northamptonshire", "Yorkshire", "Surrey",
    "Nottinghamshire", "Derbyshire", "Leicestershire", "Worcestershire",
    "Durham", "Kent", "Sussex", "Glamorgan",
})

EXHIBITION_RE = re.compile(
    r"warm[-\s]?up|exhibition|practice match|festival match|charity",
    re.IGNORECASE,
)

A_TEAM_RE = re.compile(r"\b([A-Za-z .]+)\s+A\b")


def ensure_ml_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ml_international_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT NOT NULL UNIQUE,
            match_date TEXT,
            format TEXT NOT NULL,
            gender TEXT,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            venue TEXT,
            winner TEXT,
            team1_runs INTEGER,
            team2_runs INTEGER,
            team1_wickets INTEGER,
            team2_wickets INTEGER,
            status TEXT,
            source TEXT DEFAULT 'cricsheet',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def download_zip(name: str) -> bytes:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, name)
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 1000:
        print(f"Using cached {name}")
        with open(cache_path, "rb") as handle:
            return handle.read()

    url = f"{CRICSHEET_BASE}/{name}"
    print(f"Downloading {url}")
    response = requests.get(url, timeout=180)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download {url}: HTTP {response.status_code}")
    content = response.content
    if len(content) < 1000 or not content.startswith(b"PK"):
        raise RuntimeError(f"{name} is not a valid zip ({len(content)} bytes)")
    with open(cache_path, "wb") as handle:
        handle.write(content)
    return content


def normalize_format(match_type: str, team_type: str) -> str | None:
    if (team_type or "").strip().lower() != ALLOWED_TEAM_TYPE:
        return None
    raw = (match_type or "").strip()
    if raw == "Test":
        return "Test"
    if raw == "ODI":
        return "ODI"
    if raw == "T20":
        return "T20I"
    return None


def is_national_team(name: str) -> bool:
    team = (name or "").strip()
    if not team:
        return False
    if team in FRANCHISE_EXACT or team in COUNTY_EXACT:
        return False
    if team.endswith(" A") or team.endswith(" A Women"):
        return False
    if REJECT_NAME_RE.search(team):
        return False
    if team not in NATIONAL_TEAMS:
        return False
    return True


def innings_totals(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = {}
    for innings in payload.get("innings") or []:
        team = innings.get("team")
        if not team:
            continue
        runs = 0
        wickets = 0
        for over in innings.get("overs") or []:
            for delivery in over.get("deliveries") or []:
                run_block = delivery.get("runs") or {}
                runs += int(run_block.get("total") or 0)
                wickets += len(delivery.get("wickets") or [])
        bucket = totals.setdefault(team, {"runs": 0, "wickets": 0})
        bucket["runs"] += runs
        bucket["wickets"] += wickets
    return totals


def parse_match(match_id: str, payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    info = payload.get("info") or {}
    teams = info.get("teams") or []
    if not isinstance(teams, list) or len(teams) != 2:
        return None, "invalid_teams"
    team1, team2 = str(teams[0]).strip(), str(teams[1]).strip()
    if team1 == team2:
        return None, "same_teams"

    team_type = str(info.get("team_type") or "").strip().lower()
    fmt = normalize_format(str(info.get("match_type") or ""), team_type)
    if fmt is None:
        return None, "not_international_format"

    if not is_national_team(team1) or not is_national_team(team2):
        return None, "non_national_team"

    event = info.get("event") or {}
    event_name = ""
    if isinstance(event, dict):
        event_name = str(event.get("name") or "")
    if EXHIBITION_RE.search(event_name) or EXHIBITION_RE.search(team1) or EXHIBITION_RE.search(team2):
        return None, "exhibition_or_warmup"

    dates = info.get("dates") or []
    if not dates:
        return None, "missing_date"
    match_date = str(dates[0]).strip()
    try:
        datetime.strptime(match_date, "%Y-%m-%d")
    except ValueError:
        return None, "invalid_date"

    outcome = info.get("outcome") or {}
    if not isinstance(outcome, dict):
        return None, "missing_outcome"

    result = str(outcome.get("result") or "").strip().lower()
    winner = outcome.get("winner") or outcome.get("eliminator") or outcome.get("bowl_out")
    winner = str(winner).strip() if winner else None

    if result == "no result":
        return None, "no_result"
    if result == "draw":
        status = "completed - draw"
        winner = None
    elif result == "tie" and not winner:
        status = "completed - tie"
        winner = None
    elif winner and winner in {team1, team2}:
        status = "completed"
    else:
        return None, "incomplete_or_invalid_outcome"

    gender_raw = str(info.get("gender") or "").strip().lower()
    gender = "women" if gender_raw == "female" else "men" if gender_raw == "male" else None

    venue = info.get("venue")
    venue = str(venue).strip() if venue else None

    totals = innings_totals(payload)
    t1 = totals.get(team1)
    t2 = totals.get(team2)
    team1_runs = t1["runs"] if t1 else None
    team2_runs = t2["runs"] if t2 else None
    team1_wickets = t1["wickets"] if t1 else None
    team2_wickets = t2["wickets"] if t2 else None

    if team1_runs is not None and team1_runs < 0:
        return None, "invalid_scores"
    if team2_runs is not None and team2_runs < 0:
        return None, "invalid_scores"

    return {
        "match_id": match_id,
        "match_date": match_date,
        "format": fmt,
        "gender": gender,
        "team1": team1,
        "team2": team2,
        "venue": venue,
        "winner": winner,
        "team1_runs": team1_runs,
        "team2_runs": team2_runs,
        "team1_wickets": team1_wickets,
        "team2_wickets": team2_wickets,
        "status": status,
        "source": "cricsheet",
    }, "accepted"


def collect() -> dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    ensure_ml_table(conn)

    files_processed = 0
    total_found = 0
    accepted = 0
    rejected = 0
    duplicates = 0
    inserted = 0
    reject_reasons: Counter[str] = Counter()
    format_counts: Counter[str] = Counter()
    gender_counts: Counter[str] = Counter()
    team_counts: Counter[str] = Counter()

    insert_sql = """
        INSERT OR IGNORE INTO ml_international_matches (
            match_id, match_date, format, gender, team1, team2, venue, winner,
            team1_runs, team2_runs, team1_wickets, team2_wickets, status, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for dataset in DATASETS:
        raw_zip = download_zip(dataset)
        with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
            json_names = [n for n in zf.namelist() if n.lower().endswith(".json") and not n.endswith("/")]
            print(f"{dataset}: {len(json_names)} json files")
            for name in json_names:
                files_processed += 1
                total_found += 1
                match_id = os.path.splitext(os.path.basename(name))[0]
                try:
                    with zf.open(name) as handle:
                        payload = json.loads(handle.read().decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
                    rejected += 1
                    reject_reasons["unreadable_json"] += 1
                    continue

                row, reason = parse_match(match_id, payload)
                if row is None:
                    rejected += 1
                    reject_reasons[reason] += 1
                    continue

                accepted += 1
                format_counts[row["format"]] += 1
                gender_counts[row["gender"] or "unknown"] += 1
                team_counts[row["team1"]] += 1
                team_counts[row["team2"]] += 1

                cursor = conn.execute(
                    insert_sql,
                    (
                        row["match_id"], row["match_date"], row["format"], row["gender"],
                        row["team1"], row["team2"], row["venue"], row["winner"],
                        row["team1_runs"], row["team2_runs"], row["team1_wickets"],
                        row["team2_wickets"], row["status"], row["source"],
                    ),
                )
                if cursor.rowcount == 0:
                    duplicates += 1
                else:
                    inserted += 1

        conn.commit()

    final_count = conn.execute("SELECT COUNT(*) FROM ml_international_matches").fetchone()[0]
    db_formats = conn.execute(
        "SELECT format, COUNT(*) FROM ml_international_matches GROUP BY format ORDER BY format"
    ).fetchall()
    db_genders = conn.execute(
        "SELECT gender, COUNT(*) FROM ml_international_matches GROUP BY gender ORDER BY gender"
    ).fetchall()
    db_teams = conn.execute(
        """
        SELECT team, COUNT(*) FROM (
            SELECT team1 AS team FROM ml_international_matches
            UNION ALL
            SELECT team2 AS team FROM ml_international_matches
        ) GROUP BY team ORDER BY COUNT(*) DESC
        """
    ).fetchall()
    conn.close()

    audit = {
        "files_processed": files_processed,
        "total_matches_found": total_found,
        "accepted_international_matches": accepted,
        "rejected_matches": rejected,
        "duplicates_skipped": duplicates,
        "records_inserted": inserted,
        "final_database_count": final_count,
        "reject_reasons": dict(reject_reasons),
        "accepted_by_format": dict(format_counts),
        "accepted_by_gender": dict(gender_counts),
        "db_by_format": {k: v for k, v in db_formats},
        "db_by_gender": {k: v for k, v in db_genders},
        "db_teams": db_teams,
    }
    return audit


def print_audit(audit: dict[str, Any]) -> None:
    print("\n===== CRICSHEET IMPORT AUDIT =====")
    print(f"files processed: {audit['files_processed']}")
    print(f"total matches found: {audit['total_matches_found']}")
    print(f"accepted international matches: {audit['accepted_international_matches']}")
    print(f"rejected matches: {audit['rejected_matches']}")
    print(f"duplicates skipped: {audit['duplicates_skipped']}")
    print(f"records inserted: {audit['records_inserted']}")
    print(f"final database count: {audit['final_database_count']}")
    print("rejected by reason:", audit["reject_reasons"])
    print("accepted by format:", audit["accepted_by_format"])
    print("accepted by gender:", audit["accepted_by_gender"])
    print("database by format:", audit["db_by_format"])
    print("database by gender:", audit["db_by_gender"])
    print("teams (match appearances):")
    for team, count in audit["db_teams"]:
        print(f"  {team}: {count}")


if __name__ == "__main__":
    print_audit(collect())
