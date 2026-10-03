"""
25 SQL Queries for Cricket Analytics
Beginner -> Intermediate -> Advanced
"""

import sqlite3

# Database connection
def get_db_connection():
    conn = sqlite3.connect("cricket.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==================== BEGINNER QUERIES ====================

def query_1_all_matches():
    """Query 1: Show all matches (legacy table)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches")
    return cursor.fetchall(), ["ID", "Team1", "Team2", "Status", "Score"]

def query_2_total_matches():
    """Query 2: Count total matches (legacy table)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_matches FROM matches")
    return cursor.fetchall(), ["Total Matches"]

def query_3_matches_by_status():
    """Query 3: Show matches grouped by status (legacy table)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) as match_count
        FROM matches
        GROUP BY status
    """)
    return cursor.fetchall(), ["Status", "Count"]

def query_4_team1_matches():
    """Query 4: Show all matches where team1 is displayed (legacy table)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT team1, team2, status FROM matches")
    return cursor.fetchall(), ["Team1", "Team2", "Status"]

def query_5_recent_matches():
    """Query 5: Show 5 most recent matches (legacy table)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT team1, team2, score, status FROM matches ORDER BY id DESC LIMIT 5")
    return cursor.fetchall(), ["Team1", "Team2", "Score", "Status"]

# ==================== ENHANCED QUERIES (Using new schema) ====================

