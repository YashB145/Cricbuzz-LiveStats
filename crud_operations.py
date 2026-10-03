"""
CRUD Operations for Enhanced Cricket Database
Create, Read, Update, Delete operations for all tables
"""

import sqlite3
from datetime import datetime

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect("cricket.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==================== TEAMS CRUD ====================

def create_team(name, short_name, country, captain=None, coach=None):
    """Add a new team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO teams (name, short_name, country, captain, coach)
            VALUES (?, ?, ?, ?, ?)
        """, (name, short_name, country, captain, coach))

        conn.commit()
        team_id = cursor.lastrowid
        conn.close()

        return True, f"✅ Team '{name}' created successfully! (ID: {team_id})"
    except sqlite3.IntegrityError:
        return False, f"❌ Team '{name}' already exists"
    except Exception as e:
        return False, f"❌ Error creating team: {str(e)}"

def read_all_teams():
    """Get all teams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams ORDER BY name")
        teams = cursor.fetchall()
        conn.close()
        return True, [dict(t) for t in teams]
    except Exception as e:
        return False, str(e)

def update_team(team_id, name=None, short_name=None, country=None, captain=None, coach=None):
    """Update team details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current values
        cursor.execute("SELECT name, short_name, country, captain, coach FROM teams WHERE id = ?", (team_id,))
        current = cursor.fetchone()

        if not current:
            return False, "Team not found"

        # Use new values or keep existing ones
        new_name = name if name else current['name']
        new_short_name = short_name if short_name else current['short_name']
        new_country = country if country else current['country']
        new_captain = captain if captain else current['captain']
        new_coach = coach if coach else current['coach']

        cursor.execute("""
            UPDATE teams
            SET name = ?, short_name = ?, country = ?, captain = ?, coach = ?
            WHERE id = ?
        """, (new_name, new_short_name, new_country, new_captain, new_coach, team_id))

        conn.commit()
        conn.close()

        return True, f"✅ Team {team_id} updated successfully!"
    except Exception as e:
        return False, f"❌ Error updating team: {str(e)}"

def delete_team(team_id):
    """Delete a team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if team exists
        cursor.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
        if not cursor.fetchone():
            return False, "Team not found"

        cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        conn.commit()
        conn.close()

        return True, f"✅ Team {team_id} deleted successfully!"
    except Exception as e:
        return False, f"❌ Error deleting team: {str(e)}"

# ==================== VENUES CRUD ====================

def create_venue(name, city, country, capacity=None, pitch_type=None):
    """Add a new venue"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO venues (name, city, country, capacity, pitch_type)
            VALUES (?, ?, ?, ?, ?)
        """, (name, city, country, capacity, pitch_type))

        conn.commit()
        venue_id = cursor.lastrowid
        conn.close()

        return True, f"✅ Venue '{name}' created successfully! (ID: {venue_id})"
    except sqlite3.IntegrityError:
        return False, f"❌ Venue '{name}' already exists"
    except Exception as e:
        return False, f"❌ Error creating venue: {str(e)}"

def read_all_venues():
    """Get all venues"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM venues ORDER BY name")
        venues = cursor.fetchall()
        conn.close()
        return True, [dict(v) for v in venues]
    except Exception as e:
        return False, str(e)

# ==================== PLAYERS CRUD ====================

def create_player(name, full_name, team_id, role, batting_style=None, bowling_style=None, date_of_birth=None, nationality=None):
    """Add a new player"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO players (name, full_name, team_id, role, batting_style, bowling_style, date_of_birth, nationality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, full_name, team_id, role, batting_style, bowling_style, date_of_birth, nationality))

        conn.commit()
        player_id = cursor.lastrowid
        conn.close()

        return True, f"✅ Player '{name}' created successfully! (ID: {player_id})"
    except Exception as e:
        return False, f"❌ Error creating player: {str(e)}"

def read_all_players():
    """Get all players with team names"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.name as team_name
            FROM players p
            LEFT JOIN teams t ON p.team_id = t.id
            ORDER BY p.name
        """)
        players = cursor.fetchall()
        conn.close()
        return True, [dict(p) for p in players]
    except Exception as e:
        return False, str(e)

def read_players_by_team(team_id):
    """Get all players from a specific team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, t.name as team_name
            FROM players p
            LEFT JOIN teams t ON p.team_id = t.id
            WHERE p.team_id = ?
            ORDER BY p.name
        """, (team_id,))
        players = cursor.fetchall()
        conn.close()
        return True, [dict(p) for p in players]
    except Exception as e:
        return False, str(e)

# ==================== ENHANCED MATCHES CRUD ====================

def create_enhanced_match(series_id, team1_id, team2_id, venue_id=None, match_date=None, match_time=None, status=None):
    """Add a new enhanced match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO matches_enhanced (series_id, team1_id, team2_id, venue_id, match_date, match_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (series_id, team1_id, team2_id, venue_id, match_date, match_time, status))

        conn.commit()
        match_id = cursor.lastrowid
        conn.close()

        return True, f"✅ Enhanced match created successfully! (ID: {match_id})"
    except Exception as e:
        return False, f"❌ Error creating enhanced match: {str(e)}"

