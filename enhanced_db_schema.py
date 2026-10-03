import sqlite3

def create_enhanced_database():
    """Create enhanced database with all tables and relationships"""

    conn = sqlite3.connect("cricket.db")
    cursor = conn.cursor()

    # ==================== TEAMS TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        short_name TEXT,
        country TEXT,
        captain TEXT,
        coach TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==================== VENUES TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        city TEXT,
        country TEXT,
        capacity INTEGER,
        pitch_type TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==================== SERIES TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        format TEXT CHECK(format IN ('Test', 'ODI', 'T20', 'T20I')),
        year INTEGER,
        total_matches INTEGER,
        winner_team_id INTEGER,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (winner_team_id) REFERENCES teams(id)
    )
    """)

    # ==================== PLAYERS TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        full_name TEXT,
        team_id INTEGER,
        role TEXT CHECK(role IN ('Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper')),
        batting_style TEXT,
        bowling_style TEXT,
        date_of_birth DATE,
        nationality TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )
    """)

    # ==================== ENHANCED MATCHES TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches_enhanced (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER,
        team1_id INTEGER NOT NULL,
        team2_id INTEGER NOT NULL,
        venue_id INTEGER,
        match_date DATE,
        match_time TIME,
        status TEXT,
        result TEXT,
        winner_team_id INTEGER,
        margin TEXT,
        toss_winner_id INTEGER,
        toss_decision TEXT CHECK(toss_decision IN ('Bat', 'Bowl')),
        man_of_the_match_id INTEGER,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series(id),
        FOREIGN KEY (team1_id) REFERENCES teams(id),
        FOREIGN KEY (team2_id) REFERENCES teams(id),
        FOREIGN KEY (venue_id) REFERENCES venues(id),
        FOREIGN KEY (winner_team_id) REFERENCES teams(id),
        FOREIGN KEY (toss_winner_id) REFERENCES teams(id),
        FOREIGN KEY (man_of_the_match_id) REFERENCES players(id)
    )
    """)

    # ==================== SCORECARDS TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scorecards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        innings_number INTEGER CHECK(innings_number IN (1, 2, 3, 4)),
        runs INTEGER DEFAULT 0,
        wickets INTEGER DEFAULT 0,
        overs DECIMAL(4,1) DEFAULT 0.0,
        extras INTEGER DEFAULT 0,
        declared BOOLEAN DEFAULT FALSE,
        follow_on BOOLEAN DEFAULT FALSE,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches_enhanced(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )
    """)

    # ==================== PLAYER_PERFORMANCE TABLE ====================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        player_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        innings_number INTEGER CHECK(innings_number IN (1, 2, 3, 4)),
        batting_runs INTEGER DEFAULT 0,
        batting_balls INTEGER DEFAULT 0,
        batting_fours INTEGER DEFAULT 0,
        batting_sixes INTEGER DEFAULT 0,
        batting_out_type TEXT,
        bowling_overs DECIMAL(4,1) DEFAULT 0.0,
        bowling_maidens INTEGER DEFAULT 0,
        bowling_runs INTEGER DEFAULT 0,
        bowling_wickets INTEGER DEFAULT 0,
        fielding_catches INTEGER DEFAULT 0,
        fielding_runouts INTEGER DEFAULT 0,
        fielding_stumpings INTEGER DEFAULT 0,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (match_id) REFERENCES matches_enhanced(id),
        FOREIGN KEY (player_id) REFERENCES players(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )
    """)

    # ==================== INSERT SAMPLE DATA ====================

    # Sample Teams
    teams_data = [
        ('India', 'IND', 'India', 'Rohit Sharma', 'Rahul Dravid'),
        ('Australia', 'AUS', 'Australia', 'Pat Cummins', 'Andrew McDonald'),
        ('England', 'ENG', 'England', 'Ben Stokes', 'Brendon McCullum'),
        ('Pakistan', 'PAK', 'Pakistan', 'Babar Azam', 'Grant Bradburn'),
        ('South Africa', 'SA', 'South Africa', 'Temba Bavuma', 'Rob Walter'),
        ('New Zealand', 'NZ', 'New Zealand', 'Kane Williamson', 'Gary Stead'),
        ('West Indies', 'WI', 'West Indies', 'Kraigg Brathwaite', 'Phil Simmons'),
        ('Sri Lanka', 'SL', 'Sri Lanka', 'Dasun Shanaka', 'Mickey Arthur'),
        ('Bangladesh', 'BAN', 'Bangladesh', 'Shakib Al Hasan', 'Russell Domingo'),
        ('Afghanistan', 'AFG', 'Afghanistan', 'Hashmatullah Shahidi', 'Jonathan Trott')
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO teams (name, short_name, country, captain, coach)
    VALUES (?, ?, ?, ?, ?)
    """, teams_data)

    # Sample Venues
    venues_data = [
        ('Melbourne Cricket Ground', 'Melbourne', 'Australia', 100000, 'Grass'),
        ('Lord\'s Cricket Ground', 'London', 'England', 30000, 'Grass'),
        ('Eden Gardens', 'Kolkata', 'India', 68000, 'Grass'),
        ('Wankhede Stadium', 'Mumbai', 'India', 33000, 'Grass'),
        ('Sydney Cricket Ground', 'Sydney', 'Australia', 48000, 'Grass'),
        ('Old Trafford', 'Manchester', 'England', 26000, 'Grass'),
        ('Newlands Cricket Ground', 'Cape Town', 'South Africa', 25000, 'Grass'),
        ('Gaddafi Stadium', 'Lahore', 'Pakistan', 27000, 'Grass'),
        ('R Premadasa Stadium', 'Colombo', 'Sri Lanka', 35000, 'Grass'),
        ('Shere Bangla National Stadium', 'Dhaka', 'Bangladesh', 25000, 'Grass')
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO venues (name, city, country, capacity, pitch_type)
    VALUES (?, ?, ?, ?, ?)
    """, venues_data)

    # Sample Series
    series_data = [
        ('Border-Gavaskar Trophy 2023', 'Test', 2023, 4, None),
        ('World Cup 2023', 'ODI', 2023, 48, None),
        ('IPL 2024', 'T20', 2024, 74, None),
        ('Ashes 2023', 'Test', 2023, 5, None),
        ('T20 World Cup 2024', 'T20', 2024, 55, None)
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO series (name, format, year, total_matches, winner_team_id)
    VALUES (?, ?, ?, ?, ?)
    """, series_data)

    # Sample Players
    players_data = [
        ('Virat Kohli', 'Virat Kohli', 1, 'Batsman', 'Right-handed', None, '1988-11-05', 'India'),
        ('Rohit Sharma', 'Rohit Gurunath Sharma', 1, 'Batsman', 'Right-handed', 'Right-arm off-break', '1987-04-30', 'India'),
        ('Steve Smith', 'Steven Peter Devereux Smith', 2, 'Batsman', 'Right-handed', 'Right-arm leg-break', '1989-06-02', 'Australia'),
        ('Joe Root', 'Joseph Edward Root', 3, 'Batsman', 'Right-handed', 'Right-arm off-break', '1990-12-30', 'England'),
        ('Babar Azam', 'Mohammad Babar Azam', 4, 'Batsman', 'Right-handed', 'Right-arm off-break', '1994-10-15', 'Pakistan'),
        ('Kane Williamson', 'Kane Stuart Williamson', 6, 'Batsman', 'Right-handed', 'Right-arm off-break', '1990-08-18', 'New Zealand'),
        ('Jasprit Bumrah', 'Jasprit Jasbirsingh Bumrah', 1, 'Bowler', 'Right-handed', 'Right-arm fast', '1993-12-06', 'India'),
        ('Pat Cummins', 'Patrick James Cummins', 2, 'All-rounder', 'Right-handed', 'Right-arm fast', '1993-05-08', 'Australia'),
        ('James Anderson', 'James Michael Anderson', 3, 'Bowler', 'Left-handed', 'Right-arm fast-medium', '1982-07-30', 'England'),
        ('Shaheen Afridi', 'Shaheen Shah Afridi', 4, 'Bowler', 'Left-handed', 'Left-arm fast', '2000-04-06', 'Pakistan')
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO players (name, full_name, team_id, role, batting_style, bowling_style, date_of_birth, nationality)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, players_data)

    conn.commit()
    conn.close()

    print("✅ Enhanced database created with all tables and sample data!")

if __name__ == "__main__":
    create_enhanced_database()