def query_6_all_teams():
    """Query 6: Show all teams with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, short_name, country, captain, coach FROM teams ORDER BY name")
    return cursor.fetchall(), ["ID", "Name", "Short Name", "Country", "Captain", "Coach"]

def query_7_all_players_with_teams():
    """Query 7: Show all players with their team names (JOIN)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.role, p.batting_style, p.bowling_style, t.name as team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
        ORDER BY p.name
    """)
    return cursor.fetchall(), ["ID", "Name", "Role", "Batting Style", "Bowling Style", "Team"]

def query_8_team_player_count():
    """Query 8: Count players per team (GROUP BY + JOIN)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name as team_name, COUNT(p.id) as player_count
        FROM teams t
        LEFT JOIN players p ON t.id = p.team_id
        GROUP BY t.id, t.name
        ORDER BY player_count DESC
    """)
    return cursor.fetchall(), ["Team", "Player Count"]

def query_9_venues_by_country():
    """Query 9: Show venues grouped by country"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT country, COUNT(*) as venue_count, GROUP_CONCAT(name) as venues
        FROM venues
        GROUP BY country
        ORDER BY venue_count DESC
    """)
    return cursor.fetchall(), ["Country", "Venue Count", "Venues"]

def query_10_batsmen_only():
    """Query 10: Show only batsmen players"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.batting_style, t.name as team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
        WHERE p.role = 'Batsman'
        ORDER BY p.name
    """)
    return cursor.fetchall(), ["Name", "Batting Style", "Team"]

def query_11_bowlers_only():
    """Query 11: Show only bowlers with bowling style"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.bowling_style, t.name as team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
        WHERE p.role = 'Bowler'
        ORDER BY p.name
    """)
    return cursor.fetchall(), ["Name", "Bowling Style", "Team"]

def query_12_all_rounders():
    """Query 12: Show all-rounders (both batting and bowling)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.batting_style, p.bowling_style, t.name as team_name
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
        WHERE p.role = 'All-rounder'
        ORDER BY p.name
    """)
    return cursor.fetchall(), ["Name", "Batting Style", "Bowling Style", "Team"]

def query_13_venue_capacity_analysis():
    """Query 13: Analyze venue capacities"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, city, country, capacity,
               CASE
                   WHEN capacity >= 50000 THEN 'Large'
                   WHEN capacity >= 25000 THEN 'Medium'
                   ELSE 'Small'
               END as size_category
        FROM venues
        ORDER BY capacity DESC
    """)
    return cursor.fetchall(), ["Name", "City", "Country", "Capacity", "Size Category"]

def query_14_players_by_nationality():
    """Query 14: Count players by nationality"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nationality, COUNT(*) as player_count
        FROM players
        WHERE nationality IS NOT NULL
        GROUP BY nationality
        ORDER BY player_count DESC
    """)
    return cursor.fetchall(), ["Nationality", "Player Count"]

def query_15_team_captains():
    """Query 15: Show team captains"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name as team_name, captain, coach
        FROM teams
        WHERE captain IS NOT NULL
        ORDER BY name
    """)
    return cursor.fetchall(), ["Team", "Captain", "Coach"]

def query_16_enhanced_matches_overview():
    """Query 16: Show enhanced matches with team names (JOIN)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, t1.name as team1_name, t2.name as team2_name,
               v.name as venue_name, m.match_date, m.status
        FROM matches_enhanced m
        LEFT JOIN teams t1 ON m.team1_id = t1.id
        LEFT JOIN teams t2 ON m.team2_id = t2.id
        LEFT JOIN venues v ON m.venue_id = v.id
        ORDER BY m.id DESC
    """)
    return cursor.fetchall(), ["ID", "Team 1", "Team 2", "Venue", "Date", "Status"]

def query_17_matches_by_venue():
    """Query 17: Count matches per venue (using enhanced matches)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.name as venue_name, v.city, COUNT(m.id) as match_count
        FROM venues v
        LEFT JOIN matches_enhanced m ON v.id = m.venue_id
        GROUP BY v.id, v.name, v.city
        ORDER BY match_count DESC
    """)
    return cursor.fetchall(), ["Venue", "City", "Match Count"]

def query_18_player_roles_distribution():
    """Query 18: Distribution of player roles"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, COUNT(*) as count,
               ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM players) * 100, 2) as percentage
        FROM players
        GROUP BY role
        ORDER BY count DESC
    """)
    return cursor.fetchall(), ["Role", "Count", "Percentage"]

def query_19_teams_with_most_players():
    """Query 19: Teams with most players (TOP 5)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name as team_name, COUNT(p.id) as player_count
        FROM teams t
        LEFT JOIN players p ON t.id = p.team_id
        GROUP BY t.id, t.name
        ORDER BY player_count DESC
        LIMIT 5
    """)
    return cursor.fetchall(), ["Team", "Player Count"]

def query_20_venues_by_pitch_type():
    """Query 20: Venues grouped by pitch type"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pitch_type, COUNT(*) as venue_count,
               GROUP_CONCAT(name || ' (' || city || ')') as venues
        FROM venues
        GROUP BY pitch_type
        ORDER BY venue_count DESC
    """)
    return cursor.fetchall(), ["Pitch Type", "Venue Count", "Venues"]

def query_21_players_without_team():
    """Query 21: Players not assigned to any team"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, p.role, p.nationality
        FROM players p
        WHERE p.team_id IS NULL
        ORDER BY p.name
    """)
    return cursor.fetchall(), ["Name", "Role", "Nationality"]

def query_22_matches_without_venue():
    """Query 22: Enhanced matches without venue assigned"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, t1.name as team1, t2.name as team2, m.match_date, m.status
        FROM matches_enhanced m
        LEFT JOIN teams t1 ON m.team1_id = t1.id
        LEFT JOIN teams t2 ON m.team2_id = t2.id
        WHERE m.venue_id IS NULL
        ORDER BY m.id DESC
    """)
    return cursor.fetchall(), ["ID", "Team 1", "Team 2", "Date", "Status"]

def query_23_complete_team_info():
    """Query 23: Complete team information with player counts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.name, t.short_name, t.country, t.captain, t.coach,
               COUNT(p.id) as total_players,
               COUNT(CASE WHEN p.role = 'Batsman' THEN 1 END) as batsmen,
               COUNT(CASE WHEN p.role = 'Bowler' THEN 1 END) as bowlers,
               COUNT(CASE WHEN p.role = 'All-rounder' THEN 1 END) as all_rounders
        FROM teams t
        LEFT JOIN players p ON t.id = p.team_id
        GROUP BY t.id, t.name, t.short_name, t.country, t.captain, t.coach
        ORDER BY total_players DESC
    """)
    return cursor.fetchall(), ["Team", "Short Name", "Country", "Captain", "Coach", "Total Players", "Batsmen", "Bowlers", "All-rounders"]

def query_24_venue_match_analysis():
    """Query 24: Venue analysis with match statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.name as venue, v.city, v.country, v.capacity, v.pitch_type,
               COUNT(m.id) as total_matches,
               AVG(CASE WHEN m.winner_team_id = m.team1_id THEN 1 ELSE 0 END) as home_win_rate
        FROM venues v
        LEFT JOIN matches_enhanced m ON v.id = m.venue_id
        GROUP BY v.id, v.name, v.city, v.country, v.capacity, v.pitch_type
        ORDER BY total_matches DESC
    """)
    return cursor.fetchall(), ["Venue", "City", "Country", "Capacity", "Pitch Type", "Total Matches", "Home Win Rate"]

def query_25_comprehensive_database_summary():
    """Query 25: Comprehensive database summary with all statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    summary = []

    # Count all records
    tables = ['teams', 'venues', 'players', 'matches_enhanced', 'matches']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        summary.append((f"Total {table.title()}", count))

    # Additional statistics
    cursor.execute("SELECT COUNT(DISTINCT role) as count FROM players WHERE role IS NOT NULL")
    summary.append(("Player Roles", cursor.fetchone()['count']))

    cursor.execute("SELECT COUNT(DISTINCT country) as count FROM venues WHERE country IS NOT NULL")
    summary.append(("Countries with Venues", cursor.fetchone()['count']))

    cursor.execute("SELECT COUNT(DISTINCT nationality) as count FROM players WHERE nationality IS NOT NULL")
    summary.append(("Player Nationalities", cursor.fetchone()['count']))

    cursor.execute("SELECT COUNT(*) as count FROM teams WHERE captain IS NOT NULL")
    summary.append(("Teams with Captains", cursor.fetchone()['count']))

    conn.close()

    return summary, ["Metric", "Value"]