def read_all_enhanced_matches():
    """Get all enhanced matches with team and venue names"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, t1.name as team1_name, t2.name as team2_name, v.name as venue_name, s.name as series_name
            FROM matches_enhanced m
            LEFT JOIN teams t1 ON m.team1_id = t1.id
            LEFT JOIN teams t2 ON m.team2_id = t2.id
            LEFT JOIN venues v ON m.venue_id = v.id
            LEFT JOIN series s ON m.series_id = s.id
            ORDER BY m.id DESC
        """)
        matches = cursor.fetchall()
        conn.close()
        return True, [dict(m) for m in matches]
    except Exception as e:
        return False, str(e)

# ==================== LEGACY MATCHES CRUD (for backward compatibility) ====================

def create_match(team1, team2, status, score=None):
    """Add a new match to the legacy matches table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO matches (team1, team2, status, score)
            VALUES (?, ?, ?, ?)
        """, (team1, team2, status, score))

        conn.commit()
        match_id = cursor.lastrowid
        conn.close()

        return True, f"✅ Match created successfully! (ID: {match_id})"
    except Exception as e:
        return False, f"❌ Error creating match: {str(e)}"

def read_all_matches():
    """Get all matches from legacy table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, team1, team2, status, score FROM matches ORDER BY id DESC")
        matches = cursor.fetchall()
        conn.close()
        return True, [dict(m) for m in matches]
    except Exception as e:
        return False, str(e)

def read_match_by_id(match_id):
    """Get specific match by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, team1, team2, status, score FROM matches WHERE id = ?", (match_id,))
        match = cursor.fetchone()
        conn.close()

        if match:
            return True, dict(match)
        else:
            return False, "Match not found"
    except Exception as e:
        return False, str(e)

def read_matches_by_team(team_name):
    """Get all matches involving a specific team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, team1, team2, status, score FROM matches
            WHERE team1 = ? OR team2 = ?
            ORDER BY id DESC
        """, (team_name, team_name))
        matches = cursor.fetchall()
        conn.close()
        return True, [dict(m) for m in matches]
    except Exception as e:
        return False, str(e)

def read_matches_by_status(status):
    """Get all matches with a specific status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, team1, team2, status, score FROM matches
            WHERE status LIKE ?
            ORDER BY id DESC
        """, (f"%{status}%",))
        matches = cursor.fetchall()
        conn.close()
        return True, [dict(m) for m in matches]
    except Exception as e:
        return False, str(e)

def read_unique_teams():
    """Get list of unique teams"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT team1 as team FROM matches WHERE team1 IS NOT NULL ORDER BY team1")
        teams = cursor.fetchall()
        conn.close()
        return True, [t['team'] for t in teams]
    except Exception as e:
        return False, str(e)

def read_unique_statuses():
    """Get list of unique statuses"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT status FROM matches WHERE status IS NOT NULL ORDER BY status")
        statuses = cursor.fetchall()
        conn.close()
        return True, [s['status'] for s in statuses]
    except Exception as e:
        return False, str(e)

def update_match(match_id, team1=None, team2=None, status=None, score=None):
    """Update an existing match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get current values
        cursor.execute("SELECT team1, team2, status, score FROM matches WHERE id = ?", (match_id,))
        current = cursor.fetchone()

        if not current:
            return False, "Match not found"

        # Use new values or keep existing ones
        new_team1 = team1 if team1 else current['team1']
        new_team2 = team2 if team2 else current['team2']
        new_status = status if status else current['status']
        new_score = score if score else current['score']

        cursor.execute("""
            UPDATE matches
            SET team1 = ?, team2 = ?, status = ?, score = ?
            WHERE id = ?
        """, (new_team1, new_team2, new_status, new_score, match_id))

        conn.commit()
        conn.close()

        return True, f"✅ Match {match_id} updated successfully!"
    except Exception as e:
        return False, f"❌ Error updating match: {str(e)}"

def update_match_score(match_id, score):
    """Update only the score of a match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE matches SET score = ? WHERE id = ?", (score, match_id))
        conn.commit()
        conn.close()

        return True, f"✅ Match score updated!"
    except Exception as e:
        return False, f"❌ Error updating score: {str(e)}"

def update_match_status(match_id, status):
    """Update only the status of a match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE matches SET status = ? WHERE id = ?", (status, match_id))
        conn.commit()
        conn.close()

        return True, f"✅ Match status updated!"
    except Exception as e:
        return False, f"❌ Error updating status: {str(e)}"

def delete_match(match_id):
    """Delete a match from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if match exists
        cursor.execute("SELECT id FROM matches WHERE id = ?", (match_id,))
        if not cursor.fetchone():
            return False, "Match not found"

        cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))
        conn.commit()
        conn.close()

        return True, f"✅ Match {match_id} deleted successfully!"
    except Exception as e:
        return False, f"❌ Error deleting match: {str(e)}"

def delete_matches_by_status(status):
    """Delete all matches with a specific status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM matches WHERE status LIKE ?", (f"%{status}%",))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return True, f"✅ Deleted {deleted_count} matches with status '{status}'"
    except Exception as e:
        return False, f"❌ Error deleting matches: {str(e)}"

def get_database_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) as count FROM matches")
        stats['total_matches'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT team1) as count FROM matches")
        stats['unique_teams'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(DISTINCT status) as count FROM matches")
        stats['unique_statuses'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(score) as count FROM matches WHERE score IS NOT NULL")
        stats['matches_with_scores'] = cursor.fetchone()['count']

        return True, stats
    except Exception as e:
        return False, str(e)