# Dictionary mapping query numbers to functions
QUERIES = {
    1: ("All Matches", query_1_all_matches),
    2: ("Total Match Count", query_2_total_matches),
    3: ("Matches by Status", query_3_matches_by_status),
    4: ("Team1 Matches", query_4_team1_matches),
    5: ("Recent 5 Matches", query_5_recent_matches),
    6: ("All Teams", query_6_all_teams),
    7: ("Players with Teams", query_7_all_players_with_teams),
    8: ("Team Player Count", query_8_team_player_count),
    9: ("Venues by Country", query_9_venues_by_country),
    10: ("Batsmen Only", query_10_batsmen_only),
    11: ("Bowlers Only", query_11_bowlers_only),
    12: ("All-rounders", query_12_all_rounders),
    13: ("Venue Capacity Analysis", query_13_venue_capacity_analysis),
    14: ("Players by Nationality", query_14_players_by_nationality),
    15: ("Team Captains", query_15_team_captains),
    16: ("Enhanced Matches Overview", query_16_enhanced_matches_overview),
    17: ("Matches by Venue", query_17_matches_by_venue),
    18: ("Player Roles Distribution", query_18_player_roles_distribution),
    19: ("Teams with Most Players", query_19_teams_with_most_players),
    20: ("Venues by Pitch Type", query_20_venues_by_pitch_type),
    21: ("Players Without Team", query_21_players_without_team),
    22: ("Matches Without Venue", query_22_matches_without_venue),
    23: ("Complete Team Info", query_23_complete_team_info),
    24: ("Venue Match Analysis", query_24_venue_match_analysis),
    25: ("Database Summary", query_25_comprehensive_database_summary),
}

def get_query(query_num):
    """Execute a query by number and return results"""
    if query_num in QUERIES:
        title, func = QUERIES[query_num]
        try:
            results, columns = func()
            return title, results, columns, None
        except Exception as e:
            return title, None, None, str(e)
    return "Query Not Found", None, None, "Invalid query number"

def get_all_query_titles():
    """Get list of all query titles"""
    return {num: title for num, (title, _) in QUERIES.items()}
